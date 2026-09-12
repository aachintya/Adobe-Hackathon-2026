#!/usr/bin/env python3
"""Portable static audit fallback. The agent composes the complete audit via SKILL.md."""
import argparse
import json
import re
from pathlib import Path

from collect_site import collect, AGENT_ROLES


def indexing_directives(page):
    """Preserve generic vs engine-specific scope, including scoped HTTP headers."""
    result = {key: set() for key in ("robots", "googlebot", "bingbot")}
    for engine, value in page.get("meta_robot_directives", {}).items():
        result.setdefault(engine, set()).update(x.lower() for x in re.split(r"[,\s]+", value) if x)
    # Each HTTP header field starts a new generic scope. Joining fields would
    # incorrectly assign a later generic directive to the previous named bot.
    for header in page.get("x_robots_tags", [page.get("x_robots_tag", "")]):
        scope = "robots"
        for raw in header.split(","):
            directive = raw.strip().lower()
            match = re.match(r"^([a-z][a-z0-9_-]*):\s*(.*)$", directive)
            if match and match[1] not in {"max-snippet", "max-image-preview", "max-video-preview", "unavailable_after"}:
                scope, directive = match[1], match[2]
            if directive: result.setdefault(scope, set()).add(directive)
    for values in result.values():
        if "none" in values: values.update({"noindex", "nofollow"})
    return result


