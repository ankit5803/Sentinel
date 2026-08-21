# ml/training/register_to_docker_mlflow.py
import mlflow
from mlflow.tracking import MlflowClient
import os

MLFLOW_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_URI)
client = MlflowClient(tracking_uri=MLFLOW_URI)

# Since they are mounted, we can reference them directly or log them cleanly
models = [
    {"name": "Sentinel-English-Model", "path": "english_distilbert"},
    {"name": "Sentinel-Hinglish-Model", "path": "hinglish_distilbert"}
]

print(f"🔗 Connecting to Docker MLflow at {MLFLOW_URI}...")

for m in models:
    print(f"\n📦 Registering {m['name']}...")
    
    with mlflow.start_run(run_name=f"docker-init-{m['name']}") as run:
        # Log using a local artifact path URI
        mlflow.log_artifacts(f"./artifacts/{m['path']}", artifact_path="model")
        run_id = run.info.run_id

    # Register model
    mv = mlflow.register_model(f"runs:/{run_id}/model", m["name"])
    
    # Set alias
    client.set_registered_model_alias(
        name=m["name"],
        alias="production",
        version=mv.version
    )
    print(f"✅ Set alias @production for {m['name']} (version {mv.version})")

print("\n🚀 Done!")