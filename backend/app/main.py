import re
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import langdetect
import mlflow
from mlflow.tracking import MlflowClient
from transformers import pipeline

from app.core.config import get_settings
from app.schemas import AnalyzeRequest, RiskDecision
from app.ml.risk_engine import SentinelRiskEngine
from app.db.database import get_db, engine, Base
from app.models.models import PredictionLog

settings = get_settings()

# Ensure our database tables are created
Base.metadata.create_all(bind=engine)

# Global dictionary to hold our hot-loaded models
models = {}
risk_engine = SentinelRiskEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executes once when the server starts. Loads the heavy ML models into memory.
    """
    print("⏳ Booting Sentinel API...")
    
    # 1. Detect if we are running in the Hugging Face Cloud
    in_cloud = os.environ.get("SPACE_ID") is not None
    
    # 2. Local Environment: Try MLflow
    if not in_cloud:
        os.environ["MLFLOW_TRACKING_URI"] = settings.MLFLOW_TRACKING_URI
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        try:
            print(f"Connecting to MLflow at {settings.MLFLOW_TRACKING_URI}...")
            client = MlflowClient()
            eng_version = client.get_model_version_by_alias("Sentinel-English-Model", "production").version
            hing_version = client.get_model_version_by_alias("Sentinel-Hinglish-Model", "production").version
            
            print(f"⬇️ Downloading weights from MLflow Server...")
            models["english"] = mlflow.transformers.load_model(f"models:/Sentinel-English-Model/{eng_version}")
            models["hinglish"] = mlflow.transformers.load_model(f"models:/Sentinel-Hinglish-Model/{hing_version}")
            print("✅ All ML models hot-loaded successfully from MLflow!")
        except Exception as e:
            print(f"⚠️ MLflow connection failed: {e}")
            
    # 3. Cloud Environment (or MLflow failure fallback)
    if in_cloud or "english" not in models:
        print("☁️ Cloud environment detected. Pulling custom fine-tuned weights from Hugging Face Repo...")
        try:
            # Pull your exact custom-trained model weights from your personal HF model repo
            models["english"] = pipeline(
                "text-classification", 
                model="Ankit03/sentinel-model-weights", 
                subfolder="english_distilbert"
            )
            models["hinglish"] = pipeline(
                "text-classification", 
                model="Ankit03/sentinel-model-weights", 
                subfolder="hinglish_distilbert"
            )
            print("✅ Custom fine-tuned models loaded successfully from cloud repo!")
        except Exception as fallback_e:
            print(f"❌ Critical Failure loading custom weights: {fallback_e}")
            raise fallback_e
            
    yield
    
    print("🛑 Shutting down Sentinel API. Clearing memory.")
    models.clear()

# Initialize the FastAPI app
app = FastAPI(
    title="Sentinel Risk API",
    description="Real-Time AI Threat Detection Platform",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", summary="Health Check Endpoint")
def health_check():
    """
    Simple health check endpoint to verify that the API is running.
    """
    return {"status": "ok", "message": "API is running."}

@app.post("/api/v1/analyze", response_model=RiskDecision)
def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    # 1. Language Detection & Routing
    text_lower = request.text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    hinglish_hints = {"tu", "hai", "ki", "mil", "aaj", "ghar", "bahar", "dunga", "tera", "meri", "kya", "madarchod", "bhenchod"}
    is_hinglish = bool(hinglish_hints.intersection(words))
    
    try:
        lang = langdetect.detect(request.text)
        if is_hinglish or lang in ["hi", "ne", "ur", "id", "so"]:
            selected_pipeline = models["hinglish"]
            detected_lang_label = "hinglish"
        else:
            selected_pipeline = models["english"]
            detected_lang_label = "english"
    except:
        if is_hinglish:
            selected_pipeline = models["hinglish"]
            detected_lang_label = "hinglish"
        else:
            selected_pipeline = models["english"]
            detected_lang_label = "english"

    # 2. ML Inference
    try:
        prediction = selected_pipeline(request.text, truncation=True, max_length=128)[0]
        
        if prediction['label'] == 'SAFE':
            threat_prob = 1.0 - prediction['score']
        else:
            threat_prob = prediction['score']
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # 3. Apply Contextual Risk Engine
    risk_decision = risk_engine.calculate_risk(request.text, threat_prob)

    # 4. Log to Database
    log_entry = PredictionLog(
        text=request.text,
        language_detected=detected_lang_label,
        threat_probability=risk_decision.threat_probability,
        risk_level=risk_decision.risk_level,
        immediacy=risk_decision.immediacy,
        target_identified=risk_decision.target_identified,
        confidence=risk_decision.confidence,
        reason=risk_decision.reason
    )
    db.add(log_entry)
    db.commit()

    return risk_decision