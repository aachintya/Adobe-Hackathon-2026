#!/usr/bin/env python3
"""Collect reusable source evidence, not an invented AI visibility score."""
import argparse
import copy
import gzip
import io
import json
import math
import re
import time
import zlib
from datetime import datetime, timezone
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse, urldefrag
from urllib.request import HTTPRedirectHandler, Request, build_opener
from xml.etree import ElementTree

from page_evidence import PageParser, jsonld_types, page_fields
from robots_policy import RobotsPolicy

UA = "BrandAIReadinessAudit"
AI_AGENTS = ["Googlebot", "bingbot", "OAI-SearchBot", "Claude-SearchBot", "PerplexityBot",
             "GPTBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Perplexity-User",
             "Google-Extended", "Applebot-Extended", "meta-externalagent"]
AGENT_ROLES = {"search": ["Googlebot", "bingbot", "OAI-SearchBot", "Claude-SearchBot", "PerplexityBot"],
               "training_or_other_control": ["GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "meta-externalagent"],
               "user_fetch": ["ChatGPT-User", "Claude-User", "Perplexity-User"]}
TRACKING_KEYS = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid"}
HTML_TYPES = {"text/html", "application/xhtml+xml"}


def header_value(headers, name):
    return next((v for k, v in headers.items() if k.lower() == name.lower()), "")


def resolve_link(base, href):
    try:
        url = urljoin(base, href)
        parsed = urlparse(url)
        parsed.port  # Validate invalid/out-of-range ports before requesting.
        return url
    except ValueError:
        return None


def normalize(base, href, host):
    resolved = resolve_link(base, href)
    if resolved is None: return None
    url = urldefrag(resolved)[0]; parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != host or parsed.username is not None: return None
    if re.search(r"\.(?:jpg|jpeg|png|gif|svg|webp|zip|gz|pdf|mp4|mp3|woff2?)(?:$|\?)", url, re.I): return None
    query = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in TRACKING_KEYS]
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.params, urlencode(sorted(query)), ""))


class DeadlineReached(Exception):
    pass


class SameAuthorityRedirect(HTTPRedirectHandler):
    max_redirections = 5

    def __init__(self, host, before_request, policy=None):
        self.host, self.before_request, self.policy, self.chain = host, before_request, policy, []

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != self.host or parsed.username:
            raise HTTPError(request.full_url, code, "redirect left the audited authority", headers, fp)
        if self.policy and not self.policy.can_fetch(UA, newurl):
            raise HTTPError(request.full_url, code, "redirect target blocked by collector robots policy", headers, fp)
        self.before_request()
        self.chain.append({"from": request.full_url, "to": newurl, "status": code})
        # Older urllib versions reject 308 even when its error hook is present.
        # For GET/HEAD, reuse its supported 307 path; retain the actual
        # status in the evidence and in the policy checks above.
        redirect_code = 307 if code == 308 and request.get_method() in {"GET", "HEAD"} else code
        return super().redirect_request(request, fp, redirect_code, msg, headers, newurl)

    # Supply the missing hook on older urllib versions without bypassing its
    # redirect-loop protection or our authority and robots checks.
    def http_error_308(self, request, fp, code, msg, headers):
        return self.http_error_302(request, fp, code, msg, headers)


