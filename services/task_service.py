from google import genai
from models.schemas import Tasks

TASK_EXTRACTION_SYSTEM_PROMPT = """
You are an expert assistant that extracts actionable tasks from meeting transcriptions.
Your job is to read the provided transcription and identify clear, concise tasks that need to be completed.
Return the tasks in a structured JSON format matching the schema given to you in the config.
Guidelines:
- Only include actionable items (things to do).
- Actionable verbs like I want to, I wanna, I should, I hope to, etc should be taken into account 
- If priority is not mentioned, set it to medium.
- Do not invent tasks; only extract what is clearly implied.
- Be concise and use clear language.
Transcription:
{}
"""

def extract_tasks(transcription: str):
    """Extract tasks from transcription using Gemini AI"""
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=TASK_EXTRACTION_SYSTEM_PROMPT.format(transcription),
            config={
                "response_mime_type": "application/json",
                "response_schema": Tasks,
            },
        )
        print(f"Raw response: {repr(response.text)}")
        return response
    except Exception as e:
        print(f"Error in extract_tasks: {str(e)}")
        print(f"Error type: {type(e)}")
        raise
