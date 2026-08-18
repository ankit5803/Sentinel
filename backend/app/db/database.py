# backend/app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# The Engine is the core interface to the database.
# For free cloud tiers, pool_pre_ping=True is crucial—it checks if the connection 
# is still alive before using it, preventing "server closed the connection" errors.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# SessionLocal is a factory for creating individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class that our actual database models will inherit from
Base = declarative_base()

def get_db():
    """
    Dependency generator for FastAPI. 
    Ensures that every web request gets its own database session,
    and reliably closes it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print(f"✅ Database module loaded. Configured to connect to: {settings.DATABASE_URL.split('@')[-1]}")