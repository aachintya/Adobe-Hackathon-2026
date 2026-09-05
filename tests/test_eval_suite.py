#!/usr/bin/env python3
"""Validate that forward evaluations cover the Adobe rubric's risky dimensions."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    suite=json.loads((ROOT/"evals/evals.json").read_text(encoding="utf-8")); cases=suite.get("evals",[])
    assert suite.get("skill_name")=="audit-orchestrator" and len(cases)>=12
    assert [case.get("id") for case in cases]==list(range(1,len(cases)+1))
    assert all(case.get("prompt") and case.get("private_setup") and case.get("expected_output") and len(case.get("assertions",[]))>=3 for case in cases)
    text=json.dumps(cases).lower()
    required={"rendered","entity ambiguity","path-preserving","sitemap","multilingual","images and pdfs","healthy","five-minute","training","answerability","denominators","university"}
    missing=sorted(term for term in required if term not in text)
    assert not missing,missing
    print(json.dumps({"result":"PASS","forward_cases":len(cases),"dimensions":sorted(required)},indent=2))

if __name__=="__main__": main()
