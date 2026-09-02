#!/usr/bin/env python3
"""Ensure semantic contract violations are rejected."""
import copy, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tests" / "validate_report.py"
VALID = json.loads((ROOT / "tests" / "fixtures" / "valid-report.json").read_text(encoding="utf-8"))

def rejected(mutator):
    doc = copy.deepcopy(VALID); mutator(doc)
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(doc, handle); path = Path(handle.name)
    try:
        return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True).returncode != 0
    finally:
        path.unlink(missing_ok=True)

def main():
    cases = {
        "affected exceeds checked": lambda d: d["findings"][0]["evidence"].update(affected=3, checked=2),
        "invalid timestamp": lambda d: d.update(audited_at="yesterday"),
        "missing action owner": lambda d: d["findings"][0]["suggested_action"].pop("owner_hint"),
        "unsupported mode": lambda d: d["coverage"]["modes"].append("visual_guess"),
        "unknown top action": lambda d: d["executive_summary"]["top_action_ids"].append("F-999"),
        "unstructured opportunity": lambda d: d.update(proactive_opportunities=["Add more content"])
    }
    failed = [name for name, mutate in cases.items() if not rejected(mutate)]
    print(json.dumps({"result": "PASS" if not failed else "FAIL", "rejected": len(cases) - len(failed), "failed": failed}, indent=2))
    raise SystemExit(bool(failed))

if __name__ == "__main__": main()
