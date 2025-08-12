from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, conint

class TranscriptStatus(str, Enum):
    """Enum for the status of a transcription process."""
    completed = "completed"
    failed = "failed"

class TranscriptBase(BaseModel):
    """Base schema with common attributes for a transcript."""
    # Config for Pydantic v2 and ORM compatibility
    model_config = ConfigDict(from_attributes=True)

    source_filename: str
    duration_seconds: conint(ge=0) # Ensures duration is a non-negative integer

class Transcript(TranscriptBase):
    """Full transcript schema returned on creation (POST /transcripts)."""
    id: UUID
    status: TranscriptStatus = TranscriptStatus.completed
    raw_text: str
    created_at: datetime

class TranscriptListItem(BaseModel):
    """Slim transcript schema for listings (GET /transcripts), omitting heavy raw_text."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_filename: str
    duration_seconds: conint(ge=0)
    created_at: datetime

# Optional schema for internal, server-side use only.
# This separates client input from server-generated data.
class TranscriptCreate(TranscriptBase):
    """Internal schema for creating a transcript record in the database."""
    raw_text: str
    status: TranscriptStatus
