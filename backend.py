import os
import sys
import json
import uvicorn
import datetime
from pyngrok                        import ngrok
from contextlib                     import asynccontextmanager
from dotenv                         import load_dotenv
from google                         import genai
from fastapi.responses              import JSONResponse
from services.task_service          import extract_tasks
from models.schemas                 import TextInput, DailyAffirmation
from config.settings                import MAX_AUDIO_FILE_SIZE
from fastapi                        import FastAPI, File, UploadFile, HTTPException
from services.transcription_service import (load_whisper_model, 
                                            transcribe_audio_file, 
                                            get_whisper_model_status)


load_dotenv()
global_gemini_client = genai.Client()
script_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(script_dir)   

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_whisper_model()
    yield

app = FastAPI(title="Yolt Backend", version="1.0.0", lifespan=lifespan)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Audio Transcription API is running"}

async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Transcribe an audio file to text using Whisper
    Args:
        audio_file: The audio file to transcribe (supports various formats)
    Returns:
        JSON response with the transcription text
    """
    try:
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
        
        transcription = transcribe_audio_file(audio_content)
        
        if not transcription.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio file")
        
        # Then extract tasks from the transcription
        task_response = extract_tasks(transcription)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "transcription": transcription,
                "tasks": task_response.text,
                "filename": audio_file.filename,
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
        
        # Parse the JSON response from Gemini
        try:
            if task_response.text:
                print(f"Response text to parse: {repr(task_response.text)}")
                tasks = json.loads(task_response.text)
            else:
                tasks = {"tasks": []}
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Raw response: {repr(task_response.text)}")
            # Fallback to empty tasks if JSON parsing fails
            tasks = {"tasks": []}
            
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

@app.post("/generate-affirmation")
def generate_affirmation(user_tasks:dict):
    current_timestamp = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
    response = global_gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents='''
            You are a motivational writer generating short, emotionally uplifting affirmations.

            Given a user's daily to-do list, generate a SINGLE daily affirmation that:
            - Aligns with the theme of the user's tasks
            - Focuses on the long term goals of the user on a spiritual l
            - Is poetic and inspiring (1-2 sentences max)
            - Reflects the user's energy, or mindset needed to approach the tasks
            - Does NOT repeat or list the actual tasks
            - Does NOT describe or summarize the task list
            - Sounds like a personal mantra or inner voice
            - Is general enough to feel universal, but subtly influenced by the nature of the tasks

            Only return the affirmation. No explanations, greetings, or metadata. Adhere to the attached format

            Tasks:
            {{}}

            Example tasks:
            - Finish report
            - Meditate for 10 minutes
            - Schedule doctor appointment

            Example output:
            "I trust my ability to stay focused and make space for what matters most today."'''.format(user_tasks['tasks']),
        config={
            "response_mime_type": "application/json",
            "response_schema": DailyAffirmation,
        },
    )
    json_data = json.loads(str(response.text))
    json_data["timestamp"] = current_timestamp
    print(json_data)
    print(response.text)
    return json_data

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "whisper_model_loaded": get_whisper_model_status()
    }

if __name__ == "__main__":
      # <-- Replace with your actual authtoken
    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
    if NGROK_AUTH_TOKEN:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    else:
        print("NGROK AUTH TOKEN NOT FOUND IN ENV FILE")
    # Expose the local FastAPI server via ngrok
    public_url = ngrok.connect("8000")
    print(f"Public URL: {public_url}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
