#!/usr/bin/env python3
import json, subprocess, sys, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; COLLECT=ROOT/"skills/audit-orchestrator/scripts/collect_site.py"
def collect(fixture):
    handler=partial(SimpleHTTPRequestHandler,directory=str(ROOT/"tests/fixtures"/fixture)); server=ThreadingHTTPServer(("127.0.0.1",0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        raw=subprocess.check_output([sys.executable,str(COLLECT),f"http://127.0.0.1:{server.server_port}/","--max-pages","5"],text=True)
        return json.loads(raw)
    finally: server.shutdown()
def main():
    good,bad=collect("good"),collect("bad")
    assert len(good["pages"])==3 and not good["errors"]
    assert any(p["jsonld"]["blocks"] for p in good["pages"])
    home=bad["pages"][0]
    assert "noindex" in home["meta_robots"] and home["word_count"]<80
    assert bad["robots"]["ai_agent_allowed"]["GPTBot"] is False
    assert bad["robots"]["ai_agent_allowed"]["OAI-SearchBot"] is True
    assert bad["robots"]["sitemap_hints"]==[]
    assert bad["coverage"]["rendered"].startswith("not_checked")
    print(json.dumps({"result":"PASS","good_pages":len(good["pages"]),"bad_triggers":{"noindex":True,"render_escalation":True},"uncertainty_preserved":True},indent=2))
if __name__=="__main__": main()
