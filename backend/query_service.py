from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
import base64
from io import BytesIO

from . import mongo_memory, llm_service, speech_service
from .auth import get_current_user
from .sql import User

router = APIRouter(prefix="/query", tags=["Query"])

class TextQuery(BaseModel):
    text: str

@router.post("/text")
async def handle_text_query(query: TextQuery, current_user: User = Depends(get_current_user)):
    user_id_str = str(current_user.id)
    history = mongo_memory.get_user_memory(user_id_str)
    
    response_text = llm_service.get_llm_response(query.text, history)
    
    mongo_memory.store_message(user_id_str, 'user', query.text)
    mongo_memory.store_message(user_id_str, 'assistant', response_text)
        
    return {"response": response_text}

@router.post("/image")
async def handle_image_query(query: str = Form(...), file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    user_id_str = str(current_user.id)
    history = mongo_memory.get_user_memory(user_id_str)

    # The prompt already contains all text. We just add a note about the image.
    full_prompt = f"The user has provided the following text: '{query}'. They have also uploaded an image for additional context. Please analyze the text and refer to the fact an image was provided in your response."
    
    response_text = llm_service.get_llm_response(full_prompt, history)
    
    mongo_memory.store_message(user_id_str, 'user', full_prompt)
    mongo_memory.store_message(user_id_str, 'assistant', response_text)
    
    return {"response": response_text}

@router.post("/voice")
async def handle_voice_query(
    file: UploadFile = File(...), 
    text_context: str = Form(""), # Optional text from the form
    image_context: bool = Form(False), # Flag to indicate an image was present
    current_user: User = Depends(get_current_user)
):
    user_id_str = str(current_user.id)
    
    audio_buffer = BytesIO(await file.read())
    audio_buffer.name = file.filename or "audio.wav"

    transcribed_text = speech_service.speech_to_text(audio_buffer)
    if "[stt_error]" in transcribed_text:
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {transcribed_text}")
    
    # --- COMBINE ALL INPUTS INTO ONE PROMPT ---
    prompt_parts = [f"The user said: '{transcribed_text}'."]
    if text_context:
        prompt_parts.append(f"They also wrote: '{text_context}'.")
    if image_context:
        prompt_parts.append("They also uploaded an image for context.")
    
    full_prompt = " ".join(prompt_parts)
        
    history = mongo_memory.get_user_memory(user_id_str)
    response_text = llm_service.get_llm_response(full_prompt, history)
    
    mongo_memory.store_message(user_id_str, 'user', full_prompt)
    mongo_memory.store_message(user_id_str, 'assistant', response_text)
    
    audio_bytes = speech_service.text_to_speech(response_text)
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Text-to-speech conversion failed.")
        
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return {
        "transcribed_text": transcribed_text,
        "text_response": response_text,
        "audio_response": audio_base64
    }


