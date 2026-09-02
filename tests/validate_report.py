#!/usr/bin/env python3
"""Dependency-free contract checks for an emitted report JSON."""
import argparse, json
from datetime import datetime
from urllib.parse import urlparse

SEV = {"critical", "high", "medium", "low"}
CONF = {"high", "medium"}
CATEGORY = {"discoverability", "engagement"}
PRIORITY = {"high", "medium", "low"}
EFFORT = {"low", "medium", "high"}
MODES = {"static", "rendered", "off_site", "retrieval"}
ROOT_FIELDS = {"schema_version", "site", "audited_at", "executive_summary", "summary", "coverage", "findings", "proactive_opportunities"}

def is_http_url(value):
    if not isinstance(value, str): return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

def is_nonempty(value): return isinstance(value, str) and bool(value.strip())
def is_count(value, minimum=0): return isinstance(value, int) and not isinstance(value, bool) and value >= minimum

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("report"); args = ap.parse_args()
    with open(args.report, encoding="utf-8") as handle: doc = json.load(handle)
    errors = []
    missing, extra = ROOT_FIELDS - set(doc), set(doc) - ROOT_FIELDS
    errors.extend(f"missing root field: {key}" for key in sorted(missing))
    errors.extend(f"unexpected root field: {key}" for key in sorted(extra))
    if doc.get("schema_version") != "1.1": errors.append("schema_version must be 1.1")
    if not is_http_url(doc.get("site")): errors.append("site must be an HTTP(S) URL")
    try:
        stamp = doc.get("audited_at", "").replace("Z", "+00:00"); parsed_stamp = datetime.fromisoformat(stamp)
        if parsed_stamp.tzinfo is None: errors.append("audited_at must include a timezone")
    except (AttributeError, ValueError): errors.append("audited_at must be ISO-8601")

    executive = doc.get("executive_summary", {})
    if not isinstance(executive, dict) or set(executive) != {"conclusion", "top_action_ids"}:
        errors.append("executive_summary fields do not match the contract"); executive = {}
    if not is_nonempty(executive.get("conclusion")): errors.append("executive_summary.conclusion is empty")
    top_actions = executive.get("top_action_ids")
    if not isinstance(top_actions, list) or len(top_actions) > 3 or len(top_actions) != len(set(top_actions or [])):
        errors.append("executive_summary.top_action_ids must contain at most three unique IDs")

    summary = doc.get("summary", {})
    summary_fields = {"total_findings", *SEV}
    if not isinstance(summary, dict): errors.append("summary must be an object"); summary = {}
    if set(summary) != summary_fields: errors.append("summary fields do not match the contract")
    for key in summary_fields:
        if not is_count(summary.get(key)): errors.append(f"summary.{key} must be a non-negative integer")

    coverage = doc.get("coverage", {})
    if not isinstance(coverage, dict) or set(coverage) != {"pages_checked", "modes", "not_checked"}:
        errors.append("coverage fields do not match the contract"); coverage = {}
    if not is_count(coverage.get("pages_checked")): errors.append("coverage.pages_checked must be a non-negative integer")
    modes = coverage.get("modes")
    if not isinstance(modes, list) or len(modes) != len(set(modes)) or any(mode not in MODES for mode in modes): errors.append("coverage.modes contains invalid or duplicate modes")
    not_checked = coverage.get("not_checked")
    if not isinstance(not_checked, list) or any(not is_nonempty(item) for item in not_checked): errors.append("coverage.not_checked must be a list of non-empty reasons")

    findings = doc.get("findings", [])
    if not isinstance(findings, list): errors.append("findings must be an array"); findings = []
    ids = []
    for index, finding in enumerate(findings, 1):
        prefix = f"finding {index}"
        if not isinstance(finding, dict): errors.append(f"{prefix} must be an object"); continue
        required = {"id", "title", "category", "severity", "confidence", "evidence", "suggested_action"}
        if set(finding) != required: errors.append(f"{prefix} fields do not match the contract")
        ids.append(finding.get("id"))
        if not is_nonempty(finding.get("title")): errors.append(f"{prefix} title is empty")
        if finding.get("category") not in CATEGORY: errors.append(f"{prefix} invalid category")
        if finding.get("severity") not in SEV: errors.append(f"{prefix} invalid severity")
        if finding.get("confidence") not in CONF: errors.append(f"{prefix} invalid confidence")

        evidence = finding.get("evidence", {})
        evidence_fields = {"observation", "affected", "checked", "urls"}
        if not isinstance(evidence, dict) or set(evidence) != evidence_fields: errors.append(f"{prefix} evidence fields do not match the contract"); evidence = {}
        if not is_nonempty(evidence.get("observation")): errors.append(f"{prefix} evidence observation is empty")
        affected, checked = evidence.get("affected"), evidence.get("checked")
        if not is_count(affected, 1) or not is_count(checked, 1): errors.append(f"{prefix} evidence counts must be positive integers")
        elif affected > checked: errors.append(f"{prefix} affected cannot exceed checked")
        urls = evidence.get("urls")
        if not isinstance(urls, list) or not urls or len(urls) != len(set(urls)) or any(not is_http_url(url) for url in urls): errors.append(f"{prefix} evidence URLs must be unique HTTP(S) URLs")

        action = finding.get("suggested_action", {})
        action_fields = {"summary", "priority", "effort", "owner_hint", "mechanism", "verification"}
        if not isinstance(action, dict) or set(action) != action_fields: errors.append(f"{prefix} action fields do not match the contract"); action = {}
        for key in ("summary", "owner_hint", "mechanism", "verification"):
            if not is_nonempty(action.get(key)): errors.append(f"{prefix} action {key} is empty")
        if action.get("priority") not in PRIORITY: errors.append(f"{prefix} invalid action priority")
        if action.get("effort") not in EFFORT: errors.append(f"{prefix} invalid action effort")

    expected_ids = [f"F-{index:03d}" for index in range(1, len(findings) + 1)]
    if ids != expected_ids: errors.append("finding IDs are not stable sequential IDs")
    counts = {severity: sum(item.get("severity") == severity for item in findings if isinstance(item, dict)) for severity in SEV}
    if summary.get("total_findings") != len(findings) or any(summary.get(severity) != count for severity, count in counts.items()): errors.append("summary counts do not match findings")
    opportunities = doc.get("proactive_opportunities")
    opportunity_ids = []
    if not isinstance(opportunities, list) or len(opportunities) > 3:
        errors.append("proactive_opportunities must contain at most three objects"); opportunities = []
    opportunity_fields = {"id", "title", "rationale", "priority", "effort", "owner_hint", "mechanism", "verification"}
    for index, opportunity in enumerate(opportunities, 1):
        prefix = f"opportunity {index}"
        if not isinstance(opportunity, dict) or set(opportunity) != opportunity_fields:
            errors.append(f"{prefix} fields do not match the contract"); continue
        opportunity_ids.append(opportunity.get("id"))
        for key in ("title", "rationale", "owner_hint", "mechanism", "verification"):
            if not is_nonempty(opportunity.get(key)): errors.append(f"{prefix} {key} is empty")
        if opportunity.get("priority") not in PRIORITY: errors.append(f"{prefix} invalid priority")
        if opportunity.get("effort") not in EFFORT: errors.append(f"{prefix} invalid effort")
    if opportunity_ids != [f"O-{index:03d}" for index in range(1, len(opportunity_ids) + 1)]: errors.append("opportunity IDs are not stable sequential IDs")
    valid_action_ids = set(ids) | set(opportunity_ids)
    if isinstance(top_actions, list) and any(action_id not in valid_action_ids for action_id in top_actions): errors.append("executive_summary.top_action_ids contains an unknown finding or opportunity ID")
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2)); raise SystemExit(bool(errors))

if __name__ == "__main__": main()
