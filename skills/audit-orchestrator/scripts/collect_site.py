#!/usr/bin/env python3
"""Bounded, read-only evidence collector. It reports observations, not findings."""
import argparse, gzip, io, json, re, time
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse, urldefrag
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

UA = "BrandAIReadinessAudit/1.1 (+read-only; respects robots.txt)"
BROWSER_UA = "Mozilla/5.0 (compatible; BrandAIReadinessAudit/1.1; read-only)"
AI_AGENTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "meta-externalagent"]
TRACKING_KEYS = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid"}
HTML_TYPES = {"text/html", "application/xhtml+xml"}

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.text=[]; self.title=[]; self.h1=[]; self.jsonld=[]
        self.meta=[]; self.canon=[]; self.img=[]; self.landmarks=[]; self._stack=[]; self._suppress=0; self._json=False; self._buf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self._stack.append(tag)
        if tag in {"script","style","noscript","svg"}: self._suppress += 1
        if tag in {"main","nav","header","footer","article","aside"}: self.landmarks.append(tag)
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="meta": self.meta.append(a)
        if tag=="link" and "canonical" in a.get("rel","").lower(): self.canon.append(a.get("href",""))
        if tag=="img": self.img.append({"src":a.get("src","") ,"alt":a.get("alt")})
        if tag=="script" and "ld+json" in a.get("type","").lower(): self._json=True; self._buf=[]
    def handle_endtag(self, tag):
        if tag=="script" and self._json: self.jsonld.append("".join(self._buf)); self._json=False; self._buf=[]
        if tag in {"script","style","noscript","svg"}: self._suppress=max(0,self._suppress-1)
        if tag in self._stack:
            while self._stack:
                if self._stack.pop()==tag: break
    def handle_data(self, data):
        if self._json: self._buf.append(data)
        elif not self._suppress:
            value=" ".join(data.split())
            if value: self.text.append(value)
            if "title" in self._stack: self.title.append(value)
            if "h1" in self._stack: self.h1.append(value)

class SameAuthorityRedirect(HTTPRedirectHandler):
    def __init__(self, host): super().__init__(); self.host=host.lower()
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if urlparse(newurl).netloc.lower()!=self.host:
            raise HTTPError(request.full_url,code,"redirect left the audited authority",headers,fp)
        return super().redirect_request(request,fp,code,msg,headers,newurl)

def fetch(url, timeout=12, user_agent=BROWSER_UA, limit=2_000_000, accept="text/html,application/xhtml+xml,text/plain,application/xml,text/xml"):
    request=Request(url,headers={"User-Agent":user_agent,"Accept":accept}); started=time.monotonic()
    with build_opener(SameAuthorityRedirect(urlparse(url).netloc)).open(request,timeout=max(.1,timeout)) as response:
        raw=response.read(limit+1); truncated=len(raw)>limit; raw=raw[:limit]
        if response.headers.get("Content-Encoding","").lower()=="gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream: decoded=stream.read(limit+1)
            truncated=truncated or len(decoded)>limit; raw=decoded[:limit]
        encoding=response.headers.get_content_charset() or "utf-8"
        return response.geturl(),response.status,dict(response.headers.items()),raw.decode(encoding,"replace"),round((time.monotonic()-started)*1000),truncated

def jsonld_types(value):
    found=set()
    def walk(item):
        if isinstance(item,dict):
            kind=item.get("@type")
            if isinstance(kind,str): found.add(kind)
            elif isinstance(kind,list): found.update(value for value in kind if isinstance(value,str))
            for value in item.values(): walk(value)
        elif isinstance(item,list):
            for value in item: walk(value)
    walk(value); return sorted(found)

def normalize(base, href, host):
    url=urldefrag(urljoin(base,href))[0]; parsed=urlparse(url)
    if parsed.scheme not in {"http","https"} or parsed.netloc.lower()!=host: return None
    if re.search(r"\.(?:jpg|jpeg|png|gif|svg|webp|zip|gz|pdf|mp4|mp3|woff2?)(?:$|\?)",url,re.I): return None
    query=[]
    for key,value in parse_qsl(parsed.query,keep_blank_values=True):
        lower=key.lower()
        if lower.startswith("utm_") or lower in TRACKING_KEYS: continue
        query.append((key,value))
    query.sort(); path=re.sub(r"/{2,}","/",parsed.path or "/")
    return urlunparse((parsed.scheme.lower(),parsed.netloc.lower(),path,"",urlencode(query,doseq=True),""))

def sitemap_urls(body, base, host, cap=200):
    try: root=ElementTree.fromstring(body)
    except ElementTree.ParseError: return []
    found=[]
    for element in root.iter():
        if element.tag.lower().endswith("loc") and element.text:
            candidate=normalize(base,element.text.strip(),host)
            if candidate and candidate not in found:
                found.append(candidate)
                if len(found)>=cap: break
    return found

