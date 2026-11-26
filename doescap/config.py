"""Configuration models and data structures for DoesCap."""

from __future__ import annotations

from typing import Any, Dict, Optional


class SolveResult(str):
    """String-compatible result returned after solving an hCaptcha challenge.

    Inherits from str so it can be passed directly to HTTP headers, APIs,
    and string functions without conversion, while also exposing metadata.

    Attributes:
        token: The verified hCaptcha response token (same as str value), or None.
        success: True if a valid token was acquired.
        elapsed_seconds: Total duration in seconds spent waiting for resolution.
        error: Error description if solving failed.
        metadata: Dictionary containing additional session details.
    """

    token: Optional[str]
    success: bool
    elapsed_seconds: float
    error: Optional[str]
    metadata: Dict[str, Any]

    def __new__(
        cls,
        token: Optional[str] = None,
        success: bool = False,
        elapsed_seconds: float = 0.0,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "SolveResult":
        value = str(token) if token else ""
        instance = super().__new__(cls, value)
        instance.token = token
        instance.success = success
        instance.elapsed_seconds = elapsed_seconds
        instance.error = error
        instance.metadata = metadata or {}
        return instance

    def __bool__(self) -> bool:
        return self.success and bool(self.token)

    def __repr__(self) -> str:
        if self.success and self.token:
            preview = f"{self.token[:20]}..." if len(self.token) > 20 else self.token
            return f"<SolveResult success=True token='{preview}' elapsed={self.elapsed_seconds:.2f}s>"
        return f"<SolveResult success=False error={self.error!r} elapsed={self.elapsed_seconds:.2f}s>"


class RelayConfig:
    """Configuration options for the DoesCap relay server and solver engine.

    Attributes:
        host: Host address to bind the HTTP relay server to. Defaults to "0.0.0.0".
        port: Preferred TCP port to listen on. Defaults to 8787.
        auto_open_browser: Automatically launches default browser on device. Defaults to True.
        browser_path: Optional path for custom browser in headless screencast mode.
        timeout: Maximum seconds to wait for resolution. Defaults to 300.
        title: Title displayed on the web interface header.
        theme: Web interface color scheme ("dark" or "light"). Defaults to "dark".
        allow_firewall_rule: Attempts adding Windows Firewall rule on Windows. Defaults to True.
        custom_html: Raw custom HTML template string to serve instead of default UI.
        custom_html_path: Filepath pointing to a custom HTML file to serve.
        custom_assets_dir: Filepath pointing to a directory containing static assets
            (e.g., CSS, fonts, logos) served under `/assets/*`.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8787,
        auto_open_browser: bool = True,
        browser_path: Optional[str] = None,
        timeout: int = 300,
        title: str = "DoesCap Relay",
        theme: str = "dark",
        allow_firewall_rule: bool = True,
        custom_html: Optional[str] = None,
        custom_html_path: Optional[str] = None,
        custom_assets_dir: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.auto_open_browser = auto_open_browser
        self.browser_path = browser_path
        self.timeout = timeout
        self.title = title
        self.theme = theme
        self.allow_firewall_rule = allow_firewall_rule
        self.custom_html = custom_html
        self.custom_html_path = custom_html_path
        self.custom_assets_dir = custom_assets_dir

    def __repr__(self) -> str:
        return (
            f"RelayConfig(host={self.host!r}, port={self.port}, "
            f"auto_open_browser={self.auto_open_browser}, timeout={self.timeout}, "
            f"custom_html_path={self.custom_html_path!r})"
        )
