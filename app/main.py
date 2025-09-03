import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict
import httpx
from datetime import datetime
from api.v1 import prompt

#from message.message import Message
#from clients.thinker import ThinkerClient

# WHAT: Defines the FastAPI app for handling user prompts via HTTP API.
# WHY: Fulfills the requirement for a RESTful interface.
app = FastAPI()

# do not need this yet....
# --- Middleware ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(prompt.router, prefix="/api/v1", tags=["prompt"])

# class PromptRequest(BaseModel):
#     prompt: str
#
# class PromptResponse(BaseModel):
#     result: dict

# @app.post("/prompt")
# async def handle_prompt(user_prompt: str, user_id: str = "0", session_id: str = "0"):
#     """
#     WHAT: Handles user prompts, sends them to the LLM API, and processes the response.
#     WHY: Orchestrates the main workflow as described in the requirements.
#     """
#
#     message.user_id = user_id
#     message.session_id = session_id
#     message.set_prompt(user_prompt)
#
#     timeout = httpx.Timeout(connect = 3.0, read = 30.0, write = 10.0, pool = None)
#     thinker = ThinkerClient(llm_api_url = LLM_API_URL, max_attempts = LLM_API_MAX_ATTEMPTS, timeout = timeout)
#     response = await thinker.process(message = message)
#
#     print(response)
#     return response.get("result", response.get("error", {"message": "Unknown error occurred"}))