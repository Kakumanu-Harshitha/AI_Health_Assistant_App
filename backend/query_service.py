from fastapi import APIRouter, Depends, File, UploadFile, Form
from PIL import Image
from . import mongo_memory, llm_service, speech_service
from .auth import get_current_user
from .sql import User
from transformers import BlipProcessor, BlipForConditionalGeneration

router = APIRouter(prefix="/query", tags=["Query"])

# --- Load BLIP model globally ---
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

@router.post("/image")
async def handle_image_query(
    query: str = Form(""),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    user_id_str = str(current_user.id)
    history = mongo_memory.get_user_memory(user_id_str)

    # Analyze image
    image = Image.open(file.file)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=50)
    image_caption = processor.decode(out[0], skip_special_tokens=True)

    # Build prompt (text optional)
    if query.strip() != "":
        full_prompt = f"The user said: '{query}'. The uploaded image appears to show: '{image_caption}'. Identify possible health conditions."
    else:
        full_prompt = f"The uploaded image appears to show: '{image_caption}'. Identify possible health conditions."

    # Generate LLM response
    response_text = llm_service.get_llm_response(full_prompt, history)

    # Store messages
    mongo_memory.store_message(user_id_str, "user", full_prompt)
    mongo_memory.store_message(user_id_str, "assistant", response_text)

    return {"response": response_text, "image_caption": image_caption}
