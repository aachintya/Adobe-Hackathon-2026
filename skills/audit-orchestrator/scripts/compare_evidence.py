#!/usr/bin/env python3
"""Compare two collector outputs without calling ordinary crawl variation a regression."""
import argparse, json

def page_map(doc): return {p.get("url"):p for p in doc.get("pages",[]) if p.get("status")}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("before"); ap.add_argument("after"); ap.add_argument("--output",default="-"); a=ap.parse_args()
    before=json.load(open(a.before,encoding="utf-8")); after=json.load(open(a.after,encoding="utf-8"))
    comparable=(before.get("collector")==after.get("collector") and before.get("site")==after.get("site"))
    result={"site":after.get("site"),"comparable":comparable,"warnings":[],"changes":[]}
    if not comparable: result["warnings"].append("Collector mode or site differs; do not attribute changes to the site.")
    rb,ra=before.get("robots",{}),after.get("robots",{})
    for agent in sorted(set(rb.get("ai_agent_allowed",{}))|set(ra.get("ai_agent_allowed",{}))):
        x,y=rb.get("ai_agent_allowed",{}).get(agent),ra.get("ai_agent_allowed",{}).get(agent)
        if x!=y: result["changes"].append({"kind":"robots_policy","agent":agent,"before":x,"after":y})
    pb,pa=page_map(before),page_map(after)
    for url in sorted(set(pb)&set(pa)):
        x,y=pb[url],pa[url]
        for field in ("status","final_url","canonical","meta_robots"):
            if x.get(field)!=y.get(field): result["changes"].append({"kind":"page_field","url":url,"field":field,"before":x.get(field),"after":y.get(field)})
        if not x.get("response_truncated") and not y.get("response_truncated"):
            bx,ay=x.get("text_length",0),y.get("text_length",0)
            if max(bx,ay,1) and abs(ay-bx)/max(bx,ay,1)>=.35: result["changes"].append({"kind":"material_text_delta","url":url,"before":bx,"after":ay})
    payload=json.dumps(result,indent=2,ensure_ascii=False)
    if a.output=="-": print(payload)
    else: open(a.output,"w",encoding="utf-8").write(payload+"\n")
if __name__=="__main__": main()