def baseline(evidence):
    pages = [p for p in evidence["pages"] if p.get("parse_status") == "parsed_html"]
    complete = [p for p in pages if not p.get("response_truncated")]
    findings = []

    def add(title, severity, observation, urls, checked, action, owner, mechanism, verification):
        findings.append({"id": "", "title": title, "category": "discoverability", "severity": severity,
                         "confidence": "high", "evidence": {"observation": observation, "affected": len(urls), "checked": checked, "urls": urls},
                         "suggested_action": {"summary": action, "priority": severity if severity != "critical" else "high", "effort": "low",
                                              "owner_hint": owner, "mechanism": mechanism, "verification": verification}})

    # A restriction is reported as a scoped policy observation, never proof of non-citation.
    robots = evidence["robots"]
    search_blocks = [a for a in AGENT_ROLES["search"] if robots.get("ai_agent_allowed", {}).get(a) is False]
    if search_blocks:
        rules = {a: robots.get("decisions", {}).get(a, {}).get("matched_rule") for a in search_blocks}
        add("Search crawler policy restricts the supplied audit page", "medium",
            f"Published robots policy disallows {', '.join(search_blocks)} for {evidence['site']}. Matching rules: {json.dumps(rules)}. This checks policy, not live assistant citations or provider IP access.",
            [evidence["site"]], 1, "Review the matched rules for this public landing page; permit the relevant search crawler if discovery is intended.",
            "Web platform / search owner", "Permits eligible search crawlers to retrieve this path without changing training preferences.",
            "Re-evaluate the named crawler and exact path, then use provider logs or webmaster inspection to verify actual access.")
    exclusions = []
    for page in complete:
        scopes = [k for k, v in indexing_directives(page).items() if "noindex" in v and k in {"robots", "googlebot", "bingbot"}]
        if scopes: exclusions.append((page, scopes))
    if exclusions:
        observation = "; ".join(f"{p['url']}: noindex scope={','.join(scopes)}; meta={p.get('meta_robot_directives')}; X-Robots-Tag={p.get('x_robots_tag', '')}" for p, scopes in exclusions)
        add("Indexing restrictions require review on sampled pages", "medium", observation,
            [p["url"] for p, _ in exclusions], len(complete), "Keep intentional exclusions; remove only unintended noindex directives from pages intended to acquire visitors.",
            "Search / web platform owner", "Removes the observed indexing restriction for the stated engine; does not guarantee indexing or citations.",
            "Fetch the same pages after deployment, confirm the intended scope, then request engine URL inspection where available.")
    invalid = [p for p in complete if p["jsonld"]["parse_errors"]]
    if invalid:
        add("Structured data contains invalid JSON", "low",
            "; ".join(f"{p['url']}: {json.dumps(p['jsonld']['errors'])}" for p in invalid),
            [p["url"] for p in invalid], len(complete), "Repair the identified JSON syntax errors and confirm the repaired values agree with the page.",
            "Web developer", "Makes existing structured data parseable; structured data alone does not establish AI visibility.",
            "Reparse each affected JSON-LD block and compare material fields with visible content.")
    for index, finding in enumerate(findings, 1): finding["id"] = f"F-{index:03d}"
    summary = {"total_findings": len(findings), **{severity: sum(f["severity"] == severity for f in findings) for severity in ("critical", "high", "medium", "low")}}
    limitations = ["Rendered extraction and interactive engagement not checked: static Python fallback has no browser.",
                   "Keyboard, focus, mobile layout, overlays and context retention not checked.",
                   "Off-site retrieval and independent corroboration not checked: search-capable agent required.",
                   "Buyer-question answerability and visitor journeys require agent review of saved passages and links.",
                   "Actual AI citations, provider IP access, Search Console settings and behavioral analytics not measured."]
    if evidence["errors"]: limitations.append(f"{len(evidence['errors'])} collection errors retained in evidence.json; failed requests are not treated as site defects.")
    if evidence["coverage"].get("crawl"): limitations.append(evidence["coverage"]["crawl"])
    if any(p.get("response_truncated") or p.get("evidence_truncated") for p in pages): limitations.append("Some page evidence is capped; absence cannot establish missing content.")
    readiness = [
        {"stage": "access", "status": "restricted" if search_blocks else "observed" if robots.get("ai_agent_allowed", {}).get("OAI-SearchBot") is not None else "not_checked",
         "detail": "Published robots policy checked separately for search, training controls and user fetch; real provider access remains unverified.", "urls": [robots["url"]]},
        {"stage": "extraction", "status": "observed" if pages else "not_checked",
         "detail": f"Saved source text, passages and links from {len(pages)} HTML pages. Material answerability requires agent review.", "urls": [p["url"] for p in pages]},
        {"stage": "answerability", "status": "not_checked", "detail": "Agent must test representative buyer questions against evidence.", "urls": []},
        {"stage": "corroboration", "status": "not_checked", "detail": "Requires entity comparison and independent source review.", "urls": []},
        {"stage": "engagement", "status": "not_checked", "detail": "Agent must trace task journeys and inspect browser behavior.", "urls": []}]
    return {"schema_version": "1.2", "site": evidence["site"], "audited_at": evidence["collected_at"],
            "executive_summary": {"conclusion": f"Static baseline: {len(pages)} HTML pages inspected; {len(findings)} scoped technical observations for review. The full agent audit must assess buyer questions, trust and visitor journeys. AI visibility has not been measured.",
                                  "top_action_ids": [f["id"] for f in findings[:3]]},
            "summary": summary, "coverage": {"pages_checked": len(pages), "modes": ["static"], "not_checked": limitations},
            "assessment": {"mode": "static_baseline", "readiness": readiness, "intent_tests": [], "journeys": [],
                           "visibility": {"status": "not_measured", "detail": "No recorded assistant answer runs; crawl checks are not citation measurements.", "cohorts": []}},
            "findings": findings, "proactive_opportunities": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url"); parser.add_argument("--output-dir", default="audit-output")
    parser.add_argument("--max-pages", type=int, default=12); parser.add_argument("--max-seconds", type=int, default=120)
    parser.add_argument("--resume-evidence", help="Reuse the landing-page capture from this invocation")
    parser.add_argument("--target-url", action="append", default=[], help="Observed task destination to prioritize (repeatable)")
    args = parser.parse_args()
    try:
        previous = json.loads(Path(args.resume_evidence).read_text(encoding="utf-8")) if args.resume_evidence else None
        evidence = collect(args.url, args.max_pages, args.max_seconds, resume=previous, target_urls=args.target_url)
    except (ValueError, OSError) as error: parser.error(str(error))
    destination = Path(args.output_dir); destination.mkdir(parents=True, exist_ok=True)
    for name, value in (("evidence.json", evidence), ("report.json", baseline(evidence))):
        (destination / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "static_baseline", "report": str(destination / "report.json"), "evidence": str(destination / "evidence.json")}, indent=2))


if __name__ == "__main__": main()
