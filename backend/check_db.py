# backend/check_db.py
from app.db.database import SessionLocal
from app.models.models import PredictionLog

def check_logs():
    db = SessionLocal()
    
    # Query the 5 most recent logs, ordered by newest first
    logs = db.query(PredictionLog).order_by(PredictionLog.id.desc()).limit(5).all()
    
    print("\n=== LATEST SENTINEL PREDICTION LOGS ===")
    if not logs:
        print("No logs found in the database.")
        
    for log in logs:
        print(f"ID: {log.id} | Lang: {log.language_detected} | Risk: {log.risk_level}")
        print(f"Text: '{log.text}'")
        print(f"Probability: {log.threat_probability} | Target: {log.target_identified} | Immediacy: {log.immediacy}")
        print(f"Reason: {log.reason}")
        print("-" * 60)
    
    db.close()

if __name__ == "__main__":
    check_logs()