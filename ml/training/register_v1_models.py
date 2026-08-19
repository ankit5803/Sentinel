# ml/training/register_v1_models.py
import mlflow
import mlflow.transformers
from transformers import pipeline
import os

# 1. Connect to the local MLflow server we just started
mlflow.set_tracking_uri("http://localhost:5000")

# 2. Define the paths to your local models
# Assuming you run this from the ml/training/ folder
ENGLISH_MODEL_PATH = "./artifacts/english_distilbert"
HINGLISH_MODEL_PATH = "./artifacts/hinglish_distilbert"

def register_model(language: str, model_path: str, model_name: str):
    print(f"\n🚀 Registering {language} model as Version 1...")
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model path {model_path} not found.")
        return

    # Create or set the MLflow Experiment
    mlflow.set_experiment(f"Sentinel-{language}")

    # Load the model via HuggingFace Pipeline
    print("Loading model into memory...")
    pipe = pipeline("text-classification", model=model_path, tokenizer=model_path)

    # Start an MLflow tracking run
    with mlflow.start_run(run_name="V1_Initial_Training"):
        # Log the model to the registry
        model_info = mlflow.transformers.log_model(
            transformers_model=pipe,
            artifact_path="model",
            registered_model_name=model_name
        )
        
        # We also create an alias 'production' pointing to this new version
        client = mlflow.tracking.MlflowClient()
        
        # MLflow registers it as version 1 because it's the first time
        client.set_registered_model_alias(
            name=model_name, 
            alias="production", 
            version="1"
        )
        
        print(f"✅ {language} model registered successfully!")
        print(f"🔗 Model URI: {model_info.model_uri}")
        print(f"🏷️ Tagged as @production")

if __name__ == "__main__":
    # Register English
    register_model("English", ENGLISH_MODEL_PATH, "Sentinel-English-Model")
    
    # Register Hinglish
    register_model("Hinglish", HINGLISH_MODEL_PATH, "Sentinel-Hinglish-Model")