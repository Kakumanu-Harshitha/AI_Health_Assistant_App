import os
from groq import Groq
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

STT_MODEL = "whisper-large-v3"

def speech_to_text(audio_file) -> str:
    """Transcribes audio using Groq's Whisper model."""
    if not groq_client:
        return "[stt_error] Speech service is not configured."
    try:
        transcription = groq_client.audio.transcriptions.create(
            model=STT_MODEL,
            file=audio_file,
            response_format="verbose_json"
        )
        return transcription.text
    except Exception as e:
        return f"[stt_error] {e}"
