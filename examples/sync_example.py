"""Example demonstrating synchronous usage of DoesCap."""

import os
import sys

# Ensure repository root is on sys.path when running script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from doescap import DoesCap, RelayConfig


def main():
    config = RelayConfig(
        host="0.0.0.0",
        port=8787,
        auto_open_browser=True,
        timeout=180,
        title="DoesCap Verification Portal",
        theme="dark",
    )

    with DoesCap(config=config) as relay:
        print("========================================")
        print("          DoesCap Relay Example         ")
        print("========================================")
        print(f"Local:   {relay.localhost_url}")
        print(f"Network: {relay.relay_url}")
        print("----------------------------------------")

        # Example sitekey
        demo_sitekey = "4c672d35-0701-42b2-88c3-78380b0db560"

        print("Awaiting captcha solution in browser...")
        result = relay.solve(sitekey=demo_sitekey)

        if result and result.token:
            print(f"[+] Verified successfully in {result.elapsed_seconds:.2f}s!")
            print(f"[+] Token: {result.token[:40]}... (length: {len(result.token)})")
            relay.mark_completed("Verification passed! You may return to the console.")
        else:
            print(f"[-] Verification failed: {result.error if result else 'Timed out'}")


if __name__ == "__main__":
    main()
