"""Session logging for Burp wrapper — captures every action for replay and reporting."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ActionLog:
    timestamp: str
    session_id: str
    action: str
    tool: str
    method: str
    params: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    duration_ms: int
    target_host: str | None


@dataclass
class FindingLog:
    timestamp: str
    session_id: str
    name: str
    severity: str
    url: str
    detail: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionSummary:
    session_id: str
    started_at: str
    ended_at: str | None
    target: str
    actions_count: int
    findings_count: int
    errors_count: int


SENSITIVE_KEYS = frozenset({"password", "token", "secret", "key", "cookie", "authorization"})


class SessionLogger:
    """Logs every Burp wrapper action to a JSONL file for replay and reporting."""

    def __init__(self, log_dir: str = "./logs/sessions", target: str = "unknown"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.target = target
        safe_target = target.replace("/", "_").replace(":", "_").replace(".", "_")
        self.session_file = self.log_dir / f"{self.session_id}_{safe_target}.jsonl"

        self.actions_count = 0
        self.findings_count = 0
        self.errors_count = 0
        self.started_at = datetime.now().isoformat()

        self._logger = logging.getLogger(f"burp_wrapper.{self.session_id}")
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)

    def log_action(
        self,
        tool: str,
        method: str,
        params: dict[str, Any],
        result: dict[str, Any] | None = None,
        error: str | None = None,
        duration_ms: int = 0,
        target_host: str | None = None,
    ) -> None:
        self.actions_count += 1
        if error:
            self.errors_count += 1

        entry = ActionLog(
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            action=f"{tool}.{method}",
            tool=tool,
            method=method,
            params=_sanitize_params(params),
            result=_truncate_result(result),
            error=error,
            duration_ms=duration_ms,
            target_host=target_host or self.target,
        )

        self._write(asdict(entry))

        if error:
            self._logger.error(f"{tool}.{method} failed: {error}")
        else:
            self._logger.info(f"{tool}.{method} completed in {duration_ms}ms")

    def log_finding(self, finding: dict[str, Any]) -> None:
        self.findings_count += 1

        entry = FindingLog(
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            name=finding.get("name", "Unknown"),
            severity=finding.get("severity", "info"),
            url=finding.get("url", "N/A"),
            detail=finding.get("detail", ""),
            evidence=finding.get("evidence", {}),
        )

        data = asdict(entry)
        data["type"] = "finding"
        self._write(data)

        self._logger.warning(
            f"FINDING: {entry.name} [{entry.severity}] at {entry.url}"
        )

    def end_session(self) -> SessionSummary:
        summary = SessionSummary(
            session_id=self.session_id,
            started_at=self.started_at,
            ended_at=datetime.now().isoformat(),
            target=self.target,
            actions_count=self.actions_count,
            findings_count=self.findings_count,
            errors_count=self.errors_count,
        )

        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        summary_file.write_text(json.dumps(asdict(summary), indent=2))

        self._logger.info(
            f"Session ended: {self.actions_count} actions, "
            f"{self.findings_count} findings, {self.errors_count} errors"
        )
        return summary

    def export_report(self, fmt: str = "markdown") -> str:
        actions: list[dict[str, Any]] = []
        findings: list[dict[str, Any]] = []

        if self.session_file.exists():
            for line in self.session_file.read_text().splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("type") == "finding":
                    findings.append(entry)
                else:
                    actions.append(entry)

        if fmt == "json":
            return json.dumps({"actions": actions, "findings": findings}, indent=2)
        return _markdown_report(self, actions, findings)

    def _write(self, data: dict[str, Any]) -> None:
        with open(self.session_file, "a") as f:
            f.write(json.dumps(data) + "\n")


def _sanitize_params(params: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for k, v in params.items():
        if any(s in k.lower() for s in SENSITIVE_KEYS):
            sanitized[k] = "[REDACTED]"
        else:
            sanitized[k] = v
    return sanitized


def _truncate_result(
    result: dict[str, Any] | None, max_size: int = 10000
) -> dict[str, Any] | None:
    if result is None:
        return None
    result_str = json.dumps(result)
    if len(result_str) > max_size:
        return {
            "_truncated": True,
            "_size": len(result_str),
            "_preview": result_str[:1000],
        }
    return result


def _markdown_report(
    session: SessionLogger,
    actions: list[dict[str, Any]],
    findings: list[dict[str, Any]],
) -> str:
    lines = [
        "# Session Report",
        "",
        f"**Session:** {session.session_id}",
        f"**Target:** {session.target}",
        f"**Started:** {session.started_at}",
        f"**Actions:** {len(actions)}",
        f"**Findings:** {len(findings)}",
        "",
    ]

    if findings:
        lines.append("## Findings\n")
        for f in findings:
            lines.append(f"### {f.get('name', 'Unknown')}")
            lines.append(f"- **Severity:** {f.get('severity', 'N/A')}")
            lines.append(f"- **URL:** {f.get('url', 'N/A')}")
            if f.get("detail"):
                lines.append(f"- **Detail:** {f['detail']}")
            lines.append("")

    lines.append("## Actions Timeline\n")
    lines.append("| Time | Action | Duration | Status |")
    lines.append("|------|--------|----------|--------|")
    for a in actions[-50:]:
        status = "ERR" if a.get("error") else "OK"
        lines.append(
            f"| {a['timestamp'][:19]} | {a['action']} | {a['duration_ms']}ms | {status} |"
        )

    return "\n".join(lines) + "\n"
