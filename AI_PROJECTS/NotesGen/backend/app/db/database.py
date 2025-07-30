from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# IMPORTANT: This application now uses PostgreSQL exclusively
# SQLite has been removed due to concurrency and performance issues
# that were causing "Server unavailable" errors and infinite polling loops

# PostgreSQL optimized connection settings
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    # PostgreSQL-specific optimizations
    pool_size=20,  # Increased from default 5 for concurrent PPT processing
    max_overflow=30,  # Increased from default 10 for peak loads
    pool_timeout=60,  # Increased timeout for heavy image processing
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Verify connections before use
    # PostgreSQL specific settings
    echo=False,  # Set to True for SQL debugging
    future=True,  # Use SQLAlchemy 2.0 style
)

# Validate that we're actually connected to PostgreSQL
def validate_postgresql_connection():
    """Ensure we're connected to PostgreSQL, not SQLite."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            if not result or "PostgreSQL" not in result:
                raise RuntimeError(
                    f"❌ Expected PostgreSQL but connected to: {result}. "
                    "This application requires PostgreSQL for proper operation."
                )
            logger.info(f"✅ Connected to PostgreSQL: {result}")
            return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection validation failed: {e}")
        raise RuntimeError(
            "Failed to connect to PostgreSQL. Please ensure:\n"
            "1. PostgreSQL is running\n"
            "2. Database credentials are correct\n"
            "3. Database exists and is accessible\n"
            f"Connection string: {settings.SQLALCHEMY_DATABASE_URI}"
        )

# NOTE: Validation moved to main.py startup to avoid import-time errors
# Only validate when the application actually starts

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine():
    """Get the database engine."""
    return engine
