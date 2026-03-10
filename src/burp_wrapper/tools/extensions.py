"""Extensions tools."""

from __future__ import annotations

from typing import Any

from burp_wrapper.tools.base import BaseTools


class ExtensionsTools(BaseTools):
    tool_name = "extensions"

    def list(self) -> dict[str, Any]:
        return self._call("list")

    def enable(self, name: str) -> dict[str, Any]:
        return self._call("enable", {"name": name})

    def disable(self, name: str) -> dict[str, Any]:
        return self._call("disable", {"name": name})

    def reload(self, name: str) -> dict[str, Any]:
        return self._call("reload", {"name": name})
