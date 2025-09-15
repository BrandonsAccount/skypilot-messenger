from fastapi import APIRouter, Depends, HTTPException
from services import prompt
from lib.skyhelper_logger.skyhelper_logger import fancy_logger

router = APIRouter()
log = fancy_logger(__name__)

@router.post("/prompt")
async def handle_prompt(user_prompt: str, user_id: str = "0", session_id: str = "0"):
    log.info(f"Received prompt: {user_prompt} from user_id: {user_id}, session_id: {session_id}")
    return await prompt.process(user_prompt, user_id, session_id)

