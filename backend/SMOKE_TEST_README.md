# 🧪 Whisper Backend Smoke Test

This smoke test validates the core transcription functionality using your `amir.m4a` audio file to ensure the backend works end-to-end before deployment.

## 🚀 Quick Start

```bash
# 1. Ensure your virtual environment is activated
.\.venv\Scripts\Activate.ps1

# 2. Run the smoke test
python smoke_test.py
```

## 📋 What It Tests

### ✅ **Prerequisites Check**
- Verifies `amir.m4a` file exists
- Validates environment variables (`GROQ_API_KEY`, `DATABASE_URL`)
- Checks file size and basic format

### 🎙️ **Transcription Service**
- Tests audio file loading
- Validates Groq API integration
- Verifies transcription quality
- Stores results in database

### 💾 **Database Operations**
- Tests transcript storage
- Validates record retrieval by ID
- Checks listing functionality
- Verifies data integrity

### ⚠️ **Error Handling**
- Tests empty file rejection
- Validates file size limits (25MB)
- Ensures graceful failure modes

## 📊 Sample Output

```
🧪 Starting Whisper Backend Smoke Tests
==================================================
📋 Checking prerequisites...
✅ Audio file found: amir.m4a (203.7 KB)
✅ GROQ_API_KEY configured (ends with: ...tYy)
✅ DATABASE_URL configured
🔧 Setting up database connection...
✅ Database connection successful
🎙️  Testing transcription service...
✅ Audio file loaded: 208612 bytes
🚀 Starting transcription...
✅ Transcription completed successfully!
📄 Transcript ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
📝 Text length: 1247 characters
👀 Preview: Hello, this is Amir speaking. I'm testing the Whisper transcription service...
💾 Testing database operations...
✅ Retrieved transcript by ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   📁 Filename: amir.m4a
   📅 Created: 2025-08-12 10:08:45.123456
   🔄 Status: completed
✅ Retrieved 1 recent transcripts
⚠️  Testing error handling...
✅ Empty file correctly rejected: Audio file is empty
✅ Large file correctly rejected: File size exceeds 25MB limit

==================================================
🎉 All smoke tests passed successfully!
📊 Final stats:
   🆔 Transcript ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   📏 Text length: 1247 characters
   📄 Audio file: amir.m4a

🏁 Exiting with code: 0
```

## 🔧 Prerequisites

1. **Environment Setup**:
   ```bash
   # Virtual environment activated
   .\.venv\Scripts\Activate.ps1
   
   # Dependencies installed
   uv sync
   ```

2. **Environment Variables** (`.env` file):
   ```env
   GROQ_API_KEY="gsk_..."
   GEMINI_API_KEY="AIza..."
   DATABASE_URL="postgresql://..."
   ```

3. **Files Required**:
   - `amir.m4a` in the backend directory
   - All backend services implemented

## 🚨 Troubleshooting

### **Common Issues**

**❌ "Audio file not found"**
```
Solution: Ensure amir.m4a is in the backend directory
```

**❌ "GROQ_API_KEY not set"**
```
Solution: Check your .env file has the correct API key
```

**❌ "Database setup failed"**
```
Solution: Verify your Neon database URL and connection
```

**❌ "Transcription failed"**
```
Solution: Check Groq API key validity and network connection
```

## 🎯 Success Criteria

The smoke test passes when:
- ✅ All prerequisites are met
- ✅ Audio file transcribes successfully
- ✅ Database operations work correctly  
- ✅ Error handling functions properly
- ✅ Exit code is 0

## 🔄 Running in CI/CD

This smoke test is designed to be CI/CD friendly:

```yaml
# Example GitHub Actions step
- name: Run Smoke Tests
  run: |
    cd backend
    python smoke_test.py
  env:
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## 📝 Notes

- The test uses the actual Groq API (costs ~$0.04 per run)
- Creates real database records
- Designed for fast feedback (< 30 seconds)
- Safe to run multiple times
- Provides detailed logging for debugging
