import httpx
from urllib.parse import urlparse
import logging
from typing import Any, Dict
import uuid
import json
from jsonschema import validate, ValidationError

class ThinkerClient():
    def __init__(self, llm_api_url: str, timeout, max_attempts: int = 3):
        self.llm_api_url = self._validate_url(llm_api_url, "LLM API URL")
        self.max_attempts = max_attempts
        self.timeout = timeout

    def _validate_url(self, u: str, name: str) -> str:
        if not u:
            raise ValueError(f"{name} is not set")
        p = urlparse(u)
        if p.scheme not in ("http", "https"):
            raise ValueError(f"{name} must start with http:// or https:// (got: {u!r})")
        return u

    async def process(self, message) -> dict:
        """
        Sends a message document to the LLM service using JSON-RPC 2.0 and returns the response.
        Follows MCP principles: stateless, explicit input/output, robust error handling.
        """
        jsonrpc_request = {"jsonrpc": "2.0", "method": "processMessage", "params": message.to_json(), "id": str(uuid.uuid4())}
        response_is_valid = False
        attempts = 0
        while response_is_valid == False and attempts < self.max_attempts:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.llm_api_url, json=jsonrpc_request)
                    response.raise_for_status()
                    result = response.json()

                    if "error" in result:
                        error = result["error"]
                        if error.get("code") == -32000:
                            logging.error(f"LLM rate limit exceeded: {error}", exc_info=True)
                            return {
                                "error": "Rate limit exceeded",
                                "details": error.get("message"),
                                "info": "You exceeded your current LLM quota. Check your plan and billing details."
                            }

                    if not self.validate_llm_response(result['result']):
                        logging.warning("LLM response did not match output schema, retrying...")
                        message.set_feedback("LLM response did not match output schema, retrying...")
                        attempts += 1
                        continue

                    logging.info("LLM JSON-RPC request successful", extra={"request": jsonrpc_request, "response": result})
                    return result

            except httpx.RequestError as exc:
                logging.error(f"Request error while contacting LLM: {exc}", exc_info=True)
                return {"error": "LLM service unreachable", "details": str(exc)}
            except httpx.HTTPStatusError as exc:
                logging.error(f"LLM returned HTTP error: {exc}", exc_info=True)
                return {"error": "LLM service error", "details": str(exc)}
            except Exception as exc:
                logging.error(f"Unexpected error: {exc}", exc_info=True)
                return {"error": "Unexpected error", "details": str(exc)}

    def validate_llm_response(self, response: Dict[str, Any]) -> bool:
        """
        WHAT: Validates the LLM response against output-schema.json.
        WHY: Ensures contract between LLM and messenger is maintained.
        """
        try:
            with open("message/output-schema.json") as schema_file:
                schema = json.load(schema_file)
            validate(instance=response, schema=schema)
            return True
        except (ValidationError, FileNotFoundError, json.JSONDecodeError) as exc:
            logging.error(f"LLM response validation failed: {exc}", exc_info=True)
            return False
