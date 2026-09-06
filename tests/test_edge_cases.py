#!/usr/bin/env python3
"""Exercise malformed public content, partial responses and coverage claims."""
import copy
import gzip
import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/audit-orchestrator/scripts'))
from collect_site import collect, normalize
from page_evidence import page_fields
from run_audit import baseline
from validate_report import validate


class EdgeCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.broken_robots = False

        class Site(BaseHTTPRequestHandler):
            def log_message(self, *args): pass

            def do_GET(self):
                body = b''
                if self.path == '/robots.txt':
                    body = b'User-agent: *\nAllow: /\n'
                    if cls.broken_robots:
                        body = gzip.compress(body)[:10]
                        self.send_response(200)
                        self.send_header('Content-Encoding', 'gzip')
                        self.end_headers()
                        self.wfile.write(body)
                        return
                elif self.path == '/start':
                    body = b'<base href="/catalog/"><p>Available products</p><a href="item">Item</a><a href="http://[broken">Bad URL</a><a href="/about">About</a>'
                elif self.path == '/catalog/item':
                    body = b'<p>Item costs 42.</p>'
                elif self.path == '/about':
                    body = b'<p>About the company.</p>'
                elif self.path == '/broken-response':
                    self.send_response(200)
                    self.send_header('Transfer-Encoding', 'chunked')
                    self.end_headers()
                    self.wfile.write(b'NOT-A-CHUNK\r\n')
                    return
                else:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain' if self.path == '/robots.txt' else 'text/html')
                self.end_headers()
                self.wfile.write(body)

        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Site)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_valueless_html_attributes_do_not_crash_extraction(self):
        for markup in ['<p style>Open daily.</p>', '<meta name><p>Open daily.</p>',
                       '<script type>ignored</script><p>Open daily.</p>',
                       '<link rel><p>Open daily.</p>']:
            with self.subTest(markup=markup):
                self.assertIn('Open daily.', page_fields(markup)[1]['main_text'])

    def test_bad_navigation_url_does_not_discard_a_page(self):
        result = collect(self.origin + '/start', max_pages=4, max_seconds=15)
        pages = {p['url']: p for p in result['pages']}
        self.assertIn(self.origin + '/start', pages)
        self.assertIn(self.origin + '/catalog/item', pages)
        self.assertIn(self.origin + '/about', pages)
        item = next(link for link in pages[self.origin + '/start']['links'] if link['href'] == 'item')
        self.assertEqual(item['url'], self.origin + '/catalog/item')
        self.assertEqual(validate(baseline(result)), [])

    def test_invalid_urls_are_skipped_and_path_parameters_preserved(self):
        self.assertIsNone(normalize('https://example.test/', 'http://[broken', 'example.test'))
        self.assertEqual(normalize('https://example.test/', '/offer;region=eu?utm_source=test', 'example.test'),
                         'https://example.test/offer;region=eu')

    def test_broken_gzip_robots_preserves_unknown_policy(self):
        self.__class__.broken_robots = True
        try:
            result = collect(self.origin + '/start', max_pages=1)
        finally:
            self.__class__.broken_robots = False
        self.assertIsNone(result['robots']['collector_allowed'])
        self.assertTrue(result['robots']['read_error'])
        self.assertEqual(result['pages'], [])
        self.assertEqual(validate(baseline(result)), [])

    def test_broken_chunked_response_becomes_collection_error(self):
        result = collect(self.origin + '/broken-response', max_pages=1)
        self.assertTrue(any(e['url'].endswith('/broken-response') for e in result['errors']))
        self.assertEqual(baseline(result)['findings'], [])

    def test_composed_report_requires_question_and_journey_records(self):
        original = json.loads((ROOT / 'tests/fixtures/valid-report.json').read_text())
        for field in ['intent_tests', 'journeys']:
            report = copy.deepcopy(original)
            report['assessment']['mode'] = 'agent_composed'
            report['assessment'][field] = []
            self.assertTrue(validate(report), field)
        limited = copy.deepcopy(original)
        for question in limited['assessment']['intent_tests']:
            question.update(status='not_checked', evidence=[])
        for journey in limited['assessment']['journeys']:
            journey.update(status='not_checked', steps=[])
        self.assertEqual(validate(limited), [])

    def test_visibility_run_cannot_be_counted_in_multiple_cohorts(self):
        report = json.loads((ROOT / 'tests/fixtures/valid-report.json').read_text())
        cohort = {'provider': 'test', 'surface': 'web', 'model': 'model', 'locale': 'en',
                  'prompt_kind': 'unbranded', 'valid_runs': 1, 'failed_runs': 0, 'not_run': 0,
                  'distinct_prompts': 1, 'mentioned_runs': 0, 'cited_runs': 0,
                  'mention_rate': 0, 'citation_rate': 0, 'run_ids': ['R1']}
        report['assessment']['visibility'].update(status='measured_sample', cohorts=[cohort])
        self.assertEqual(validate(report), [])
        report['assessment']['visibility']['cohorts'].append({**cohort, 'surface': 'api'})
        self.assertTrue(validate(report))
        report['assessment']['visibility']['cohorts'][1] = {**cohort, 'run_ids': ['R2']}
        self.assertTrue(validate(report))


if __name__ == '__main__': unittest.main()
