"""Organizer tools."""

from __future__ import annotations

from typing import Any

from burp_wrapper.tools.base import BaseTools


class OrganizerTools(BaseTools):
    tool_name = "organizer"

    def add(self, request_id: str, collection: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"request_id": request_id}
        if collection is not None:
            params["collection"] = collection
        return self._call("add", params)

    def list(self, collection: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if collection is not None:
            params["collection"] = collection
        return self._call("list", params)

    def annotate(self, organizer_id: str, notes: str) -> dict[str, Any]:
        return self._call(
            "annotate", {"organizer_id": organizer_id, "notes": notes}
        )

    def get_collections(self) -> dict[str, Any]:
        return self._call("getCollections")

    def create_collection(self, name: str) -> dict[str, Any]:
        return self._call("createCollection", {"name": name})
