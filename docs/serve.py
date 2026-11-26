"""Local HTTP development server to preview and browse the DoesCap docs."""

from __future__ import annotations

import http.server
import os
import socketserver
import sys
import webbrowser

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8088


class ReusableDocsServer(socketserver.TCPServer):
    """TCPServer allowing immediate port reuse after restart."""

    allow_reuse_address = True


class DocsHandler(http.server.SimpleHTTPRequestHandler):
    """Static handler with caching disabled so doc edits appear immediately."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    os.chdir(DOCS_DIR)
    with ReusableDocsServer(("127.0.0.1", PORT), DocsHandler) as httpd:
        url = f"http://127.0.0.1:{PORT}/index.html"
        print("==================================================")
        print("              DOESCAP DOCUMENTATION               ")
        print("==================================================")
        print(f"[*] Serving docs from: {DOCS_DIR}")
        print(f"[*] Local URL:         {url}")
        print("--------------------------------------------------")
        print("[*] Press Ctrl+C to stop.")

        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Stopped docs server.")


if __name__ == "__main__":
    main()
