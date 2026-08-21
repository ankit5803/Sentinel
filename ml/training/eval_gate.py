# ml/training/eval_gate.py
import mlflow
import mlflow.transformers
import pandas as pd
from sklearn.metrics import f1_score
import torch
import os
from transformers import pipeline # <-- Added this import so the Challenger can load!

# Ensure the Arena explicitly connects to the Dockerized MLflow server
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def run_arena(language: str, challenger_uri: str, test_data_path: str, target_class: str):
    print(f"\n{'='*50}")
    print(f"🏟️ WELCOME TO THE EVALUATION ARENA: {language.upper()}")
    print(f"{'='*50}")

    model_name = f"Sentinel-{language}-Model"
    champion_uri = f"models:/{model_name}@production"
    
    # 1. Load the Test Data
    print(f"📂 Loading test dataset: {test_data_path}")
    df = pd.read_csv(test_data_path)
    
    # To keep the eval fast for testing, let's randomly sample 500 rows if it's too large
    if len(df) > 500:
        df = df.sample(n=500, random_state=42).copy()
    
    # FIX: We now use 'sentence' instead of 'text'
    texts = df['sentence'].tolist()
    true_labels = df['label'].tolist()

    # Determine device (Use GPU if available for blazing fast inference)
    device = 0 if torch.cuda.is_available() else -1
    print(f"⚡ Compute Device set to: {'GPU' if device == 0 else 'CPU'}")

    # 2. Load the Champion (Production)
    print(f"\n👑 Loading Champion from MLflow: {champion_uri}")
    try:
        champion_pipe = mlflow.transformers.load_model(champion_uri, return_type="pipeline")
        champion_pipe.model.to(device)
    except Exception as e:
        print(f"⚠️ No Champion found (or failed to load). Error: {e}")
        champion_pipe = None

    # 3. Load the Challenger
    print(f"🥊 Loading Challenger from: {challenger_uri}")
    challenger_pipe = pipeline("text-classification", model=challenger_uri, tokenizer=challenger_uri, device=device)

    # 4. Fight! (Run Inference)
    print("\n⚔️ THE BATTLE BEGINS (Running Inference)...")
    
    # Champion Predictions
    champ_f1 = 0.0
    if champion_pipe:
        print("-> Champion is predicting...")
        champ_preds_raw = champion_pipe(texts, batch_size=16, truncation=True, max_length=128)
        champ_preds = [p['label'] for p in champ_preds_raw]
        champ_f1 = f1_score(true_labels, champ_preds, pos_label=target_class, zero_division=0)
    else:
        print("-> No champion to predict. Champion F1 defaults to 0.0")

    # Challenger Predictions
    print("-> Challenger is predicting...")
    challenger_preds_raw = challenger_pipe(texts, batch_size=16, truncation=True, max_length=128)
    challenger_preds = [p['label'] for p in challenger_preds_raw]
    challenger_f1 = f1_score(true_labels, challenger_preds, pos_label=target_class, zero_division=0)

    # 5. The Verdict
    print(f"\n{'='*50}")
    print("🏆 THE VERDICT")
    print(f"{'='*50}")
    print(f"👑 Champion F1 Score ({target_class}):   {champ_f1:.4f}")
    print(f"🥊 Challenger F1 Score ({target_class}): {challenger_f1:.4f}")

    if challenger_f1 > champ_f1:
        print("\n🎉 CHALLENGER WINS! The new model is better.")
        print(f"Next Step (Automated): Register Challenger to MLflow and tag as @production.")
        return True
    else:
        print("\n❌ CHALLENGER DEFEATED! The production model remains safer.")
        print("Next Step (Automated): Discard Challenger. Keep Production intact.")
        return False

if __name__ == "__main__":
    ENGLISH_CHALLENGER_PATH = "./artifacts/english_distilbert"
    ENGLISH_TEST_DATA = "../data/processed/english_test.csv"
    
    run_arena(
        language="English",
        challenger_uri=ENGLISH_CHALLENGER_PATH,
        test_data_path=ENGLISH_TEST_DATA,
        target_class="VIOLENT_THREAT"
    )