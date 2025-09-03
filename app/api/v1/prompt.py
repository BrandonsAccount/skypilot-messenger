from fastapi import APIRouter, Depends, HTTPException
from services import prompt

router = APIRouter()

@router.post("/prompt")
async def handle_prompt(user_prompt: str, user_id: str = "0", session_id: str = "0"):
    return await prompt.process(user_prompt, user_id, session_id)

