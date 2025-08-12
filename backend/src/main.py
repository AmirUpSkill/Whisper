from fastapi import FastAPI
from .core.database import engine  # Import the database engine
from .db import models  # Import the models module

# Create all database tables on startup (for development)
# In production, you would use Alembic migrations instead
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Whisper AI Vision API",
    version="1.0.0",
    description="AI-native transcript processing and insights generation",
)

@app.get("/")
def read_root():
    """A simple health check endpoint."""
    return {
        "status": "ok", 
        "message": "Welcome to Whisper AI Vision API Backend!",
        "version": "1.0.0"
    }

# TODO: Add CORS middleware when frontend is ready
# TODO: Add API routers for transcript endpoints
