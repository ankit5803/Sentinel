import os
import sys
import torch
import pandas as pd
from sklearn.metrics import f1_score
from transformers import pipeline
import mlflow
import mlflow.transformers
from huggingface_hub import HfApi

# Ensure MLflow tracking URI points locally
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def run_arena(language: str, challenger_uri: str, test_data_path: str, target_class: str):
    print(f"\n{'='*50}")
    print(f"🏟️ WELCOME TO THE EVALUATION ARENA: {language.upper()}")
    print(f"{'='*50}")

    model_name = f"Sentinel-{language.capitalize()}-Model"
    champion_uri = f"models:/{model_name}@production"
    
    # 1. Load the Test Data
    print(f"📂 Loading test dataset: {test_data_path}")
    try:
        df = pd.read_csv(test_data_path)
    except Exception as e:
        print(f"⚠️ Failed to load test data from {test_data_path} (using mock fallback): {e}")
        # Fallback dummy test set if file is missing
        text_key = 'sentence' if language.lower() == 'english' else 'text'
        df = pd.DataFrame({text_key: ["test text input"], "label": [target_class]})
    
    if len(df) > 500:
        df = df.sample(n=500, random_state=42).copy()
    
    # Ensure correct column name for text
    text_col = 'sentence' if 'sentence' in df.columns else 'text'
    texts = df[text_col].tolist()
    true_labels = df['label'].tolist()

    device = 0 if torch.cuda.is_available() else -1
    print(f"⚡ Compute Device set to: {'GPU' if device == 0 else 'CPU'}")

    # 2. Load the Champion (Production) from MLflow
    print(f"\n👑 Loading Champion from MLflow: {champion_uri}")
    try:
        champion_pipe = mlflow.transformers.load_model(champion_uri, return_type="pipeline")
        champion_pipe.model.to(device)
    except Exception as e:
        print(f"⚠️ No active MLflow Champion found for {language}. Defaulting Champion F1 to 0.0.")
        champion_pipe = None

    # 3. Load the Challenger
    print(f"🥊 Loading Challenger from: {challenger_uri}")
    try:
        challenger_pipe = pipeline("text-classification", model=challenger_uri, tokenizer=challenger_uri, device=device)
    except Exception as e:
        print(f"❌ Failed to load challenger model: {e}")
        return False

    # 4. Fight! (Run Inference)
    print("\n⚔️ THE BATTLE BEGINS (Running Inference)...")
    
    champ_f1 = 0.0
    if champion_pipe:
        print("-> Champion is predicting...")
        champ_preds_raw = champion_pipe(texts, batch_size=16, truncation=True, max_length=128)
        champ_preds = [p['label'] for p in champ_preds_raw]
        champ_f1 = f1_score(true_labels, champ_preds, pos_label=target_class, zero_division=0)

    print("-> Challenger is predicting...")
    challenger_preds_raw = challenger_pipe(texts, batch_size=16, truncation=True, max_length=128)
    challenger_preds = [p['label'] for p in challenger_preds_raw]
    challenger_f1 = f1_score(true_labels, challenger_preds, pos_label=target_class, zero_division=0)

    # 5. The Verdict & Dynamic Version Deployment Sync
    print(f"\n{'='*50}")
    print("🏆 THE VERDICT")
    print(f"{'='*50}")
    print(f"👑 Champion F1 Score ({target_class}):   {champ_f1:.4f}")
    print(f"🥊 Challenger F1 Score ({target_class}): {challenger_f1:.4f}")

    if challenger_f1 >= champ_f1:
        print(f"\n🎉 CHALLENGER WINS! The new {language} model is better.")
        print(f"🚀 Registering {language} Challenger to MLflow registry...")
        
        latest_version = "1"
        try:
            result = mlflow.register_model(model_uri=challenger_uri, name=model_name)
            latest_version = result.version
            
            client = mlflow.tracking.MlflowClient()
            client.set_registered_model_alias(name=model_name, alias="production", version=latest_version)
            print(f"✅ Dynamically registered and promoted version {latest_version} to alias @production!")
        except Exception as e:
            print(f"⚠️ MLflow registration skipped/failed: {e}")

        # Push winning weights directly to the language-specific folder on Hugging Face Hub
        print(f"☁️ Syncing winning {language} model weights to Hugging Face Hub...")
        try:
            api = HfApi()
            api.upload_folder(
                folder_path=challenger_uri,
                path_in_repo=f"{language.lower()}_distilbert",
                repo_id="Ankit03/sentinel-model-weights",
                repo_type="model",
                commit_message=f"Auto-promoted {language} model version {latest_version}"
            )
            print(f"🚀 Successfully pushed {language} weights to https://huggingface.co/Ankit03/sentinel-model-weights/tree/main/{language.lower()}_distilbert !")
        except Exception as e:
            print(f"❌ Failed to push to Hugging Face Hub: {e}")

        return True
    else:
        print(f"\n❌ CHALLENGER DEFEATED! The production {language} model remains safer.")
        return False

if __name__ == "__main__":
    # Standalone test execution block
    run_arena(
        language="English",
        challenger_uri="backend/app/ml/artifacts/english_distilbert",
        test_data_path="ml/data/processed/english_test.csv",
        target_class="VIOLENT_THREAT"
    )