"""Project & Config tools."""

from __future__ import annotations

from typing import Any

from burp_wrapper.tools.base import BaseTools


class ConfigTools(BaseTools):
    tool_name = "config"

    def get_project(self) -> dict[str, Any]:
        return self._call("getProject")

    def get_user(self) -> dict[str, Any]:
        return self._call("getUser")

    def export_project(self) -> dict[str, Any]:
        return self._call("exportProject")

    def import_project(self, json_config: str) -> dict[str, Any]:
        return self._call("importProject", {"json_config": json_config})
