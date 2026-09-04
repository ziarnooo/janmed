"""Lokalny podgląd dist/ - python3 serve.py  (domyślnie http://127.0.0.1:4399)"""

import functools
import http.server
import os
import socketserver

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
PORT = int(os.environ.get("PORT", "4399"))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


socketserver.TCPServer.allow_reuse_address = True

if __name__ == "__main__":
    handler = functools.partial(Handler, directory=DIST)
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        print("serving %s on http://127.0.0.1:%d" % (DIST, PORT), flush=True)
        httpd.serve_forever()
