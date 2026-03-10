"""Transport layer for communicating with the Burp MCP Server."""

from __future__ import annotations

from typing import Any

import httpx

from burp_wrapper.exceptions import BurpAPIError, BurpConnectionError


class BurpTransport:
    """JSON-RPC transport over HTTP to the Burp MCP Server (port 9876)."""

    def __init__(self, base_url: str = "http://127.0.0.1:9876", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout)
        self._request_id = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC call to the MCP server.

        The Burp MCP Server uses JSON-RPC 2.0 over HTTP.
        Endpoint: POST /message with tools/call wrapper.
        """
        params = params or {}
        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params,
            },
        }

        try:
            resp = self._http.post("/message", json=payload)
        except httpx.ConnectError as e:
            raise BurpConnectionError(
                f"Cannot connect to Burp at {self.base_url}. "
                "Make sure Burp Suite is running with the MCP Server extension enabled."
            ) from e

        if resp.status_code != 200:
            raise BurpAPIError(
                code=resp.status_code,
                message=f"HTTP {resp.status_code}: {resp.text}",
            )

        data = resp.json()

        if "error" in data:
            err = data["error"]
            raise BurpAPIError(
                code=err.get("code", -1),
                message=err.get("message", str(err)),
            )

        # Extract result from JSON-RPC response
        result = data.get("result", {})

        # The MCP tools/call wraps the actual result in content
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                first = content[0]
                if isinstance(first, dict) and "text" in first:
                    import json

                    try:
                        return json.loads(first["text"])
                    except (json.JSONDecodeError, TypeError):
                        return {"raw": first["text"]}

        return result

    def close(self):
        self._http.close()
