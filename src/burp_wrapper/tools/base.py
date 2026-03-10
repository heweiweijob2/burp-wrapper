"""Base class for tool namespaces with auto-logging."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from burp_wrapper.exceptions import NotImplementedInBurpMCP

if TYPE_CHECKING:
    from burp_wrapper.client import BurpClient


class BaseTools:
    """Base class providing _call with automatic session logging."""

    tool_name: str = "base"

    def __init__(self, client: BurpClient):
        self._client = client

    def _call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        target_host: str | None = None,
    ) -> dict[str, Any]:
        """Call the Burp API and log the action."""
        params = params or {}
        start = time.time()
        error: str | None = None
        result: dict[str, Any] | None = None

        try:
            result = self._client._call(f"{self.tool_name}.{method}", params)
            return result
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration_ms = int((time.time() - start) * 1000)
            session = self._client.session
            if session is not None:
                session.log_action(
                    tool=self.tool_name,
                    method=method,
                    params=params,
                    result=result,
                    error=error,
                    duration_ms=duration_ms,
                    target_host=target_host,
                )

    def _not_implemented(self, method: str) -> None:
        """Raise for methods not supported by the official Burp MCP Server."""
        raise NotImplementedInBurpMCP(
            f"{self.tool_name}.{method} is not supported by the official Burp MCP Server. "
            "Options: 1) Fork the MCP Server to add this tool in Kotlin, "
            "2) Create a custom Burp extension, "
            "3) Use an alternative method."
        )
