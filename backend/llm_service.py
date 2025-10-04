import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- CORRECTED MODEL NAME ---
# Updated to a currently supported and recommended model from Groq.
LLM_MODEL = "llama-3.1-8b-instant"

# Initialize client
client = None
if os.getenv("GROQ_API_KEY"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Groq client initialized.")
else:
    print("⚠️ WARNING: GROQ_API_KEY not found! LLM service disabled.")

def get_llm_response(prompt: str, conversation_history: list = None) -> str:
    """Generates a structured, safe medical response."""
    if not client:
        return "LLM service is unavailable — please check the GROQ_API_KEY in your .env file."

    system_prompt = (
        "You are a highly sophisticated and empathetic AI Health Assistant. "
        "Your primary role is to provide safe, informative, and helpful preliminary guidance based on user-provided symptoms, medical questions, or images. "
        "You must adhere to the following strict guidelines for every response:\n\n"
        "1.  **Safety First Disclaimer (Mandatory):** ALWAYS begin your response with a clear and prominent disclaimer. State that you are an AI assistant, not a medical professional, and your analysis is for informational purposes only. Strongly urge the user to consult a qualified healthcare provider for an accurate diagnosis and treatment plan.\n\n"
        "2.  **Symptom Analysis:** Carefully analyze the symptoms or query provided by the user.\n\n"
        "3.  **Provide Potential Conditions:** Based on the analysis, list a few *potential* conditions that might be associated with the symptoms. Use cautious language like 'Some conditions that can cause these symptoms include...' or 'This could possibly be related to...'.\n\n"
        "4.  **Actionable Advice & Recommendations:** Provide general, safe, and actionable advice. This should include:\n"
        "    - **Lifestyle suggestions:** (e.g., 'Getting adequate rest and staying hydrated can be beneficial.')\n"
        "    - **Dietary recommendations:** (e.g., 'For skin health, some people find it helpful to incorporate more leafy greens and reduce processed sugars.')\n\n"
        "5.  **NEVER Diagnose:** Under no circumstances should you provide a definitive diagnosis. Do not say 'You have...' or 'This is...'. Always frame it as a possibility.\n\n"
        "6.  **Empathetic Tone:** Maintain a professional, calm, and empathetic tone throughout the conversation."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=LLM_MODEL,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"❌ ERROR: Groq API call failed. Error: {e}")
        return "I'm sorry, I encountered an error while processing your request."

