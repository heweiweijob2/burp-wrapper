"""Sequencer tools."""

from __future__ import annotations

from typing import Any

from burp_wrapper.tools.base import BaseTools


class SequencerTools(BaseTools):
    tool_name = "sequencer"

    def start_live_capture(
        self,
        request_id: str,
        token_config: dict[str, Any],
        sample_count: int = 200,
    ) -> dict[str, Any]:
        return self._call(
            "startLiveCapture",
            {
                "request_id": request_id,
                "token_config": token_config,
                "sample_count": sample_count,
            },
        )

    def capture_status(self, capture_id: str) -> dict[str, Any]:
        return self._call("captureStatus", {"capture_id": capture_id})

    def analyze(self, capture_id: str) -> dict[str, Any]:
        return self._call("analyze", {"capture_id": capture_id})

    def analyze_manual(self, tokens: list[str]) -> dict[str, Any]:
        return self._call("analyzeManual", {"tokens": tokens})

    def results(self, analysis_id: str) -> dict[str, Any]:
        return self._call("results", {"analysis_id": analysis_id})
