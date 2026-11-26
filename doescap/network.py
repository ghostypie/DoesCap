"""Network and system utility helpers for DoesCap."""

from __future__ import annotations

import os
import socket
import subprocess
from typing import Tuple


def get_local_ip() -> str:
    """Discover the primary local IPv4 address on the current network interface.

    Returns:
        A valid IPv4 string (e.g. '192.168.1.50') or '127.0.0.1' if disconnected.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    return "127.0.0.1"


def find_free_port(preferred_port: int, host: str = "0.0.0.0") -> int:
    """Verify if the preferred port is open, or locate an ephemeral available port.

    Args:
        preferred_port: Desired port number.
        host: Host to test binding on.

    Returns:
        An available integer port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, preferred_port))
            return s.getsockname()[1]
        except OSError:
            pass

    # Find ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def setup_windows_firewall_rule(port: int, rule_name: str = "DoesCap Relay") -> bool:
    """Optionally register a Windows Defender Firewall rule for the relay port.

    Args:
        port: TCP port to permit inbound traffic on.
        rule_name: Display name for the firewall rule.

    Returns:
        True if successfully added or existing, False otherwise.
    """
    if os.name != "nt":
        return False

    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name} {port}",
        "dir=in",
        "action=allow",
        "protocol=TCP",
        f"localport={port}",
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        return res.returncode == 0
    except Exception:
        return False
