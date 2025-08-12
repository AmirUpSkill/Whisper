#!/usr/bin/env python3
"""
Smoke Test for Whisper Backend Transcription Service

This script tests the core transcription functionality using the amir.m4a file
to ensure the service works end-to-end before deployment.

Usage:
    python smoke_test.py

Requirements:
    - amir.m4a file in the same directory
    - Environment variables set in .env
    - Database accessible (Neon)
"""

import asyncio
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.core.database import Base
from src.services.transcription_service import transcribe_and_store
from src.db.crud.crud_transcript import get_transcript_by_id, get_all_transcripts


class SmokeTest:
    """Comprehensive smoke test for the transcription service."""
    
    def __init__(self):
        self.audio_file = Path(__file__).parent / "amir.m4a"
        self.engine = None
        self.SessionLocal = None
        
    def setup_database(self):
        """Initialize database connection for testing."""
        print("🔧 Setting up database connection...")
        
        try:
            # Create engine and session
            self.engine = create_engine(settings.DATABASE_URL)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            
            print("✅ Database connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        print("📋 Checking prerequisites...")
        
        # Check if audio file exists
        if not self.audio_file.exists():
            print(f"❌ Audio file not found: {self.audio_file}")
            return False
        
        print(f"✅ Audio file found: {self.audio_file} ({self.audio_file.stat().st_size / 1024:.1f} KB)")
        
        # Check environment variables
        try:
            if not settings.GROQ_API_KEY:
                print("❌ GROQ_API_KEY not set in environment")
                return False
            print(f"✅ GROQ_API_KEY configured (ends with: ...{settings.GROQ_API_KEY[-4:]})")
            
            if not settings.DATABASE_URL:
                print("❌ DATABASE_URL not set in environment") 
                return False
            print("✅ DATABASE_URL configured")
            
        except Exception as e:
            print(f"❌ Environment configuration error: {e}")
            return False
        
        return True
    
    async def test_transcription(self):
        """Test the core transcription functionality."""
        print("🎙️  Testing transcription service...")
        
        # Read audio file
        try:
            with open(self.audio_file, 'rb') as f:
                audio_bytes = f.read()
            print(f"✅ Audio file loaded: {len(audio_bytes)} bytes")
        except Exception as e:
            print(f"❌ Failed to read audio file: {e}")
            return False
        
        # Get database session
        db = self.SessionLocal()
        
        try:
            # Perform transcription
            print("🚀 Starting transcription...")
            transcript_id, raw_text = await transcribe_and_store(
                db=db,
                filename="amir.m4a",
                audio_bytes=audio_bytes,
                mime_type="audio/m4a"
            )
            
            print("✅ Transcription completed successfully!")
            print(f"📄 Transcript ID: {transcript_id}")
            print(f"📝 Text length: {len(raw_text)} characters")
            
            # Show first 100 characters of transcription
            preview = raw_text[:100] + "..." if len(raw_text) > 100 else raw_text
            print(f"👀 Preview: {preview}")
            
            return transcript_id, raw_text
            
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return False
        finally:
            db.close()
    
    def test_database_operations(self, transcript_id):
        """Test database CRUD operations."""
        print("💾 Testing database operations...")
        
        db = self.SessionLocal()
        
        try:
            # Test retrieve by ID
            transcript = get_transcript_by_id(db, transcript_id)
            if transcript:
                print(f"✅ Retrieved transcript by ID: {transcript.id}")
                print(f"   📁 Filename: {transcript.source_filename}")
                print(f"   📅 Created: {transcript.created_at}")
                print(f"   🔄 Status: {transcript.status.value}")
            else:
                print("❌ Failed to retrieve transcript by ID")
                return False
            
            # Test list all transcripts
            all_transcripts = get_all_transcripts(db, limit=5)
            print(f"✅ Retrieved {len(all_transcripts)} recent transcripts")
            
            return True
            
        except Exception as e:
            print(f"❌ Database operations failed: {e}")
            return False
        finally:
            db.close()
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("⚠️  Testing error handling...")
        
        db = self.SessionLocal()
        
        try:
            # Test with empty file
            try:
                await transcribe_and_store(
                    db=db,
                    filename="empty.mp3",
                    audio_bytes=b"",
                    mime_type="audio/mpeg"
                )
                print("❌ Empty file validation should have failed")
                return False
            except ValueError as e:
                print(f"✅ Empty file correctly rejected: {str(e)}")
            
            # Test with oversized file (simulate)
            large_data = b"x" * (26 * 1024 * 1024)  # 26MB
            try:
                await transcribe_and_store(
                    db=db,
                    filename="large.mp3",
                    audio_bytes=large_data,
                    mime_type="audio/mpeg"
                )
                print("❌ Large file validation should have failed")
                return False
            except ValueError as e:
                print(f"✅ Large file correctly rejected: {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
        finally:
            db.close()
    
    async def run_all_tests(self):
        """Run all smoke tests."""
        print("🧪 Starting Whisper Backend Smoke Tests")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Aborting tests.")
            return False
        
        # Setup database
        if not self.setup_database():
            print("\n❌ Database setup failed. Aborting tests.")
            return False
        
        # Test transcription
        result = await self.test_transcription()
        if not result:
            print("\n❌ Transcription test failed. Aborting remaining tests.")
            return False
        
        transcript_id, raw_text = result
        
        # Test database operations
        if not self.test_database_operations(transcript_id):
            print("\n❌ Database operations test failed.")
            return False
        
        # Test error handling
        if not await self.test_error_handling():
            print("\n❌ Error handling test failed.")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All smoke tests passed successfully!")
        print(f"📊 Final stats:")
        print(f"   🆔 Transcript ID: {transcript_id}")
        print(f"   📏 Text length: {len(raw_text)} characters")
        print(f"   📄 Audio file: {self.audio_file.name}")
        
        return True


async def main():
    """Main function to run smoke tests."""
    smoke_test = SmokeTest()
    
    try:
        success = await smoke_test.run_all_tests()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit_code = 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        exit_code = 1
    
    print(f"\n🏁 Exiting with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    # Run the smoke tests
    asyncio.run(main())
