import re
import os
import torch
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import langdetect
import mlflow
from mlflow.tracking import MlflowClient
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import get_settings
from app.schemas import AnalyzeRequest, RiskDecision
from app.ml.risk_engine import SentinelRiskEngine
from app.db.database import get_db, engine, Base
from app.models.models import PredictionLog

# Safely import Hugging Face spaces for ZeroGPU support
try:
    import spaces
    gpu_decorator = spaces.GPU
except ImportError:
    # Graceful fallback for local development
    def gpu_decorator(func):
        return func

settings = get_settings()
Base.metadata.create_all(bind=engine)

# Global dictionary to hold models & tokenizers directly (bypassing pipelines)
models = {}
risk_engine = SentinelRiskEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Booting Sentinel API...")
    in_cloud = os.environ.get("SPACE_ID") is not None

    if not in_cloud:
        os.environ["MLFLOW_TRACKING_URI"] = settings.MLFLOW_TRACKING_URI
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        try:
            client = MlflowClient()
            eng_version = client.get_model_version_by_alias("Sentinel-English-Model", "production").version
            hing_version = client.get_model_version_by_alias("Sentinel-Hinglish-Model", "production").version

            eng_pipe = mlflow.transformers.load_model(f"models:/Sentinel-English-Model/{eng_version}")
            hing_pipe = mlflow.transformers.load_model(f"models:/Sentinel-Hinglish-Model/{hing_version}")

            models["english"] = {"model": eng_pipe.model, "tokenizer": eng_pipe.tokenizer}
            models["hinglish"] = {"model": hing_pipe.model, "tokenizer": hing_pipe.tokenizer}
            print("✅ All ML models hot-loaded successfully from MLflow!")
        except Exception as e:
            print(f"⚠️ MLflow connection failed: {e}")

    if in_cloud or "english" not in models:
        print("☁️ Cloud environment detected. Explicitly loading custom models from HF repo...")
        try:
            eng_tokenizer = AutoTokenizer.from_pretrained("Ankit03/sentinel-model-weights", subfolder="english_distilbert")
            eng_model = AutoModelForSequenceClassification.from_pretrained("Ankit03/sentinel-model-weights", subfolder="english_distilbert")
            models["english"] = {"model": eng_model, "tokenizer": eng_tokenizer}

            hing_tokenizer = AutoTokenizer.from_pretrained("Ankit03/sentinel-model-weights", subfolder="hinglish_distilbert")
            hing_model = AutoModelForSequenceClassification.from_pretrained("Ankit03/sentinel-model-weights", subfolder="hinglish_distilbert")
            models["hinglish"] = {"model": hing_model, "tokenizer": hing_tokenizer}

            print("✅ Custom fine-tuned models loaded successfully via explicit AutoClasses!")
        except Exception as fallback_e:
            print(f"❌ Critical Failure loading custom weights: {fallback_e}")
            raise fallback_e

    yield
    print("🛑 Shutting down Sentinel API. Clearing memory.")
    models.clear()

app = FastAPI(
    title="Sentinel Risk API",
    description="Real-Time AI Threat Detection Platform",
    version="1.0.0",
    lifespan=lifespan
)

@gpu_decorator
def run_inference(lang_label: str, text: str):
    """
    Native PyTorch inference for ZeroGPU context.
    This strips away HF pipeline wrappers to avoid internal JSON serialization bugs.
    """
    model = models[lang_label]["model"]
    tokenizer = models[lang_label]["tokenizer"]

    # Dynamically acquire the ZeroGPU hardware context
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Tokenize — explicitly disable token_type_ids so we never generate a key
    # that DistilBERT's forward() doesn't accept in the first place.
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        return_token_type_ids=False,
    )

    # Belt-and-suspenders: some tokenizer configs ignore return_token_type_ids
    # depending on version, so strip it again defensively if it slipped through.
    inputs.pop("token_type_ids", None)

    # Push to GPU
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Execute inference securely
    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    predicted_id = outputs.logits.argmax(dim=-1).item()

    # EXPLICITLY cast to native python types so ZeroGPU's serializer doesn't crash
    score = float(probs[predicted_id].item())
    label = str(model.config.id2label[predicted_id])

    return {"label": label, "score": score}

@app.get("/health", summary="Health Check Endpoint")
def health_check():
    return {"status": "ok", "message": "API is running."}

@app.post("/api/v1/analyze", response_model=RiskDecision)
def analyze_text(request: AnalyzeRequest, db: Session = Depends(get_db)):
    text_lower = request.text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))

    hinglish_hints = {"tu", "hai", "ki", "mil", "aaj", "ghar", "bahar", "dunga", "tera", "meri", "kya", "madarchod", "bhenchod"}
    is_hinglish = bool(hinglish_hints.intersection(words))

    try:
        lang = langdetect.detect(request.text)
        if is_hinglish or lang in ["hi", "ne", "ur", "id", "so"]:
            detected_lang_label = "hinglish"
        else:
            detected_lang_label = "english"
    except:
        if is_hinglish:
            detected_lang_label = "hinglish"
        else:
            detected_lang_label = "english"

    try:
        # Run inference natively
        prediction = run_inference(detected_lang_label, request.text)

        # Check label confidently regardless of model format (SAFE vs LABEL_0)
        if prediction['label'].upper() in ['SAFE', 'LABEL_0']:
            threat_prob = 1.0 - prediction['score']
        else:
            threat_prob = prediction['score']

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {repr(e)}")

    risk_decision = risk_engine.calculate_risk(request.text, threat_prob)

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