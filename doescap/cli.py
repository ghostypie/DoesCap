"""Command-line interface (CLI) for DoesCap."""

from __future__ import annotations

import argparse
import sys
from .client import DoesCap
from .config import RelayConfig
from .network import get_local_ip


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="doescap",
        description="DoesCap: Lightweight cross-platform hCaptcha relay and solver tool.",
    )
    parser.add_argument(
        "--sitekey",
        "-s",
        required=True,
        help="Target hCaptcha sitekey.",
    )
    parser.add_argument(
        "--rqdata",
        "-r",
        default=None,
        help="Optional rqdata payload string.",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Relay server bind address (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8787,
        help="Relay server port (default: 8787).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Disable automatic browser opening.",
    )
    parser.add_argument(
        "--browser",
        default=None,
        help="Path or keyword for browser to use in screencast mode.",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--title",
        default="DoesCap Relay",
        help="Web UI title header.",
    )
    parser.add_argument(
        "--custom-html",
        default=None,
        help="File path to custom HTML page template.",
    )
    parser.add_argument(
        "--assets-dir",
        default=None,
        help="Directory path containing custom static assets served at /assets/*.",
    )
    parser.add_argument(
        "--captcha-host",
        default=None,
        help="Optional hCaptcha origin hostname override (e.g., discord.com) for Enterprise challenges.",
    )

    args = parser.parse_args()

    config = RelayConfig(
        host=args.host,
        port=args.port,
        auto_open_browser=not args.no_browser,
        browser_path=args.browser,
        timeout=args.timeout,
        title=args.title,
        custom_html_path=args.custom_html,
        custom_assets_dir=args.assets_dir,
        captcha_host=args.captcha_host,
    )

    relay = DoesCap(config=config)
    local_ip = get_local_ip()

    print("==================================================")
    print("           DOESCAP RELAY SOLVER")
    print("==================================================")
    print(f"[*] Local access:   http://127.0.0.1:{config.port}/")
    print(f"[*] Network access: http://{local_ip}:{config.port}/")
    print(f"[*] Sitekey:        {args.sitekey}")
    if args.rqdata:
        print(f"[*] rqdata:         {args.rqdata[:30]}...")
    if args.custom_html:
        print(f"[*] Custom HTML:    {args.custom_html}")
    if args.assets_dir:
        print(f"[*] Assets Dir:     {args.assets_dir}")
    print(f"[*] Timeout:        {args.timeout}s")
    print("--------------------------------------------------")
    print("[*] Waiting for verification in browser...")

    try:
        result = relay.solve(sitekey=args.sitekey, rqdata=args.rqdata)
        if result and result.token:
            print("[+] Solved successfully!")
            print(f"[+] Elapsed: {result.elapsed_seconds:.2f}s")
            print(f"[+] Token:\n{result.token}")
            relay.mark_completed("Verification successful!")
            return 0
        else:
            print(f"[-] Solve failed: {result.error if result else 'Timed out'}", file=sys.stderr)
            return 1
    except KeyboardInterrupt:
        print("\n[!] Cancelled by user.")
        return 130
    finally:
        relay.close()


if __name__ == "__main__":
    sys.exit(main())
