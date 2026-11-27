"""Example demonstrating how to port and use a custom webpage design in DoesCap."""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from doescap import DoesCap, RelayConfig

CUSTOM_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>My Custom Product Verification</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      background: #0f172a;
      color: #f8fafc;
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 20px;
    }
    .custom-box {
      background: #1e293b;
      border: 2px solid #334155;
      border-radius: 16px;
      padding: 32px;
      max-width: 440px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
    }
    h1 { font-size: 20px; margin-bottom: 8px; color: #38bdf8; }
    p { font-size: 13px; color: #94a3b8; margin-bottom: 24px; }
    #widget-target { display: flex; justify-content: center; min-height: 78px; margin: 20px 0; }
    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 9999px;
      background: #334155;
      font-size: 11px;
      font-weight: 600;
      color: #cbd5e1;
    }
    .solved { background: #065f46; color: #34d399; }
  </style>
</head>
<body>
  <div class="custom-box">
    <h1>Custom Brand Gateway</h1>
    <p>Please complete human verification to access the service.</p>
    
    <div id="status" class="status-badge">Connecting...</div>

    <div id="widget-target"></div>
  </div>

  <script>
    const statusEl = document.getElementById('status');

    fetch('/status')
      .then(res => res.json())
      .then(info => {
        statusEl.textContent = 'Challenge Ready';
        
        window.__onReady = function() {
          const opts = {
            sitekey: info.sitekey,
            theme: 'dark',
            callback: function(token) {
              statusEl.textContent = 'Verified! Forwarding...';
              statusEl.className = 'status-badge solved';
              
              // Post verified token back to DoesCap relay server
              fetch('/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token })
              });
            }
          };
          if (info.rqdata) {
            opts.rqdata = info.rqdata;
          }
          const widgetId = hcaptcha.render('widget-target', opts);
          if (info.rqdata && window.hcaptcha && window.hcaptcha.setData) {
            try { window.hcaptcha.setData(widgetId, { rqdata: info.rqdata }); } catch (e) {}
          }
        };

        const s = document.createElement('script');
        s.src = 'https://js.hcaptcha.com/1/api.js?onload=__onReady&render=explicit';
        s.async = true;
        document.head.appendChild(s);
      });
  </script>
</body>
</html>
"""


def main():
    config = RelayConfig(
        host="0.0.0.0",
        port=8787,
        custom_html=CUSTOM_HTML_TEMPLATE,
    )

    print("Launching DoesCap with custom branded frontend design...")
    with DoesCap(config=config) as relay:
        print(f"Relay online: {relay.localhost_url}")
        token = relay.solve(
            sitekey="10000000-ffff-ffff-ffff-000000000001",
            timeout=120,
        )

        if token:
            print(f"[+] Successfully captured token using custom design: {token[:40]}...")
        else:
            print("[-] Cancelled or timed out.")


if __name__ == "__main__":
    main()
