import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
# Assuming you have loaded environment variables (e.g., using load_dotenv())
username = "harshitha2006"
password = "Kharshitha123"
uri = f"mongodb+srv://{username}:{password}@cluster0.i79tx42.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
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

def get_user_memory(user_id: str, limit: int = 20):
    """Retrieves the last 'limit' messages for the LLM, in chronological order."""
    if memory_collection is None: return []
    
    # --- THE FIX ---
    # This projection now *only* fetches the 'role' and 'content' fields.
    # This prevents the 'datetime is not JSON serializable' error that was crashing the backend.
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
        {"_id": 0} # Get all fields except the internal ID for the dashboard
    ).sort("timestamp", -1).limit(limit)
    
    return list(messages)

