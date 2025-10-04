import os
from groq import Groq
from elevenlabs.client import ElevenLabs
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVEN_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

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

def text_to_speech(text: str) -> bytes:
    """Converts text to speech audio bytes, preferring ElevenLabs."""
    if eleven_client:
        try:
            audio = eleven_client.generate(text=text, voice="Rachel", model="eleven_multilingual_v2")
            return b"".join(audio)
        except Exception as e:
            print(f"⚠️ ElevenLabs failed: {e}. Falling back to gTTS.")

    try:
        tts = gTTS(text=text, lang='en', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        print(f"❌ gTTS failed: {e}")
        return b""
