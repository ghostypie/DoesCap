# DoesCap

A standalone, high-performance hCaptcha relay and verification library for Python.

Built for seamless operation across **Windows**, **macOS**, **Linux**, and **Android (Termux)**.

---

## Author & Community

- **Author**: **GhoSty** &mdash; [https://github.com/ghostypie](https://github.com/ghostypie)
- **Live Documentation**: [https://ghostypie.github.io/DoesCap/](https://ghostypie.github.io/DoesCap/)
- **PyPI Package**: [https://pypi.org/project/doescap/](https://pypi.org/project/doescap/)
- **Discord Support Server**: [https://discord.com/invite/asMJGgDA7u](https://discord.com/invite/asMJGgDA7u)
- **Support / Donate (Donatree)**: [https://donatr.ee/brutality/](https://donatr.ee/brutality/)

---

## Key Features

- **Zero-Latency Direct Solver (Default)**: Renders the official challenge natively in the user's browser with 60Hz/120Hz touch responsiveness, forwarding Enterprise `rqdata` via `hcaptcha.render` and `hcaptcha.setData` with zero extra CPU or RAM consumption.
- **Custom Webpage Designs**: Port your own custom HTML, CSS, logos, fonts, and layouts via `custom_html`, `custom_html_path`, and `custom_assets_dir` (including `{{ title }}`, `{{ theme }}`, `{{ sitekey }}`, and `{{ rqdata }}` SSR placeholders).
- **Universal Android & Termux Support**: Automatically handles Termux URL opening tools (`termux-open-url`, `termux-open`) and native Android activity intents (`am start`).
- **Modular 2D Documentation**: Multi-page 2D neo-brutalist documentation site with cross-page search, Next/Previous module navigation, and dark mode toggle in the `docs/` folder.
- **Headless Screencast Mode**: Optional fallback mode that runs a headless Chromium instance (`browser_path`) and mirrors frames over HTTP when `websocket-client` is installed, automatically falling back to Direct Mode if unavailable.
- **LAN Relay Accessibility**: Automatically determines local network IP address (`get_local_ip`), allowing mobile devices on the same Wi-Fi network to complete challenges running on desktop or remote hosts.
- **Full Type Hints & Async Support**: Both synchronous (`solve`, `solve_captcha`) and asynchronous (`async_solve`, `async_solve_captcha`) APIs returning string-subclass `SolveResult` objects.
- **Standalone CLI**: Command-line tool `doescap` for immediate terminal verification.

---

## Documentation

Full modular documentation is included in the `docs/` folder:
- **Offline / Local preview**: Open [docs/index.html](docs/index.html) in any browser, or run:
  ```bash
  python docs/serve.py
  ```
- Features a ReadTheDocs-style sidebar, cross-page search (`Ctrl+K`), Next/Previous module navigation buttons, REST API specs, parameter tables, and a 2D neo-brutalist light/dark mode toggle.

---

## Installation

```bash
pip install doescap
```

To enable headless CDP screencast streaming (optional):

```bash
pip install "doescap[screencast]"
```

---

## Quickstart

### 1. Functional Sync API

```python
from doescap import solve_captcha

token = solve_captcha(
    sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
    rqdata=None,
    port=8787,
    auto_open_browser=True,
)

if token:
    print(f"Verified Token: {token}")
else:
    print("Verification failed or timed out.")
```

### 2. Functional Async API

```python
import asyncio
from doescap import async_solve_captcha

async def main():
    token = await async_solve_captcha(
        sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
        port=8787,
    )
    print("Token:", token)

asyncio.run(main())
```

### 3. Object-Oriented Client

```python
from doescap import DoesCap, RelayConfig

config = RelayConfig(
    host="0.0.0.0",
    port=8787,
    auto_open_browser=True,
    timeout=300,
    title="DoesCap Verification Portal",
    theme="dark",
)

with DoesCap(config=config) as relay:
    result = relay.solve(
        sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
        rqdata=None,
        task_name="Verification Challenge",
    )

    if result:
        print(f"Solved in {result.elapsed_seconds:.2f}s")
        print(f"Token: {result.token}")
        # Compatible directly as a str in headers: {"X-Captcha-Key": result}
        relay.mark_claimed(task_name="Verification Challenge", promo_code="PASS-200")
```

### 4. Custom Webpage Design & Branding

You can supply your own custom HTML template and static assets:

```python
from doescap import DoesCap, RelayConfig

config = RelayConfig(
    host="0.0.0.0",
    port=8787,
    custom_html_path="path/to/my_template.html",
    custom_assets_dir="path/to/my_assets",
)

with DoesCap(config=config) as relay:
    token = relay.solve(sitekey="YOUR_SITEKEY")
```

#### Custom HTML Contract
Your custom HTML can read SSR placeholders (`{{ title }}`, `{{ theme }}`, `{{ sitekey }}`, `{{ rqdata }}`, `{{ captcha_host }}`) or communicate with two lightweight endpoints:
1. `GET /status`: Returns JSON with active `sitekey`, `rqdata`, `captcha_host`, `mode`, `solved`, `claimed`, `task_name`, `promo_code`, and `success_message`.
2. When `rqdata` or `captcha_host` is present, append `&host=` to the `api.js` URL, pass `opts.rqdata` / `opts.host` into `hcaptcha.render(...)`, and call `hcaptcha.setData(widgetId, { rqdata, host })`.
3. `POST /solve`: Send `{ "token": token }` once hCaptcha's callback fires.

Static files inside `custom_assets_dir` are served securely under `/assets/*`.

---

## Configuration Reference

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `host` | `str` | `"0.0.0.0"` | Host IP to bind the relay webserver to. |
| `port` | `int` | `8787` | Preferred TCP port. Ephemeral port chosen if busy. |
| `auto_open_browser` | `bool` | `True` | Automatically opens default browser on the device. |
| `browser_path` | `str \| None` | `None` | Path or binary keyword for headless CDP screencast mode. |
| `timeout` | `int` | `300` | Max wait time in seconds before returning `None`. |
| `title` | `str` | `"DoesCap Relay"` | Title string displayed in the web UI header. |
| `theme` | `str` | `"dark"` | UI theme (`"dark"` or `"light"`). |
| `allow_firewall_rule` | `bool` | `True` | Attempts Windows Firewall port opening on Windows. |
| `custom_html` | `str \| None` | `None` | Raw HTML string to serve as the custom UI. |
| `custom_html_path` | `str \| None` | `None` | Filepath to a custom `.html` template to serve. |
| `custom_assets_dir` | `str \| None` | `None` | Directory of assets (CSS, images, fonts) served at `/assets/*`. |
| `captcha_host` | `str \| None` | `None` | Optional hCaptcha origin hostname override (e.g. `"discord.com"`) for origin-locked Enterprise captchas. |

---

## Termux Android Usage

`DoesCap` works directly in Termux on Android without requiring root or display servers (no X11 / VNC needed).

1. Install Python in Termux:
   ```bash
   pkg update && pkg install python
   ```
2. Install package:
   ```bash
   pip install doescap
   ```
3. Run or import in your script. When executed, it launches your mobile Chrome or default Android browser via system intents, lets you complete the challenge smoothly with hardware-accelerated touch, and captures the solution token.

---

## CLI & Testing

```bash
doescap --sitekey "YOUR_SITEKEY" --rqdata "OPTIONAL_RQDATA" --captcha-host "discord.com" --port 8787
```

With custom HTML and assets:
```bash
doescap --sitekey "YOUR_SITEKEY" --custom-html "./my_ui.html" --assets-dir "./assets"
```

Run the offline unit test suite:
```bash
pytest
```

---

## License

MIT License &mdash; Copyright (c) 2026 [GhoSty](https://github.com/ghostypie).
