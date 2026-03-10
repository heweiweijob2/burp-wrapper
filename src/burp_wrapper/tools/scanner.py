"""Scanner tools (Pro only)."""

from __future__ import annotations

from typing import Any

from burp_wrapper.tools.base import BaseTools


class ScannerTools(BaseTools):
    tool_name = "scanner"

    def crawl(
        self,
        target: str | list[str],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"target": target}
        if config is not None:
            params["config"] = config
        return self._call("crawl", params)

    def audit(
        self,
        target: str | list[str] | None = None,
        request_id: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if target is not None:
            params["target"] = target
        if request_id is not None:
            params["request_id"] = request_id
        if config is not None:
            params["config"] = config
        return self._call("audit", params)

    def crawl_and_audit(
        self,
        target: str | list[str],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"target": target}
        if config is not None:
            params["config"] = config
        return self._call("crawlAndAudit", params)

    def status(self, scan_id: str) -> dict[str, Any]:
        return self._call("status", {"scan_id": scan_id})

    def issues(
        self,
        scan_id: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if scan_id is not None:
            params["scan_id"] = scan_id
        if filters is not None:
            params["filters"] = filters
        return self._call("issues", params)

    def pause(self, scan_id: str) -> dict[str, Any]:
        return self._call("pause", {"scan_id": scan_id})

    def resume(self, scan_id: str) -> dict[str, Any]:
        return self._call("resume", {"scan_id": scan_id})

    def stop(self, scan_id: str) -> dict[str, Any]:
        return self._call("stop", {"scan_id": scan_id})

    def get_issue_definitions(self) -> dict[str, Any]:
        return self._call("getIssueDefinitions")
