from prefect import task, flow
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# Import our Eval Gate!
from eval_gate import run_arena

# FIX 1: Corrected Database URL for Docker Compose
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sentinel_db")

@task(name="1. Extract Live Traffic", retries=2, retry_delay_seconds=5)
def extract_live_data(language: str):
    print(f"🗄️ [Task 1] Extracting drifted {language} data from PostgreSQL...")
    engine = create_engine(DB_URL)
    query = f"SELECT text FROM prediction_logs WHERE language_detected = '{language.lower()}'"
    
    df = pd.read_sql(query, engine).dropna()
    print(f"✅ Extracted {len(df)} recent logs for retraining.")
    
    # In a real scenario, we would label these (via weak-supervision or human-in-the-loop)
    # For this pipeline, we will simulate appending them to the dataset.
    return len(df)

@task(name="2. Train Challenger Model")
def train_challenger(language: str, row_count: int, mock: bool = True):
    print(f"🥊 [Task 2] Training new {language} Challenger model on {row_count} new rows...")
    
    if mock:
        print("⏩ MOCK MODE ON: Simulating a 15-minute DistilBERT GPU training job...")
        time.sleep(3) # Simulate training time for the tutorial
        # FIX 2: Point to the new artifact location
        challenger_path = f"backend/app/ml/artifacts/{language.lower()}_distilbert"
    else:
        # This would trigger your actual train_distilbert.py via subprocess
        print("🔥 REAL MODE: Booting up PyTorch and CUDA...")
        import subprocess
        subprocess.run(["python", "train_distilbert.py"])
        challenger_path = f"backend/app/ml/artifacts/{language.lower()}_distilbert_v2"
        
    print(f"✅ Challenger model saved at {challenger_path}")
    return challenger_path

@task(name="3. The Evaluation Gate")
def run_evaluation_gate(language: str, challenger_uri: str):
    print(f"⚔️ [Task 3] Sending Challenger to the Arena against Production...")
    
    # FIX 3: Corrected path from root directory
    test_data_path = f"ml/data/processed/{language.lower()}_test.csv"
    target_class = "VIOLENT_THREAT" if language.lower() == "english" else "NON_VIOLENT_ABUSE"
    
    # Call the exact arena function we built on Day 7!
    passed_gate = run_arena(
        language=language, 
        challenger_uri=challenger_uri, 
        test_data_path=test_data_path,
        target_class=target_class
    )
    
    if passed_gate:
        print("🚀 PIPELINE SUCCESS: Challenger promoted to Production!")
    else:
        print("🛡️ PIPELINE SUCCESS: Challenger defeated. Production remains safe.")
    
    return passed_gate

@flow(name="Sentinel Self-Healing Workflow", log_prints=True)
def self_healing_pipeline(language: str = "English", mock_training: bool = True):
    print(f"\n{'='*50}")
    print(f"🤖 INITIATING SELF-HEALING PIPELINE: {language.upper()}")
    print(f"{'='*50}")
    
    # Task 1
    row_count = extract_live_data(language)
    
    # Task 2
    challenger_uri = train_challenger(language, row_count, mock=mock_training)
    
    # Task 3
    run_evaluation_gate(language, challenger_uri)

if __name__ == "__main__":
    # We set mock_training=True so you don't have to wait 15 mins for DistilBERT right now!
    # In your real demo, you can flip this to False.
    self_healing_pipeline(language="English", mock_training=True)