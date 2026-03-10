"""Core Burp Suite API client with session logging."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from burp_wrapper.session_logger import SessionLogger
from burp_wrapper.tools.clickbandit import ClickbanditTools
from burp_wrapper.tools.collaborator import CollaboratorTools
from burp_wrapper.tools.comparer import ComparerTools
from burp_wrapper.tools.config import ConfigTools
from burp_wrapper.tools.dashboard import DashboardTools
from burp_wrapper.tools.decoder import DecoderTools
from burp_wrapper.tools.engagement import EngagementTools
from burp_wrapper.tools.extensions import ExtensionsTools
from burp_wrapper.tools.inspector import InspectorTools
from burp_wrapper.tools.intruder import IntruderTools
from burp_wrapper.tools.logger import LoggerTools
from burp_wrapper.tools.organizer import OrganizerTools
from burp_wrapper.tools.proxy import ProxyTools
from burp_wrapper.tools.repeater import RepeaterTools
from burp_wrapper.tools.scanner import ScannerTools
from burp_wrapper.tools.search import SearchTools
from burp_wrapper.tools.sequencer import SequencerTools
from burp_wrapper.tools.target import TargetTools
from burp_wrapper.transport import BurpTransport


class BurpClient:
    """Client for the Burp Suite MCP Server API.

    Supports context manager for automatic session cleanup:

        with BurpClient(target="example.com") as burp:
            history = burp.proxy.get_history()
        # session report generated automatically
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:9876",
        timeout: float = 30.0,
        enable_logging: bool = True,
        log_dir: str = "./logs/sessions",
        target: str = "unknown",
    ):
        self.base_url = base_url
        self.transport = BurpTransport(base_url, timeout)
        self.session: SessionLogger | None = None

        if enable_logging:
            self.session = SessionLogger(log_dir=log_dir, target=target)

    def _call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a call to the Burp MCP server via the transport layer."""
        return self.transport.call(method, params)

    def health_check(self) -> dict[str, Any]:
        """Check that Burp is accessible."""
        return self.transport.call("health", {})

    def end_session(self) -> Any:
        """End the session and generate the summary."""
        if self.session:
            return self.session.end_session()
        return None

    def export_report(self, fmt: str = "markdown") -> str:
        """Export the session report."""
        if self.session:
            return self.session.export_report(fmt)
        return ""

    def close(self) -> None:
        """Close the HTTP transport."""
        self.transport.close()

    def __enter__(self) -> BurpClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.end_session()
        self.close()

    # --- Tool namespaces ---

    @cached_property
    def proxy(self) -> ProxyTools:
        return ProxyTools(self)

    @cached_property
    def repeater(self) -> RepeaterTools:
        return RepeaterTools(self)

    @cached_property
    def intruder(self) -> IntruderTools:
        return IntruderTools(self)

    @cached_property
    def scanner(self) -> ScannerTools:
        return ScannerTools(self)

    @cached_property
    def decoder(self) -> DecoderTools:
        return DecoderTools(self)

    @cached_property
    def collaborator(self) -> CollaboratorTools:
        return CollaboratorTools(self)

    @cached_property
    def target(self) -> TargetTools:
        return TargetTools(self)

    @cached_property
    def sequencer(self) -> SequencerTools:
        return SequencerTools(self)

    @cached_property
    def comparer(self) -> ComparerTools:
        return ComparerTools(self)

    @cached_property
    def logger(self) -> LoggerTools:
        return LoggerTools(self)

    @cached_property
    def dashboard(self) -> DashboardTools:
        return DashboardTools(self)

    @cached_property
    def organizer(self) -> OrganizerTools:
        return OrganizerTools(self)

    @cached_property
    def search(self) -> SearchTools:
        return SearchTools(self)

    @cached_property
    def inspector(self) -> InspectorTools:
        return InspectorTools(self)

    @cached_property
    def engagement(self) -> EngagementTools:
        return EngagementTools(self)

    @cached_property
    def extensions(self) -> ExtensionsTools:
        return ExtensionsTools(self)

    @cached_property
    def config(self) -> ConfigTools:
        return ConfigTools(self)

    @cached_property
    def clickbandit(self) -> ClickbanditTools:
        return ClickbanditTools(self)