class Client:
    def __init__(self, origin, seconds):
        self.host = urlparse(origin).netloc.lower()
        self.deadline = time.monotonic() + seconds
        self.next_request = 0.0
        self.policy = None
        self.requests = 0
        self.interval = .5

    def before_request(self):
        delay = max(0, self.next_request - time.monotonic())
        if time.monotonic() + delay >= self.deadline: raise DeadlineReached()
        if delay: time.sleep(delay)
        self.next_request = time.monotonic() + self.interval
        self.requests += 1

    def fetch(self, url, timeout=8, limit=2_000_000, policy=True):
        self.before_request()
        handler = SameAuthorityRedirect(self.host, self.before_request, self.policy if policy else None)
        request = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml,text/plain"})
        started = time.monotonic()
        with build_opener(handler).open(request, timeout=max(.1, min(timeout, self.deadline - started))) as response:
            chunks, size = [], 0
            while size <= limit:
                if time.monotonic() >= self.deadline: raise DeadlineReached()
                chunk = response.read1(min(65536, limit + 1 - size))
                if not chunk: break
                chunks.append(chunk); size += len(chunk)
            raw = b"".join(chunks); truncated = len(raw) > limit; raw = raw[:limit]
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream: decoded = stream.read(limit + 1)
                truncated = truncated or len(decoded) > limit; raw = decoded[:limit]
            encoding = response.headers.get_content_charset() or "utf-8"
            try: body = raw.decode(encoding, "replace")
            except LookupError: body = raw.decode("utf-8", "replace")
            headers = dict(response.headers.items())
            headers["X-Robots-Tag"] = ", ".join(response.headers.get_all("X-Robots-Tag", []))
            headers["X-Robots-Tag-Values"] = response.headers.get_all("X-Robots-Tag", [])
            return {"final_url": response.geturl(), "status": response.status, "headers": headers, "body": body,
                    "latency_ms": round((time.monotonic() - started) * 1000), "response_truncated": truncated,
                    "redirects": handler.chain, "content_type": response.headers.get("Content-Type", "")}


def sitemap_inventory(body, base, host, cap=200):
    try: root = ElementTree.fromstring(body)
    except ElementTree.ParseError: return [], False
    is_index = root.tag.rsplit("}", 1)[-1].lower() == "sitemapindex"
    found = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1].lower() == "loc" and element.text:
            candidate = normalize(base, element.text.strip(), host)
            if candidate and candidate not in found: found.append(candidate)
            if len(found) >= cap: break
    return found, is_index


def sitemap_urls(body, base, host, cap=200):
    return sitemap_inventory(body, base, host, cap)[0]


def page_type(url):
    path = urlparse(url).path.lower()
    for category, pattern in [("decision", r"pricing|plans|compare"), ("offering", r"product|service|solution"),
                              ("entity", r"about|company|team"), ("task", r"contact|support|help|docs|book"),
                              ("proof", r"case-stud|customer|security"), ("article", r"blog|news|article")]:
        if re.search(pattern, path): return category
    return "home" if path == "/" else "other"


def resume_selection(previous, start, host, targets):
    """Reuse this invocation's captures; only prioritize observed HTML links."""
    if (not isinstance(previous, dict) or previous.get("site") != start
            or previous.get("collector") != "static"
            or previous.get("collector_version") != "2.1"):
        raise ValueError("Resume evidence must be a current collector capture of the same supplied URL")
    pages = previous.get("pages")
    if not isinstance(pages, list) or not pages or len(pages) > 40:
        raise ValueError("Resume evidence needs 1-40 captured page records")
    for field in ("limits", "coverage"):
        if not isinstance(previous.get(field), dict): raise ValueError(f"Resume {field} must be an object")
    for field in ("sitemaps", "errors"):
        if not isinstance(previous.get(field), list) or any(not isinstance(x, dict) or not isinstance(x.get("url"), str) for x in previous[field]):
            raise ValueError(f"Resume {field} must contain URL records")
    for container, field in (("limits", "max_seconds"), ("limits", "effective_request_interval_seconds"),
                             ("coverage", "request_count"), ("coverage", "elapsed_seconds")):
        value = previous[container].get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Resume {container}.{field} must be a finite nonnegative number")
    if not isinstance(previous["coverage"].get("sample_types", {}), dict):
        raise ValueError("Resume sample_types must be an object")
    try:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(previous["collected_at"])).total_seconds()
    except (KeyError, TypeError, ValueError):
        raise ValueError("Resume evidence needs its original UTC capture timestamp")
    if not 0 <= age < 300:
        raise ValueError("Resume evidence is only reusable within the original five-minute invocation")
    observed, seen = [], set()
    for page in pages:
        if not isinstance(page, dict) or not normalize(start, page.get("url", ""), host):
            raise ValueError("Resume page is outside the supplied authority")
        for field in ("url", "final_url"):
            if page.get(field):
                normalized = normalize(start, page[field], host)
                if normalized: seen.add(normalized)
        base = page.get("link_base_url", page.get("final_url", page["url"]))
        if not isinstance(base, str) or not isinstance(page.get("links", []), list):
            raise ValueError("Resume page needs a URL base and link records")
        for link in page.get("links", []):
            if not isinstance(link, dict) or (link.get("href") is not None and not isinstance(link["href"], str)):
                raise ValueError("Resume links must be captured link objects")
            if not link.get("href"): continue
            candidate = normalize(base, link["href"], host)
            if candidate and candidate not in observed: observed.append(candidate)
    selected = []
    for target in targets:
        candidate = normalize(start, target, host)
        if candidate not in observed:
            raise ValueError("Task targets must be observed same-authority HTML link destinations; inspect documents or other authorities with host tools")
        if candidate not in selected: selected.append(candidate)
    for error in previous.get("errors", []):
        candidate = normalize(start, error.get("url", ""), host)
        if candidate: seen.add(candidate)
    return [item for item in observed if item not in seen], seen, selected


