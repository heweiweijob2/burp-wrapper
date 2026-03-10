"""Tests for the core BurpClient."""


import httpx

from burp_wrapper.client import BurpClient


def _ok(result: dict) -> httpx.Response:
    """Helper to build a JSON-RPC success response."""
    return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": result})


class TestBurpClientInit:
    def test_default_base_url(self):
        c = BurpClient(enable_logging=False)
        assert c.base_url == "http://127.0.0.1:9876"

    def test_custom_base_url(self):
        c = BurpClient(base_url="http://localhost:8080", enable_logging=False)
        assert c.base_url == "http://localhost:8080"

    def test_logging_disabled(self):
        c = BurpClient(enable_logging=False)
        assert c.session is None

    def test_logging_enabled(self, tmp_path):
        c = BurpClient(enable_logging=True, log_dir=str(tmp_path), target="test")
        assert c.session is not None
        assert c.session.target == "test"


class TestBurpClientCall:
    def test_call_delegates_to_transport(self, client, mock_api):
        mock_api.post("/message").mock(return_value=_ok({"data": "ok"}))
        result = client._call("proxy.getHistory", {"limit": 10})
        assert result == {"data": "ok"}

    def test_call_without_params(self, client, mock_api):
        mock_api.post("/message").mock(return_value=_ok({"tasks": []}))
        result = client._call("dashboard.getTasks")
        assert result == {"tasks": []}


class TestBurpClientContextManager:
    def test_context_manager_calls_end_session(self, tmp_path):
        with BurpClient(
            enable_logging=True, log_dir=str(tmp_path), target="test"
        ) as burp:
            session_id = burp.session.session_id

        # Summary file should exist after __exit__
        summary_file = tmp_path / f"{session_id}_summary.json"
        assert summary_file.exists()

    def test_context_manager_closes_transport(self, mock_api):
        mock_api.post("/message").mock(return_value=_ok({}))
        with BurpClient(enable_logging=False) as burp:
            burp._call("test")
        # No assertion needed — just verifying no exception


class TestBurpClientToolNamespaces:
    def test_has_all_namespaces(self, client):
        namespaces = [
            "proxy", "repeater", "intruder", "scanner", "decoder",
            "collaborator", "target", "sequencer", "comparer", "logger",
            "dashboard", "organizer", "search", "inspector", "engagement",
            "extensions", "config", "clickbandit",
        ]
        for ns in namespaces:
            assert hasattr(client, ns), f"Missing namespace: {ns}"

    def test_namespace_instances_are_cached(self, client):
        assert client.proxy is client.proxy
        assert client.intruder is client.intruder

    def test_tool_name_is_set(self, client):
        assert client.proxy.tool_name == "proxy"
        assert client.intruder.tool_name == "intruder"
        assert client.scanner.tool_name == "scanner"


class TestBurpClientSessionLogging:
    def test_tool_calls_are_logged(self, tmp_path, mock_api):
        mock_api.post("/message").mock(return_value=_ok({"total": 0, "entries": []}))
        with BurpClient(
            enable_logging=True, log_dir=str(tmp_path), target="example.com"
        ) as burp:
            burp.proxy.get_history(limit=10)

        assert burp.session.actions_count == 1

    def test_export_report(self, tmp_path, mock_api):
        mock_api.post("/message").mock(return_value=_ok({"total": 0, "entries": []}))
        with BurpClient(
            enable_logging=True, log_dir=str(tmp_path), target="example.com"
        ) as burp:
            burp.proxy.get_history()
            report = burp.export_report("markdown")

        assert "Session Report" in report
        assert "proxy" in report
