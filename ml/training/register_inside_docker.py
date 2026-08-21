# ml/training/register_inside_docker.py
import mlflow
from mlflow.tracking import MlflowClient
from transformers import pipeline
import os

MLFLOW_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_URI)
client = MlflowClient(tracking_uri=MLFLOW_URI)

base_dir = os.path.dirname(os.path.abspath(__file__))

models_to_register = [
    {"name": "Sentinel-English-Model", "path": os.path.join(base_dir, "artifacts", "english_distilbert")},
    {"name": "Sentinel-Hinglish-Model", "path": os.path.join(base_dir, "artifacts", "hinglish_distilbert")}
]

print(f"🔗 Connecting to MLflow at {MLFLOW_URI}...")

for m in models_to_register:
    print(f"\n📦 Looking for model at: {m['path']}")
    if not os.path.exists(m["path"]):
        print(f"❌ Path not found: {m['path']}")
        continue

    print(f"📦 Loading pipeline for {m['name']}...")
    pipe = pipeline("text-classification", model=m["path"], tokenizer=m["path"])

    print(f"🚀 Logging transformer model to MLflow...")
    with mlflow.start_run(run_name=f"docker-native-{m['name']}") as run:
        mlflow.transformers.log_model(
            transformers_model=pipe,
            artifact_path="model",
            pip_requirements=["torch>=2.0.0", "transformers>=4.40.0"]
        )
        run_id = run.info.run_id

    mv = mlflow.register_model(f"runs:/{run_id}/model", m["name"])
    client.set_registered_model_alias(name=m["name"], alias="production", version=mv.version)
    print(f"✅ Successfully registered {m['name']} as version {mv.version} with alias @production")

print("\n🎉 All models successfully registered with native transformers flavor!")