def header_value(headers, name):
    return next((value for key,value in headers.items() if key.lower()==name.lower()),"")

def remaining(deadline, maximum): return max(.1,min(maximum,deadline-time.monotonic()))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("--output",default="-"); ap.add_argument("--max-pages",type=int,default=20); ap.add_argument("--max-seconds",type=int,default=270)
    args=ap.parse_args(); args.max_pages=max(1,min(args.max_pages,40)); args.max_seconds=max(15,min(args.max_seconds,295))
    supplied=args.url if "://" in args.url else "https://"+args.url; parsed=urlparse(supplied)
    if parsed.scheme not in {"http","https"} or not parsed.netloc: raise SystemExit("URL must be public HTTP(S)")
    origin=f"{parsed.scheme.lower()}://{parsed.netloc.lower()}/"; host=parsed.netloc.lower(); start=normalize(origin,supplied,host) or origin; deadline=time.monotonic()+args.max_seconds
    robots=urljoin(origin,"/robots.txt"); rp=RobotFileParser(); rp.set_url(robots)
    robots_error=None; robots_status=None; robots_body=""; robots_final=None; robots_type=""; robots_truncated=False; robots_state="unreachable"
    try:
        robots_final,robots_status,headers,robots_body,_,robots_truncated=fetch(robots,timeout=remaining(deadline,8),user_agent=UA,limit=512_000,accept="text/plain")
        if urlparse(robots_final).netloc.lower()!=host: raise ValueError("robots redirect left the audited authority")
        robots_type=header_value(headers,"Content-Type"); rp.parse(robots_body.splitlines())
        robots_state="present" if any(line.strip().lower().startswith("user-agent:") for line in robots_body.splitlines()) else "present_no_parseable_groups"
    except HTTPError as error:
        robots_status=error.code
        if 400<=error.code<=499: robots_state="unavailable_4xx"; rp.parse([])
        else: robots_state="unreachable_5xx"; robots_error=f"HTTP {error.code}"
    except Exception as error: robots_state="unreachable_network"; robots_error=type(error).__name__+": "+str(error)[:160]
    hints=[] if robots_error else [line.split(":",1)[1].strip() for line in robots_body.splitlines() if line.lower().startswith("sitemap:") and line.split(":",1)[1].strip()]
    policies={agent:(rp.can_fetch(agent,start) if not robots_error else None) for agent in AI_AGENTS}; wildcard=rp.can_fetch("*",start) if not robots_error else None
    out={"site":start,"origin":origin,"collected_at":datetime.now(timezone.utc).isoformat(),"collector":"static","collector_version":"1.1","limits":{"max_pages":args.max_pages,"max_seconds":args.max_seconds,"max_bytes_per_page":2_000_000,"rate_per_second":2,"robots_timeout_seconds":8,"page_timeout_seconds":12,"robots_parse_bytes":512_000},"robots":{"url":robots,"final_url":robots_final,"status":robots_status,"state":robots_state,"content_type":robots_type,"response_truncated":robots_truncated,"read_error":robots_error,"wildcard_allowed":wildcard,"ai_agent_allowed":policies,"sitemap_hints":hints},"sitemaps":[],"pages":[],"errors":[],"ai_probe":{"status":"not_checked"},"coverage":{"rendered":"not_checked: collector is static","off_site":"not_checked: requires search-capable agent","deadline_reached":False}}
    if robots_error or wildcard is False: out["coverage"]["crawl"]="not_checked: robots policy unavailable or supplied path is blocked"
    else:
        discovered=[]
        for candidate in (hints or [urljoin(origin,"/sitemap.xml")])[:3]:
            if time.monotonic()>=deadline: break
            sitemap=normalize(origin,candidate,host)
            if not sitemap or not rp.can_fetch("*",sitemap): continue
            try:
                final,status,headers,body,elapsed,truncated=fetch(sitemap,timeout=remaining(deadline,8),limit=1_000_000,accept="application/xml,text/xml,text/plain")
                if urlparse(final).netloc.lower()!=host: raise ValueError("sitemap redirect left the audited authority")
                urls=sitemap_urls(body,final,host); discovered.extend(urls)
                out["sitemaps"].append({"url":sitemap,"final_url":final,"status":status,"content_type":header_value(headers,"Content-Type"),"response_truncated":truncated,"latency_ms":elapsed,"urls_discovered":len(urls)})
            except HTTPError as error:
                if sitemap in hints or error.code not in {404,410}: out["errors"].append({"url":sitemap,"error":"HTTPError","detail":str(error)[:300]})
            except (URLError,TimeoutError,ValueError,OSError) as error: out["errors"].append({"url":sitemap,"error":type(error).__name__,"detail":str(error)[:300]})
        queue=deque([start]+[url for url in discovered if url!=start]); seen=set()
        while queue and len(out["pages"])<args.max_pages and time.monotonic()<deadline:
            url=queue.popleft()
            if url in seen: continue
            seen.add(url)
            if not rp.can_fetch("*",url): out["pages"].append({"url":url,"robots_allowed":False}); continue
            try:
                final,status,headers,html,elapsed,truncated=fetch(url,timeout=remaining(deadline,12))
                if urlparse(final).netloc.lower()!=host: raise ValueError("page redirect left the audited authority")
                content_type=header_value(headers,"Content-Type"); media_type=content_type.split(";",1)[0].strip().lower(); path_policies={agent:rp.can_fetch(agent,url) for agent in AI_AGENTS}
                if media_type not in HTML_TYPES:
                    out["pages"].append({"url":url,"final_url":final,"robots_allowed":True,"robots_ai_allowed":path_policies,"status":status,"content_type":content_type,"response_truncated":truncated,"latency_ms":elapsed,"parse_status":"skipped_non_html"}); continue
                parser=PageParser(); parser.feed(html); metas={item.get("name",item.get("property","")).lower():item.get("content","") for item in parser.meta if item.get("name") or item.get("property")}
                parsed_ld=[]; ld_errors=0
                for block in parser.jsonld:
                    try: parsed_ld.append(json.loads(block))
                    except Exception: ld_errors+=1
                words=re.findall(r"\b[\w'-]+\b"," ".join(parser.text))
                page={"url":url,"final_url":final,"robots_allowed":True,"robots_ai_allowed":path_policies,"status":status,"content_type":content_type,"response_truncated":truncated,"latency_ms":elapsed,"parse_status":"parsed_html","title":" ".join(parser.title)[:300],"h1":parser.h1[:10],"word_count":len(words),"text_length":len(" ".join(parser.text)),"landmarks":sorted(set(parser.landmarks)),"meta_robots":metas.get("robots",""),"meta_robot_directives":{"robots":metas.get("robots",""),"googlebot":metas.get("googlebot",""),"bingbot":metas.get("bingbot","")},"description":metas.get("description",""),"canonical":parser.canon,"links_count":len(parser.links),"images":{"count":len(parser.img),"missing_alt":sum(item["alt"] is None for item in parser.img),"empty_alt":sum(item["alt"]=="" for item in parser.img)},"jsonld":{"blocks":len(parser.jsonld),"parse_errors":ld_errors,"types":jsonld_types(parsed_ld)},"text_sample":" ".join(parser.text)[:1200]}
                out["pages"].append(page)
                if url==start and policies.get("GPTBot") and time.monotonic()+.5<deadline:
                    time.sleep(.5)
                    try:
                        bot_final,bot_status,_,bot_html,_,bot_truncated=fetch(url,timeout=remaining(deadline,12),user_agent="GPTBot/1.0")
                        if urlparse(bot_final).netloc.lower()!=host: raise ValueError("GPTBot probe redirect left the audited authority")
                        bot_parser=PageParser(); bot_parser.feed(bot_html); bot_len=len(" ".join(bot_parser.text)); ratio=(bot_len/page["text_length"]) if page["text_length"] else None
                        out["ai_probe"]={"status":"checked","agent":"GPTBot","http_status":bot_status,"text_length":bot_len,"browser_text_length":page["text_length"],"text_ratio":round(ratio,3) if ratio is not None else None,"response_truncated":bot_truncated}
                    except Exception as error: out["ai_probe"]={"status":"checked","agent":"GPTBot","error":type(error).__name__,"detail":str(error)[:200]}
                for href in parser.links:
                    candidate=normalize(final,href,host)
                    if candidate and candidate not in seen and len(queue)<args.max_pages*8: queue.append(candidate)
            except (HTTPError,URLError,TimeoutError,ValueError,OSError) as error: out["errors"].append({"url":url,"error":type(error).__name__,"detail":str(error)[:300]})
            if time.monotonic()+.5<deadline: time.sleep(.5)
        out["coverage"]["deadline_reached"]=bool(queue and time.monotonic()>=deadline)
        if out["coverage"]["deadline_reached"]: out["coverage"]["crawl"]="partial: global collection deadline reached"
    payload=json.dumps(out,indent=2,ensure_ascii=False)
    if args.output=="-": print(payload)
    else:
        with open(args.output,"w",encoding="utf-8") as handle: handle.write(payload+"\n")

if __name__=="__main__": main()
