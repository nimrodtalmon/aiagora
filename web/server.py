"""AI-Agora web app: static pages only (no simulation on the server).

    python web/server.py 5401      -> http://127.0.0.1:5401/

GET /        the explainer deck (web/deck, built by web/deck/src/build.py)
GET /play    the playground: alone vs together (web/play.html, runs in the browser)
GET /app     neighborhood prototype: group chat vs agora with conditional commitments (web/app.html)
GET /brief/       research brief: the current results (web/brief/src/build.py)
GET /scale/       research brief: the scale paradox (web/scale/src/build.py)
GET /directions/  research brief: directions, evidence, app concept (web/directions/src/build.py)

Standard library only. Links are relative, so the app works under any path
prefix (talmonlab serves it at /agora/).
"""
import os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

WEB = os.path.dirname(os.path.abspath(__file__))
FILES = {
    "/": ("deck/index.html", "text/html"),
    "/index.html": ("deck/index.html", "text/html"),
    "/assets/deck.css": ("deck/assets/deck.css", "text/css"),
    "/assets/deck.js": ("deck/assets/deck.js", "application/javascript"),
    "/play": ("play.html", "text/html"),
    "/play/": ("play.html", "text/html"),
    "/brief/": ("brief/index.html", "text/html"),
    "/scale/": ("scale/index.html", "text/html"),
    "/directions/": ("directions/index.html", "text/html"),
    "/app": ("app.html", "text/html"),
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/app/":
            self.send_response(301); self.send_header("Location", "../app"); self.end_headers(); return
        if path in ("/brief", "/directions", "/scale"):       # relative links need the slash
            self.send_response(301); self.send_header("Location", path.lstrip("/") + "/"); self.end_headers(); return
        if path in ("/groups", "/groups/"):          # old address of the Problem 1 brief
            self.send_response(301); self.send_header("Location", ("../" if path.endswith("/") else "") + "brief/"); self.end_headers(); return
        f = FILES.get(path)
        if not f:
            self.send_response(404); self.end_headers(); self.wfile.write(b"not found"); return
        body = open(os.path.join(WEB, f[0]), "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", f[1] + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 5401))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
