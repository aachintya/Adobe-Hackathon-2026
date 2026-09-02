#!/usr/bin/env python3
"""Exercise path, sitemap, URL, content-type, and redirect safety invariants."""
import json, subprocess, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COLLECT=ROOT/"skills/audit-orchestrator/scripts/collect_site.py"

def main():
    outside_hits=[]
    class Outside(BaseHTTPRequestHandler):
        def do_GET(self):
            outside_hits.append(self.path); self.send_response(200); self.end_headers(); self.wfile.write(b"outside")
        def log_message(self,*args): pass
    outside=ThreadingHTTPServer(("127.0.0.1",0),Outside); threading.Thread(target=outside.serve_forever,daemon=True).start()

    class Site(BaseHTTPRequestHandler):
        def send(self,code,kind,body,location=None):
            self.send_response(code); self.send_header("Content-Type",kind)
            if location: self.send_header("Location",location)
            self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            base=f"http://127.0.0.1:{self.server.server_port}"
            if self.path=="/robots.txt": return self.send(200,"text/plain",f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n".encode())
            if self.path=="/sitemap.xml": return self.send(200,"application/xml",f"<?xml version='1.0'?><urlset><url><loc>{base}/sitemap-only</loc></url></urlset>".encode())
            if self.path=="/deep/start": return self.send(200,"text/html",b"<html><head><title>Start</title></head><body><main><h1>Start path</h1><a href='/product?utm_source=test&amp;b=2&amp;a=1'>Product</a><a href='/asset.txt'>Asset</a><a href='/outside'>Outside</a></main></body></html>")
            if self.path=="/sitemap-only": return self.send(200,"text/html",b"<html><body><main><h1>Sitemap only</h1></main></body></html>")
            if self.path=="/product?a=1&b=2": return self.send(200,"text/html",b"<html><body><main><h1>Product</h1></main></body></html>")
            if self.path=="/asset.txt": return self.send(200,"text/plain",b"not html")
            if self.path=="/outside": return self.send(302,"text/plain",b"",f"http://127.0.0.1:{outside.server_port}/escaped")
            return self.send(404,"text/plain",b"missing")
        def log_message(self,*args): pass

    site=ThreadingHTTPServer(("127.0.0.1",0),Site); threading.Thread(target=site.serve_forever,daemon=True).start()
    try:
        start=f"http://127.0.0.1:{site.server_port}/deep/start"
        raw=subprocess.check_output([sys.executable,str(COLLECT),start,"--max-pages","10","--max-seconds","30"],text=True)
        result=json.loads(raw); pages=result["pages"]; urls={page["url"]:page for page in pages}
        assert result["site"]==start
        assert result["sitemaps"][0]["urls_discovered"]==1
        assert f"http://127.0.0.1:{site.server_port}/sitemap-only" in urls
        normalized=f"http://127.0.0.1:{site.server_port}/product?a=1&b=2"
        assert normalized in urls and not any("utm_" in url for url in urls)
        asset=f"http://127.0.0.1:{site.server_port}/asset.txt"
        assert urls[asset]["parse_status"]=="skipped_non_html"
        assert any(item["url"].endswith("/outside") and "audited authority" in item["detail"] for item in result["errors"])
        assert outside_hits==[]
        assert all("robots_ai_allowed" in page for page in pages if page.get("robots_allowed") and page.get("parse_status"))
        print(json.dumps({"result":"PASS","path_preserved":True,"sitemap_discovery":True,"query_normalized":True,"non_html_skipped":True,"cross_site_redirect_blocked_before_fetch":True,"path_agent_policies":True},indent=2))
    finally:
        site.shutdown(); outside.shutdown()

if __name__=="__main__": main()
