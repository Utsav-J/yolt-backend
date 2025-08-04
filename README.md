# Audio Transcription API

A FastAPI-based web service that transcribes audio files to text using OpenAI's Whisper model and extracts tasks using Google's Gemini AI.

## Project Structure

```
YOLT/
├── backend.py              # Main FastAPI application
├── requirements.txt        # Python dependencies
├── test_api.py            # API testing script
├── model_config.py        # AI model configurations
├── .env                   # Environment variables
├── config/
│   ├── __init__.py
│   └── settings.py        # Application settings
├── services/
│   ├── __init__.py
│   ├── transcription_service.py  # Whisper transcription logic
│   └── task_service.py    # Gemini task extraction logic
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic data models
└── whisper/               # Whisper model cache directory
```

## Features

- Upload audio files in various formats (WAV, MP3, M4A, etc.)
- Automatic speech-to-text transcription using Whisper
- Task extraction from audio files using Gemini AI
- Task extraction from text input using Gemini AI
- RESTful API with JSON responses
- Health check endpoints
- File size validation (25MB limit)
- Modular architecture with separated concerns

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file with your API keys
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

### Starting the Server

Run the FastAPI server:
```bash
python backend.py
```

Or using uvicorn directly:
```bash
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health status with Whisper model status

#### Audio Transcription
- **POST** `/transcribe` - Upload an audio file for transcription

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `audio_file` (file upload)

**Response:**
```json
{
    "filename": "audio.wav",
    "transcription": "Hello, this is a test transcription.",
    "status": "success"
}
```

#### Task Extraction from Audio
- **POST** `/extract-tasks-from-audio` - Upload an audio file for transcription and task extraction

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `audio_file` (file upload)

**Response:**
```json
{
    "filename": "meeting.wav",
    "transcription": "Full transcribed text...",
    "tasks": "JSON formatted task list",
    "status": "success"
}
```

#### Task Extraction from Text
- **POST** `/extract-tasks-from-text` - Extract tasks from provided text

**Request:**
```json
{
    "text": "Your long text content here..."
}
```

**Response:**
```json
{
    "input_text": "Your long text content here...",
    "tasks": "JSON formatted task list",
    "status": "success"
}
```

### Testing the API

Use the provided test script:
```bash
python test_api.py path/to/your/audio/file.wav
```

Or use curl:
```bash
# Transcription only
curl -X POST "http://localhost:8000/transcribe" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "audio_file=@your_audio_file.wav"

# Task extraction from audio
curl -X POST "http://localhost:8000/extract-tasks-from-audio" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "audio_file=@your_audio_file.wav"

# Task extraction from text
curl -X POST "http://localhost:8000/extract-tasks-from-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "We need to complete the project by Friday."}'
```

## Architecture

### Services Layer
- **`transcription_service.py`**: Handles Whisper model loading and audio transcription
- **`task_service.py`**: Manages Gemini AI integration for task extraction

### Models Layer
- **`schemas.py`**: Pydantic models for request/response validation

### Configuration
- **`settings.py`**: Application configuration and constants

### Main Application
- **`backend.py`**: FastAPI routes and endpoint definitions only

## Supported Audio Formats

The API supports various audio formats that Whisper can process:
- WAV, MP3, M4A, FLAC, OGG, and more

## Configuration

- **File Size Limit**: 25MB (configurable in `config/settings.py`)
- **Whisper Model**: Uses the "base" model (configurable in `transcription_service.py`)
- **Server Host/Port**: Configurable in the `uvicorn.run()` call

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- OpenAI Whisper
- Google GenerativeAI
- PyTorch
- NumPy
- python-dotenv

## Environment Variables

Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Notes

- The Whisper model is loaded once at startup for better performance
- Temporary files are automatically cleaned up after transcription
- The API includes proper error handling and validation
- Modular architecture allows for easy maintenance and testing
