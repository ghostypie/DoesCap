"""Modern, self-contained HTML/CSS/JS frontend for DoesCap."""

from __future__ import annotations


def render_html_page(title: str = "DoesCap Relay", theme: str = "dark") -> str:
    """Generate the full responsive HTML template for client interactions."""
    bg_color = "#0a0a0c" if theme == "dark" else "#f8f9fa"
    card_bg = "#121316" if theme == "dark" else "#ffffff"
    card_border = "#26282e" if theme == "dark" else "#e2e8f0"
    text_color = "#f3f4f6" if theme == "dark" else "#0f172a"
    subtext_color = "#9ca3af" if theme == "dark" else "#64748b"
    accent_color = "#3b82f6" if theme == "dark" else "#2563eb"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
  <meta name="theme-color" content="{bg_color}">
  <style>
    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    :root {{
      --bg-color: {bg_color};
      --card-bg: {card_bg};
      --card-border: {card_border};
      --text-color: {text_color};
      --subtext-color: {subtext_color};
      --accent: {accent_color};
      --success: #10b981;
    }}
    html, body {{
      width: 100%;
      min-height: 100vh;
      background-color: var(--bg-color);
      color: var(--text-color);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 16px;
      width: 100%;
    }}
    .card {{
      width: 100%;
      max-width: 490px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      position: relative;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--card-border);
    }}
    .title-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .icon {{
      width: 20px;
      height: 20px;
      fill: none;
      stroke: var(--accent);
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .title-text {{
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }}
    .task-label {{
      font-size: 11px;
      font-weight: 500;
      color: var(--subtext-color);
      margin-top: 2px;
    }}
    .badge {{
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(156, 163, 175, 0.1);
      color: var(--subtext-color);
      border: 1px solid var(--card-border);
    }}
    .badge.active {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border-color: rgba(59, 130, 246, 0.3);
    }}
    .badge.solved {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.3);
    }}
    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
    }}
    .badge.active .pulse-dot {{
      animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}
    .stage-wrapper {{
      width: 100%;
      min-height: 200px;
      background: rgba(0, 0, 0, 0.2);
      border: 1px dashed var(--card-border);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
      margin-bottom: 18px;
    }}
    #f {{
      display: none;
      max-width: 100%;
      height: auto;
      cursor: crosshair;
      user-select: none;
      -webkit-user-drag: none;
      touch-action: none;
    }}
    #direct-container {{
      display: none;
      z-index: 10;
      margin: 16px auto;
      min-height: 80px;
      align-items: center;
      justify-content: center;
    }}
    .loader-box {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      color: var(--subtext-color);
      font-size: 13px;
    }}
    .spinner {{
      width: 32px;
      height: 32px;
      border: 3px solid rgba(156, 163, 175, 0.2);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }}
    @keyframes spin {{
      to {{ transform: rotate(360deg); }}
    }}
    .tap-effect {{
      position: absolute;
      width: 24px;
      height: 24px;
      border: 2px solid var(--accent);
      border-radius: 50%;
      transform: translate(-50%, -50%) scale(0.5);
      pointer-events: none;
      z-index: 100;
      animation: ripple 0.35s ease-out forwards;
    }}
    @keyframes ripple {{
      to {{
        transform: translate(-50%, -50%) scale(1.6);
        opacity: 0;
      }}
    }}
    .footer-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(0, 0, 0, 0.15);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 12px;
      color: var(--subtext-color);
    }}
    .btn {{
      background: var(--card-bg);
      color: var(--text-color);
      border: 1px solid var(--card-border);
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .btn:hover {{
      border-color: var(--subtext-color);
    }}
    .btn-primary {{
      background: var(--text-color);
      color: var(--bg-color);
      border-color: var(--text-color);
    }}
    .btn-primary:hover {{
      opacity: 0.9;
    }}
    .hint {{
      margin-top: 14px;
      font-size: 12px;
      color: var(--subtext-color);
      text-align: center;
      line-height: 1.5;
    }}
    #success-screen {{
      display: none;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 16px 8px;
      animation: fadeIn 0.3s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .success-icon-box {{
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: rgba(16, 185, 129, 0.15);
      border: 2px solid var(--success);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
    }}
    .success-icon-box svg {{
      width: 28px;
      height: 28px;
      stroke: var(--success);
      stroke-width: 2.5;
      fill: none;
    }}
    .success-title {{
      font-size: 18px;
      font-weight: 700;
      color: var(--text-color);
      margin-bottom: 6px;
    }}
    .success-task-name {{
      font-size: 13px;
      color: var(--subtext-color);
      margin-bottom: 14px;
      font-weight: 500;
    }}
    .code-card {{
      width: 100%;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 16px;
      text-align: center;
    }}
    .code-title {{
      font-size: 11px;
      color: var(--subtext-color);
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }}
    .code-text {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: 1.5px;
      color: var(--text-color);
      user-select: all;
      cursor: pointer;
      margin-bottom: 10px;
      word-break: break-all;
    }}
    .success-desc {{
      font-size: 12px;
      color: var(--subtext-color);
      line-height: 1.6;
    }}
    @media (max-width: 480px) {{
      .card {{
        padding: 18px 14px;
      }}
      .btn {{
        min-height: 40px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="header">
        <div class="title-group">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <div>
            <div class="title-text">{title}</div>
            <div id="task-label-text" class="task-label" style="display:none;"></div>
          </div>
        </div>
        <div id="status-badge" class="badge">
          <span class="pulse-dot"></span>
          <span id="status-text">INITIALIZING</span>
        </div>
      </div>

      <div id="main-panel">
        <div id="stage" class="stage-wrapper">
          <div id="loader" class="loader-box">
            <div class="spinner"></div>
            <span>Waiting for captcha widget...</span>
          </div>
          <img id="f" alt="Screencast Stream">
          <div id="direct-container"></div>
        </div>

        <div class="footer-bar">
          <div>Relay: <strong id="endpoint-label">...</strong></div>
          <button id="copy-btn" class="btn" onclick="copyCurrentUrl()">Copy Link</button>
        </div>

        <div class="hint">
          Solve the puzzle challenge in this window.<br>
          Verification completes automatically.
        </div>
      </div>

      <div id="success-screen">
        <div class="success-icon-box">
          <svg viewBox="0 0 24 24">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
        <h2 id="success-heading" class="success-title">Verification Complete</h2>
        <div id="claimed-task-name" class="success-task-name" style="display:none;"></div>

        <div id="promo-code-card" class="code-card" style="display:none;">
          <div class="code-title">Redeemable Code</div>
          <div id="promo-code-value" class="code-text" onclick="copyCode()" title="Click to copy code"></div>
          <button id="copy-code-btn" class="btn btn-primary" onclick="copyCode()">Copy Code</button>
        </div>

        <p id="success-subtext" class="success-desc">
          Captcha token has been verified and returned to the application.<br>
          You may safely close this tab.
        </p>
      </div>
    </div>
  </div>

  <script>
    const statusBadge = document.getElementById('status-badge');
    const statusText = document.getElementById('status-text');
    const endpointLabel = document.getElementById('endpoint-label');
    const loader = document.getElementById('loader');
    const imgFrame = document.getElementById('f');
    const directContainer = document.getElementById('direct-container');
    const mainPanel = document.getElementById('main-panel');
    const successScreen = document.getElementById('success-screen');
    const taskLabelEl = document.getElementById('task-label-text');
    const claimedTaskEl = document.getElementById('claimed-task-name');
    const promoCard = document.getElementById('promo-code-card');
    const promoValue = document.getElementById('promo-code-value');

    endpointLabel.textContent = window.location.host;

    let directInitialized = false;
    let lastBlobUrl = null;

    function pullFrame() {{
      fetch('/frame.jpg?' + Date.now())
        .then(res => {{
          if (res.status !== 200) throw 0;
          return res.blob();
        }})
        .then(blob => {{
          const url = URL.createObjectURL(blob);
          imgFrame.src = url;
          if (imgFrame.style.display !== 'block') {{
            imgFrame.style.display = 'block';
            loader.style.display = 'none';
          }}
          if (lastBlobUrl) URL.revokeObjectURL(lastBlobUrl);
          lastBlobUrl = url;
        }})
        .catch(() => {{}});
    }}

    function calculateCoords(e) {{
      const rect = imgFrame.getBoundingClientRect();
      const scaleX = imgFrame.naturalWidth ? (imgFrame.naturalWidth / rect.width) : 1;
      const scaleY = imgFrame.naturalHeight ? (imgFrame.naturalHeight / rect.height) : 1;
      return {{
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
      }};
    }}

    function showTapMarker(clientX, clientY) {{
      const stage = document.getElementById('stage');
      const r = stage.getBoundingClientRect();
      const dot = document.createElement('div');
      dot.className = 'tap-effect';
      dot.style.left = (clientX - r.left) + 'px';
      dot.style.top = (clientY - r.top) + 'px';
      stage.appendChild(dot);
      setTimeout(() => dot.remove(), 400);
    }}

    function sendInputEvent(kind, x, y) {{
      fetch('/input', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ t: kind, x: x, y: y }})
      }}).catch(() => {{}});
    }}

    let lastMoveTime = 0;
    imgFrame.addEventListener('mousemove', e => {{
      const now = Date.now();
      if (now - lastMoveTime < 35) return;
      lastMoveTime = now;
      const p = calculateCoords(e);
      sendInputEvent('move', p.x, p.y);
    }});

    imgFrame.addEventListener('mousedown', e => {{
      e.preventDefault();
      showTapMarker(e.clientX, e.clientY);
      const p = calculateCoords(e);
      sendInputEvent('press', p.x, p.y);
    }});

    window.addEventListener('mouseup', e => {{
      const p = calculateCoords(e);
      sendInputEvent('release', p.x, p.y);
    }});

    imgFrame.addEventListener('touchstart', e => {{
      e.preventDefault();
      if (!e.touches.length) return;
      const t = e.touches[0];
      showTapMarker(t.clientX, t.clientY);
      const p = calculateCoords(t);
      sendInputEvent('press', p.x, p.y);
    }}, {{ passive: false }});

    imgFrame.addEventListener('touchmove', e => {{
      e.preventDefault();
      if (!e.touches.length) return;
      const p = calculateCoords(e.touches[0]);
      sendInputEvent('move', p.x, p.y);
    }}, {{ passive: false }});

    imgFrame.addEventListener('touchend', e => {{
      e.preventDefault();
      if (!e.changedTouches.length) return;
      const p = calculateCoords(e.changedTouches[0]);
      sendInputEvent('release', p.x, p.y);
    }}, {{ passive: false }});

    function initDirectSolver(sitekey, rqdata) {{
      if (directInitialized) return;
      directInitialized = true;

      loader.style.display = 'none';
      imgFrame.style.display = 'none';
      directContainer.style.display = 'flex';

      window.__onHCaptchaReady = function() {{
        if (!window.hcaptcha || !window.hcaptcha.render) {{
          setTimeout(window.__onHCaptchaReady, 100);
          return;
        }}
        try {{
          const options = {{
            sitekey: sitekey,
            theme: '{theme}',
            callback: function(token) {{
              statusText.textContent = 'VERIFIED';
              statusBadge.className = 'badge solved';
              fetch('/solve', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ token: token }})
              }}).catch(() => {{}});
            }},
            'expired-callback': function() {{
              statusText.textContent = 'EXPIRED';
              statusBadge.className = 'badge';
            }},
            'error-callback': function(err) {{
              console.error('hCaptcha error:', err);
            }}
          }};
          if (rqdata) options.rqdata = rqdata;

          const widgetId = hcaptcha.render('direct-container', options);
          if (rqdata && window.hcaptcha.setData) {{
            try {{ window.hcaptcha.setData(widgetId, {{ rqdata: rqdata }}); }} catch(e) {{}}
          }}
          statusText.textContent = 'READY TO SOLVE';
          statusBadge.className = 'badge active';
        }} catch(e) {{
          console.error('Failed to render hCaptcha:', e);
        }}
      }};

      if (window.hcaptcha && window.hcaptcha.render) {{
        window.__onHCaptchaReady();
      }} else {{
        const script = document.createElement('script');
        script.src = 'https://js.hcaptcha.com/1/api.js?onload=__onHCaptchaReady&render=explicit';
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
      }}
    }}

    let screencastInterval = null;
    let isSolved = false;

    function pollStatus() {{
      fetch('/status')
        .then(r => r.json())
        .then(st => {{
          if (st.task_name && taskLabelEl) {{
            taskLabelEl.textContent = st.task_name;
            taskLabelEl.style.display = 'block';
          }}

          if (st.mode === 'direct' && st.sitekey) {{
            initDirectSolver(st.sitekey, st.rqdata);
          }} else if (st.mode === 'screencast' && !screencastInterval) {{
            screencastInterval = setInterval(pullFrame, 200);
            pullFrame();
          }}

          if (st.solved || st.claimed) {{
            if (!isSolved) {{
              isSolved = true;
              statusText.textContent = st.claimed ? 'CLAIMED' : 'VERIFIED';
              statusBadge.className = 'badge solved';
              mainPanel.style.display = 'none';
              successScreen.style.display = 'flex';
            }}

            if (st.claimed) {{
              statusText.textContent = 'CLAIMED';
            }}
            if (st.task_name) {{
              claimedTaskEl.textContent = st.task_name;
              claimedTaskEl.style.display = 'block';
            }}
            if (st.promo_code) {{
              promoValue.textContent = st.promo_code;
              promoCard.style.display = 'block';
            }}
            if (st.success_message) {{
              document.getElementById('success-subtext').textContent = st.success_message;
            }}
          }} else if (st.mode === 'direct' || st.rect) {{
            statusText.textContent = 'ACTIVE';
            statusBadge.className = 'badge active';
          }}
        }})
        .catch(() => {{}});
    }}

    setInterval(pollStatus, 300);
    pollStatus();

    function copyCurrentUrl() {{
      const btn = document.getElementById('copy-btn');
      const url = window.location.href;
      copyHelper(url, btn, 'Copied!', 'Copy Link');
    }}

    function copyCode() {{
      const btn = document.getElementById('copy-code-btn');
      const text = (promoValue ? promoValue.textContent : '').trim();
      copyHelper(text, btn, 'Copied!', 'Copy Code');
    }}

    function copyHelper(text, btnElement, successText, originalText) {{
      if (!text) return;
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(text).then(showCopied).catch(fallbackCopy);
      }} else {{
        fallbackCopy();
      }}

      function showCopied() {{
        if (btnElement) {{
          btnElement.textContent = successText;
          setTimeout(() => {{ btnElement.textContent = originalText; }}, 2000);
        }}
      }}

      function fallbackCopy() {{
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        try {{
          document.execCommand('copy');
          showCopied();
        }} catch(e) {{
          window.prompt('Copy to clipboard:', text);
        }}
        document.body.removeChild(ta);
      }}
    }}
  </script>
</body>
</html>
"""
