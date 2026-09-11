"""Focused tests for the offline exact-quote locality experiment."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/audit-orchestrator/scripts/probe_answer_locality.py"
sys.path.insert(0, str(SCRIPT.parent))
import probe_answer_locality as probe_module


def evidence(text, **overrides):
    page = {
        "url": "https://example.test/",
        "final_url": "https://example.test/",
        "status": 200,
        "parse_status": "parsed_html",
        "main_text": text,
        "response_truncated": False,
        "evidence_truncated": False,
    }
    page.update(overrides)
    return {"site": "https://example.test/", "pages": [page]}


def cases(*elements, ref="page:0", ident="case"):
    return {"cases": [{"id": ident, "ref": ref, "elements": list(elements)}]}


class AnswerLocalityTests(unittest.TestCase):
    def test_shortest_span_uses_duplicate_occurrences(self):
        text = "answer filler qualifier answer near qualifier"
        result = probe_module.probe(
            evidence(text),
            cases({"label": "answer", "quote": "answer"}, {"label": "qualifier", "quote": "qualifier"}),
            budgets=(2, 4),
        )["cases"][0]
        self.assertEqual(result["status"], "measured")
        self.assertEqual(result["minimum_span_words"], 2)
        self.assertEqual(result["excerpt"], "qualifier answer")

    def test_split_and_colocated_qualifiers_respect_budget_and_phase_boundaries(self):
        text = "answer qualifier one two three four five six seven eight nine ten answer qualifier"
        result = probe_module.probe(
            evidence(text),
            cases({"label": "answer", "quote": "answer"}, {"label": "qualifier", "quote": "qualifier"}),
            budgets=(2, 4),
        )["cases"][0]
        self.assertEqual(result["minimum_span_words"], 2)
        by_budget = {window["budget_words"]: window for window in result["windows"]}
        self.assertTrue(by_budget[2]["fits_contiguous_window"])
        self.assertFalse(all(phase["all_elements_together"] for phase in by_budget[2]["phases"]))
        self.assertTrue(by_budget[4]["fits_contiguous_window"])

    def test_quote_mismatch_is_distinct_from_missing_page(self):
        result = probe_module.probe(
            evidence("answer is present"),
            cases({"label": "answer", "quote": "answer"}, {"label": "qualifier", "quote": "absent"}),
        )["cases"][0]
        self.assertEqual(result["status"], "quote_not_found")
        self.assertEqual(result["unmatched_elements"], ["qualifier"])
        missing = probe_module.probe(
            {"pages": []},
            cases({"label": "answer", "quote": "answer"}, {"label": "qualifier", "quote": "qualifier"}),
        )["cases"][0]
        self.assertEqual(missing["status"], "not_checked")

    def test_punctuation_and_whitespace_normalization_are_exact(self):
        result = probe_module.probe(
            evidence("PostgreSQL,\n is reliable."),
            cases({"label": "name", "quote": "PostgreSQL,"}, {"label": "fact", "quote": "is reliable."}),
        )["cases"][0]
        self.assertEqual(result["status"], "measured")
        self.assertEqual(result["minimum_span_words"], 3)

    def test_failed_captures_are_untested_and_truncated_matches_are_scoped(self):
        elements = ({"label": "a", "quote": "answer"}, {"label": "b", "quote": "qualifier"})
        for overrides in ({"status": 500}, {"parse_status": "fetch_error"}, {"main_text": "", "status": 200}, {"response_truncated": True}):
            with self.subTest(overrides=overrides):
                result = probe_module.probe(evidence("answer qualifier", **overrides), cases(*elements))["cases"][0]
                if overrides.get("response_truncated"):
                    self.assertEqual(result["status"], "measured")
                    self.assertFalse(result["capture_complete"])
                else:
                    self.assertEqual(result["status"], "not_checked")
        result = probe_module.probe(evidence("answer qualifier", evidence_truncated=True), cases(*elements))["cases"][0]
        self.assertEqual(result["status"], "measured")
        self.assertFalse(result["capture_complete"])

    def test_unicode_quotes_and_hash_preserve_original_source(self):
        text = "réponse qualité café."
        result = probe_module.probe(
            evidence(text),
            cases({"label": "answer", "quote": "réponse"}, {"label": "qualifier", "quote": "qualité"}),
        )["cases"][0]
        self.assertEqual(result["status"], "measured")
        self.assertEqual(result["excerpt"], "réponse qualité")
        self.assertTrue(result["source_text_sha256"])

    def test_cli_writes_safe_output_and_does_not_mutate_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path, cases_path, output_path = (root / name for name in ("evidence.json", "cases.json", "out.json"))
            evidence_path.write_text(json.dumps(evidence("answer qualifier"), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            cases_path.write_text(json.dumps(cases({"label": "answer", "quote": "answer"}, {"label": "qualifier", "quote": "qualifier"}), indent=2) + "\n", encoding="utf-8")
            before = (evidence_path.read_bytes(), cases_path.read_bytes())
            completed = subprocess.run([sys.executable, str(SCRIPT), str(evidence_path), str(cases_path), "--words", "2", "--output", str(output_path)], capture_output=True, text=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual((evidence_path.read_bytes(), cases_path.read_bytes()), before)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["input_sha256"]["evidence"], __import__("hashlib").sha256(before[0]).hexdigest())
            self.assertEqual(payload["cases"][0]["status"], "measured")
            for collision in (evidence_path, cases_path, output_path):
                original = collision.read_bytes()
                result = subprocess.run([sys.executable, str(SCRIPT), str(evidence_path), str(cases_path), "--output", str(collision)], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(collision.read_bytes(), original)

    def test_budget_changes_do_not_change_measured_separation(self):
        data = evidence("Price is $12. " + "background " * 100 + "Annual billing required.")
        selected = cases({"label": "price", "quote": "Price is $12."}, {"label": "condition", "quote": "Annual billing required."})
        short = probe_module.probe(data, selected, budgets=(80,))["cases"][0]
        long = probe_module.probe(data, selected, budgets=(160,))["cases"][0]
        self.assertEqual(short["minimum_span_words"], 106)
        self.assertEqual(short["minimum_span_words"], long["minimum_span_words"])
        self.assertFalse(short["windows"][0]["fits_contiguous_window"])
        self.assertTrue(long["windows"][0]["fits_contiguous_window"])


if __name__ == "__main__":
    unittest.main()
