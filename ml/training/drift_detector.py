import os
import sys
from pathlib import Path
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently import ColumnMapping
from sqlalchemy import create_engine

# 1. Add the backend directory to Python's path so we can import app settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.core.config import get_settings

# 2. Grab the DATABASE_URL straight from your centralized config
settings = get_settings()
DB_URL = settings.DATABASE_URL