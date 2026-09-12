#!/usr/bin/env python3
"""Fail-closed quality scoring from private, explicit adjudications."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime
from pathlib import Path
from typing import Any

VERDICTS = {"correct", "partial", "false", "duplicate", "unsubstantiated"}
DIMENSIONS = ("scope", "evidence", "severity", "action_correctness", "action_mechanism", "action_specificity", "action_verification")

def report_sha256(source: str | Path | bytes) -> str:
    return hashlib.sha256(source if isinstance(source, bytes) else Path(source).read_bytes()).hexdigest()

def _entry_map(value: Any) -> dict[str, dict]:
    if isinstance(value, list):
        return {str(x.get("item_id", x.get("report_id", x.get("finding_id", "")))): x for x in value if isinstance(x, dict)}
    if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
        return {str(k): dict(v, item_id=str(v.get("item_id", k))) for k, v in value.items()}
    return {}

def _mean(values: list[int]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None

def _blank_quality() -> dict:
    return {"finding_precision": None, "root_recall": None, "root_recall_full": None, "root_recall_partial": None, "high_or_critical_recall": None, "false_findings": None, "duplicate_findings": None, "scope_agreement": None, "evidence_fidelity": None, "severity_agreement": None, "actions": {d: None for d in DIMENSIONS[3:]}, "answer_requirement_support": None}

def evaluate_report(report: dict, expected: dict, adjudication: dict, *, report_path: str | Path | None = None, report_bytes: bytes | None = None) -> dict:
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"complete": False, "incomplete_run": True, "validation_errors": ["report is not an object"], "quality": _blank_quality(), "runtime": {"completion": 0}}
    findings = [x for x in report.get("findings", []) if isinstance(x, dict)]; opportunities = [x for x in report.get("proactive_opportunities", []) if isinstance(x, dict)]
    finding_ids = [str(x.get("id")) for x in findings if x.get("id") is not None]; item_ids = finding_ids + [str(x.get("id")) for x in opportunities if x.get("id") is not None]
    if len(item_ids) != len(set(item_ids)): errors.append("duplicate report item IDs")
    for field in ("findings", "proactive_opportunities"):
        value = report.get(field, [])
        if not isinstance(value, list) or any(not isinstance(x, dict) or not isinstance(x.get("id"), str) or not x["id"] for x in value):
            errors.append(f"{field} must contain objects with nonempty IDs")
    roots = expected.get("expected_roots", [])
    if not isinstance(roots, list) or not all(isinstance(x, dict) and x.get("id") is not None for x in roots): errors.append("expected_roots must be a list of objects with IDs"); roots = []
    root_ids = {str(x["id"]) for x in roots}
    if len(root_ids) != len(roots): errors.append("duplicate expected root IDs")
    raw_ads = adjudication.get("adjudications")
    ads = _entry_map(raw_ads)
    if not isinstance(raw_ads, (dict, list)) or len(ads) != len(raw_ads): errors.append("malformed or duplicate adjudication entries")
    for x in sorted(set(item_ids) - set(ads)): errors.append(f"unreviewed report item: {x}")
    for x in sorted(set(ads) - set(item_ids)): errors.append(f"unknown report item in adjudication: {x}")
    if report_path is None and report_bytes is None: errors.append("report_path or report_bytes required for SHA256 verification")
    if report_path is not None or report_bytes is not None:
        raw = report_bytes if report_bytes is not None else Path(report_path).read_bytes()
        if adjudication.get("report_sha256") != report_sha256(raw): errors.append("adjudication report SHA256 mismatch")
        try:
            if json.loads(raw) != report: errors.append("report object differs from the hash-bound bytes")
        except (ValueError, UnicodeDecodeError): errors.append("hash-bound report bytes are not valid JSON")
    reviewed: dict[str, dict] = {}
    for iid, a in ads.items():
        verdict = a.get("verdict"); rid = a.get("root_id")
        if verdict not in VERDICTS: errors.append(f"invalid verdict for {iid}"); continue
        if iid in finding_ids and verdict in {"correct", "partial", "duplicate"} and str(rid) not in root_ids: errors.append(f"{verdict} item {iid} requires known root_id")
        if rid is not None and str(rid) not in root_ids: errors.append(f"unknown root ID for {iid}")
        reviewed[iid] = a
        if iid in finding_ids:
            required_dimensions = DIMENSIONS
        else:
            required_dimensions = ("evidence", "action_correctness", "action_mechanism", "action_specificity", "action_verification")
        if iid in item_ids:
            for d in required_dimensions:
                v = a.get(d)
                if isinstance(v, bool) or not isinstance(v, int) or v not in (0, 1, 2): errors.append(f"invalid or missing {d} for {iid}: expected integer 0, 1, or 2")
    for rid in root_ids:
        group = [a for iid, a in reviewed.items() if iid in finding_ids and str(a.get("root_id")) == rid]
        if sum(a.get("verdict") in {"correct", "partial"} for a in group) > 1: errors.append(f"multiple accepted findings assigned to root {rid}; mark duplicates")
        if any(a.get("verdict") == "duplicate" for a in group) and not any(a.get("verdict") in {"correct", "partial"} for a in group): errors.append(f"duplicate root assignment without accepted finding: {rid}")
    support = adjudication.get("answer_support", {}); support_values: list[int] = []
    tests = report.get("assessment", {}).get("intent_tests", []) if isinstance(report.get("assessment"), dict) else []
    if not isinstance(support, dict): errors.append("answer_support must be an object")
    elif set(support) - {str(i) for i in range(len(tests))}: errors.append("unknown question in answer_support")
    for qi, q in enumerate(tests):
        entry = support.get(str(qi), support.get(qi, {})) if isinstance(support, dict) else {}; required = q.get("required_elements", []) if isinstance(q, dict) else []
        if not isinstance(entry, dict): errors.append(f"invalid answer_support for question {qi}"); continue
        if set(entry) - set(required): errors.append(f"unknown answer element for question {qi}")
        for element in required:
            v = entry.get(element)
            if isinstance(v, bool) or not isinstance(v, int) or v not in (0, 1, 2): errors.append(f"invalid or missing answer support question {qi}: {element}")
            else: support_values.append(v)
    runtime = adjudication.get("runtime"); runtime_out = {"completion": 0, "duration_seconds": None, "timestamp_kind": None}
    if not isinstance(runtime, dict): errors.append("runtime adjudication required")
    else:
        completion = runtime.get("completion"); runtime_out["completion"] = 1 if completion == "completed" else 0; runtime_out["timestamp_kind"] = runtime.get("timestamp_kind")
        if completion not in {"completed", "failed", "interrupted"}: errors.append("invalid runtime completion")
        if runtime.get("timestamp_kind") not in {"exact_delivery", "observed_completion_upper_bound", "not_measured"}: errors.append("invalid timestamp_kind")
        if runtime.get("timestamp_kind") == "not_measured":
            if not isinstance(runtime.get("reason"), str) or not runtime["reason"].strip():
                errors.append("unmeasured runtime needs an explicit reason")
            runtime_out["reason"] = runtime.get("reason")
        else:
            try:
                start = datetime.fromisoformat(str(runtime["observer_start"]).replace("Z", "+00:00")); end = datetime.fromisoformat(str(runtime["delivery"]).replace("Z", "+00:00"))
                if start.tzinfo is None or end.tzinfo is None: raise ValueError
                runtime_out["duration_seconds"] = (end - start).total_seconds()
                if runtime_out["duration_seconds"] < 0: errors.append("runtime delivery precedes observer_start")
            except (KeyError, TypeError, ValueError): errors.append("runtime observer_start and delivery must be timezone-aware timestamps")
    if errors: return {"complete": False, "incomplete_run": True, "validation_errors": errors, "quality": _blank_quality(), "runtime": runtime_out}
    accepted = [i for i in finding_ids if reviewed[i]["verdict"] in {"correct", "partial"}]; full = {str(reviewed[i]["root_id"]) for i in accepted if reviewed[i]["verdict"] == "correct"}; partial = {str(reviewed[i]["root_id"]) for i in accepted}; highcrit = {str(x["id"]) for x in roots if str(x.get("severity", "")).lower() in {"high", "critical"}}
    q = {"finding_precision": round(sum(1 if reviewed[i]["verdict"] == "correct" else .5 for i in accepted) / len(finding_ids), 4) if finding_ids else None, "root_recall": round((len(full) + .5 * len(partial-full)) / len(root_ids), 4) if root_ids else None, "root_recall_full": len(full)/len(root_ids) if root_ids else None, "root_recall_partial": len(partial)/len(root_ids) if root_ids else None, "high_or_critical_recall": (len(full & highcrit) + .5 * len((partial-full) & highcrit))/len(highcrit) if highcrit else None, "false_findings": sum(reviewed[i]["verdict"] in {"false", "unsubstantiated"} for i in finding_ids), "duplicate_findings": sum(reviewed[i]["verdict"] == "duplicate" for i in finding_ids), "scope_agreement": _mean([reviewed[i]["scope"] for i in finding_ids]), "evidence_fidelity": _mean([reviewed[i]["evidence"] for i in item_ids]), "severity_agreement": _mean([reviewed[i]["severity"] for i in finding_ids]), "actions": {d: _mean([reviewed[i][d] for i in item_ids]) for d in DIMENSIONS[3:]}, "answer_requirement_support": _mean(support_values)}
    if expected.get("ground_truth_complete", True) is not True:
        for key in ("root_recall", "root_recall_full", "root_recall_partial", "high_or_critical_recall"):
            q[key] = None
    return {"complete": True, "validation_errors": [], "quality": q, "runtime": runtime_out}

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("reports", nargs="+"); ap.add_argument("--expected", required=True); ap.add_argument("--adjudications", required=True); args = ap.parse_args(argv)
    expected = json.loads(Path(args.expected).read_text()); mapping = json.loads(Path(args.adjudications).read_text()); out = []
    for name in args.reports:
        try:
            raw = Path(name).read_bytes(); report = json.loads(raw); ad = mapping.get(name, mapping.get(Path(name).name, mapping)) if isinstance(mapping, dict) else {}; result = evaluate_report(report, expected, ad, report_bytes=raw)
        except Exception as exc: result = {"complete": False, "incomplete_run": True, "validation_errors": [f"report could not be loaded: {exc}"], "quality": _blank_quality(), "runtime": {"completion": 0}}
        out.append({"report": name, **result})
    print(json.dumps(out[0] if len(out) == 1 else {"reports": out}, indent=2, sort_keys=True)); return 0 if all(x["complete"] for x in out) else 2
if __name__ == "__main__": raise SystemExit(main())
