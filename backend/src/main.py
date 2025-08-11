from fastapi import FastAPI

app = FastAPI(
    title = "Whisper AI Vision API - Backend",
    version = "1.0.0",
)
@app.get("/")
def read_root():
    """
        A Simple health check endpoint
    """
    return {
        "status" : "ok",
        "message" : "Welcome to Whisper AI Vision API - Backend"
    }