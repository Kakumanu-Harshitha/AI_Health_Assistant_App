
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
uri=os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client["Health_Assistant"]
memory_collection = db["Health_Memory"]

def store_message(user_id: str, role: str, content: str):
    """Stores a message in the user's conversation history."""
    if memory_collection is None: return
    memory_collection.insert_one({
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc)
    })

def get_user_memory(user_id: str, limit: int = 10):
    """Retrieves the last 'limit' messages for the LLM, in chronological order."""
    if memory_collection is None: return []
    
    messages = memory_collection.find(
        {"user_id": user_id},
        {"_id": 0, "role": 1, "content": 1} 
    ).sort("timestamp", -1).limit(limit)
    
    return list(reversed(list(messages)))

def get_full_history_for_dashboard(user_id: str, limit: int = 100):
    """Retrieves full history with timestamps for the dashboard."""
    if memory_collection is None: return []
    
    messages = memory_collection.find(
        {"user_id": user_id},
        {"_id": 0} 
    ).sort("timestamp", -1).limit(limit)
    
    return list(messages)
