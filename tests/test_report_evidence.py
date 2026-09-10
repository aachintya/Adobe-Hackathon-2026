#!/usr/bin/env python3
"""Offline regressions for false evidence claims and healthy scoped reviews."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from report_evidence import validate_evidence
from validate_report import validate


ROOT = Path(__file__).resolve().parents[1]


def fixture():
    report = json.loads((ROOT / "tests/fixtures/valid-report.json").read_text(encoding="utf-8"))
    report["assessment"]["journeys"][0]["steps"][0]["action"] = "[source] Inspect opening copy and next-step link"
    pages = []
    for url, title, text, robots in (("https://example.test/", "Example", "Welcome to Example.", "noindex"),
                                    ("https://example.test/offer.html", "Experience it", "Experience it Better. Faster. Different.", "")):
        pages.append({"url": url, "final_url": url, "status": 200, "parse_status": "parsed_html",
                      "response_truncated": False, "evidence_truncated": False, "main_text": text,
                      "h1": [title], "description": "A captured description", "meta_robots": robots,
                      "base_href": None, "links": [{"href": "/", "text": "Click here"}]})
    evidence = {"site": report["site"], "pages": pages, "sitemaps": [], "errors": []}
    quote = {"type": "quote", "ref": "page:1", "field": "main_text", "quote": "Better. Faster. Different."}
    review = {"review_version": "1", "observations": [], "claims": {
        "F-001": {"assertions": [{"type": "field_equals", "ref": "page:0", "field": "meta_robots", "value": "noindex"}],
                  "checked_refs": ["page:0", "page:1"], "affected_refs": ["page:0"]},
        "F-002": {"assertions": [copy.deepcopy(quote)], "checked_refs": ["page:0", "page:1"], "affected_refs": ["page:1"]},
        "O-001": {"assertions": [copy.deepcopy(quote)]}},
        "answers": [{"test_index": index, "evidence_index": 0, "ref": "page:1", "field": field}
                    for index, field in enumerate(("main_text", "links.0.text", "h1.0"))],
        "journeys": [{"journey_index": 0, "mode": "source", "steps": [
            {"step_index": 0, "ref": "page:1", "assertions": [copy.deepcopy(quote)]}]}],
        "corroboration": []}
    return report, evidence, review


def host(ref="host:page", url="https://example.test/offer.html", mode="static", kind="page", status=200):
    return {"id": ref, "url": url, "final_url": url, "mode": mode, "kind": kind,
            "status": status, "complete": False, "text": "Captured useful passage.",
            "provenance": {"tool": "test public fetch", "reference": "saved:test-observation",
                           "observed_at": "2026-09-10T00:00:00Z"}}


class EvidenceReviewTests(unittest.TestCase):
    def setUp(self):
        self.report, self.evidence, self.review = fixture()

    def errors(self):
        return validate_evidence(self.report, self.evidence, self.review)

    def assertRejected(self, message):
        errors = self.errors()
        self.assertTrue(any(message in error for error in errors), errors)

    def test_healthy_composed_report_and_qualitative_quote(self):
        self.assertEqual(validate(self.report), [])
        self.assertEqual(self.errors(), [])

    def test_every_finding_and_opportunity_requires_support(self):
        for ident in ("F-001", "O-001"):
            with self.subTest(ident=ident):
                self.review["claims"][ident]["assertions"] = []
                self.assertRejected("nonempty typed assertions")
                self.setUp()
        self.review["claims"].pop("O-001")
        self.assertRejected("every finding and opportunity")

    def test_missing_metadata_opportunity_rejects_captured_description(self):
        self.review["claims"]["O-001"]["assertions"] = [{"type": "field_absent", "ref": "page:0", "field": "description"}]
        self.assertRejected("missing-field claim contradicts a present field")

    def test_absence_requires_captured_field_and_complete_success(self):
        assertion = {"type": "field_absent", "ref": "page:0", "field": "description"}
        self.review["claims"]["O-001"]["assertions"] = [assertion]
        self.evidence["pages"][0]["description"] = ""
        self.assertEqual(self.errors(), [])
        for key, value in (("response_truncated", True), ("evidence_truncated", True), ("status", 500)):
            original = self.evidence["pages"][0][key]
            with self.subTest(key=key):
                self.evidence["pages"][0][key] = value
                self.assertRejected("absence requires complete successful evidence")
            self.evidence["pages"][0][key] = original
        del self.evidence["pages"][0]["description"]
        self.assertRejected("field was not captured; unknown is not absence")

    def test_host_empty_field_cannot_override_collector_counterevidence(self):
        observation = host(url="https://example.test/")
        observation.update(complete=True, fields={"description": ""})
        self.review["observations"].append(observation)
        self.review["claims"]["O-001"]["assertions"] = [{"type": "field_absent", "ref": "host:page", "field": "description"}]
        self.assertRejected("another observation of this URL contains")

    def test_field_equality_distinguishes_boolean_from_integer(self):
        self.evidence["pages"][0]["robots_allowed"] = True
        self.review["claims"]["F-001"]["assertions"] = [{"type": "field_equals", "ref": "page:0", "field": "robots_allowed", "value": 1}]
        self.assertRejected("field value contradicts")

    def test_cross_page_quote_cannot_support_affected_page(self):
        self.review["claims"]["F-001"]["assertions"] = copy.deepcopy(self.review["claims"]["F-002"]["assertions"])
        self.assertRejected("every affected page needs its own supporting assertion")

    def test_missing_refs_and_unobserved_structured_report_urls_rejected(self):
        self.review["claims"]["O-001"]["assertions"][0]["ref"] = "page:99"
        self.assertRejected("unknown evidence ref")
        self.report["assessment"]["readiness"][0]["urls"] = ["https://example.test/uninspected"]
        self.assertRejected("unobserved report URL")

    def test_collector_must_belong_to_report_site(self):
        self.evidence["site"] = "https://other.example/"
        self.assertRejected("collector site does not match")

    def test_page_count_excludes_external_resources_failures_and_duplicate_modes(self):
        self.review["observations"].extend([host(mode="rendered"),
            host("host:external", "https://institution.example/club", "off_site", "external"),
            host("host:failed", "https://example.test/failed", status=500),
            host("host:resource", "https://example.test/file.txt", kind="resource")])
        self.report["coverage"]["modes"] = ["static", "rendered", "off_site"]
        self.assertEqual(self.errors(), [])
        self.report["coverage"]["pages_checked"] = 3
        self.assertRejected("2 unique inspected first-party pages")

    def test_new_inspected_page_must_be_counted(self):
        self.review["observations"].append(host(url="https://example.test/team"))
        self.assertRejected("3 unique inspected first-party pages")
        self.report["coverage"]["pages_checked"] = 3
        self.assertEqual(self.errors(), [])

    def test_first_party_count_honors_observed_landing_redirect_only(self):
        landing = host("host:landing", self.report["site"])
        landing["final_url"] = "https://www.example.test/"
        self.review["observations"].extend([landing,
            host("host:www-team", "https://www.example.test/team"),
            host("host:other-host", "https://other.example.test/team")])
        self.report["coverage"]["pages_checked"] = 4
        self.assertEqual(self.errors(), [])
        self.review["observations"].remove(landing)
        self.report["coverage"]["pages_checked"] = 2
        self.assertEqual(self.errors(), [])

    def test_quotes_allow_whitespace_but_never_paraphrases_or_wrong_urls(self):
        self.report["assessment"]["intent_tests"][0]["evidence"][0]["quote"] = "Better.\n Faster.   Different."
        self.assertEqual(self.errors(), [])
        self.report["assessment"]["intent_tests"][0]["evidence"][0]["quote"] = "Better and different"
        self.assertRejected("verbatim excerpt")
        self.report["assessment"]["intent_tests"][1]["evidence"][0]["url"] = "https://example.test/"
        self.assertRejected("quote provenance URL mismatch")

    def test_missing_answer_cannot_be_inferred_from_truncated_reading(self):
        self.evidence["pages"][1]["evidence_truncated"] = True
        self.assertRejected("missing_in_sample cannot follow from incomplete evidence")

    def broken_link(self):
        source = self.evidence["pages"][1]
        source.update(final_url="https://example.test/about/", links=[{"href": "team", "text": "Team"}])
        destination = host("host:destination", "https://example.test/about/team", kind="resource", status=404)
        self.review["observations"].append(destination)
        self.review["claims"]["F-002"]["assertions"] = [
            {"type": "broken_link", "ref": "page:1", "href": "team", "destination_ref": "host:destination"}]
        # The fixture's independent answer about the old link needs updating.
        self.report["assessment"]["intent_tests"][1]["evidence"][0]["quote"] = "Team"
        return source, destination

    def test_broken_link_uses_observed_redirect_final_url_and_literal_href(self):
        source, destination = self.broken_link()
        self.assertEqual(self.errors(), [])
        destination.update(url="https://example.test/team", final_url="https://example.test/team")
        self.assertRejected("resolved destination needs an observed HTTP 404 or 410")
        destination.update(url="https://example.test/base/team", final_url="https://example.test/base/team")
        source.update(base_href="/base/", link_base_url="https://example.test/base/")
        self.assertEqual(self.errors(), [])
        self.review["claims"]["F-002"]["assertions"][0]["href"] = "invented"
        self.assertRejected("literal href was not captured")

    def test_broken_link_requires_http_failure_not_restriction_or_tool_error(self):
        source, destination = self.broken_link()
        for status in (200, 403, 429, 500, None):
            with self.subTest(status=status):
                destination["status"] = status
                self.assertRejected("resolved destination needs an observed HTTP 404 or 410")
        destination["status"] = 410
        self.assertEqual(self.errors(), [])
        source.pop("base_href")
        self.assertRejected("captured base_href")

    def test_collector_error_can_prove_destination_http_404(self):
        _, destination = self.broken_link()
        self.evidence["errors"].append({"url": destination["url"], "status": 404, "error": "HTTPError"})
        self.review["observations"] = []
        self.review["claims"]["F-002"]["assertions"][0]["destination_ref"] = "error:0"
        self.assertEqual(self.errors(), [])

    def test_unknown_status_host_text_supports_external_quotes_but_not_absence(self):
        observation = host("host:institution", "https://institution.example/club", "off_site", "external", None)
        self.review["observations"].append(observation)
        self.report["coverage"]["modes"].append("off_site")
        self.report["assessment"]["readiness"][3].update(status="observed", urls=[observation["url"]])
        self.review["corroboration"] = [{"ref": observation["id"], "field": "text", "quote": observation["text"]}]
        self.assertEqual(self.errors(), [])
        observation.update(complete=True, fields={"description": ""})
        self.review["claims"]["O-001"]["assertions"] = [{"type": "field_absent", "ref": observation["id"], "field": "description"}]
        self.assertRejected("absence requires complete successful evidence")
        observation["status"] = 403
        self.assertRejected("verbatim excerpt from readable captured evidence")

    def test_unknown_status_rendered_observation_supports_a_labeled_journey(self):
        observation = host(mode="rendered", status=None)
        self.review["observations"].append(observation)
        self.report["coverage"]["modes"].append("rendered")
        self.report["assessment"]["journeys"][0]["steps"][0]["action"] = "[rendered] Read the opened page"
        self.review["journeys"][0].update(mode="rendered", steps=[{"step_index": 0, "ref": observation["id"],
            "assertions": [{"type": "quote", "ref": observation["id"], "field": "text", "quote": observation["text"]}]}])
        self.assertEqual(self.errors(), [])
        observation.update(url="https://example.test/extra", final_url="https://example.test/extra")
        self.assertRejected("3 unique inspected first-party pages")

    def test_source_check_cannot_be_reported_as_rendered_interaction(self):
        self.review["journeys"][0]["mode"] = "rendered"
        self.report["assessment"]["journeys"][0]["steps"][0]["action"] = "[rendered] Click the link"
        self.assertRejected("interaction mode contradicts observed evidence")
        self.setUp()
        self.report["assessment"]["journeys"][0]["steps"][0]["action"] = "Click the link"
        self.assertRejected("report action must label its [source] reading mode")

    def test_corroboration_needs_actual_external_sources_and_provenance(self):
        self.report["assessment"]["readiness"][3]["status"] = "observed"
        self.assertRejected("observed corroboration needs captured external source support")
        observation = host("host:institution", "https://institution.example/club", "off_site", "external")
        self.review["observations"].append(observation)
        self.review["corroboration"] = [{"ref": observation["id"], "field": "text", "quote": observation["text"]}]
        self.assertRejected("must cite its actual external source URL")
        self.report["assessment"]["readiness"][3]["urls"] = [observation["url"]]
        self.assertEqual(self.errors(), [])
        observation["provenance"].pop("reference")
        self.assertRejected("tool-output reference")

    def test_malformed_input_fails_closed(self):
        for review in (None, {}, {**self.review, "observations": [None]}, {**self.review, "claims": []}):
            with self.subTest(review=review):
                self.assertTrue(validate_evidence(self.report, self.evidence, review))

    def test_cli_reports_validation_scope_and_requires_both_evidence_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / f"{name}.json" for name in ("report", "evidence", "review")]
            for path, value in zip(paths, (self.report, self.evidence, self.review)):
                path.write_text(json.dumps(value), encoding="utf-8")
            base = [sys.executable, "-B", str(ROOT / "tests/validate_report.py"), str(paths[0])]
            def run(extra):
                result = subprocess.run(base + extra, capture_output=True, text=True, cwd=directory)
                return result.returncode, json.loads(result.stdout)
            code, result = run([])
            self.assertEqual(code, 0)
            self.assertEqual(result["scope"], "schema_and_report_consistency")
            code, result = run(["--evidence", str(paths[1])])
            self.assertEqual(code, 1)
            self.assertIn("required together", result["errors"][0])
            code, result = run(["--evidence", str(paths[1]), "--review", str(paths[2])])
            self.assertEqual(code, 0, result)
            self.assertEqual(result["scope"], "schema_and_evidence_consistency")


if __name__ == "__main__":
    unittest.main()
