#!/usr/bin/env python3

import uuid
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx

DEFAULT_TIMEOUT = 10.0
DEFAULT_RETRIES = 3
BACKOFF_FACTOR = 0.5  # seconds

class MCPClient:
    def __init__(self, rpc_url: str, auth_header: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        if not rpc_url:
            raise ValueError("rpc_url must be provided for MCPClient")
        # Ensure URL has a scheme (http://) for httpx to resolve properly
        parsed = urlparse(rpc_url)
        if not parsed.scheme:
            raise ValueError("rpc_url must include scheme (e.g. http://host:port/path)")
        self.rpc_url = rpc_url
        self.auth_header = auth_header
        self.timeout = timeout

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None, retries: int = DEFAULT_RETRIES) -> Any:
        """
        Call the MCP JSON-RPC endpoint and return the parsed JSON response envelope.

        - On success this returns the parsed JSON body (typically a JSON-RPC envelope).
        - If the envelope contains an "error" field, the envelope is still returned (caller must inspect).
        - Transport/network errors (connectivity) and HTTP 4xx/5xx responses still raise RuntimeError.
        """
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        if params is not None:
            payload["params"] = params

        headers = {"Content-Type": "application/json"}
        if self.auth_header:
            headers["Authorization"] = self.auth_header

        attempt = 0
        backoff = BACKOFF_FACTOR
        while True:
            attempt += 1
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    r = await client.post(self.rpc_url, json=payload, headers=headers)
                    # Raise for HTTP status errors (transport-level), caller will handle application-level errors
                    r.raise_for_status()
                    try:
                        data = r.json()
                    except Exception:
                        # Non-JSON response from MCP — treat as a transport error
                        raise RuntimeError(f"MCP RPC at {self.rpc_url} returned non-JSON response (status {r.status_code})")
                    # Return the full JSON-RPC envelope to the caller (caller inspects 'result' vs 'error')
                    return data
            except (httpx.ConnectError, httpx.NetworkError) as exc:
                # Transient network/DNS/connectivity problems
                if attempt <= retries:
                    # brief backoff then retry
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 5.0)
                    continue
                # exhausted retries: raise informative error
                raise RuntimeError(f"Failed to connect to MCP RPC at {self.rpc_url}: {exc}") from exc
            except httpx.HTTPStatusError as exc:
                # Received HTTP 4xx/5xx - include body if available
                body = ""
                try:
                    body = r.text
                except Exception:
                    body = "<unreadable body>"
                raise RuntimeError(f"MCP RPC at {self.rpc_url} returned HTTP {r.status_code}: {body}") from exc
            except Exception as exc:
                # Any other unexpected error
                raise RuntimeError(f"Unexpected error calling MCP RPC at {self.rpc_url}: {exc}") from exc

    async def initialize(self):
        # Returns the full JSON-RPC envelope; caller should inspect envelope["result"] or envelope["error"]
        return await self.call(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "clientInfo": {"name": "MessengerHost", "version": "0.1.0"},
                "capabilities": {"tools": True, "resources": True, "prompts": True},
            },
        )

    async def list_tools(self):
        # Returns the full JSON-RPC envelope; caller should inspect envelope["result"] or envelope["error"]
        return await self.call("tools/list", {})

    async def list_resources(self):
        return await self.call("resources/list", {})

    async def list_prompts(self):
        return await self.call("prompts/list", {})