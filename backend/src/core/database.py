from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config import settings  # Import the settings object we just created

# Create the SQLAlchemy engine using the database URL from our settings
engine = create_engine(settings.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models to inherit from
Base = declarative_base()

# Dependency for FastAPI routes to get a DB session
def get_db():
    """
    A generator that yields a new SQLAlchemy session for each request.
    It ensures the session is always closed, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
