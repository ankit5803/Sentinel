import mlflow
from mlflow.tracking import MlflowClient
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

MLFLOW_TRACKING_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()

models_to_register = [
    {"name": "Sentinel-English-Model", "path": "backend/app/ml/artifacts/english_distilbert"},
    {"name": "Sentinel-Hinglish-Model", "path": "backend/app/ml/artifacts/hinglish_distilbert"}
]

print(f"🔗 Connecting to Docker MLflow at {MLFLOW_TRACKING_URI}...\n")

for m in models_to_register:
    print(f"📦 Registering {m['name']}...")
    
    # Load the local model into memory as a HuggingFace Pipeline
    pipe = pipeline("text-classification", model=m['path'], tokenizer=m['path'], device="cpu")
    
    # Log and register it using MLflow's official Transformers flavor
    with mlflow.start_run(run_name=f"docker-init-{m['name']}") as run:
        mlflow.transformers.log_model(
            transformers_model=pipe,
            artifact_path="model",
            registered_model_name=m['name'],
            pip_requirements=["torch", "transformers"]  # <--- FIX: Bypass the TF bug
        )
        
    # Find the latest version we just registered
    latest_version = client.search_model_versions(f"name='{m['name']}'")[0].version
    
    # Set the @production alias so main.py can find it!
    client.set_registered_model_alias(m['name'], "production", latest_version)
    
    print(f"✅ Created version '{latest_version}' and tagged as @production\n")

print("🚀 Done! MLflow is fully seeded.")