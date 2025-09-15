from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
from api.v1 import prompt

# WHAT: Defines the FastAPI app for handling user prompts via HTTP API.
# WHY: Fulfills the requirement for a RESTful interface.
app = FastAPI()

app.include_router(prompt.router, prefix="/api/v1", tags=["prompt"])