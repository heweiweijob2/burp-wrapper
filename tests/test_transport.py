"""Tests for the transport layer."""

import json

import httpx
import pytest
import respx

from burp_wrapper.exceptions import BurpAPIError, BurpConnectionError
from burp_wrapper.transport import BurpTransport


@pytest.fixture
def transport():
    return BurpTransport(base_url="http://127.0.0.1:9876")


class TestTransportCall:
    def test_sends_jsonrpc_to_message_endpoint(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            route = mock.post("/message").mock(
                return_value=httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {"data": "ok"}})
            )
            result = transport.call("proxy.getHistory", {"limit": 10})

            body = json.loads(route.calls.last.request.content.decode())
            assert body["jsonrpc"] == "2.0"
            assert body["method"] == "tools/call"
            assert body["params"]["name"] == "proxy.getHistory"
            assert body["params"]["arguments"] == {"limit": 10}
            assert result == {"data": "ok"}

    def test_increments_request_id(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            route = mock.post("/message").mock(
                return_value=httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {}})
            )
            transport.call("a")
            transport.call("b")

            body1 = json.loads(route.calls[0].request.content.decode())
            body2 = json.loads(route.calls[1].request.content.decode())
            assert body1["id"] == 1
            assert body2["id"] == 2

    def test_raises_connection_error(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            mock.post("/message").mock(side_effect=httpx.ConnectError("refused"))
            with pytest.raises(BurpConnectionError, match="Cannot connect"):
                transport.call("test")

    def test_raises_api_error_on_http_error(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            mock.post("/message").mock(return_value=httpx.Response(500, text="Internal Server Error"))
            with pytest.raises(BurpAPIError, match="HTTP 500"):
                transport.call("test")

    def test_raises_api_error_on_jsonrpc_error(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            mock.post("/message").mock(
                return_value=httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "Method not found"}})
            )
            with pytest.raises(BurpAPIError, match="Method not found"):
                transport.call("nonexistent")

    def test_unwraps_mcp_content_response(self, transport):
        """The MCP tools/call wraps results in content[].text."""
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            mock.post("/message").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "content": [
                                {"type": "text", "text": '{"total": 5, "entries": []}'}
                            ]
                        },
                    },
                )
            )
            result = transport.call("proxy.getHistory")
            assert result == {"total": 5, "entries": []}

    def test_handles_non_json_content_text(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            mock.post("/message").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "result": {
                            "content": [{"type": "text", "text": "plain string result"}]
                        },
                    },
                )
            )
            result = transport.call("decoder.encode")
            assert result == {"raw": "plain string result"}

    def test_default_params_empty_dict(self, transport):
        with respx.mock(base_url="http://127.0.0.1:9876") as mock:
            route = mock.post("/message").mock(
                return_value=httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {}})
            )
            transport.call("dashboard.getTasks")
            body = json.loads(route.calls.last.request.content.decode())
            assert body["params"]["arguments"] == {}