def collect(url, max_pages=12, max_seconds=120, *, resume=None, target_urls=None):
    max_pages, max_seconds = max(1, min(max_pages, 40)), max(5, min(max_seconds, 180))
    supplied = url if "://" in url else "https://" + url
    parsed = urlparse(supplied)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        raise ValueError("URL must be HTTP(S) without credentials")
    origin = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}/"; host = parsed.netloc.lower()
    start = normalize(origin, supplied, host)
    if not start: raise ValueError("Starting URL must be an HTML page, not a media/archive file")
    target_urls = target_urls or []
    if target_urls and resume is None:
        raise ValueError("Task targets require --resume-evidence from the landing-page pass")
    queue, seen, selected = resume_selection(resume, start, host, target_urls) if resume is not None else ([start], set(), [])
    if resume is not None and max_pages < len(resume["pages"]):
        raise ValueError("--max-pages is the total page cap and cannot be below the saved page count")
    client = Client(origin, max_seconds)
    out = {"site": start, "origin": origin, "collected_at": datetime.now(timezone.utc).isoformat(),
           "collector": "static", "collector_version": "2.1", "agent_roles": AGENT_ROLES,
           "limits": {"max_pages": max_pages, "max_seconds": max_seconds, "rate_per_second": 2, "max_bytes_per_page": 2_000_000},
           "robots": {}, "sitemaps": [], "pages": [], "errors": [],
           "ai_probe": {"status": "not_checked", "reason": "No bot impersonation: local requests do not verify provider IP access."},
           "coverage": {"rendered": "not_checked: collector is static", "off_site": "not_checked: requires search-capable agent",
                        "actual_ai_visibility": "not_measured: requires recorded assistant answers and citations", "deadline_reached": False}}
    if resume is not None:
        out = copy.deepcopy(resume)
        out["limits"]["max_pages"] = max_pages
        out["limits"]["max_seconds"] += max_seconds
        # Recheck robots in the second pass; never treat a saved policy as new evidence.
        # This delay also preserves throttling across immediately adjacent invocations.
        client.next_request = time.monotonic() + max(.5, out["limits"].get("effective_request_interval_seconds", .5))
    prior_requests = out["coverage"].get("request_count", 0)
    prior_elapsed = out["coverage"].get("elapsed_seconds", 0)
    out.setdefault("collection_passes", [])
    out["coverage"]["selected_task_urls"] = list(dict.fromkeys(out["coverage"].get("selected_task_urls", []) + selected))
    out["coverage"]["selected_already_attempted"] = [item for item in selected if item in seen]
    def record_error(target, error):
        item = {"url": target, "error": type(error).__name__, "detail": str(error)[:300]}
        if isinstance(error, HTTPError): item["status"] = error.code
        out["errors"].append(item)
    robots_url = urljoin(origin, "robots.txt")
    body, state, robots_error, status, metadata = "", "unreachable_network", None, None, {}
    try:
        response = client.fetch(robots_url, limit=512_000, policy=False)
        body, status = response["body"], response["status"]
        metadata = {k: response[k] for k in ("final_url", "content_type", "response_truncated", "redirects")}
        if response["response_truncated"]:
            # An omitted later Allow/group can reverse a decision; do not assert it.
            state, robots_error = "truncated", "Robots response exceeded 500 KiB; policy incomplete"
        else: state = "present" if re.search(r"(?im)^\s*user-agent\s*:", body) else "present_no_parseable_groups"
    except HTTPError as error:
        status = error.code
        if 400 <= error.code <= 499: state = "unavailable_4xx"
        else: state, robots_error = "unreachable_5xx" if error.code >= 500 else "redirect_unchecked", str(error)
    except (URLError, OSError, ValueError, EOFError, HTTPException, zlib.error, DeadlineReached) as error:
        robots_error = f"{type(error).__name__}: {error}"
    policy = RobotsPolicy(body); client.policy = policy
    client.interval = max(.5, policy.crawl_delay(UA))
    client.next_request += client.interval - .5
    out["limits"]["effective_request_interval_seconds"] = client.interval
    decisions = {agent: policy.decision(agent, start) if not robots_error else {"allowed": None, "matched_rule": None} for agent in AI_AGENTS}
    hints = [line.split(":", 1)[1].strip() for line in body.splitlines() if line.lower().startswith("sitemap:")]
    out["robots"] = {"url": robots_url, "status": status, "state": state, **metadata, "read_error": robots_error,
                     "rules_text": body, "wildcard_allowed": policy.can_fetch("*", start) if not robots_error else None,
                     "collector_allowed": policy.can_fetch(UA, start) if not robots_error else None,
                     "ai_agent_allowed": {k: v["allowed"] for k, v in decisions.items()}, "decisions": decisions,
                     "sitemap_hints": hints}
    try:
        if robots_error or not policy.can_fetch(UA, start):
            out["coverage"]["crawl"] = "not_checked: robots policy unavailable or supplied path is blocked for this collector"
        else:
            # Fetch the actual requested page first. Expensive inventories must not consume its budget.
            types = dict(out["coverage"].get("sample_types", {}))
            sitemaps_seen = {item["url"] for item in out["sitemaps"]}
            inventory_pending = [item for item in hints or [urljoin(origin, "sitemap.xml")] if item not in sitemaps_seen]
            selected_order = {item: i for i, item in enumerate(selected)}
            while (queue or inventory_pending) and len(out["pages"]) < max_pages:
                if time.monotonic() >= client.deadline: raise DeadlineReached()
                if seen and inventory_pending and len(sitemaps_seen) < 3 and not any(item in selected_order for item in queue):
                    sitemap = normalize(origin, inventory_pending.pop(0), host)
                    if not sitemap or sitemap in sitemaps_seen or not policy.can_fetch(UA, sitemap): continue
                    sitemaps_seen.add(sitemap)
                    try:
                        response = client.fetch(sitemap, limit=1_000_000)
                        urls, is_index = sitemap_inventory(response["body"], response["final_url"], host)
                        out["sitemaps"].append({"url": sitemap, "status": response["status"], "is_index": is_index,
                                                "urls_discovered": len(urls), "response_truncated": response["response_truncated"]})
                        if is_index: inventory_pending.extend(urls[:3])
                        else: queue.extend(x for x in urls if x not in seen and x not in queue)
                    except HTTPError as error:
                        if sitemap in hints or error.code not in {404, 410}: record_error(sitemap, error)
                    except (URLError, OSError, ValueError, EOFError, HTTPException, zlib.error) as error: record_error(sitemap, error)
                if not queue:
                    if len(sitemaps_seen) >= 3: break
                    continue
                if seen: queue.sort(key=lambda x: (selected_order.get(x, len(selected_order)), types.get(page_type(x), 0), page_type(x) == "other"))
                target = queue.pop(0)
                if target in seen: continue
                seen.add(target)
                path_policy = {agent: policy.decision(agent, target) for agent in AI_AGENTS}
                if not policy.can_fetch(UA, target):
                    out["pages"].append({"url": target, "robots_allowed": False, "robots_ai_allowed": {k: v["allowed"] for k, v in path_policy.items()}})
                    continue
                try:
                    response = client.fetch(target)
                    page = {"url": target, "robots_allowed": True,
                            **{k: response[k] for k in ("final_url", "status", "content_type", "latency_ms", "response_truncated", "redirects")},
                            "robots_ai_allowed": {k: v["allowed"] for k, v in path_policy.items()},
                            "robots_decisions": path_policy,
                            "final_robots_ai_allowed": {a: policy.can_fetch(a, response["final_url"]) for a in AI_AGENTS},
                            "x_robots_tag": header_value(response["headers"], "X-Robots-Tag"),
                            "x_robots_tags": header_value(response["headers"], "X-Robots-Tag-Values"),
                            "last_modified": header_value(response["headers"], "Last-Modified"), "sample_type": page_type(target)}
                    if page["content_type"].split(";", 1)[0].strip().lower() not in HTML_TYPES:
                        page["parse_status"] = "skipped_non_html"
                    else:
                        parser, fields = page_fields(response["body"])
                        page.update(fields); page["parse_status"] = "parsed_html"
                        link_base = response["final_url"]
                        if parser.base_href is not None:
                            declared_base = resolve_link(link_base, parser.base_href)
                            if declared_base and urlparse(declared_base).scheme in {"http", "https"}:
                                link_base = declared_base
                        page["link_base_url"] = link_base
                        for link in page["links"]:
                            link["url"] = resolve_link(link_base, link["href"]) if link.get("href") is not None else None
                            if link["url"] is None: link["resolution_error"] = "Missing or malformed URL; not followed"
                        for href in parser.links:
                            if not href: continue
                            candidate = normalize(link_base, href, host)
                            if candidate and candidate not in seen and candidate not in queue and len(queue) < max_pages * 10:
                                queue.append(candidate)
                    out["pages"].append(page)
                    types[page_type(target)] = types.get(page_type(target), 0) + 1
                except (HTTPError, URLError, OSError, ValueError, EOFError, HTTPException, zlib.error, RecursionError) as error: record_error(target, error)
            out["coverage"]["sample_types"] = types
    except DeadlineReached:
        out["coverage"]["deadline_reached"] = True
        out["coverage"]["crawl"] = "partial: collection budget reached; compose from saved evidence"
    elapsed = round(max_seconds - max(0, client.deadline - time.monotonic()), 2)
    out["collection_passes"].append({"max_seconds": max_seconds, "elapsed_seconds": elapsed,
                                     "request_count": client.requests, "target_urls": selected})
    out["coverage"]["request_count"] = prior_requests + client.requests
    out["coverage"]["elapsed_seconds"] = round(prior_elapsed + elapsed, 2)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url"); parser.add_argument("--output", default="-")
    parser.add_argument("--max-pages", type=int, default=12); parser.add_argument("--max-seconds", type=int, default=120)
    parser.add_argument("--resume-evidence", help="Landing-page evidence from this same invocation")
    parser.add_argument("--target-url", action="append", default=[], help="Observed task destination to fetch before inventory (repeatable)")
    args = parser.parse_args()
    try:
        from pathlib import Path
        previous = json.loads(Path(args.resume_evidence).read_text(encoding="utf-8")) if args.resume_evidence else None
        result = collect(args.url, args.max_pages, args.max_seconds, resume=previous, target_urls=args.target_url)
    except (ValueError, OSError) as error: parser.error(str(error))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output == "-": print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        from pathlib import Path
        Path(args.output).write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__": main()
