import os

# Configuration settings
SCRIPT_DIR = os.path.dirname(__file__)
WHISPER_PATH = os.path.join("..","whisper")

# Print whisper path for debugging
print(f"Whisper path: {WHISPER_PATH}")

# File size limits
MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024  # 25MB
