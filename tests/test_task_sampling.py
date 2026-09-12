"""Task-led resumption must reuse captures and preserve network boundaries."""
import copy
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/audit-orchestrator/scripts'))
from collect_site import collect


class TaskSamplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hits = []
        class Site(BaseHTTPRequestHandler):
            def do_GET(self):
                cls.hits.append(self.path)
                if self.path == '/robots.txt':
                    body, kind = 'User-agent: *\nAllow: /\nDisallow: /private\n', 'text/plain'
                elif self.path == '/sitemap.xml':
                    body, kind = '<urlset><url><loc>/pricing</loc></url></urlset>', 'application/xml'
                elif self.path == '/start':
                    body, kind = """<main><h1>Regional training centre</h1>
                    <a href='/pricing'>Store plans</a><a href='/team'>Our team</a>
                    <a href='/r/73?lang=ta'>சேர்க்கை / eligibility</a>
                    <a href='/r/84'>Application instructions</a><a href='/private'>Private staff area</a>
                    <a href='/fee.pdf'>Fee document</a><a href='http://elsewhere.invalid/info'>Partner</a>
                    <a href=''>Apply</a><a>Placeholder</a></main>""", 'text/html'
                else:
                    body, kind = '<main><h1>Information</h1><p>Source content.</p></main>', 'text/html'
                self.send_response(200); self.send_header('Content-Type', kind)
                self.end_headers(); self.wfile.write(body.encode())
            def log_message(self, *_): pass
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Site)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def landing(self):
        return collect(self.origin + '/start', max_pages=1, max_seconds=15)

    def test_selected_opaque_destinations_precede_inventory_without_refetch(self):
        self.hits.clear()
        first = self.landing(); before = copy.deepcopy(first)
        result = collect(self.origin + '/start', 3, 15, resume=first,
                         target_urls=[self.origin + '/r/73?lang=ta', self.origin + '/r/84'])
        self.assertEqual(first, before)
        self.assertEqual([p['url'] for p in result['pages']],
                         [self.origin + '/start', self.origin + '/r/73?lang=ta', self.origin + '/r/84'])
        self.assertEqual(self.hits.count('/start'), 1)
        self.assertEqual(self.hits.count('/robots.txt'), 2)
        self.assertNotIn('/sitemap.xml', self.hits)
        self.assertEqual(result['collected_at'], first['collected_at'])
        self.assertEqual(len(result['collection_passes']), 2)
        self.assertEqual(result['coverage']['request_count'], len(self.hits))
        self.assertEqual(result['limits']['max_pages'], 3)
        self.assertEqual(result['limits']['max_seconds'], 30)

    def test_task_target_still_obeys_robots(self):
        first = self.landing(); self.hits.clear()
        result = collect(self.origin + '/start', 2, 15, resume=first, target_urls=[self.origin + '/private'])
        self.assertNotIn('/private', self.hits)
        self.assertFalse(result['pages'][1]['robots_allowed'])

    def test_invalid_resume_or_target_fails_before_network(self):
        first = self.landing(); self.hits.clear()
        for target in ['/invented', '/fee.pdf', 'http://elsewhere.invalid/info']:
            with self.subTest(target=target), self.assertRaises(ValueError):
                collect(self.origin + '/start', 3, 15, resume=first, target_urls=[target])
        stale = copy.deepcopy(first)
        stale['collected_at'] = (datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat()
        for previous in [stale, {**first, 'site': self.origin + '/another'}]:
            with self.assertRaises(ValueError): collect(self.origin + '/start', 3, 15, resume=previous)
        malformed = copy.deepcopy(first); malformed['pages'][0]['links'] = ['bad']
        with self.assertRaises(ValueError): collect(self.origin + '/start', 3, 15, resume=malformed)
        with self.assertRaises(ValueError): collect(self.origin + '/start', 3, 15, target_urls=['/r/84'])
        self.assertEqual(self.hits, [])

    def test_cli_reads_resume_before_replacing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            cmd = [sys.executable, str(ROOT / 'skills/audit-orchestrator/scripts/run_audit.py'),
                   self.origin + '/start', '--output-dir', folder, '--max-seconds', '15']
            subprocess.run(cmd + ['--max-pages', '1'], check=True, capture_output=True)
            subprocess.run(cmd + ['--max-pages', '2', '--resume-evidence', str(Path(folder) / 'evidence.json'),
                                  '--target-url', self.origin + '/r/84'], check=True, capture_output=True)
            evidence = json.loads((Path(folder) / 'evidence.json').read_text())
            self.assertEqual(len(evidence['pages']), 2)
            self.assertTrue(evidence['pages'][1]['url'].endswith('/r/84'))


if __name__ == '__main__': unittest.main()
