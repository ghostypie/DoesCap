"""Example demonstrating asynchronous usage of DoesCap."""

import asyncio
import os
import sys

# Ensure repository root is on sys.path when running script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from doescap import async_solve_captcha


async def main():
    print("Starting async DoesCap solver...")

    # Example sitekey
    demo_sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"

    token = await async_solve_captcha(
        sitekey=demo_sitekey,
        port=8787,
        auto_open_browser=True,
        timeout=120,
    )

    if token:
        print(f"[+] Obtained token asynchronously: {token[:40]}...")
    else:
        print("[-] Async solve timed out or failed.")


if __name__ == "__main__":
    asyncio.run(main())
