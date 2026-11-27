"""Offline unit and integration test suite for DoesCap."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

import pytest

import doescap
from doescap import (
    DoesCap,
    RelayConfig,
    SolveResult,
    async_solve_captcha,
    get_local_ip,
    solve_captcha,
)
from doescap.browser import find_browser, is_android_termux
from doescap.network import find_free_port


def _wait_for_server(relay: DoesCap, timeout: float = 3.0) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if relay._server is not None and relay._active_port != 0:
            return f"http://127.0.0.1:{relay._active_port}"
        time.sleep(0.02)
    raise TimeoutError("Relay server did not bind in time")


def test_solve_result_str_behavior() -> None:
    res = SolveResult(
        token="P1_abc123",
        success=True,
        elapsed_seconds=1.25,
        metadata={"mode": "direct"},
    )
    assert isinstance(res, str)
    assert res == "P1_abc123"
    assert bool(res) is True
    assert {"X-Captcha-Key": res}["X-Captcha-Key"] == "P1_abc123"
    assert "success=True" in repr(res)

    empty = SolveResult(token=None, success=False, error="timed out")
    assert empty == ""
    assert bool(empty) is False
    assert "success=False" in repr(empty)


def test_relay_config_defaults_and_overrides() -> None:
    cfg = RelayConfig()
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 8787
    assert cfg.auto_open_browser is True
    assert cfg.browser_path is None
    assert cfg.timeout == 300
    assert cfg.title == "DoesCap Relay"
    assert cfg.theme == "dark"
    assert cfg.allow_firewall_rule is True
    assert cfg.custom_html is None
    assert cfg.custom_html_path is None
    assert cfg.custom_assets_dir is None

    relay = DoesCap(host="127.0.0.1", port=9001, auto_open_browser=False, theme="light")
    assert relay.config.host == "127.0.0.1"
    assert relay.config.port == 9001
    assert relay.config.auto_open_browser is False
    assert relay.config.theme == "light"


def test_network_helpers() -> None:
    ip = get_local_ip()
    assert isinstance(ip, str) and len(ip.split(".")) == 4

    port = find_free_port(0, "127.0.0.1")
    assert isinstance(port, int) and port > 0


def test_termux_detection_and_find_browser(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.delenv("ANDROID_ROOT", raising=False)
    monkeypatch.delenv("TERMUX_VERSION", raising=False)
    monkeypatch.setenv("PREFIX", "/usr/local")
    assert is_android_termux() is False

    monkeypatch.setenv("TERMUX_VERSION", "0.118.0")
    assert is_android_termux() is True
    assert find_browser() == (None, None)

    fake_bin = tmp_path / "custom_browser.exe"
    fake_bin.write_text("", encoding="utf-8")
    exe, label = find_browser(str(fake_bin))
    assert exe == str(fake_bin)
    assert label == "Custom Browser"


def test_live_http_endpoints_and_solve_flow(tmp_path) -> None:
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "theme.css").write_text("body { background: #161616; }", encoding="utf-8")

    custom_html = (
        "<html><head><title>{{ title }}</title></head>"
        "<body data-theme='{{ theme }}' data-sitekey='{{ sitekey }}' data-rq='{{ rqdata }}'>"
        "<link rel='stylesheet' href='/assets/theme.css'>"
        "</body></html>"
    )

    cfg = RelayConfig(
        host="127.0.0.1",
        port=0,
        auto_open_browser=False,
        allow_firewall_rule=False,
        title="Custom DoesCap Test",
        theme="light",
        custom_html=custom_html,
        custom_assets_dir=str(assets_dir),
    )

    with DoesCap(config=cfg) as relay:
        outcome = {}

        def worker() -> None:
            outcome["result"] = relay.solve(
                sitekey="10000000-ffff-ffff-ffff-000000000001",
                rqdata="rq_payload_xyz",
                task_name="UnitTestTask",
                timeout=5,
            )

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        base = _wait_for_server(relay)

        # GET / (verify SSR interpolation & CORS)
        with urllib.request.urlopen(base + "/") as resp:
            assert resp.status == 200
            assert resp.headers.get("Access-Control-Allow-Origin") == "*"
            html = resp.read().decode("utf-8")
            assert "<title>Custom DoesCap Test</title>" in html
            assert "data-theme='light'" in html
            assert "data-sitekey='10000000-ffff-ffff-ffff-000000000001'" in html
            assert "data-rq='rq_payload_xyz'" in html

        # GET /status
        with urllib.request.urlopen(base + "/status") as resp:
            status = json.loads(resp.read().decode("utf-8"))
            assert status["mode"] == "direct"
            assert status["sitekey"] == "10000000-ffff-ffff-ffff-000000000001"
            assert status["rqdata"] == "rq_payload_xyz"
            assert status["task_name"] == "UnitTestTask"
            assert status["solved"] is False

        # GET /frame.jpg returns 204 when empty
        with urllib.request.urlopen(base + "/frame.jpg") as resp:
            assert resp.status == 204

        # GET /assets/theme.css
        with urllib.request.urlopen(base + "/assets/theme.css") as resp:
            assert resp.status == 200
            assert "background: #161616" in resp.read().decode("utf-8")

        # Path traversal protection on /assets/
        with pytest.raises(urllib.error.HTTPError) as exc_info:
            urllib.request.urlopen(base + "/assets/../secret.txt")
        assert exc_info.value.code == 404

        # POST /solve without token -> 400
        bad_req = urllib.request.Request(
            base + "/solve",
            data=json.dumps({}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as bad_exc:
            urllib.request.urlopen(bad_req)
        assert bad_exc.value.code == 400

        # POST /solve with valid token -> 200
        ok_req = urllib.request.Request(
            base + "/solve",
            data=json.dumps({"token": "  P1_verified_token_999  "}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(ok_req) as resp:
            assert resp.status == 200
            assert json.loads(resp.read().decode("utf-8"))["ok"] is True

        t.join(timeout=3)
        res = outcome["result"]
        assert isinstance(res, SolveResult)
        assert res == "P1_verified_token_999"
        assert res.success is True
        assert res.metadata["mode"] == "direct"

        # Lifecycle methods update public status cleanly even after solve() returns
        relay.mark_completed("All done!")
        assert relay.get_public_status()["success_message"] == "All done!"

        relay.mark_claimed(task_name="Enterprise Quest", promo_code="GHOSTY-2026")
        with urllib.request.urlopen(base + "/status") as resp:
            post_claim = json.loads(resp.read().decode("utf-8"))
            assert post_claim["solved"] is True
            assert post_claim["claimed"] is True
            assert post_claim["task_name"] == "Enterprise Quest"
            assert post_claim["promo_code"] == "GHOSTY-2026"

        # Verify built-in template handles post-solve claimed state updates
        from doescap.templates import render_html_page
        default_page = render_html_page(title="DoesCap", theme="dark")
        assert "if (st.solved || st.claimed)" in default_page
        assert "hcaptcha.setData" in default_page


def test_custom_html_path_and_timeout(tmp_path) -> None:
    html_file = tmp_path / "portal.html"
    html_file.write_text("<h1>{{ title }} :: {{ sitekey }}</h1>", encoding="utf-8")

    cfg = RelayConfig(
        host="127.0.0.1",
        port=0,
        auto_open_browser=False,
        allow_firewall_rule=False,
        title="FileTemplate",
        custom_html_path=str(html_file),
    )

    with DoesCap(config=cfg) as relay:
        # Verify timeout returns None and cleans up
        res = relay.solve(sitekey="test-sitekey", timeout=0)
        assert res is None
        assert relay._server is None


def test_async_solve_and_functional_helpers() -> None:
    relay = DoesCap(
        host="127.0.0.1",
        port=0,
        auto_open_browser=False,
    )
    relay.config.allow_firewall_rule = False

    async def runner() -> SolveResult | None:
        async def submit_soon() -> None:
            base = _wait_for_server(relay)
            req = urllib.request.Request(
                base + "/solve",
                data=json.dumps({"token": "ASYNC_OK_TOKEN"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req).read()

        task = asyncio.create_task(submit_soon())
        res = await relay.async_solve(sitekey="10000000-ffff-ffff-ffff-000000000001", timeout=5)
        await task
        return res

    try:
        res = asyncio.run(runner())
        assert res == "ASYNC_OK_TOKEN"
        assert res is not None and res.success is True
    finally:
        relay.close()

    assert callable(solve_captcha)
    assert callable(async_solve_captcha)
    assert hasattr(doescap, "__version__")
