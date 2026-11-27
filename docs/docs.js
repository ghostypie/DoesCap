// Module navigation tree, cross-page search index, and shared UI controls for DoesCap docs

const DOCS_MODULES = [
  {
    id: "getting-started",
    page: "index.html",
    groupTitle: "GETTING STARTED",
    items: [
      { label: "Overview", href: "index.html#overview" },
      { label: "Quick Start", href: "index.html#quick-start" },
      { label: "Installation", href: "index.html#installation" }
    ]
  },
  {
    id: "architecture",
    page: "architecture.html",
    groupTitle: "ARCHITECTURE & MODES",
    items: [
      { label: "Direct In-Browser Mode", href: "architecture.html#direct-mode" },
      { label: "Headless Screencast Mode", href: "architecture.html#cdp-mode" },
      { label: "Termux Mobile Setup", href: "architecture.html#termux" }
    ]
  },
  {
    id: "endpoints",
    page: "endpoints.html",
    groupTitle: "ENDPOINTS (REST API)",
    items: [
      { label: "GET /", href: "endpoints.html#endpoint-root" },
      { label: "GET /status", href: "endpoints.html#endpoint-status" },
      { label: "POST /solve", href: "endpoints.html#endpoint-solve" },
      { label: "GET /frame.jpg", href: "endpoints.html#endpoint-frame" },
      { label: "POST /input", href: "endpoints.html#endpoint-input" },
      { label: "GET /assets/*", href: "endpoints.html#endpoint-assets" }
    ]
  },
  {
    id: "api",
    page: "api.html",
    groupTitle: "PYTHON API REFERENCE",
    items: [
      { label: "DoesCap Class", href: "api.html#api-relay" },
      { label: "RelayConfig Options", href: "api.html#api-config" },
      { label: "SolveResult Subclass", href: "api.html#api-result" },
      { label: "Functional & Net Helpers", href: "api.html#api-functional" }
    ]
  },
  {
    id: "theming",
    page: "theming.html",
    groupTitle: "CUSTOM WEBPAGES & THEMES",
    items: [
      { label: "Custom HTML Templates", href: "theming.html#custom-html" },
      { label: "Asset Hosting (/assets/*)", href: "theming.html#custom-assets" }
    ]
  },
  {
    id: "cli",
    page: "cli.html",
    groupTitle: "CLI & DIAGNOSTICS",
    items: [
      { label: "CLI Tool Reference", href: "cli.html#cli-reference" },
      { label: "Automated Testing", href: "cli.html#testing" },
      { label: "Production Notes", href: "cli.html#notes" }
    ]
  }
];

const SEARCH_INDEX = [
  { module: "Getting Started", title: "Overview & Base URL", keywords: "doescap overview base url python windows macos linux termux ghosty", href: "index.html#overview" },
  { module: "Getting Started", title: "Quick Start (Sync & Async)", keywords: "quick start solve_captcha async_solve_captcha asyncio token", href: "index.html#quick-start" },
  { module: "Getting Started", title: "Installation & Extras", keywords: "pip install doescap websocket-client screencast", href: "index.html#installation" },
  { module: "Architecture", title: "Direct In-Browser Mode", keywords: "direct mode browser_path zero overhead 60hz 120hz", href: "architecture.html#direct-mode" },
  { module: "Architecture", title: "Headless CDP Screencast Mode", keywords: "headless cdp screencast chromium find_browser chrome brave edge", href: "architecture.html#cdp-mode" },
  { module: "Architecture", title: "Android & Termux Setup", keywords: "android termux am start termux-open-url pkg install", href: "architecture.html#termux" },
  { module: "REST API", title: "GET / (Serve Relay Frontend)", keywords: "get root html frontend cors options", href: "endpoints.html#endpoint-root" },
  { module: "REST API", title: "GET /status", keywords: "get status sitekey rqdata mode solved claimed task_name promo_code rect", href: "endpoints.html#endpoint-status" },
  { module: "REST API", title: "POST /solve", keywords: "post solve submit token h-captcha-response", href: "endpoints.html#endpoint-solve" },
  { module: "REST API", title: "GET /frame.jpg", keywords: "get frame jpg jpeg screencast mirror", href: "endpoints.html#endpoint-frame" },
  { module: "REST API", title: "POST /input", keywords: "post input mouse touch coordinates press move release", href: "endpoints.html#endpoint-input" },
  { module: "REST API", title: "GET /assets/*", keywords: "get assets static css js png svg ttf woff2 mime commonpath", href: "endpoints.html#endpoint-assets" },
  { module: "Python API", title: "DoesCap Class (HCaptchaRelay)", keywords: "doescap hcaptcharelay solve async_solve solve_relay mark_claimed mark_failed mark_completed close cleanup relay_url localhost_url", href: "api.html#api-relay" },
  { module: "Python API", title: "RelayConfig Options", keywords: "relayconfig host port auto_open_browser browser_path timeout title theme allow_firewall_rule custom_html custom_html_path custom_assets_dir", href: "api.html#api-config" },
  { module: "Python API", title: "SolveResult String Subclass", keywords: "solveresult str token success elapsed_seconds metadata", href: "api.html#api-result" },
  { module: "Python API", title: "Functional & Network Helpers", keywords: "solve_captcha async_solve_captcha get_local_ip __version__", href: "api.html#api-functional" },
  { module: "Custom Theming", title: "Custom HTML Templates & SSR Placeholders", keywords: "custom_html custom_html_path ssr placeholders title theme sitekey rqdata", href: "theming.html#custom-html" },
  { module: "Custom Theming", title: "Static Asset Hosting (/assets/*)", keywords: "custom_assets_dir static assets css logo commonpath", href: "theming.html#custom-assets" },
  { module: "CLI & Testing", title: "CLI Tool Reference", keywords: "doescap cli sitekey rqdata host port no-browser browser timeout title custom-html assets-dir", href: "cli.html#cli-reference" },
  { module: "CLI & Testing", title: "Automated & Sandbox Testing (pytest)", keywords: "pytest tests test_doescap sitekey automated testing", href: "cli.html#testing" },
  { module: "CLI & Testing", title: "Production Notes & Firewall", keywords: "notes firewall netsh deferred cleanup 25s 10s", href: "cli.html#notes" }
];

