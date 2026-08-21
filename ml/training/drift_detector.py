# ml/training/drift_detector.py
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently import ColumnMapping
from sqlalchemy import create_engine
import os

# Connect to the local Postgres database (The Vault)
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sentinel")

def check_drift(language: str, reference_csv_path: str):
    print(f"\n{'='*50}")
    print(f"🕵️  EVIDENTLY AI DRIFT DETECTOR: {language.upper()}")
    print(f"{'='*50}")

    # 1. Load Reference Data (The data the model was originally trained on)
    print(f"📂 Loading Reference Data from {reference_csv_path}...")
    reference_data = pd.read_csv(reference_csv_path)
    
    # We only need the text column for text drift, let's rename it to standard 'text'
    # based on our previous setup, the column might be 'sentence'
    if 'sentence' in reference_data.columns:
        reference_data = reference_data.rename(columns={'sentence': 'text'})
    
    reference_data = reference_data[['text']].dropna()

    # 2. Load Current Data (Live production data from Postgres)
    print("🗄️  Extracting Live Traffic from PostgreSQL Vault...")
    engine = create_engine(DB_URL)
    
    try:
        # Fetch only logs for the specific language
        query = f"SELECT text FROM prediction_logs WHERE language_detected = '{language.lower()}'"
        current_data = pd.read_sql(query, engine).dropna()
    except Exception as e:
        print(f"❌ Failed to fetch from database. Error: {e}")
        return False

    if len(current_data) < 10:
        print(f"⚠️ Not enough live data to run drift detection (Found {len(current_data)} rows). Needs at least 10.")
        return False

    print(f"✅ Found {len(current_data)} live production logs.")

    # 3. Setup Evidently Column Mapping
    print("📊 Calculating Data Drift (Text Distribution)...")
    column_mapping = ColumnMapping(
        text_features=['text'],
        numerical_features=[],
        categorical_features=[]
    )

    # 4. Run the Report
    drift_report = Report(metrics=[DataDriftPreset()])
    drift_report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
    
    # 5. Extract Results
    report_dict = drift_report.as_dict()
    dataset_drift = report_dict["metrics"][0]["result"]["dataset_drift"]
    
    print(f"\n{'='*50}")
    print("🚨 DRIFT VERDICT")
    print(f"{'='*50}")
    
    if dataset_drift:
        print("⚠️  DATA DRIFT DETECTED! The production traffic looks significantly different from the training data.")
        print("-> Action Required: Triggering Automated Retraining Pipeline (Prefect).")
    else:
        print("✅ No Drift Detected. Production traffic matches training distribution. The model is safe.")
    
    # Generate a beautiful HTML report
    report_path = f"{language.lower()}_drift_report.html"
    drift_report.save_html(report_path)
    print(f"📄 Detailed visual report saved to: {report_path}")

    return dataset_drift

if __name__ == "__main__":
    ENGLISH_TRAIN_PATH = "../data/processed/english_train.csv"
    
    check_drift(
        language="English",
        reference_csv_path=ENGLISH_TRAIN_PATH
    )