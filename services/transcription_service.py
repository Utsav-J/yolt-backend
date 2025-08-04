import os
import tempfile
import whisper

# Global variable to store the Whisper model
whisper_model = None

def load_whisper_model():
    """Load the local Whisper model from default cache location"""
    global whisper_model
    if whisper_model is None:
        print("Loading local Whisper model (base)...")
        whisper_model = whisper.load_model("base", download_root="whisper")
        print("Whisper model loaded successfully!")
    return whisper_model

def transcribe_audio_file(audio_data: bytes) -> str:
    """Transcribe audio data using Whisper model"""
    model = load_whisper_model()
    
    # Save audio data to temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_data)
        temp_filename = temp_file.name
    
    try:
        # Load and transcribe audio
        audio = whisper.load_audio(temp_filename)
        audio = whisper.pad_or_trim(audio)
        result = model.transcribe(audio)
        
        # Ensure we return a string
        transcription = result.get("text", "")
        return str(transcription) if transcription else ""
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def get_whisper_model_status():
    """Check if Whisper model is loaded"""
    return whisper_model is not None
