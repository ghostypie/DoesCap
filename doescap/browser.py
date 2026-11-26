"""Cross-platform browser launcher and binary detector."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import webbrowser
from typing import Optional, Tuple


def is_android_termux() -> bool:
    """Check if execution environment is running inside Android or Termux."""
    return (
        "ANDROID_ROOT" in os.environ
        or "TERMUX_VERSION" in os.environ
        or "com.termux" in os.environ.get("PREFIX", "")
    )


def open_browser(url: str) -> bool:
    """Open the given URL in the default browser across all operating systems.

    Supports Android/Termux via termux tools and Android Activity Manager (am),
    Linux via xdg-open, and standard systems via Python's webbrowser module.

    Args:
        url: Full HTTP/HTTPS URL string to open.

    Returns:
        True if an opener command was initiated successfully, False otherwise.
    """
    candidates = [
        # Termux URL openers
        ["termux-open-url", url],
        ["termux-open", url],
        # Android Chrome intent
        ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"],
        ["am", "start", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"],
        # Android generic VIEW intent
        ["am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url],
        ["am", "start", "-a", "android.intent.action.VIEW", "-d", url],
        # Explicit system path for am on rooted or restricted devices
        ["/system/bin/am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"],
        ["/system/bin/am", "start", "-a", "android.intent.action.VIEW", "-d", url, "-n", "com.android.chrome/com.google.android.apps.chrome.Main"],
        ["/system/bin/am", "start", "--user", "0", "-a", "android.intent.action.VIEW", "-d", url],
        ["/system/bin/am", "start", "-a", "android.intent.action.VIEW", "-d", url],
        # Linux desktop
        ["xdg-open", url],
    ]

    for cmd in candidates:
        try:
            exe = shutil.which(cmd[0]) or (cmd[0] if os.path.exists(cmd[0]) else None)
            if exe:
                subprocess.Popen(
                    [exe] + cmd[1:],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
        except Exception:
            continue

    # Fallback to standard Python webbrowser
    try:
        webbrowser.open(url, new=2)
        return True
    except Exception:
        return False


def find_browser(override_path: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Locate an installed Chromium-compatible browser executable.

    Args:
        override_path: Optional explicit file path or keyword binary name.

    Returns:
        Tuple of (executable_path, friendly_name), or (None, None) if not found.
    """
    if override_path:
        clean = override_path.strip().strip('"').strip("'")
        if os.path.isfile(clean):
            return clean, "Custom Browser"

        kw = clean.lower()
        which_path = shutil.which(kw)
        if which_path and "WindowsApps" not in which_path and os.path.isfile(which_path):
            return which_path, f"{kw.capitalize()} (PATH)"

    # Termux does not host full desktop Chromium with CDP by default
    if is_android_termux():
        return None, None

    if os.name == "nt":
        prog = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        prog86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
        local = os.environ.get("LOCALAPPDATA", "")

        chrome_candidates = [
            os.path.join(prog, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(prog86, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local, "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(local, "Google", "Chrome SxS", "Application", "chrome.exe"),
        ]
        for p in chrome_candidates:
            if os.path.isfile(p):
                return p, "Google Chrome"

        brave_candidates = [
            os.path.join(prog, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            os.path.join(local, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            os.path.join(prog86, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
        ]
        for p in brave_candidates:
            if os.path.isfile(p):
                return p, "Brave Browser"

        chromium_candidates = [
            os.path.join(local, "Chromium", "Application", "chrome.exe"),
            os.path.join(prog, "Chromium", "Application", "chrome.exe"),
            os.path.join(prog86, "Chromium", "Application", "chrome.exe"),
        ]
        for p in chromium_candidates:
            if os.path.isfile(p):
                return p, "Chromium"

        edge_candidates = [
            os.path.join(prog86, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(prog, "Microsoft", "Edge", "Application", "msedge.exe"),
            os.path.join(local, "Microsoft", "Edge", "Application", "msedge.exe"),
        ]
        for p in edge_candidates:
            if os.path.isfile(p):
                return p, "Microsoft Edge"

        opera_candidates = [
            os.path.join(local, "Programs", "Opera", "opera.exe"),
            os.path.join(local, "Programs", "Opera GX", "opera.exe"),
            os.path.join(prog, "Opera", "launcher.exe"),
            os.path.join(prog86, "Opera", "launcher.exe"),
        ]
        for p in opera_candidates:
            if os.path.isfile(p):
                return p, "Opera"

        vivaldi_candidates = [
            os.path.join(local, "Vivaldi", "Application", "vivaldi.exe"),
            os.path.join(prog, "Vivaldi", "Application", "vivaldi.exe"),
            os.path.join(prog86, "Vivaldi", "Application", "vivaldi.exe"),
        ]
        for p in vivaldi_candidates:
            if os.path.isfile(p):
                return p, "Vivaldi"

    if sys.platform == "darwin":
        mac_paths = [
            ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "Google Chrome"),
            ("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", "Brave Browser"),
            ("/Applications/Chromium.app/Contents/MacOS/Chromium", "Chromium"),
            ("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "Microsoft Edge"),
            ("/Applications/Opera.app/Contents/MacOS/Opera", "Opera"),
            ("/Applications/Vivaldi.app/Contents/MacOS/Vivaldi", "Vivaldi"),
        ]
        for p, name in mac_paths:
            if os.path.isfile(p):
                return p, name

    linux_names = [
        ("google-chrome-stable", "Google Chrome"),
        ("google-chrome", "Google Chrome"),
        ("brave-browser", "Brave Browser"),
        ("brave", "Brave Browser"),
        ("chromium", "Chromium"),
        ("chromium-browser", "Chromium"),
        ("msedge", "Microsoft Edge"),
        ("opera", "Opera"),
        ("vivaldi", "Vivaldi"),
    ]
    for binary_name, friendly_name in linux_names:
        p = shutil.which(binary_name)
        if p and "WindowsApps" not in p and os.path.isfile(p):
            return p, friendly_name

    return None, None
