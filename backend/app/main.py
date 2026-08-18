# backend/app/main.py
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from transformers import pipeline
import langdetect

from app.core.config import get_settings
from app.schemas import AnalyzeRequest, RiskDecision
from app.ml.risk_engine import SentinelRiskEngine
from app.db.database import get_db, engine, Base
from app.models.models import PredictionLog

settings = get_settings()

# Ensure our database tables are created (in a real prod app, use Alembic for migrations)
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
    print(f"Loading English model from: {settings.ENGLISH_MODEL_PATH}")
    
    try:
        # Load Hugging Face pipelines using your fine-tuned artifacts
        models["english"] = pipeline(
            "text-classification", 
            model=settings.ENGLISH_MODEL_PATH, 
            tokenizer=settings.ENGLISH_MODEL_PATH
        )
        models["hinglish"] = pipeline(
            "text-classification", 
            model=settings.HINGLISH_MODEL_PATH, 
            tokenizer=settings.HINGLISH_MODEL_PATH
        )
        print("✅ All ML models hot-loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load models. Ensure training artifacts exist. Error: {e}")
    
    yield # The application runs while yielded
    
    # Executes when server shuts down
    print("🛑 Shutting down Sentinel API. Clearing memory.")
    models.clear()

# Initialize the FastAPI app
app = FastAPI(
    title="Sentinel Risk API",
    description="Real-Time AI Threat Detection Platform",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/api/v1/analyze", response_model=RiskDecision)
def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for text analysis.
    1. Detects language (with manual heuristic overrides).
    2. Routes to correct DistilBERT model.
    3. Passes output to Risk Engine.
    4. Logs to PostgreSQL.
    """
    # 1. Language Detection & Routing
    text_lower = request.text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    # Common structural Hinglish/Hindi romanized words
    hinglish_hints = {"tu", "hai", "ki", "mil", "aaj", "ghar", "bahar", "dunga", "tera", "meri", "kya", "madarchod", "bhenchod"}
    
    is_hinglish = bool(hinglish_hints.intersection(words))
    
    try:
        lang = langdetect.detect(request.text)
        # Route to Hinglish if it hits our hints, OR if langdetect accidentally guesses similar latin-script languages
        if is_hinglish or lang in ["hi", "ne", "ur", "id", "so"]:
            selected_pipeline = models["hinglish"]
            detected_lang_label = "hinglish"
        else:
            selected_pipeline = models["english"]
            detected_lang_label = "english"
    except:
        # Fallback if langdetect throws an error
        if is_hinglish:
            selected_pipeline = models["hinglish"]
            detected_lang_label = "hinglish"
        else:
            selected_pipeline = models["english"]
            detected_lang_label = "english"

    # 2. ML Inference
    try:
        # Pipeline returns e.g. [{'label': 'VIOLENT_THREAT', 'score': 0.88}]
        prediction = selected_pipeline(request.text, truncation=True, max_length=128)[0]
        
        # We want the probability of the THREAT/ABUSE class specifically.
        # If the model predicts SAFE, the threat probability is (1 - safe_score)
        if prediction['label'] == 'SAFE':
            threat_prob = 1.0 - prediction['score']
        else:
            threat_prob = prediction['score']
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # 3. Apply Contextual Risk Engine
    risk_decision = risk_engine.calculate_risk(request.text, threat_prob)

    # 4. Log to Database (The Vault)
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

    # 5. Return to User
    return risk_decision