from message.message import Message
from clients.thinker import ThinkerClient
from message.message import Message
import httpx
import os

LLM_API_URL = f"{os.getenv('LLM_API_URL')}/jsonrpc"
LLM_API_MAX_ATTEMPTS = int(os.getenv("LLM_API_MAX_ATTEMPTS", 3))
MCP_CLIENT_URL = os.getenv("MCP_CLIENT_URL")

async def process(user_prompt: str, user_id: str = "0", session_id: str = "0"):
    # prepare the message object that we will send to the LLM API
    message = Message()
    message.user_id = user_id
    message.session_id = session_id
    message.set_prompt(user_prompt)

    # use the ThinkerClient to send the message to the LLM API
    timeout = httpx.Timeout(connect = 3.0, read = 30.0, write = 10.0, pool = None)
    thinker = ThinkerClient(llm_api_url = LLM_API_URL, max_attempts = LLM_API_MAX_ATTEMPTS, timeout = timeout)
    response = await thinker.process(message = message)
    response["result"]["context"] = message.to_json()

    print(response)
    return response.get("result", response.get("error", {"message": "Unknown error occurred"}))