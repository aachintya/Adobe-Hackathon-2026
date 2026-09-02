#!/usr/bin/env python3
"""Score a composed report for evidence coverage and prohibited overclaims."""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tests" / "validate_report.py"
DEFAULT_EXPECTATIONS = ROOT / "tests" / "fixtures" / "problem-expectations.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("expectations", nargs="?", default=str(DEFAULT_EXPECTATIONS))
    args = ap.parse_args()
    report_path, expectations_path = Path(args.report), Path(args.expectations)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    expected = json.loads(expectations_path.read_text(encoding="utf-8"))
    checks, failures = [], []

    validation = subprocess.run([sys.executable, str(VALIDATOR), str(report_path)], capture_output=True, text=True)
    contract_ok = validation.returncode == 0
    checks.append({"name": "report contract", "passed": contract_ok, "weight": 30})
    if not contract_ok: failures.append("Report contract failed: " + validation.stdout.strip())

    findings = report.get("findings", [])
    for concept in expected.get("expected_concepts", []):
        matched = False
        for finding in findings:
            haystack = (finding.get("title", "") + " " + finding.get("evidence", {}).get("observation", "")).lower()
            if finding.get("category") == concept["category"] and any(term.lower() in haystack for term in concept["terms"]):
                matched = True; break
        checks.append({"name": concept["name"], "passed": matched, "weight": 10})
        if not matched: failures.append("Missing expected concept: " + concept["name"])

    not_checked_text = " ".join(report.get("coverage", {}).get("not_checked", [])).lower()
    for term in expected.get("required_not_checked_terms", []):
        matched = term.lower() in not_checked_text
        checks.append({"name": "not_checked: " + term, "passed": matched, "weight": 5})
        if not matched: failures.append("Missing not_checked disclosure: " + term)

    serialized = json.dumps(report, ensure_ascii=False).lower()
    no_overclaims = not any(claim.lower() in serialized for claim in expected.get("forbidden_claims", []))
    checks.append({"name": "no prohibited overclaims", "passed": no_overclaims, "weight": 15})
    if not no_overclaims: failures.append("Report contains a prohibited outcome or conformance claim")

    executive = report.get("executive_summary", {})
    executive_ok = bool(executive.get("conclusion")) and 0 < len(executive.get("top_action_ids", [])) <= 3
    checks.append({"name": "non-expert executive summary", "passed": executive_ok, "weight": 10})
    if not executive_ok: failures.append("Executive conclusion or top actions are missing")

    opportunities = report.get("proactive_opportunities", [])
    opportunity_ok = len(opportunities) >= expected.get("minimum_opportunities", 0)
    checks.append({"name": "evidence-linked proactive opportunity", "passed": opportunity_ok, "weight": 10})
    if not opportunity_ok: failures.append("Required proactive opportunity is missing")

    both_halves = {item.get("category") for item in findings} >= {"discoverability", "engagement"}
    checks.append({"name": "both Adobe problem halves", "passed": both_halves, "weight": 10})
    if not both_halves: failures.append("Report does not cover both discoverability and engagement findings")

    available = sum(item["weight"] for item in checks)
    earned = sum(item["weight"] for item in checks if item["passed"])
    score = round(100 * earned / available) if available else 0
    passed = contract_ok and score >= expected.get("minimum_score", 100)
    print(json.dumps({"passed": passed, "score": score, "checks": checks, "failures": failures}, indent=2))
    raise SystemExit(not passed)

if __name__ == "__main__": main()
