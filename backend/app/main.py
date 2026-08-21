# backend/app/main.py
import re
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import langdetect
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
    Executes once when the server starts. Loads the heavy ML models into memory
    directly from the absolute container path resolved via Path(__file__).
    """
    print("⏳ Booting Sentinel API...")
    
    # Resolve absolute paths inside the container (/app/ml/artifacts/...)
    BASE_DIR = Path(__file__).resolve().parent 
    eng_dir = BASE_DIR / "ml" / "artifacts" / "english_distilbert"
    hing_dir = BASE_DIR / "ml" / "artifacts" / "hinglish_distilbert"

    try:
        print(f"Loading English model from: {eng_dir}")
        models["english"] = pipeline("text-classification", model=str(eng_dir), tokenizer=str(eng_dir))

        print(f"Loading Hinglish model from: {hing_dir}")
        models["hinglish"] = pipeline("text-classification", model=str(hing_dir), tokenizer=str(hing_dir))

        print("✅ All ML models hot-loaded successfully from local disk!")
    except Exception as e:
        print(f"❌ Failed to load local models: {e}")
        raise e
    
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
    Returns a JSON response with status and message.
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