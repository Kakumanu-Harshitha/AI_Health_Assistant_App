from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
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

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load model once (do this globally to avoid reloading every time)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

@router.post("/image")
async def handle_image_query(
    query: str = Form(""),  # text is optional now
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    user_id_str = str(current_user.id)
    history = mongo_memory.get_user_memory(user_id_str)

    # Step 1: Analyze the image
    image = Image.open(file.file)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    image_caption = processor.decode(out[0], skip_special_tokens=True)

    # Step 2: Build a full prompt with text + image description
    if query:
        full_prompt = (
            f"The user said: '{query}'. "
            f"The uploaded image appears to show: '{image_caption}'. "
            f"Based on both, identify any possible health conditions or diseases."
        )
    else:
        full_prompt = (
            f"The uploaded image appears to show: '{image_caption}'. "
            f"Please identify possible health conditions or diseases visible."
        )

    # Step 3: Generate LLM response
    response_text = llm_service.get_llm_response(full_prompt, history)

    mongo_memory.store_message(user_id_str, "user", full_prompt)
    mongo_memory.store_message(user_id_str, "assistant", response_text)

    return {"response": response_text, "image_caption": image_caption}


@router.post("/voice")
async def handle_voice_query(
    file: UploadFile = File(...), 
    text_context: str = Form(""), 
    image_context: bool = Form(False), 
    current_user: User = Depends(get_current_user)
):
    user_id_str = str(current_user.id)
    
    audio_buffer = BytesIO(await file.read())
    audio_buffer.name = file.filename or "audio.wav"

    transcribed_text = speech_service.speech_to_text(audio_buffer)
    if "[stt_error]" in transcribed_text:
        raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {transcribed_text}")
    
    # Combine all inputs
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
    
    # Return only text, no audio
    return {
        "transcribed_text": transcribed_text,
        "text_response": response_text
    }
