#!/usr/bin/env python3
"""Regression coverage for guarded permanent redirects."""
import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / "skills/audit-orchestrator/scripts/collect_site.py"
HTML = b"<html><body><main><h1>Redirect target</h1></main></body></html>"


def collect(server, path="/", max_pages="1"):
    raw = subprocess.check_output([
        sys.executable, str(COLLECT),
        f"http://127.0.0.1:{server.server_port}{path}",
        "--max-pages", max_pages, "--max-seconds", "20",
    ], text=True)
    return json.loads(raw)


class Outside(BaseHTTPRequestHandler):
    hits = 0

    def do_GET(self):
        type(self).hits += 1
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def main():
    outside = ThreadingHTTPServer(("127.0.0.1", 0), Outside)
    threading.Thread(target=outside.serve_forever, daemon=True).start()

    class Site(BaseHTTPRequestHandler):
        hits = []

        def do_GET(self):
            type(self).hits.append(self.path)
            if self.path == "/robots.txt":
                self.send_response(200); self.send_header("Content-Type", "text/plain")
                self.end_headers(); self.wfile.write(b"User-agent: *\nAllow: /\n")
            elif self.path == "/":
                self.send_response(308); self.send_header("Location", "/target")
                self.end_headers()
            elif self.path == "/target":
                self.send_response(200); self.send_header("Content-Type", "text/html")
                self.end_headers(); self.wfile.write(HTML)
            elif self.path == "/cross":
                self.send_response(308); self.send_header("Location", f"http://127.0.0.1:{outside.server_port}/escaped")
                self.end_headers()
            elif self.path == "/blocked":
                self.send_response(308); self.send_header("Location", "/private")
                self.end_headers()
            elif self.path == "/private":
                self.send_response(200); self.send_header("Content-Type", "text/html")
                self.end_headers(); self.wfile.write(HTML)
            elif self.path == "/loop":
                self.send_response(308); self.send_header("Location", "/loop")
                self.end_headers()
            else:
                self.send_response(404); self.end_headers()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Site)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        result = collect(server)
        target = f"http://127.0.0.1:{server.server_port}/target"
        assert result["pages"] and result["pages"][0]["final_url"] == target
        assert result["pages"][0]["redirects"] == [{"from": f"http://127.0.0.1:{server.server_port}/", "to": target, "status": 308}]

        Outside.hits = 0
        result = collect(server, "/cross")
        assert Outside.hits == 0
        assert any(error.get("status") == 308 and "audited authority" in error["detail"] for error in result["errors"])

        # A redirect target blocked by robots must be rejected before fetch.
        Site.hits = []
        original = Site.do_GET
        def blocked_robots(self):
            if self.path == "/robots.txt":
                self.send_response(200); self.send_header("Content-Type", "text/plain")
                self.end_headers(); self.wfile.write(b"User-agent: *\nDisallow: /private\n")
                return
            original(self)
        Site.do_GET = blocked_robots
        result = collect(server, "/blocked")
        assert "/private" not in Site.hits
        assert any(error.get("status") == 308 and "robots policy" in error["detail"] for error in result["errors"])
        Site.do_GET = original

        result = collect(server, "/loop")
        assert any(error.get("status") == 308 for error in result["errors"])
        assert len([path for path in Site.hits if path == "/loop"]) <= 6
        print(json.dumps({"result": "PASS", "same_authority": True, "cross_authority_blocked": True,
                          "robots_target_blocked": True, "loop_bounded": True}, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        outside.shutdown()
        outside.server_close()


if __name__ == "__main__":
    main()
