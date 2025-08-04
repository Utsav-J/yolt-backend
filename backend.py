# import os
import json
import uvicorn
from contextlib                     import asynccontextmanager
from fastapi.responses              import JSONResponse
from dotenv                         import load_dotenv
from services.task_service          import extract_tasks
from models.schemas                 import TextInput
from config.settings                import MAX_AUDIO_FILE_SIZE
from fastapi                        import FastAPI, File, UploadFile, HTTPException
from services.transcription_service import (load_whisper_model, 
                                            transcribe_audio_file, 
                                            get_whisper_model_status)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_whisper_model()
    yield

app = FastAPI(title="Yolt Backend", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Audio Transcription API is running"}

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file to text using Whisper
    Args:
        audio_file: The audio file to transcribe (supports various formats)
    Returns:
        JSON response with the transcription text
    """
    try:
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        if audio_file.size and audio_file.size > MAX_AUDIO_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 25MB")
        
        audio_content = await audio_file.read()
        
        if not audio_content:
            raise HTTPException(status_code=400, detail="Empty audio file")
        transcription = transcribe_audio_file(audio_content)
        
        return JSONResponse(
            status_code=200,
            content={
                "filename": audio_file.filename,
                "transcription": transcription,
                "status": "success"
            }
        )
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing audio file: {str(e)}"
        )

@app.post("/extract-tasks-from-audio")
async def extract_tasks_from_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file and extract tasks using Gemini AI
    Args:
        audio_file: The audio file to transcribe and extract tasks from
    Returns:
        JSON response with the transcription and extracted tasks
    """
    try:
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio file provided")
        if audio_file.size and audio_file.size > MAX_AUDIO_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 25MB")
        
        audio_content = await audio_file.read()
        
        if not audio_content:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # First transcribe the audio
        transcription = transcribe_audio_file(audio_content)
        
        if not transcription.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio file")
        
        # Then extract tasks from the transcription
        task_response = extract_tasks(transcription)
        
        return JSONResponse(
            status_code=200,
            content={
                "filename": audio_file.filename,
                "transcription": transcription,
                "tasks": task_response.text,
                "status": "success"
            }
        )
        
    except Exception as e:
        print(f"Error during task extraction from audio: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing audio file for task extraction: {str(e)}"
        )

@app.post("/extract-tasks-from-text")
async def extract_tasks_from_text(text_input: TextInput):
    """
    Extract tasks from provided text using Gemini AI
    Args:
        text_input: JSON object containing the text to extract tasks from
    Returns:
        JSON response with the extracted tasks
    """
    try:
        if not text_input.text or not text_input.text.strip():
            raise HTTPException(status_code=400, detail="No text provided or text is empty")
        
        # Extract tasks from the provided text
        task_response = extract_tasks(text_input.text)
        if task_response.text:
            tasks = json.loads(task_response.text)
        return JSONResponse(
            status_code=200,
            content={
                "input_text": text_input.text,
                "tasks": tasks,
                "status": "success"
            }
        )
        
    except Exception as e:
        print(f"Error during task extraction from text: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing text for task extraction: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "whisper_model_loaded": get_whisper_model_status()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
