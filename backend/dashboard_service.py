
from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from .mongo_memory import get_full_history_for_dashboard
from .auth import get_current_user
from .sql import User 

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/history", response_model=List[Dict[str, Any]])
def get_user_history(current_user: User = Depends(get_current_user)):
    """Fetches the complete conversation history for the logged-in user."""
    user_id_str = str(current_user.id)
    history = get_full_history_for_dashboard(user_id_str, limit=100)
    return history
