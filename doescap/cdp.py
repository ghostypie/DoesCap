"""Chrome DevTools Protocol (CDP) client for headless screencast mode."""

from __future__ import annotations

import json
import threading
from typing import Any, Dict, Optional, Tuple

try:
    import websocket
    HAVE_WEBSOCKET = True
except ImportError:
    websocket = None
    HAVE_WEBSOCKET = False

CDP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)

CDP_BOOT_SCRIPT = """
(() => {{
  if (window.__hcrBoot && document.getElementById('hcr-box')) return 'ok';
  window.__hcrBoot = 1;
  window.__hcrToken = null;
  let host = document.getElementById('hcr-box');
  const rq = {rqdata};
  const ch = {captcha_host};
  if (!host) {{
    host = document.createElement('div');
    host.id = 'hcr-box';
    host.style.cssText = 'position:fixed;left:20px;top:80px;z-index:2147483647';
    if (rq) host.setAttribute('data-rqdata', rq);
    host.setAttribute('data-sitekey', {sitekey});
    document.body.appendChild(host);
  }}

  window.__hcrReady = () => {{
    if (!window.hcaptcha || !window.hcaptcha.render) return setTimeout(window.__hcrReady, 100);
    const opts = {{
      sitekey: {sitekey},
      callback: function(token) {{ window.__hcrToken = token; }},
      "error-callback": function(e) {{ console.error('hcr error', e); }},
      "expired-callback": function() {{ window.__hcrToken = null; }}
    }};
    if (rq) opts.rqdata = rq;
    if (ch) opts.host = ch;
    try {{
      window.__hcrId = hcaptcha.render('hcr-box', opts);
      if (window.hcaptcha && window.hcaptcha.setData) {{
        const sd = {{}};
        if (rq) sd.rqdata = rq;
        if (ch) sd.host = ch;
        if (Object.keys(sd).length > 0) {{
          try {{ window.hcaptcha.setData(window.__hcrId, sd); }} catch(e) {{}}
        }}
      }}
    }} catch (e) {{
      console.error('render failed', e);
    }}
  }};

  if (window.hcaptcha && window.hcaptcha.render) {{
    window.__hcrReady();
  }} else {{
    const s = document.createElement('script');
    let apiUrl = 'https://js.hcaptcha.com/1/api.js?onload=__hcrReady&render=explicit';
    if (ch) {{
      apiUrl += '&host=' + encodeURIComponent(ch);
    }}
    s.src = apiUrl;
    document.head.appendChild(s);
  }}
  return 'ok';
}})()
"""

CDP_RECT_SCRIPT = """(() => {
  const frames = Array.from(document.querySelectorAll('iframe'));
  const challengeFrame = frames.find(f => (f.title === 'hCaptcha challenge' || (f.src && f.src.includes('frame=challenge'))) && f.getBoundingClientRect().width > 100 && f.getBoundingClientRect().y > -500);
  if (challengeFrame) {
    const r = challengeFrame.getBoundingClientRect();
    if (r.width > 100 && r.height > 100) {
      return { x: r.x, y: r.y, w: r.width, h: r.height };
    }
  }
  const checkboxFrame = document.querySelector('#hcr-box iframe') || frames.find(f => f.title && f.title.includes('checkbox'));
  if (!checkboxFrame) return null;
  const r = checkboxFrame.getBoundingClientRect();
  if (!r.width || !r.height) return null;
  return { x: r.x, y: r.y, w: r.width, h: r.height };
})()"""

CDP_TOKEN_SCRIPT = """(() => {
  if (window.__hcrToken) return window.__hcrToken;
  const hResp = document.querySelector('textarea[name="h-captcha-response"]');
  if (hResp && hResp.value) return hResp.value;
  const gResp = document.querySelector('textarea[name="g-recaptcha-response"]');
  if (gResp && gResp.value) return gResp.value;
  return '';
})()"""


class CdpClient:
    """Thread-safe Chrome DevTools Protocol client using WebSocket."""

    def __init__(self, ws_url: str):
        if not HAVE_WEBSOCKET:
            raise ImportError(
                "The 'websocket-client' package is required for Headless Screencast mode. "
                "Install it via: pip install websocket-client"
            )
        self._id = 0
        self._pending: Dict[int, Tuple[threading.Event, Dict[str, Any]]] = {}
        self.ws = websocket.create_connection(ws_url, timeout=10)
        self._closed = False
        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self) -> None:
        while not self._closed:
            try:
                raw = self.ws.recv()
            except Exception:
                break
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except Exception:
                continue

            mid = msg.get("id")
            if mid is not None and mid in self._pending:
                evt, slot = self._pending.pop(mid)
                slot["result"] = msg.get("result")
                slot["error"] = msg.get("error")
                evt.set()

    def send(self, method: str, params: Optional[dict] = None, timeout: float = 10.0) -> dict:
        """Send a synchronous JSON-RPC command over CDP and await its response."""
        self._id += 1
        mid = self._id
        slot: Dict[str, Any] = {}
        evt = threading.Event()
        self._pending[mid] = (evt, slot)

        payload = json.dumps({"id": mid, "method": method, "params": params or {}})
        self.ws.send(payload)

        if not evt.wait(timeout):
            raise TimeoutError(f"CDP call {method} timed out after {timeout}s")
        if slot.get("error"):
            raise RuntimeError(f"CDP command {method} failed: {slot['error']}")
        return slot.get("result") or {}

    def evaluate(self, expression: str) -> Any:
        """Evaluate a JavaScript expression in the page context."""
        res = self.send("Runtime.evaluate", {"expression": expression, "returnByValue": True})
        return res.get("result", {}).get("value")

    def close(self) -> None:
        """Gracefully disconnect WebSocket."""
        self._closed = True
        try:
            self.ws.close()
        except Exception:
            pass
