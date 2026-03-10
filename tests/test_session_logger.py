"""Tests for the session logger."""

import json
from pathlib import Path

import pytest

from burp_wrapper.session_logger import SessionLogger, _sanitize_params, _truncate_result


@pytest.fixture
def tmp_log_dir(tmp_path):
    return str(tmp_path / "logs")


@pytest.fixture
def logger(tmp_log_dir):
    return SessionLogger(log_dir=tmp_log_dir, target="example.com")


class TestSessionLoggerInit:
    def test_creates_log_dir(self, tmp_log_dir):
        SessionLogger(log_dir=tmp_log_dir, target="test")
        assert Path(tmp_log_dir).exists()

    def test_session_id_format(self, logger):
        assert len(logger.session_id) == 15  # YYYYMMDD_HHMMSS

    def test_initial_counts_zero(self, logger):
        assert logger.actions_count == 0
        assert logger.findings_count == 0
        assert logger.errors_count == 0


class TestLogAction:
    def test_writes_to_jsonl_file(self, logger):
        logger.log_action(
            tool="proxy", method="getHistory", params={"limit": 10}, duration_ms=50
        )
        content = logger.session_file.read_text().strip()
        entry = json.loads(content)
        assert entry["tool"] == "proxy"
        assert entry["method"] == "getHistory"
        assert entry["duration_ms"] == 50

    def test_increments_action_count(self, logger):
        logger.log_action(tool="proxy", method="get", params={})
        logger.log_action(tool="proxy", method="get", params={})
        assert logger.actions_count == 2

    def test_increments_error_count(self, logger):
        logger.log_action(tool="proxy", method="get", params={}, error="fail")
        assert logger.errors_count == 1

    def test_sanitizes_sensitive_params(self, logger):
        logger.log_action(
            tool="proxy",
            method="get",
            params={"password": "secret123", "host": "example.com"},
        )
        content = logger.session_file.read_text().strip()
        entry = json.loads(content)
        assert entry["params"]["password"] == "[REDACTED]"
        assert entry["params"]["host"] == "example.com"

    def test_truncates_large_results(self, logger):
        big_result = {"data": "x" * 20000}
        logger.log_action(tool="t", method="m", params={}, result=big_result)
        content = logger.session_file.read_text().strip()
        entry = json.loads(content)
        assert entry["result"]["_truncated"] is True
        assert entry["result"]["_size"] > 10000


class TestLogFinding:
    def test_writes_finding(self, logger):
        logger.log_finding({
            "name": "SQL Injection",
            "severity": "high",
            "url": "https://example.com/login",
            "detail": "Error-based SQLi",
        })
        content = logger.session_file.read_text().strip()
        entry = json.loads(content)
        assert entry["type"] == "finding"
        assert entry["name"] == "SQL Injection"
        assert entry["severity"] == "high"

    def test_increments_findings_count(self, logger):
        logger.log_finding({"name": "XSS", "severity": "medium", "url": "/"})
        assert logger.findings_count == 1


class TestEndSession:
    def test_writes_summary_file(self, logger):
        logger.log_action(tool="t", method="m", params={})
        logger.end_session()
        summary_file = logger.log_dir / f"{logger.session_id}_summary.json"
        assert summary_file.exists()
        data = json.loads(summary_file.read_text())
        assert data["actions_count"] == 1
        assert data["target"] == "example.com"

    def test_returns_summary(self, logger):
        summary = logger.end_session()
        assert summary.session_id == logger.session_id
        assert summary.ended_at is not None


class TestExportReport:
    def test_markdown_report(self, logger):
        logger.log_action(tool="proxy", method="getHistory", params={}, duration_ms=100)
        logger.log_finding({"name": "XSS", "severity": "high", "url": "/vuln"})
        report = logger.export_report("markdown")
        assert "# Session Report" in report
        assert "XSS" in report
        assert "proxy.getHistory" in report

    def test_json_report(self, logger):
        logger.log_action(tool="t", method="m", params={})
        report = logger.export_report("json")
        data = json.loads(report)
        assert "actions" in data
        assert "findings" in data
        assert len(data["actions"]) == 1


class TestSanitizeParams:
    def test_redacts_password(self):
        assert _sanitize_params({"password": "x"}) == {"password": "[REDACTED]"}

    def test_redacts_token(self):
        assert _sanitize_params({"auth_token": "x"}) == {"auth_token": "[REDACTED]"}

    def test_keeps_safe_params(self):
        assert _sanitize_params({"host": "x"}) == {"host": "x"}


class TestTruncateResult:
    def test_none_passthrough(self):
        assert _truncate_result(None) is None

    def test_small_result_passthrough(self):
        r = {"a": 1}
        assert _truncate_result(r) == {"a": 1}

    def test_large_result_truncated(self):
        r = {"data": "x" * 20000}
        result = _truncate_result(r)
        assert result["_truncated"] is True
