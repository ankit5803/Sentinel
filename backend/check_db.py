import sys
import os

# Force Python to look inside the backend folder
sys.path.insert(0, os.path.abspath("backend"))

from app.db.database import SessionLocal
from app.models.models import PredictionLog

print("🔌 Connecting to Render PostgreSQL Vault...")

try:
    # Open a database session
    db = SessionLocal()
    
    # Query the 5 most recent logs, ordered by ID descending
    recent_logs = db.query(PredictionLog).order_by(PredictionLog.id.desc()).limit(5).all()
    
    if not recent_logs:
        print("⚠️ Database connection successful, but no logs found. The table is empty.")
    else:
        print(f"✅ Success! Found {len(recent_logs)} recent logs:\n")
        for log in recent_logs:
            # We use a fallback for timestamp just in case your model field is named differently
            print(f"ID: {log.id} | Risk: {log.risk_level} | Target: {log.target_identified}")
            print(f"Payload: '{log.text}'")
            print("-" * 50)
            
except Exception as e:
    print(f"❌ Database connection failed: {e}")
finally:
    db.close()