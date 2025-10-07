from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from typing import Optional
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Import all required custom service modules
from . import mongo_memory
from . import llm_service
from . import speech_service
from .auth import get_current_user
from .sql import User

# --- Router Setup ---
router = APIRouter(prefix="/query", tags=["Query Service"])

# --- Load Image Captioning Model Globally ---
try:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print("✅ BLIP image captioning model loaded successfully.")
except Exception as e:
    processor = None
    model = None
    print(f"⚠️ WARNING: Could not load BLIP model. Image functionality will be disabled. Error: {e}")


# --- NEW UNIFIED MULTIMODAL ENDPOINT ---
@router.post("/multimodal")
async def handle_multimodal_query(
    current_user: User = Depends(get_current_user),
    text_query: str = Form(""),
    audio_file: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None)
):
    """
    Handles any combination of text, voice, and image inputs in a single request.
    """
    user_id_str = str(current_user.id)
    transcribed_text = None
    image_caption = None
    prompt_parts = []

    # 1. Process Voice Input (if provided)
    if audio_file:
        transcribed_text = speech_service.speech_to_text(audio_file)
        if transcribed_text.startswith("[stt_error]"):
            raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {transcribed_text}")
        prompt_parts.append(f"The user said: '{transcribed_text}'.")

    # 2. Process Image Input (if provided)
    if image_file:
        if not model or not processor:
            raise HTTPException(status_code=503, detail="Image processing service is currently unavailable.")
        image = Image.open(image_file.file).convert("RGB")
        inputs = processor(image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        image_caption = processor.decode(out[0], skip_special_tokens=True)
        prompt_parts.append(f"The uploaded image appears to show: '{image_caption}'.")

    # 3. Process Text Input (if provided)
    if text_query.strip():
        prompt_parts.append(f"They also typed: '{text_query}'.")
        
    # 4. Check if any input was provided
    if not prompt_parts:
        raise HTTPException(status_code=400, detail="No input provided. Please provide text, voice, or an image.")

    # 5. Assemble the final prompt and get LLM response
    final_prompt = " ".join(prompt_parts)
    history = mongo_memory.get_user_memory(user_id_str)
    text_response = llm_service.get_llm_response(final_prompt, history)

    # 6. Store the conversation
    mongo_memory.store_message(user_id_str, "user", final_prompt)
    mongo_memory.store_message(user_id_str, "assistant", text_response)

    # 7. Return all relevant data to the frontend
    return {
        "text_response": text_response,
        "transcribed_text": transcribed_text,
        "image_caption": image_caption
    }

