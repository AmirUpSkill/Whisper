from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc

from .. import models
from ... import schemas


def get_transcript_by_id(db: Session, transcript_id: UUID) -> Optional[models.Transcript]:
    """
    Retrieves a single transcript from the database by its ID.
    
    Args:
        db: Database session
        transcript_id: The UUID of the transcript to retrieve
        
    Returns:
        Transcript model instance or None if not found
    """
    try:
        return db.query(models.Transcript).filter(models.Transcript.id == transcript_id).first()
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_all_transcripts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Transcript]:
    """
    Retrieves a list of all transcripts with pagination, ordered by creation date (newest first).
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Transcript model instances
    """
    try:
        return (
            db.query(models.Transcript)
            .order_by(desc(models.Transcript.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def create_transcript(db: Session, transcript: schemas.TranscriptCreate) -> models.Transcript:
    """
    Creates a new transcript record in the database.
    
    Args:
        db: Database session
        transcript: TranscriptCreate schema with the data to insert
        
    Returns:
        The created Transcript model instance with all database-generated fields populated
        
    Raises:
        SQLAlchemyError: If database operation fails
    """
    try:
        # Create a new SQLAlchemy model instance from the Pydantic schema data
        db_transcript = models.Transcript(**transcript.model_dump())
        
        db.add(db_transcript)  # Add the new instance to the session
        db.commit()           # Commit the transaction to the database
        db.refresh(db_transcript)  # Refresh the instance to get DB-generated values
        
        return db_transcript
        
    except SQLAlchemyError as e:
        db.rollback()  # Rollback the transaction on error
        raise e


def get_transcript_count(db: Session) -> int:
    """
    Gets the total count of transcripts in the database.
    Useful for pagination metadata.
    
    Args:
        db: Database session
        
    Returns:
        Total number of transcript records
    """
    try:
        return db.query(models.Transcript).count()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
