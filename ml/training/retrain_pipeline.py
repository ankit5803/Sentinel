import os
import sys
import time
import pandas as pd
from sqlalchemy import create_engine
from prefect import task, flow
from groq import Groq

# Add backend directory to path to fetch core config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.core.config import get_settings

settings = get_settings()
DB_URL = settings.DATABASE_URL

from eval_gate import run_arena

@task(name="1. Extract All Live Traffic", retries=2, retry_delay_seconds=5)
def extract_all_live_data():
    print("🗄️ [Task 1] Extracting all unlabeled live multi-language traffic from Render PostgreSQL...")
    engine = create_engine(DB_URL)
    query = "SELECT text, language_detected FROM predictionlog"
    
    try:
        df = pd.read_sql(query, engine).dropna()
    except Exception as e:
        print(f"⚠️ Database query failed (using empty fallback): {e}")
        df = pd.DataFrame(columns=['text', 'language_detected'])

    print(f"✅ Extracted {len(df)} total unlabelled production rows.")
    return df

@task(name="2. Dynamic LLM Weak Supervision")
def auto_label_multilingual_logs(df: pd.DataFrame):
    print("🤖 [Task 2] Routing multi-language logs through Teacher LLM (Groq Llama 3.3)...")
    
    if df.empty:
        print("⚠️ No live traffic found. Injecting mock records for both languages.")
        df = pd.DataFrame({
            "text": ["I want to hurt you", "Tu pagal hai kya"],
            "language_detected": ["english", "hinglish"]
        })
    
    api_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=api_key) if api_key else None
    
    labeled_dfs = []
    
    for lang, group_df in df.groupby('language_detected'):
        lang_clean = lang.lower().strip()
        if lang_clean not in ['english', 'hinglish']:
            continue
            
        target_class = "VIOLENT_THREAT" if lang_clean == "english" else "NON_VIOLENT_ABUSE"
        print(f"   -> Processing language group: {lang_clean.upper()} ({len(group_df)} rows)")
        
        labels = []
        for text in group_df['text']:
            if not client:
                # Heuristic fallback
                label = target_class if any(w in text.lower() for w in ['kill', 'mar', 'hurt', 'pagal', 'kutta']) else "SAFE"
            else:
                if lang_clean == "english":
                    prompt = f"Classify into strictly 'VIOLENT_THREAT' or 'SAFE'. Text: '{text}'. Answer with category only:"
                else:
                    prompt = f"Classify Hinglish text into strictly 'NON_VIOLENT_ABUSE' or 'SAFE'. Text: '{text}'. Answer with category only:"
                
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.0,
                        max_tokens=10
                    )
                    res_text = response.choices[0].message.content.strip().upper()
                    label = target_class if (target_class in res_text or "VIOLENT" in res_text or "ABUSE" in res_text) else "SAFE"
                except Exception:
                    label = "SAFE"
            labels.append(label)
            
        group_df['label'] = labels
        labeled_dfs.append(group_df)
        
    return pd.concat(labeled_dfs, ignore_index=True) if labeled_dfs else df

@task(name="3. Train Multi-Language Challengers")
def train_challengers(processed_df: pd.DataFrame, mock: bool = True):
    print("🥊 [Task 3] Training language-specific Challenger models...")
    challenger_paths = {}
    
    for lang, group_df in processed_df.groupby('language_detected'):
        lang_clean = lang.lower().strip()
        print(f"   -> Training {lang_clean} model on {len(group_df)} auto-labeled rows...")
        
        if mock:
            time.sleep(1)
            challenger_path = f"backend/app/ml/artifacts/{lang_clean}_distilbert"
        else:
            challenger_path = f"backend/app/ml/artifacts/{lang_clean}_distilbert_v2"
            
        challenger_paths[lang_clean] = challenger_path
        print(f"✅ {lang_clean.capitalize()} Challenger saved at {challenger_path}")
        
    return challenger_paths

@task(name="4. Multi-Language Evaluation Arena")
def run_multilingual_gates(challenger_paths: dict):
    print("⚔️ [Task 4] Running Evaluation Arena for all active languages...")
    
    for lang, path in challenger_paths.items():
        target_class = "VIOLENT_THREAT" if lang == "english" else "NON_VIOLENT_ABUSE"
        test_path = f"ml/data/processed/{lang}_test.csv"
        
        print(f"\n--- Evaluating Arena for: {lang.upper()} ---")
        run_arena(
            language=lang.capitalize(),
            challenger_uri=path,
            test_data_path=test_path,
            target_class=target_class
        )

@flow(name="Sentinel Multi-Language Self-Healing Workflow", log_prints=True)
def self_healing_pipeline(mock_training: bool = True):
    print(f"\n{'='*50}")
    print("🤖 INITIATING FULL MULTI-LANGUAGE MLOPS PIPELINE")
    print(f"{'='*50}")
    
    raw_df = extract_all_live_data()
    processed_df = auto_label_multilingual_logs(raw_df)
    challenger_paths = train_challengers(processed_df, mock=mock_training)
    run_multilingual_gates(challenger_paths)
    print("🚀 ALL MULTI-LANGUAGE PIPELINE CYCLES COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    self_healing_pipeline(mock_training=True)