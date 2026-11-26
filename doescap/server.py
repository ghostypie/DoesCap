"""Lightweight, resilient HTTP relay server for DoesCap verification."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, TYPE_CHECKING

from .templates import render_html_page

if TYPE_CHECKING:
    from .client import DoesCap

# Common MIME type fallbacks
MIME_MAP = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".ttf": "font/ttf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".otf": "font/otf",
}


class ReusableThreadingServer(ThreadingHTTPServer):
    """Threading HTTPServer with SO_REUSEADDR enabled and error suppression."""

    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        err_type = sys.exc_info()[0]
        if err_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return
        super().handle_error(request, client_address)


def build_request_handler(relay: "DoesCap") -> type[BaseHTTPRequestHandler]:
    """Create a RequestHandler class bound to the active DoesCap instance."""

    class RelayHTTPHandler(BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:
            # Suppress default console access logging
            pass

        def _send_response(
            self,
            code: int,
            body: Any,
            content_type: str = "application/json",
        ) -> None:
            try:
                data = body if isinstance(body, bytes) else body.encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
                self.end_headers()
                self.wfile.write(data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass

        def do_OPTIONS(self) -> None:
            try:
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
                self.send_header("Content-Length", "0")
                self.end_headers()
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass

        def _resolve_custom_html(self) -> Optional[str]:
            """Retrieve custom HTML content if configured."""
            if relay.config.custom_html:
                return relay.config.custom_html

            if relay.config.custom_html_path:
                path = os.path.abspath(relay.config.custom_html_path)
                if os.path.isfile(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            return f.read()
                    except Exception:
                        pass
            return None

        def _serve_static_asset(self, raw_path: str) -> bool:
            """Safely serve custom static assets preventing directory traversal."""
            assets_dir = relay.config.custom_assets_dir
            if not assets_dir or not os.path.isdir(assets_dir):
                return False

            base_dir = os.path.abspath(assets_dir)
            clean_rel = urllib.parse.unquote(raw_path.split("?")[0]).lstrip("/\\")
            if clean_rel.startswith("assets/"):
                clean_rel = clean_rel[len("assets/"):].lstrip("/\\")

            target_file = os.path.abspath(os.path.join(base_dir, clean_rel))

            # Validate path containment
            try:
                common = os.path.commonpath([base_dir, target_file])
                if common != base_dir or not os.path.isfile(target_file):
                    return False
            except Exception:
                return False

            ext = os.path.splitext(target_file)[1].lower()
            mime_type = MIME_MAP.get(ext) or mimetypes.guess_type(target_file)[0] or "application/octet-stream"

            try:
                with open(target_file, "rb") as f:
                    data = f.read()
                self._send_response(200, data, mime_type)
                return True
            except Exception:
                return False

        def do_GET(self) -> None:
            try:
                if self.path.startswith("/frame.jpg"):
                    frame = relay.get_current_frame()
                    if frame:
                        self._send_response(200, frame, "image/jpeg")
                    else:
                        self._send_response(204, b"")
                elif self.path.startswith("/status"):
                    status_info = relay.get_public_status()
                    self._send_response(200, json.dumps(status_info))
                elif self.path.startswith("/assets/") and relay.config.custom_assets_dir:
                    if not self._serve_static_asset(self.path):
                        self._send_response(404, b"Asset Not Found", "text/plain")
                else:
                    # Check for custom webpage template
                    custom_html = self._resolve_custom_html()
                    if custom_html is not None:
                        status = relay.get_public_status()
                        # Optional SSR placeholder interpolation
                        rendered = (
                            custom_html
                            .replace("{{ title }}", relay.config.title)
                            .replace("{{ theme }}", relay.config.theme)
                            .replace("{{ sitekey }}", status.get("sitekey", ""))
                            .replace("{{ rqdata }}", status.get("rqdata", ""))
                        )
                        self._send_response(200, rendered, "text/html; charset=utf-8")
                    else:
                        default_html = render_html_page(
                            title=relay.config.title,
                            theme=relay.config.theme,
                        )
                        self._send_response(200, default_html, "text/html; charset=utf-8")
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass

        def do_POST(self) -> None:
            try:
                if self.path.startswith("/input"):
                    length = int(self.headers.get("Content-Length", 0))
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                    relay.handle_input_event(
                        kind=payload.get("t", "move"),
                        x=float(payload.get("x", 0)),
                        y=float(payload.get("y", 0)),
                    )
                    self._send_response(200, '{"ok":true}')
                elif self.path.startswith("/solve"):
                    length = int(self.headers.get("Content-Length", 0))
                    payload = json.loads(self.rfile.read(length).decode("utf-8"))
                    token_val = payload.get("token")
                    if token_val:
                        relay.submit_token(str(token_val).strip())
                        self._send_response(200, '{"ok":true}')
                    else:
                        self._send_response(400, '{"error":"missing token"}')
                else:
                    self._send_response(404, '{"error":"not found"}')
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                pass
            except Exception as e:
                self._send_response(500, json.dumps({"error": str(e)}))

    return RelayHTTPHandler
