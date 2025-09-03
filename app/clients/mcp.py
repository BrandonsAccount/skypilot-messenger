#!/usr/bin/env python3

import uuid, httpx
from typing import Any, Dict, Optional

class MCPClient:
    def __init__(self, rpc_url: str, auth_header: Optional[str] = None):
        self.rpc_url = rpc_url
        self.auth_header = auth_header

    async def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        if params is not None:
            payload["params"] = params

        headers = {"Content-Type": "application/json"}
        if self.auth_header:
            headers["Authorization"] = self.auth_header

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(self.rpc_url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(f"RPC error: {data['error']}")
            return data["result"]

    async def initialize(self):
        return await self.call("initialize", {
            "protocolVersion": "2025-03-26",
            "clientInfo": {"name": "MessengerHost", "version": "0.1.0"},
            "capabilities": {"tools": True, "resources": True, "prompts": True},
        })

    async def list_tools(self):
        return await self.call("tools/list", {})

    async def list_resources(self):
        return await self.call("resources/list", {})

    async def list_prompts(self):
        return await self.call("prompts/list", {})