// Apply saved theme immediately to avoid flash of wrong theme
(function applyInitialTheme() {
  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const target = (saved === "dark" || (!saved && prefersDark)) ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", target);
})();

function setDrawerState(open) {
  const sb = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  if (sb) sb.classList.toggle("open", open);
  if (backdrop) backdrop.classList.toggle("visible", open);
  document.body.classList.toggle("drawer-open", open);
}

function toggleSidebar() {
  const sb = document.getElementById("sidebar");
  setDrawerState(!(sb && sb.classList.contains("open")));
}

function enhanceMobileHeader() {
  const mobileBar = document.querySelector(".mobile-bar");
  if (!mobileBar) return;
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  mobileBar.innerHTML = `
    <a href="index.html" style="font-family: var(--font-head); font-size: 16px; color: var(--ink); text-decoration: none;">DOESCAP DOCS</a>
    <div class="mobile-bar-actions">
      <button id="mobile-theme-btn" class="mobile-theme-btn" aria-label="Toggle light or dark theme" onclick="toggleTheme()">${isDark ? "☀" : "☾"}</button>
      <button class="mobile-menu-btn" aria-label="Toggle navigation menu" onclick="toggleSidebar()">MENU ☰</button>
    </div>
  `;

  if (!document.getElementById("sidebar-backdrop")) {
    const bd = document.createElement("div");
    bd.id = "sidebar-backdrop";
    bd.className = "sidebar-backdrop";
    bd.addEventListener("click", () => setDrawerState(false));
    document.body.appendChild(bd);
  }
}

