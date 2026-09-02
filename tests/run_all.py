#!/usr/bin/env python3
"""Run the Adobe submission's deterministic validation suite."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, str(ROOT / "tests" / "test_skill_structure.py")],
    [sys.executable, str(ROOT / "tests" / "run_simulations.py")],
    [sys.executable, str(ROOT / "tests" / "test_robots_scenarios.py")],
    [sys.executable, str(ROOT / "tests" / "test_collector_generalization.py")],
    [sys.executable, str(ROOT / "tests" / "test_eval_suite.py")],
    [sys.executable, str(ROOT / "tests" / "validate_report.py"), str(ROOT / "tests" / "fixtures" / "valid-report.json")],
    [sys.executable, str(ROOT / "tests" / "test_validator_failures.py")],
    [sys.executable, str(ROOT / "tests" / "evaluate_report_quality.py"), str(ROOT / "examples" / "problem-site-report.json")]
]

def main():
    for command in COMMANDS: subprocess.run(command, check=True)
    print("ALL VALIDATION CHECKS PASSED")

if __name__ == "__main__": main()
