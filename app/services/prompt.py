from message.message import Message
from clients.thinker import ThinkerClient
from clients.mcp import MCPClient
from typing import Any, Dict, Optional
from lib.skyhelper_logger.skyhelper_logger import fancy_logger
import httpx
import os
import json

THINKER_API_URL = os.getenv('THINKER_API_URL')
THINKER_API_MAX_ATTEMPTS = int(os.getenv("THINKER_API_MAX_ATTEMPTS", 3))
JIRA_MCP_URL = os.getenv('JIRA_MCP_URL')
timeout = httpx.Timeout(connect = 3.0, read = 30.0, write = 10.0, pool = None)
thinker = ThinkerClient(thinker_api_url = THINKER_API_URL, max_attempts = THINKER_API_MAX_ATTEMPTS, timeout = timeout)

log = fancy_logger(__name__)

async def process(user_prompt: str, user_id: str = "0", session_id: str = "0"):
    message = await prepare_message(user_prompt, user_id, session_id)

    mcp_client = MCPClient(rpc_url = JIRA_MCP_URL)
    await mcp_client.initialize()
    message.capabilities = await mcp_client.list_tools()

    # send the message to thinker, handle the response, and call tools as needed
    attempts = 1
    while attempts <= THINKER_API_MAX_ATTEMPTS:
        response = await converse_with_thinker(message)
        message.set_llm_response(json.dumps(response, ensure_ascii=False))

        # handle the response from Thinker
        if response is None:
            return {"error": "No response from Thinker"}
        elif "error" in response:
            return {"error": response["error"]}
        elif "result" not in response:
            return {"error": "Malformed response from Thinker"}
        elif response["result"]['answer'] and response["result"]['actions'] == []:
            print('\n\n\n\nFinal Response to return to GUI:')
            log.info(message.to_json())
            return json.loads(message.to_json())

        # this is just being used to short-circuit the loop for now while testing
        #return response.get("result", response.get("error", {"message": "Unknown error occurred"}))

        # if the response includes actions, call the tools and update the message
        for action in response['result']['actions']:
            tool_name = action['tool']
            tool_input = action.get('input', {})
            tool_result = await mcp_client.call(tool_name, tool_input)
            message.set_feedback(json.dumps(tool_result, ensure_ascii=False))

        attempts += 1

async def prepare_message(user_prompt: str, user_id: str = "0", session_id: str = "0") -> Message:
    message = Message()
    message.user_id = user_id
    message.session_id = session_id
    message.set_prompt(user_prompt)
    return message

async def converse_with_thinker(message: Message) -> Dict[str, Any]:
    response = await thinker.process(message = message)
    return response
