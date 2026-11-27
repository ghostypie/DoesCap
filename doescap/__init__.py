"""
DoesCap: A lightweight, cross-platform hCaptcha relay and solver library.

Works natively on Windows, macOS, Linux, and Android (Termux).
Provides both Direct In-Browser solving (zero overhead, 60/120Hz native touch)
and Headless CDP Screencast mode.
"""

from __future__ import annotations

from .config import RelayConfig, SolveResult
from .client import DoesCap, HCaptchaRelay, solve_captcha, async_solve_captcha
from .network import get_local_ip

__version__ = "1.0.1"
__author__ = "GhoSty"
__all__ = [
    "DoesCap",
    "HCaptchaRelay",
    "RelayConfig",
    "SolveResult",
    "solve_captcha",
    "async_solve_captcha",
    "get_local_ip",
    "__version__",
]
