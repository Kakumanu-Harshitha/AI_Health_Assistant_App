from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
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

# --- Text-Only Query Endpoint ---
@router.post("/text")
async def handle_text_query(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Handles queries that only contain text."""
    user_id_str = str(current_user.id)
    text_input = payload.get("text", "")
    if not text_input.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    history = mongo_memory.get_user_memory(user_id_str)
    response_text = llm_service.get_llm_response(text_input, history)

    mongo_memory.store_message(user_id_str, "user", text_input)
    mongo_memory.store_message(user_id_str, "assistant", response_text)

    return {"response": response_text}

# --- Image Query Endpoint ---
@router.post("/image")
async def handle_image_query(
    query: str = Form(""),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Handles queries that include an image (and optional text)."""
    if not model or not processor:
        raise HTTPException(status_code=503, detail="Image processing service is currently unavailable.")
        
    user_id_str = str(current_user.id)
    history = mongo_memory.get_user_memory(user_id_str)

    # Analyze image to generate a caption
    image = Image.open(file.file).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    image_caption = processor.decode(out[0], skip_special_tokens=True)

    # Build a comprehensive prompt for the LLM
    if query.strip():
        full_prompt = f"The user asked: '{query}'. The uploaded image appears to show: '{image_caption}'. Based on both the text and the image, identify possible health conditions."
    else:
        full_prompt = f"The uploaded image appears to show: '{image_caption}'. Identify possible health conditions based on this image."

    # Generate LLM response
    response_text = llm_service.get_llm_response(full_prompt, history)

    # Store messages in memory
    mongo_memory.store_message(user_id_str, "user", full_prompt)
    mongo_memory.store_message(user_id_str, "assistant", response_text)

    return {"response": response_text, "image_caption": image_caption}

# --- Voice Query Endpoint (No TTS) ---
@router.post("/voice")
async def handle_voice_query(
    file: UploadFile = File(...),
    text_context: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Handles multimodal queries initiated with voice (STT only)."""
    user_id_str = str(current_user.id)
    
    # 1. Transcribe the user's audio
    transcribed_text = speech_service.speech_to_text(file)
    if transcribed_text.startswith("[stt_error]"):
        raise HTTPException(status_code=500, detail=f"Speech-to-Text failed: {transcribed_text}")

    # 2. Combine all inputs into a single prompt
    prompt_parts = [f"The user said: '{transcribed_text}'."]
    if text_context.strip():
        prompt_parts.append(f"They also typed: '{text_context}'.")
    final_prompt = " ".join(prompt_parts)

    # 3. Retrieve history and generate the text response
    history = mongo_memory.get_user_memory(user_id_str)
    text_response = llm_service.get_llm_response(final_prompt, history)

    # 4. Store the conversation
    mongo_memory.store_message(user_id_str, "user", final_prompt)
    mongo_memory.store_message(user_id_str, "assistant", text_response)

    # 5. Return only the text data to the frontend
    return {
        "transcribed_text": transcribed_text,
        "text_response": text_response
    }

