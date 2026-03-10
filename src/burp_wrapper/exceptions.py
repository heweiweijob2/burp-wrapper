"""Custom exceptions for the Burp wrapper."""

from __future__ import annotations


class BurpWrapperError(Exception):
    """Base exception for the wrapper."""


class BurpConnectionError(BurpWrapperError):
    """Cannot connect to Burp Suite."""


class BurpAPIError(BurpWrapperError):
    """Error returned by the Burp API."""

    def __init__(self, code: int = -1, message: str = "Unknown error"):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class NotImplementedInBurpMCP(BurpWrapperError):
    """Feature not supported by the official Burp MCP Server.

    Solutions:
    1. Fork the MCP Server and add the tool in Kotlin
    2. Create a custom Burp extension exposing this feature
    3. Use an alternative (e.g. quick_fuzz via repeater instead of intruder)
    """


class SessionError(BurpWrapperError):
    """Error related to session logging."""
