#!/usr/bin/env python3
import json, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COLLECT=ROOT/"skills/audit-orchestrator/scripts/collect_site.py"
HTML=b"<!doctype html><html><head><title>Test</title></head><body><main><h1>Test site</h1><p>Readable public content for a deterministic robots scenario.</p></main></body></html>"

def run(status=200, body=b"User-agent: *\nAllow: /\n", redirect=False):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path=="/robots.txt" and redirect:
                self.send_response(302); self.send_header("Location","/policy.txt"); self.end_headers(); return
            if self.path in {"/robots.txt","/policy.txt"}:
                self.send_response(status); self.send_header("Content-Type","text/plain; charset=utf-8"); self.end_headers(); self.wfile.write(body); return
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(HTML)
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler); threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        raw=subprocess.check_output([sys.executable,str(COLLECT),f"http://127.0.0.1:{server.server_port}/","--max-pages","1"],text=True)
        return json.loads(raw)
    finally: server.shutdown()

def main():
    named=run(body=b"User-agent: GPTBot\nDisallow: /\nUser-agent: *\nAllow: /\n")
    assert named["robots"]["ai_agent_allowed"]["GPTBot"] is False and len(named["pages"])==1
    for code in (401,403,404):
        result=run(status=code)
        assert result["robots"]["state"]=="unavailable_4xx" and len(result["pages"])==1
    failed=run(status=503)
    assert failed["robots"]["state"]=="unreachable_5xx" and len(failed["pages"])==0
    malformed=run(body=b"this is not a group\nDisallow: /private\n")
    assert malformed["robots"]["state"]=="present_no_parseable_groups" and len(malformed["pages"])==1
    blocked=run(body=b"User-agent: *\nDisallow: /\n")
    assert blocked["robots"]["wildcard_allowed"] is False and len(blocked["pages"])==0
    redirected=run(redirect=True)
    assert redirected["robots"]["final_url"].endswith("/policy.txt") and len(redirected["pages"])==1
    print(json.dumps({"result":"PASS","scenarios":["named-agent block","401","403","404","503","malformed","wildcard root block","redirect"]},indent=2))
if __name__=="__main__": main()
