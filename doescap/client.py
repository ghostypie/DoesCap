"""Main client interface for DoesCap."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import random
import subprocess
import threading
import time
import urllib.request
from typing import Any, Callable, Dict, Optional

from .browser import find_browser, open_browser
from .cdp import (
    CdpClient,
    CDP_BOOT_SCRIPT,
    CDP_RECT_SCRIPT,
    CDP_TOKEN_SCRIPT,
    CDP_USER_AGENT,
    HAVE_WEBSOCKET,
)
from .config import RelayConfig, SolveResult
from .network import find_free_port, get_local_ip, setup_windows_firewall_rule
from .server import build_request_handler, ReusableThreadingServer

logger = logging.getLogger("doescap")


class DoesCap:
    """Cross-platform hCaptcha relay orchestrator.

    Supports zero-overhead Direct In-Browser verification (fast, native 60/120Hz),
    Headless CDP Screencast mode, and custom developer webpage designs.
    """

    def __init__(
        self,
        config: Optional[RelayConfig] = None,
        *,
        host: Optional[str] = None,
        port: Optional[int] = None,
        auto_open_browser: Optional[bool] = None,
        browser_path: Optional[str] = None,
        timeout: Optional[int] = None,
        title: Optional[str] = None,
        theme: Optional[str] = None,
        custom_html: Optional[str] = None,
        custom_html_path: Optional[str] = None,
        custom_assets_dir: Optional[str] = None,
        captcha_host: Optional[str] = None,
    ):
        if config is not None:
            self.config = config
        else:
            self.config = RelayConfig()

        if host is not None:
            self.config.host = host
        if port is not None:
            self.config.port = port
        if auto_open_browser is not None:
            self.config.auto_open_browser = auto_open_browser
        if browser_path is not None:
            self.config.browser_path = browser_path
        if timeout is not None:
            self.config.timeout = timeout
        if title is not None:
            self.config.title = title
        if theme is not None:
            self.config.theme = theme
        if custom_html is not None:
            self.config.custom_html = custom_html
        if custom_html_path is not None:
            self.config.custom_html_path = custom_html_path
        if custom_assets_dir is not None:
            self.config.custom_assets_dir = custom_assets_dir
        if captcha_host is not None:
            self.config.captcha_host = captcha_host

        self._lock = threading.Lock()
        self._server: Optional[ReusableThreadingServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._headless_proc: Optional[subprocess.Popen] = None
        self._cdp: Optional[CdpClient] = None
        self._active_port: int = self.config.port

        self._state: Dict[str, Any] = {
            "mode": "direct",
            "sitekey": "",
            "rqdata": "",
            "captcha_host": "",
            "task_name": "",
            "promo_code": "",
            "solved": False,
            "claimed": False,
            "token": "",
            "frame": b"",
            "rect": None,
            "success_message": "",
            "error": "",
        }

    @property
    def relay_url(self) -> str:
        """Get the network HTTP URL pointing to this relay server."""
        ip = get_local_ip()
        return f"http://{ip}:{self._active_port}/"

    @property
    def localhost_url(self) -> str:
        """Get the localhost URL pointing to this relay server."""
        return f"http://127.0.0.1:{self._active_port}/"

    def get_public_status(self) -> Dict[str, Any]:
        """Fetch read-only status dictionary for client polling."""
        with self._lock:
            return {
                "mode": self._state["mode"],
                "sitekey": self._state["sitekey"],
                "rqdata": self._state["rqdata"],
                "captcha_host": self._state["captcha_host"],
                "task_name": self._state["task_name"],
                "promo_code": self._state["promo_code"],
                "solved": self._state["solved"],
                "claimed": self._state["claimed"],
                "success_message": self._state["success_message"],
                "error": self._state["error"],
                "rect": self._state["rect"],
            }

    def get_current_frame(self) -> bytes:
        """Get current screencast frame JPEG bytes."""
        with self._lock:
            return self._state.get("frame", b"")

    def submit_token(self, token: str) -> None:
        """Record a verified captcha token from web callback."""
        with self._lock:
            self._state["token"] = token
            self._state["solved"] = True

    def mark_completed(self, message: str = "Verification complete!") -> None:
        """Update client UI with a success notice."""
        with self._lock:
            self._state["success_message"] = message

    def mark_claimed(
        self,
        quest_name: str = "",
        reward_name: str = "",
        promo_code: str = "",
        task_name: Optional[str] = None,
    ) -> None:
        """Notify the web UI that the reward or task was successfully processed."""
        display_name = task_name or quest_name or reward_name
        with self._lock:
            self._state["claimed"] = True
            if display_name:
                self._state["task_name"] = display_name
            if promo_code:
                self._state["promo_code"] = promo_code
            self._state["success_message"] = "Action completed and confirmed successfully."

        # Schedule deferred cleanup after 25s so user can view/copy any promo code
        threading.Thread(target=self._delayed_cleanup, args=(25,), daemon=True).start()

    def mark_failed(self, error_msg: str) -> None:
        """Notify the web UI that the server action failed."""
        with self._lock:
            self._state["error"] = error_msg
        threading.Thread(target=self._delayed_cleanup, args=(10,), daemon=True).start()

    def _delayed_cleanup(self, delay: int = 25) -> None:
        time.sleep(delay)
        self.close()

    def handle_input_event(self, kind: str, x: float, y: float) -> None:
        """Forward user input (mouse/touch) into headless CDP session."""
        cdp = self._cdp
        if not cdp:
            return

        with self._lock:
            rect = self._state.get("rect")
        if not rect:
            return

        px = float(rect.get("x", 0)) + x
        py = float(rect.get("y", 0)) + y

        try:
            if kind == "move":
                cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseMoved",
                    "x": px,
                    "y": py,
                    "button": "none",
                    "buttons": 0,
                })
            elif kind == "press":
                cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseMoved",
                    "x": px,
                    "y": py,
                    "button": "none",
                    "buttons": 0,
                })
                cdp.send("Input.dispatchMouseEvent", {
                    "type": "mousePressed",
                    "x": px,
                    "y": py,
                    "button": "left",
                    "buttons": 1,
                    "clickCount": 1,
                })
            elif kind == "release":
                cdp.send("Input.dispatchMouseEvent", {
                    "type": "mouseReleased",
                    "x": px,
                    "y": py,
                    "button": "left",
                    "buttons": 0,
                    "clickCount": 1,
                })
        except Exception as e:
            logger.debug("Failed dispatching CDP input: %s", e)

    def _start_http_server(self) -> None:
        """Initialize and start background HTTP server."""
        if self._server is not None:
            return

        self._active_port = find_free_port(self.config.port, self.config.host)
        handler_cls = build_request_handler(self)

        try:
            self._server = ReusableThreadingServer((self.config.host, self._active_port), handler_cls)
        except OSError:
            self._active_port = find_free_port(0, self.config.host)
            self._server = ReusableThreadingServer((self.config.host, self._active_port), handler_cls)

        if self.config.allow_firewall_rule:
            setup_windows_firewall_rule(self._active_port, "DoesCap Relay")

        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        logger.info("DoesCap Relay server listening on %s:%d", self.config.host, self._active_port)

    def _stop_http_server(self) -> None:
        """Shutdown background HTTP server."""
        if self._server is not None:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:
                pass
            self._server = None
            self._server_thread = None

    def _mirror_screencast_loop(self, cdp: CdpClient) -> None:
        """Background thread polling frames from CDP page."""
        while True:
            with self._lock:
                if self._state.get("solved"):
                    break
            try:
                rect = cdp.evaluate(CDP_RECT_SCRIPT)
                if rect and rect.get("w") and rect.get("h"):
                    with self._lock:
                        self._state["rect"] = rect
                    clip_x = max(0.0, float(rect["x"]))
                    clip_y = max(0.0, float(rect["y"]))
                    shot = cdp.send("Page.captureScreenshot", {
                        "format": "jpeg",
                        "quality": 82,
                        "clip": {
                            "x": clip_x,
                            "y": clip_y,
                            "width": float(rect["w"]),
                            "height": float(rect["h"]),
                            "scale": 1,
                        },
                    })
                    if shot and shot.get("data"):
                        with self._lock:
                            self._state["frame"] = base64.b64decode(shot["data"])
            except Exception:
                pass
            time.sleep(0.20)

    def _poll_cdp_token_loop(self, cdp: CdpClient, timeout: int) -> Optional[str]:
        """Poll page runtime for solved hCaptcha token."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if self._state.get("solved") and self._state.get("token"):
                    return self._state["token"]
            try:
                token = cdp.evaluate(CDP_TOKEN_SCRIPT)
                if token:
                    clean = str(token).strip().strip('"').strip("'")
                    if clean:
                        self.submit_token(clean)
                        return clean
            except Exception:
                pass
            time.sleep(0.4)
        return None

    def solve(
        self,
        sitekey: str,
        rqdata: Optional[str] = None,
        *,
        timeout: Optional[int] = None,
        token: Optional[str] = None,
        context_token: Optional[str] = None,
        rqtoken: Optional[str] = None,
        quest_name: Optional[str] = None,
        task_name: Optional[str] = None,
        custom_html: Optional[str] = None,
        custom_html_path: Optional[str] = None,
        captcha_host: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[SolveResult]:
        """Solve an hCaptcha challenge synchronously.

        Returns an instance of SolveResult which behaves identically to a string
        containing the token, or None if cancelled/timed out.
        """
        start_time = time.time()
        effective_timeout = timeout if timeout is not None else self.config.timeout
        effective_task = task_name or quest_name or ""
        effective_captcha_host = (
            captcha_host if captcha_host is not None else (self.config.captcha_host or "")
        )
        auth_token = context_token or token

        if custom_html is not None:
            self.config.custom_html = custom_html
        if custom_html_path is not None:
            self.config.custom_html_path = custom_html_path

        # Determine operating mode
        use_screencast = False
        browser_exe = None
        browser_name = None

        if self.config.browser_path and HAVE_WEBSOCKET:
            browser_exe, browser_name = find_browser(self.config.browser_path)
            if browser_exe:
                use_screencast = True

        with self._lock:
            self._state = {
                "mode": "screencast" if use_screencast else "direct",
                "sitekey": sitekey,
                "rqdata": rqdata or "",
                "captcha_host": effective_captcha_host,
                "task_name": effective_task,
                "promo_code": "",
                "solved": False,
                "claimed": False,
                "token": "",
                "frame": b"",
                "rect": None,
                "success_message": "",
                "error": "",
            }

        # Start relay HTTP server
        self._start_http_server()

        # Launch default browser on client device
        if self.config.auto_open_browser:
            local_url = self.localhost_url
            threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()

        # DIRECT MODE
        if not use_screencast:
            try:
                deadline = time.time() + effective_timeout
                while time.time() < deadline:
                    with self._lock:
                        if self._state["solved"] and self._state["token"]:
                            elapsed = time.time() - start_time
                            return SolveResult(
                                token=self._state["token"],
                                success=True,
                                elapsed_seconds=elapsed,
                                metadata={"mode": "direct", "port": self._active_port},
                            )
                        if self._state["error"]:
                            return None
                    time.sleep(0.3)

                return None
            finally:
                with self._lock:
                    was_solved = self._state["solved"]
                if not was_solved:
                    self.close()

        # SCREENCAST MODE (via headless Chromium CDP)
        cdp_port = random.randint(20000, 60000)
        temp_dir = os.path.join(
            os.environ.get("TEMP", os.environ.get("TMP", os.getcwd())),
            f"doescap_relay_{cdp_port}",
        )

        launch_args = [
            browser_exe,
            f"--remote-debugging-port={cdp_port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={temp_dir}",
            "--no-first-run",
            "--window-size=1280,900",
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-sandbox",
            "--disable-extensions",
            "--disable-background-networking",
            f"--user-agent={CDP_USER_AGENT}",
            "--disable-blink-features=AutomationControlled",
            "about:blank",
        ]

        try:
            self._headless_proc = subprocess.Popen(
                launch_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.warning("Failed launching headless browser '%s': %s. Falling back to Direct Mode.", browser_name, e)
            with self._lock:
                self._state["mode"] = "direct"
            return self.solve(
                sitekey,
                rqdata,
                timeout=effective_timeout,
                token=auth_token,
                task_name=effective_task,
            )

        # Await CDP readiness
        cdp_http = f"http://127.0.0.1:{cdp_port}"
        cdp_ready = False
        for _ in range(35):
            try:
                with urllib.request.urlopen(f"{cdp_http}/json/version", timeout=2) as resp:
                    resp.read()
                    cdp_ready = True
                    break
            except Exception:
                time.sleep(0.3)

        if not cdp_ready:
            logger.warning("Headless CDP port timed out. Falling back to Direct Mode.")
            self._kill_headless()
            with self._lock:
                self._state["mode"] = "direct"
            return self.solve(
                sitekey,
                rqdata,
                timeout=effective_timeout,
                token=auth_token,
                task_name=effective_task,
            )

        try:
            new_tab_url = f"{cdp_http}/json/new?about:blank"
            try:
                req = urllib.request.Request(new_tab_url, method="PUT")
                with urllib.request.urlopen(req, timeout=10) as r:
                    tab_info = json.loads(r.read())
            except Exception:
                with urllib.request.urlopen(new_tab_url, timeout=10) as r:
                    tab_info = json.loads(r.read())

            self._cdp = CdpClient(tab_info["webSocketDebuggerUrl"])
            self._cdp.send("Page.enable")
            self._cdp.send("Runtime.enable")
            self._cdp.send("Network.enable")

            stealth_js = (
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                "window.chrome = { runtime: {} };"
            )
            if auth_token:
                stealth_js += f"; try {{ window.localStorage.setItem('token', JSON.stringify({json.dumps(auth_token)})); }} catch(e) {{}}"

            self._cdp.send("Page.addScriptToEvaluateOnNewDocument", {"source": stealth_js})
            self._cdp.send("Page.navigate", {"url": "about:blank"})
            time.sleep(1.0)

            self._cdp.evaluate(CDP_BOOT_SCRIPT.format(
                sitekey=json.dumps(sitekey),
                rqdata=json.dumps(rqdata),
                captcha_host=json.dumps(effective_captcha_host),
            ))

            threading.Thread(target=self._mirror_screencast_loop, args=(self._cdp,), daemon=True).start()

            solved = self._poll_cdp_token_loop(self._cdp, effective_timeout)
            elapsed = time.time() - start_time
            if solved:
                return SolveResult(
                    token=solved,
                    success=True,
                    elapsed_seconds=elapsed,
                    metadata={"mode": "screencast", "browser": browser_name},
                )
            return None
        except Exception as err:
            logger.warning("CDP session encountered error: %s. Falling back to Direct Mode.", err)
            with self._lock:
                self._state["mode"] = "direct"
            return self.solve(
                sitekey,
                rqdata,
                timeout=effective_timeout,
                token=auth_token,
                task_name=effective_task,
            )
        finally:
            self._kill_headless()
            with self._lock:
                was_solved = self._state["solved"]
            if not was_solved:
                self.close()

    # Drop-in compatibility alias
    solve_relay = solve

    async def async_solve(
        self,
        sitekey: str,
        rqdata: Optional[str] = None,
        *,
        timeout: Optional[int] = None,
        token: Optional[str] = None,
        context_token: Optional[str] = None,
        rqtoken: Optional[str] = None,
        quest_name: Optional[str] = None,
        task_name: Optional[str] = None,
        custom_html: Optional[str] = None,
        custom_html_path: Optional[str] = None,
        captcha_host: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[SolveResult]:
        """Solve an hCaptcha challenge asynchronously without blocking the event loop."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.solve(
                sitekey=sitekey,
                rqdata=rqdata,
                timeout=timeout,
                token=token,
                context_token=context_token,
                rqtoken=rqtoken,
                quest_name=quest_name,
                task_name=task_name,
                custom_html=custom_html,
                custom_html_path=custom_html_path,
                captcha_host=captcha_host,
                **kwargs,
            ),
        )

    def _kill_headless(self) -> None:
        """Terminate headless browser subprocess and CDP connection."""
        if self._cdp:
            try:
                self._cdp.close()
            except Exception:
                pass
            self._cdp = None

        if self._headless_proc:
            try:
                self._headless_proc.terminate()
                self._headless_proc.wait(timeout=2)
            except Exception:
                try:
                    self._headless_proc.kill()
                except Exception:
                    pass
            self._headless_proc = None

    def close(self) -> None:
        """Tear down all server and process resources."""
        self._kill_headless()
        self._stop_http_server()

    def cleanup(self) -> None:
        """Alias for close()."""
        self.close()

    def __enter__(self) -> "DoesCap":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


# Backward-compatible alias
HCaptchaRelay = DoesCap


def solve_captcha(
    sitekey: str,
    rqdata: Optional[str] = None,
    *,
    port: int = 8787,
    host: str = "0.0.0.0",
    auto_open_browser: bool = True,
    browser_path: Optional[str] = None,
    timeout: int = 300,
    title: str = "DoesCap Relay",
    custom_html: Optional[str] = None,
    custom_html_path: Optional[str] = None,
    custom_assets_dir: Optional[str] = None,
    captcha_host: Optional[str] = None,
    **kwargs: Any,
) -> Optional[str]:
    """Convenience functional helper to solve hCaptcha in a single call."""
    config = RelayConfig(
        host=host,
        port=port,
        auto_open_browser=auto_open_browser,
        browser_path=browser_path,
        timeout=timeout,
        title=title,
        custom_html=custom_html,
        custom_html_path=custom_html_path,
        custom_assets_dir=custom_assets_dir,
        captcha_host=captcha_host,
    )
    with DoesCap(config=config) as relay:
        result = relay.solve(sitekey=sitekey, rqdata=rqdata, **kwargs)
        return str(result) if result else None


async def async_solve_captcha(
    sitekey: str,
    rqdata: Optional[str] = None,
    *,
    port: int = 8787,
    host: str = "0.0.0.0",
    auto_open_browser: bool = True,
    browser_path: Optional[str] = None,
    timeout: int = 300,
    title: str = "DoesCap Relay",
    custom_html: Optional[str] = None,
    custom_html_path: Optional[str] = None,
    custom_assets_dir: Optional[str] = None,
    captcha_host: Optional[str] = None,
    **kwargs: Any,
) -> Optional[str]:
    """Convenience asynchronous helper to solve hCaptcha in a single call."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: solve_captcha(
            sitekey=sitekey,
            rqdata=rqdata,
            port=port,
            host=host,
            auto_open_browser=auto_open_browser,
            browser_path=browser_path,
            timeout=timeout,
            title=title,
            custom_html=custom_html,
            custom_html_path=custom_html_path,
            custom_assets_dir=custom_assets_dir,
            captcha_host=captcha_host,
            **kwargs,
        ),
    )
