#!/usr/bin/env python3
"""Dependency-free validation of the bundled schema subset and report semantics.

This is deliberately not advertised as a general JSON Schema implementation.
"""
import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "skills/audit-orchestrator/references/report-schema.json"


def validate_shape(value, schema, path="$", errors=None):
    errors = [] if errors is None else errors
    kinds = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
             "string": lambda x: isinstance(x, str), "integer": lambda x: type(x) is int,
             "number": lambda x: type(x) in {int, float}, "null": lambda x: x is None,
             "boolean": lambda x: type(x) is bool}
    expected = schema.get("type")
    if expected and not any(kinds[k](value) for k in (expected if isinstance(expected, list) else [expected])):
        errors.append(f"{path}: expected {expected}"); return errors
    if "const" in schema and value != schema["const"]: errors.append(f"{path}: invalid constant")
    if "enum" in schema and value not in schema["enum"]: errors.append(f"{path}: invalid value")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append(f"{path}.{key}: required")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys(): errors.append(f"{path}.{key}: unexpected field")
        for key, child in value.items():
            if key in properties: validate_shape(child, properties[key], f"{path}.{key}", errors)
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")): errors.append(f"{path}: invalid array length")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value): errors.append(f"{path}: duplicate values")
        for index, child in enumerate(value): validate_shape(child, schema.get("items", {}), f"{path}[{index}]", errors)
    elif isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0): errors.append(f"{path}: empty/short string")
        if "pattern" in schema and not re.search(schema["pattern"], value): errors.append(f"{path}: invalid pattern")
        if schema.get("format") == "uri":
            try:
                parsed = urlparse(value)
                if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username: errors.append(f"{path}: invalid HTTP(S) URL")
            except ValueError: errors.append(f"{path}: invalid URL")
        if schema.get("format") == "date-time":
            try:
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if stamp.utcoffset() != timedelta(0): errors.append(f"{path}: UTC timestamp required")
            except ValueError: errors.append(f"{path}: invalid timestamp")
    elif type(value) in {int, float}:
        if not schema.get("minimum", -float("inf")) <= value <= schema.get("maximum", float("inf")): errors.append(f"{path}: number out of range")
    return errors


def validate(doc):
    errors = validate_shape(doc, json.loads(SCHEMA.read_text(encoding="utf-8")))
    if errors: return errors
    findings, opportunities = doc["findings"], doc["proactive_opportunities"]
    for prefix, items in (("F", findings), ("O", opportunities)):
        if [x["id"] for x in items] != [f"{prefix}-{i:03d}" for i in range(1, len(items) + 1)]: errors.append(f"{prefix}: IDs must be sequential")
    ids = {x["id"] for x in findings + opportunities}
    if any(x not in ids for x in doc["executive_summary"]["top_action_ids"]): errors.append("unknown top action")
    if doc["summary"]["total_findings"] != len(findings): errors.append("total count mismatch")
    for severity in ("critical", "high", "medium", "low"):
        if doc["summary"][severity] != sum(f["severity"] == severity for f in findings): errors.append(f"{severity} count mismatch")
    for f in findings:
        if f["evidence"]["affected"] > f["evidence"]["checked"]: errors.append(f"{f['id']}: affected exceeds checked")
    assessment = doc["assessment"]
    if assessment["mode"] == "agent_composed":
        if not 3 <= len(assessment["intent_tests"]) <= 5: errors.append("composed audit needs 3-5 question records, including not_checked outcomes")
        if len(assessment["journeys"]) != 2: errors.append("composed audit needs two journey records, including not_checked outcomes")
    stages = [r["stage"] for r in assessment["readiness"]]
    if sorted(stages) != sorted(["access", "extraction", "answerability", "corroboration", "engagement"]): errors.append("readiness must cover each of five stages exactly once")
    stage_status = {r["stage"]: r["status"] for r in assessment["readiness"]}
    if stage_status.get("answerability") == "observed" and not any(t["status"] != "not_checked" for t in assessment["intent_tests"]):
        errors.append("observed answerability requires at least one assessed question; all questions are not_checked")
    if stage_status.get("engagement") == "observed" and not any(j["steps"] for j in assessment["journeys"]):
        errors.append("observed engagement requires recorded journey steps; empty journeys are not observed")
    for test in assessment["intent_tests"]:
        if test["status"] != "not_checked" and not test["evidence"]: errors.append("question outcome needs evidence")
        if not test["required_elements"]: errors.append("question needs required answer elements")
    for journey in assessment["journeys"]:
        if journey["status"] != "not_checked" and not journey["steps"]: errors.append("journey outcome needs observed steps")
    visibility = assessment["visibility"]
    measured = any(c["valid_runs"] for c in visibility["cohorts"])
    if (visibility["status"] == "measured_sample") != measured: errors.append("visibility status disagrees with successful recorded runs")
    cohort_keys, run_ids = set(), set()
    for c in visibility["cohorts"]:
        key = tuple(c[field] for field in ("provider", "surface", "model", "locale", "prompt_kind"))
        if key in cohort_keys: errors.append("duplicate visibility cohort")
        cohort_keys.add(key)
        if run_ids.intersection(c["run_ids"]): errors.append("visibility run belongs to multiple cohorts")
        run_ids.update(c["run_ids"])
        n = c["valid_runs"]
        if n and not c["distinct_prompts"]: errors.append("successful visibility runs need a prompt")
        if c["distinct_prompts"] > n or c["mentioned_runs"] > n or c["cited_runs"] > n: errors.append("visibility numerator exceeds denominator")
        if len(c["run_ids"]) != n + c["failed_runs"] + c["not_run"] or len(set(c["run_ids"])) != len(c["run_ids"]): errors.append("visibility run IDs/counts disagree")
        for rate, numerator in (("mention_rate", "mentioned_runs"), ("citation_rate", "cited_runs")):
            expected = c[numerator] / n if n else None
            if c[rate] != expected: errors.append(f"visibility {rate} does not match recorded counts")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report")
    parser.add_argument("--evidence", help="Saved collector JSON; requires --review")
    parser.add_argument("--review", help="Evidence review sidecar JSON; requires --evidence")
    args = parser.parse_args()
    scope = "schema_and_report_consistency"
    errors = []
    if bool(args.evidence) != bool(args.review):
        errors.append("--evidence and --review are required together for evidence verification")
    else:
        try:
            doc = json.loads(Path(args.report).read_text(encoding="utf-8"))
            errors = validate(doc)
            if args.evidence and not errors:
                from report_evidence import validate_evidence
                scope = "schema_and_evidence_consistency"
                errors.extend(validate_evidence(doc,
                    json.loads(Path(args.evidence).read_text(encoding="utf-8")),
                    json.loads(Path(args.review).read_text(encoding="utf-8"))))
        except (ValueError, OSError) as error:
            errors = [str(error)]
    print(json.dumps({"valid": not errors, "scope": scope, "errors": errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__": main()
