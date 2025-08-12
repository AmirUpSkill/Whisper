import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base  # Import the Base class from our core module
from ..schemas.transcript import TranscriptStatus  # Import the status enum from schemas


class Transcript(Base):
    """
    SQLAlchemy model for the 'transcripts' table.
    This class defines the database table schema.
    """
    __tablename__ = "transcripts"

    # Columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    source_filename = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    status = Column(SAEnum(TranscriptStatus), nullable=False, default=TranscriptStatus.completed)
    
    # Auto-managed timestamp with proper timezone handling
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, filename='{self.source_filename}', status='{self.status}')>"
