import os
from groq import Groq
from dotenv import load_dotenv
from fastapi import UploadFile # It's good practice to add type hints

# Load environment variables from .env file
load_dotenv()

# --- Initialize Groq Client ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client for Speech-to-Text initialized.")
else:
    print("⚠️ WARNING: GROQ_API_KEY not found! Speech-to-Text service will be disabled.")

STT_MODEL = "whisper-large-v3"

def speech_to_text(audio_file: UploadFile) -> str:
    """
    Transcribes an audio file using Groq's Whisper model.
    """
    if not groq_client:
        return "[stt_error] Speech service is not configured due to missing API key."

    try:
        # --- THE FIX IS HERE ---
        # Create a tuple containing the filename and the file-like object (.file)
        # This is the format the Groq SDK expects.
        file_tuple = (audio_file.filename, audio_file.file)

        transcription = groq_client.audio.transcriptions.create(
            model=STT_MODEL,
            file=file_tuple,  # Pass the correctly formatted tuple to the API
            response_format="verbose_json"
        )
        return transcription.text
    except Exception as e:
        print(f"❌ ERROR: Groq STT API call failed. Error: {e}")
        return f"[stt_error] {e}"
