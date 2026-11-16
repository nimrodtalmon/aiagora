"""AI-Agora web app: the replay viewer plus runs on demand.

    python web/server.py 5401      -> http://127.0.0.1:5401/

GET /                    the viewer
GET /api/run?n=&m=&k=&b=&p=&seed=   run all settings on one neighborhood (JSON)

Standard library only (plus the simulator's numpy/scipy). Links are relative,
so the app works under any path prefix (talmonlab serves it at /agora/).
"""
import json, os, sys
from collections import OrderedDict
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from agora.run import run                      # noqa: E402
from agora.replay import bundle                # noqa: E402
from agora.data.synthetic import neighborhood  # noqa: E402

SHOWN = ("silos", "central", "grassroots")
LIMITS = {"n": (6, 40, 30), "m": (3, 12, 12), "k": (2, 6, 3),
          "b": (1, 12, 6), "seed": (0, 99999, 0)}
CACHE = OrderedDict()


def params(q):
    out = {}
    for key, (lo, hi, default) in LIMITS.items():
        try:
            out[key] = min(hi, max(lo, int(q.get(key, [default])[0])))
        except ValueError:
            out[key] = default
    try:
        out["p"] = min(0.9, max(0.0, float(q.get("p", ["0"])[0])))
    except ValueError:
        out["p"] = 0.0
    out["b"] = min(out["b"], out["m"])
    return out


def compute(p):
    key = tuple(sorted(p.items()))
    if key in CACHE:
        CACHE.move_to_end(key)
        return CACHE[key]
    inst = neighborhood(p["n"], p["m"], p["k"], informed=p["p"], seed=p["seed"])
    results = {s: run(inst, s, budget=p["b"], seed=p["seed"]) for s in SHOWN}
    data = bundle(inst, results, {"budget": p["b"], "informed": p["p"],
                                  "seed": p["seed"]})
    body = json.dumps(data, separators=(",", ":")).encode()
    CACHE[key] = body
    if len(CACHE) > 200:
        CACHE.popitem(last=False)
    return body


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            html = open(os.path.join(ROOT, "web", "viewer.html"), "rb").read()
            return self.send(200, html, "text/html; charset=utf-8")
        if url.path == "/api/run":
            try:
                return self.send(200, compute(params(parse_qs(url.query))),
                                 "application/json")
            except Exception as e:                       # keep the app up
                return self.send(500, json.dumps({"error": str(e)}).encode(),
                                 "application/json")
        self.send(404, b"not found", "text/plain")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 5401))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
