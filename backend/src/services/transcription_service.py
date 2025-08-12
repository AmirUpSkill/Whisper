import io
import logging
from uuid import UUID
from typing import Tuple
from groq import Groq
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.crud import crud_transcript
from ..schemas import TranscriptCreate, TranscriptStatus

# Configure logging
logger = logging.getLogger(__name__)

# --- Initialize Groq Client --- 
client = Groq(api_key=settings.GROQ_API_KEY)

# --- Audio Processing Constants ---
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB limit for Groq free tier
SUPPORTED_FORMATS = {"mp3", "wav", "m4a", "flac", "ogg", "webm", "mp4", "mpeg", "mpga"}

def get_audio_duration(audio_bytes: bytes) -> int:
    """
    Calculate audio duration from bytes.
    For now, returns 0 as a placeholder. In production, you'd use librosa or similar.
    
    Args:
        audio_bytes: The audio file as bytes
        
    Returns:
        Duration in seconds (currently returns 0 as placeholder)
    """
    # TODO: Implement actual duration calculation using librosa
    # For now, return 0 to avoid blocking the MVP
    return 0

def validate_audio_file(audio_bytes: bytes, filename: str) -> None:
    """
    Validate audio file size and format.
    
    Args:
        audio_bytes: The audio file as bytes
        filename: Original filename
        
    Raises:
        ValueError: If file is invalid
    """
    if len(audio_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit")
    
    if len(audio_bytes) == 0:
        raise ValueError("Audio file is empty")
    
    # Basic format validation based on file extension
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ""
    if file_extension not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported file format: {file_extension}. Attempting transcription anyway.")

async def transcribe_and_store(
    *,
    db: Session,
    filename: str,
    audio_bytes: bytes,
    mime_type: str = "audio/mpeg"
) -> Tuple[UUID, str]:
    """
    Transcribes audio bytes using the Groq API and stores the result in the database.
    
    Args:
        db: Database session
        filename: Original filename of the audio file
        audio_bytes: Audio file content as bytes
        mime_type: MIME type of the audio file
        
    Returns:
        Tuple of (transcript_id, raw_text)
        
    Raises:
        ValueError: If audio file is invalid
        RuntimeError: If transcription fails
    """
    logger.info(f"Starting transcription for file: {filename}")
    
    # Validate the audio file
    validate_audio_file(audio_bytes, filename)
    
    try:
        # Call Groq API for transcription
        transcription = client.audio.transcriptions.create(
            file=(filename, io.BytesIO(audio_bytes), mime_type),
            model="whisper-large-v3-turbo",
            response_format="text",
            language=None,  # Let Whisper auto-detect language
            temperature=0.0  # Deterministic output
        )
        
        logger.info(f"Transcription successful for {filename}")
        
    except Exception as e:
        logger.error(f"Groq transcription failed for {filename}: {str(e)}")
        
        # Create failed transcript record
        failed_transcript = TranscriptCreate(
            source_filename=filename,
            duration_seconds=get_audio_duration(audio_bytes),
            raw_text="",
            status=TranscriptStatus.failed,
        )
        
        db_transcript = crud_transcript.create_transcript(db=db, transcript=failed_transcript)
        raise RuntimeError(f"Groq transcription failed: {str(e)}") from e
    
    # Process the successful transcription
    raw_text = transcription.strip() if transcription else ""
    
    if not raw_text:
        logger.warning(f"Empty transcription result for {filename}")
    
    duration_seconds = get_audio_duration(audio_bytes)
    
    # Create transcript record in database
    transcript_in = TranscriptCreate(
        source_filename=filename,
        duration_seconds=duration_seconds,
        raw_text=raw_text,
        status=TranscriptStatus.completed,
    )
    
    try:
        db_transcript = crud_transcript.create_transcript(db=db, transcript=transcript_in)
        logger.info(f"Transcript stored successfully with ID: {db_transcript.id}")
        
        return db_transcript.id, raw_text
        
    except Exception as e:
        logger.error(f"Database error while storing transcript: {str(e)}")
        raise RuntimeError(f"Failed to store transcript: {str(e)}") from e
