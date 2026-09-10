#!/usr/bin/env python3
"""Exercise no-clobber finalization, timing boundaries and exact-byte receipts."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/audit-orchestrator/scripts"))
import finalize_report as finalizer


class FinalizeReportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="finalize audit ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.paths = [self.root / name for name in ("draft.json", "evidence.json", "review.json")]
        for path in self.paths:
            path.write_bytes(b'{ "sample": "unchanged bytes" }\n')
        self.output = self.root / "results" / "final-report.json"
        self.receipt = self.output.with_name(self.output.name + ".receipt.json")
        self.start = datetime(2026, 9, 10, 10, tzinfo=timezone.utc)
        self.stamp = self.start.isoformat()

    def run_gate(self, seconds=12, **kwargs):
        clock = kwargs.pop("clock", lambda: self.start + timedelta(seconds=seconds))
        return finalizer.finalize(*self.paths, self.output, kwargs.pop("started_at", self.stamp), clock=clock, **kwargs)

    def write_composed_fixture(self):
        url = "https://club.test/"
        answers = [("What is offered?", "coding", "The club teaches coding."),
                   ("Who may join?", "students", "Students may join."),
                   ("How can I contact the club?", "email", "Contact club@example.test.")]
        evidence = {"site": url, "pages": [{"url": url, "final_url": url, "status": 200,
                    "parse_status": "parsed_html", "response_truncated": False,
                    "evidence_truncated": False, "main_text": " ".join(item[2] for item in answers)}]}
        report = {"schema_version": "1.2", "site": url, "audited_at": self.stamp,
                  "executive_summary": {"conclusion": "Three visitor questions are answered in the sampled page. Browser journeys remain untested.", "top_action_ids": []},
                  "summary": {"total_findings": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
                  "coverage": {"pages_checked": 1, "modes": ["static"], "not_checked": ["Browser and off-site tools unavailable."]},
                  "findings": [], "proactive_opportunities": [],
                  "assessment": {"mode": "agent_composed", "readiness": [
                      {"stage": stage, "status": "observed" if stage in {"extraction", "answerability"} else "not_checked",
                       "detail": "Page facts inspected; no browser or external inspection.", "urls": [url] if stage in {"extraction", "answerability"} else []}
                      for stage in ("access", "extraction", "answerability", "corroboration", "engagement")],
                      "intent_tests": [{"question": question, "required_elements": [required], "status": "answered",
                                        "evidence": [{"url": url, "quote": quote}], "reason": "The page explicitly supplies this fact."}
                                       for question, required, quote in answers],
                      "journeys": [{"task": task, "starting_context": "Visitor on the homepage.", "steps": [],
                                    "status": "not_checked", "reason": "Browser unavailable."}
                                   for task in ("Find joining details", "Find the contact route")],
                      "visibility": {"status": "not_measured", "detail": "No actual assistant runs.", "cohorts": []}}}
        review = {"review_version": "1", "observations": [], "claims": {}, "journeys": [], "corroboration": [],
                  "answers": [{"test_index": index, "evidence_index": 0, "ref": "page:0", "field": "main_text"}
                              for index in range(len(answers))]}
        for path, value in zip(self.paths, (report, evidence, review)):
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return report, evidence, review

    @patch.object(finalizer, "_validate", return_value=[])
    def test_validated_report_retains_exact_bytes_and_hashes(self, validator):
        result = self.run_gate(seconds=299.999999)
        self.assertEqual(self.output.read_bytes(), self.paths[0].read_bytes())
        self.assertEqual(json.loads(self.receipt.read_text()), result)
        self.assertEqual(result["elapsed_seconds"], 299.999999)
        for name, path in zip(("report", "evidence", "review"), self.paths):
            self.assertEqual(result["sha256"][name], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertIn("not semantic truth", " ".join(result["limits"]))
        self.assertIn("host delivery", " ".join(result["limits"]))
        validator.assert_called_once()
        self.assertEqual(list(self.output.parent.glob("*.tmp")), [])

    @patch.object(finalizer, "_validate", return_value=[])
    def test_300_second_boundary_rejected_before_and_after_validation(self, validator):
        for times in ((300, 300), (1, 300), (1, 301), (1, 299, 300), (1, 299, 299, 300), (1, 299, 299, 299, 300)):
            with self.subTest(times=times):
                values = iter(self.start + timedelta(seconds=value) for value in times)
                with self.assertRaisesRegex(finalizer.FinalizationError, "deadline"):
                    self.run_gate(clock=lambda: next(values))
                self.assertFalse(self.output.exists())
                self.assertFalse(self.receipt.exists())
                self.assertEqual(self.paths[0].read_bytes(), b'{ "sample": "unchanged bytes" }\n')

    def test_future_naive_and_non_utc_starts_are_rejected(self):
        for stamp in ("2026-09-10T10:01:00Z", "2026-09-10T10:00:00", "2026-09-10T15:30:00+05:30", "2026-09-10"):
            with self.subTest(stamp=stamp), self.assertRaises(finalizer.FinalizationError):
                self.run_gate(started_at=stamp, seconds=0)
        self.assertFalse(self.output.exists())

    def test_naive_clock_rejected(self):
        with self.assertRaisesRegex(finalizer.FinalizationError, "clock"):
            self.run_gate(clock=lambda: datetime(2026, 9, 10, 10))

    @patch.object(finalizer, "_validate", return_value=["unsupported absence"])
    def test_validation_failure_preserves_inputs_without_success_files(self, validator):
        original = [path.read_bytes() for path in self.paths]
        with self.assertRaisesRegex(finalizer.FinalizationError, "unsupported absence"):
            self.run_gate()
        self.assertEqual([path.read_bytes() for path in self.paths], original)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())

    def test_malformed_and_non_object_json_rejected(self):
        for value in (b"{broken", b"[]", b"null", b"\xff", b'{"x":NaN}', b'{"x":Infinity}'):
            with self.subTest(value=value):
                self.paths[1].write_bytes(value)
                with self.assertRaisesRegex(finalizer.FinalizationError, "evidence"):
                    self.run_gate()
                self.assertFalse(self.output.exists())

    @patch.object(finalizer, "_validate", return_value=[])
    def test_existing_output_or_receipt_is_never_overwritten(self, validator):
        self.output.parent.mkdir()
        for occupied in (self.output, self.receipt):
            with self.subTest(occupied=occupied):
                occupied.write_bytes(b"old success")
                with self.assertRaisesRegex(finalizer.FinalizationError, "existing"):
                    self.run_gate()
                self.assertEqual(occupied.read_bytes(), b"old success")
                occupied.unlink()
        self.assertFalse(self.output.exists())
        validator.assert_not_called()

    @patch.object(finalizer, "_validate", return_value=[])
    def test_broken_output_symlink_is_not_followed(self, validator):
        self.output.parent.mkdir()
        self.output.symlink_to(self.root / "missing.json")
        with self.assertRaisesRegex(finalizer.FinalizationError, "existing"):
            self.run_gate()
        self.assertTrue(self.output.is_symlink())
        self.assertFalse((self.root / "missing.json").exists())

    @patch.object(finalizer, "_validate", return_value=[])
    def test_concurrent_receipt_creation_rolls_back_only_own_report(self, validator):
        real_link = os.link
        def competing_link(source, destination):
            if destination == self.receipt:
                self.receipt.write_bytes(b"other invocation")
            return real_link(source, destination)
        with patch.object(finalizer.os, "link", side_effect=competing_link):
            with self.assertRaises(FileExistsError):
                self.run_gate()
        self.assertFalse(self.output.exists())
        self.assertEqual(self.receipt.read_bytes(), b"other invocation")
        self.assertEqual(list(self.output.parent.glob("*.tmp")), [])

    def test_real_schema_validation_rejects_incomplete_report(self):
        with self.assertRaisesRegex(finalizer.FinalizationError, "report schema"):
            self.run_gate()
        self.assertFalse(self.output.exists())

    def test_schema_valid_static_baseline_cannot_finalize(self):
        report, _, _ = self.write_composed_fixture()
        report["assessment"]["mode"] = "static_baseline"
        self.paths[0].write_text(json.dumps(report), encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationError, "requires assessment.mode=agent_composed"):
            self.run_gate()
        self.assertFalse(self.output.exists())

    def test_real_evidence_failure_prevents_publication(self):
        _, _, review = self.write_composed_fixture()
        review["answers"][0]["ref"] = "page:99"
        self.paths[2].write_text(json.dumps(review), encoding="utf-8")
        with self.assertRaisesRegex(finalizer.FinalizationError, "evidence review"):
            self.run_gate()
        self.assertFalse(self.output.exists())
        self.assertFalse(self.receipt.exists())

    def test_input_aliases_cannot_be_output(self):
        original = [path.read_bytes() for path in self.paths]
        for path in self.paths:
            with self.subTest(path=path), self.assertRaises(finalizer.FinalizationError):
                finalizer.finalize(*self.paths, path, self.stamp, clock=lambda: self.start)
        self.assertEqual([path.read_bytes() for path in self.paths], original)

    def test_relocated_cli_loads_bundled_validators_from_unrelated_cwd(self):
        self.write_composed_fixture()
        relocated = self.root / "extracted package"
        script = relocated / "skills/audit-orchestrator/scripts/finalize_report.py"
        script.parent.mkdir(parents=True)
        shutil.copy2(Path(finalizer.__file__), script)
        tests = relocated / "tests"
        tests.mkdir()
        shutil.copy2(ROOT / "tests/validate_report.py", tests / "validate_report.py")
        shutil.copy2(ROOT / "tests/report_evidence.py", tests / "report_evidence.py")
        refs = relocated / "skills/audit-orchestrator/references"
        refs.mkdir()
        shutil.copy2(ROOT / "skills/audit-orchestrator/references/report-schema.json", refs / "report-schema.json")
        result = subprocess.run([sys.executable, "-B", str(script), "--report", str(self.paths[0]),
                                 "--evidence", str(self.paths[1]), "--review", str(self.paths[2]),
                                 "--output", str(self.output), "--started-at", datetime.now(timezone.utc).isoformat()],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["finalized"])
        self.assertEqual(self.output.read_bytes(), self.paths[0].read_bytes())
        receipt = json.loads(self.receipt.read_text())
        self.assertEqual(receipt["sha256"]["report"], hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_cli_deadline_error_is_structured_stderr_and_keeps_draft(self):
        original = self.paths[0].read_bytes()
        result = subprocess.run([sys.executable, "-B", finalizer.__file__, "--report", str(self.paths[0]),
                                 "--evidence", str(self.paths[1]), "--review", str(self.paths[2]),
                                 "--output", str(self.output), "--started-at", "2000-01-01T00:00:00Z"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertFalse(json.loads(result.stderr)["finalized"])
        self.assertEqual(self.paths[0].read_bytes(), original)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
