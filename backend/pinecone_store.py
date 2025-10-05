import os
from pinecone import Pinecone 
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)


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