function renderSidebar(currentPage) {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;

  const isDark = document.documentElement.getAttribute("data-theme") === "dark";

  const navGroupsHtml = DOCS_MODULES.map(group => {
    const isCurrentGroup = group.page === currentPage;
    const linksHtml = group.items.map((item, idx) => {
      const isFirstOnPage = isCurrentGroup && idx === 0 && !window.location.hash;
      const hashTarget = item.href.split("#")[1];
      const matchesHash = isCurrentGroup && window.location.hash === "#" + hashTarget;
      const activeClass = (matchesHash || isFirstOnPage) ? "active" : "";
      return `<li class="nav-item"><a href="${item.href}" class="${activeClass}" data-page="${group.page}" data-hash="${hashTarget}">${item.label}</a></li>`;
    }).join("");

    return `
      <div class="nav-group">
        <a class="nav-title" href="${group.page}">${group.groupTitle}</a>
        <ul class="nav-items">${linksHtml}</ul>
      </div>
    `;
  }).join("");

  sidebar.innerHTML = `
    <div class="brand-section">
      <div class="brand-top-row">
        <a class="brand-link" href="index.html">
          DOESCAP
          <span class="brand-pill">v1.0.1</span>
        </a>
        <button class="drawer-close-btn" aria-label="Close navigation menu" onclick="setDrawerState(false)">✕</button>
      </div>
      <div class="brand-subtitle">Universal Solver &amp; Relay Suite for Python</div>
    </div>

    <div class="search-box">
      <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input
        id="search-input"
        class="search-input"
        type="text"
        aria-label="Search documentation"
        placeholder="Search all docs (Ctrl+K)..."
        autocomplete="off"
        oninput="handleSearch(this.value)"
      >
    </div>

    <div id="search-results" class="search-results" aria-live="polite"></div>

    <nav id="nav-wrapper" class="nav-wrapper" aria-label="Documentation modules">
      ${navGroupsHtml}
    </nav>

    <div class="sidebar-footer">
      <button id="theme-button" class="theme-button" aria-label="Toggle light or dark theme" onclick="toggleTheme()">
        <span id="theme-icon" aria-hidden="true">${isDark ? "☀" : "☾"}</span>
        <span id="theme-label">${isDark ? "SWITCH TO LIGHT" : "SWITCH TO DARK"}</span>
      </button>
    </div>
  `;

  sidebar.querySelectorAll(".nav-item a, .nav-title").forEach(link => {
    link.addEventListener("click", () => setDrawerState(false));
  });
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const target = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", target);
  localStorage.setItem("theme", target);

  const label = document.getElementById("theme-label");
  const icon = document.getElementById("theme-icon");
  const mobBtn = document.getElementById("mobile-theme-btn");
  if (label && icon) {
    label.textContent = target === "dark" ? "SWITCH TO LIGHT" : "SWITCH TO DARK";
    icon.textContent = target === "dark" ? "☀" : "☾";
  }
  if (mobBtn) {
    mobBtn.textContent = target === "dark" ? "☀" : "☾";
  }
}

function copySnippet(btn) {
  const pre = btn.closest(".code-box");
  const code = pre ? pre.querySelector("code") : null;
  if (!code) return;
  const text = code.innerText;

  function markCopied() {
    const orig = btn.textContent;
    btn.textContent = "COPIED!";
    setTimeout(() => { btn.textContent = orig; }, 1800);
  }

  function execFallback() {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try {
      if (document.execCommand("copy")) markCopied();
    } catch (e) {}
    document.body.removeChild(ta);
  }

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(markCopied).catch(execFallback);
  } else {
    execFallback();
  }
}

function handleSearch(query) {
  const q = query.trim().toLowerCase();
  const resultsBox = document.getElementById("search-results");
  const navWrapper = document.getElementById("nav-wrapper");
  if (!resultsBox || !navWrapper) return;

  if (!q) {
    resultsBox.classList.remove("visible");
    resultsBox.innerHTML = "";
    navWrapper.style.display = "";
    return;
  }

  const matches = SEARCH_INDEX.filter(entry =>
    entry.title.toLowerCase().includes(q) ||
    entry.module.toLowerCase().includes(q) ||
    entry.keywords.toLowerCase().includes(q)
  );

  navWrapper.style.display = "none";
  resultsBox.classList.add("visible");

  if (!matches.length) {
    resultsBox.innerHTML = `<div class="search-empty">No matches for "${q.replace(/</g, "&lt;")}"</div>`;
    return;
  }

  resultsBox.innerHTML = matches.map(m => `
    <a class="search-result-item" href="${m.href}" onclick="setDrawerState(false)">
      <span class="search-result-module">${m.module}</span>
      <div class="search-result-title">${m.title}</div>
    </a>
  `).join("");
}

function initDocs(currentPage) {
  enhanceMobileHeader();
  renderSidebar(currentPage);

  window.addEventListener("keydown", e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      const inp = document.getElementById("search-input");
      if (inp) {
        inp.focus();
        inp.select();
      }
    }
    if (e.key === "Escape") {
      setDrawerState(false);
    }
  });

  window.addEventListener("scroll", () => {
    const targets = document.querySelectorAll("section[id], div[id^='endpoint-'], div[id^='api-']");
    let currentId = "";
    const scrollPos = window.scrollY + 140;

    targets.forEach(el => {
      const rect = el.getBoundingClientRect();
      const top = rect.top + window.scrollY;
      if (scrollPos >= top && scrollPos < top + el.offsetHeight) {
        currentId = el.id;
      }
    });

    if (currentId) {
      document.querySelectorAll(`.nav-item a[data-page="${currentPage}"]`).forEach(link => {
        link.classList.toggle("active", link.getAttribute("data-hash") === currentId);
      });
    }
  });
}
