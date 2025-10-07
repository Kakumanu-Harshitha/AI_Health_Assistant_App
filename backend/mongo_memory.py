import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# --- Initialize MongoDB Client ---
MONGO_URI = os.getenv("MONGO_URI")
memory_collection = None
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client["Health_Assistant"]
        memory_collection = db["Health_Memory"]
        print("✅ MongoDB client initialized.")
    except Exception as e:
        print(f"⚠️ WARNING: Could not connect to MongoDB. Memory service disabled. Error: {e}")
else:
    print("⚠️ WARNING: MONGO_URI not found! Memory service disabled.")


def store_message(user_id: str, role: str, content: str):
    """Stores a message in the user's conversation history."""
    if memory_collection is None: return
    try:
        memory_collection.insert_one({
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc)
        })
    except Exception as e:
        print(f"❌ ERROR: Failed to store message in MongoDB. Error: {e}")

def get_user_memory(user_id: str, limit: int = 10) -> list:
    """Retrieves the last 'limit' messages for the LLM, in chronological order."""
    if memory_collection is None: return []
    try:
        messages = memory_collection.find(
            {"user_id": user_id},
            {"_id": 0, "role": 1, "content": 1} 
        ).sort("timestamp", -1).limit(limit)
        
        # Reverse the results to be in chronological order for the LLM context
        return list(reversed(list(messages)))
    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve user memory from MongoDB. Error: {e}")
        return []

def get_full_history_for_dashboard(user_id: str, limit: int = 100) -> list:
    """Retrieves full history with timestamps for the dashboard view."""
    if memory_collection is None: return []
    try:
        messages = memory_collection.find(
            {"user_id": user_id},
            {"_id": 0} 
        ).sort("timestamp", -1).limit(limit)
        return list(messages)
    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve dashboard history from MongoDB. Error: {e}")
        return []
