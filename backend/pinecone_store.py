import os
# Import the Pinecone class and 'init' is no longer needed
from pinecone import Pinecone 
from dotenv import load_dotenv # <-- Make sure this is imported

load_dotenv()
# --- INITIALIZATION (Updated) ---
# 1. Create the Pinecone client instance
# We'll name the instance 'pc'
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# 2. Get the index instance using the 'pc' client
# NOTE: The index object is now fetched via the client instance (pc)
index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)

# --------------------------------

def upsert_memory(user_id: str, embedding: list, text: str):
    if not index or not embedding:
        return
    vid = f"{user_id}-{abs(hash(text))}"
    index.upsert([(vid, embedding, {"text": text, "user_id": user_id})])

def query_memory(embedding: list, top_k: int = 3):
    if not index or not embedding:
        return []
    res = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    return [m['metadata']['text'] for m in res['matches']]