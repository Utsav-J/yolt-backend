from google import genai
from model_config import TASK_EXTRACTION_SYSTEM_PROMPT
from models.schemas import Tasks

def extract_tasks(transcription: str):
    """Extract tasks from transcription using Gemini AI"""
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=TASK_EXTRACTION_SYSTEM_PROMPT.format(transcription),
        config={
            "response_mime_type": "application/json",
            "response_schema": Tasks,
        },
    )
    print(response.text)
    return response
