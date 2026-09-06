#!/usr/bin/env python3
"""Build the actual ZIP, extract to a path with spaces and run from an unrelated cwd."""
import json
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


def main():
    subprocess.run([sys.executable, str(ROOT/'scripts/package_submission.py')], check=True, capture_output=True)
    archive = ROOT/'dist/brand-ai-readiness-audit.zip'
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT/'tests/fixtures/good')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory(prefix='audit zip test ') as directory:
            temp = Path(directory)
            with ZipFile(archive) as package: package.extractall(temp/'extracted marketplace')
            root = temp/'extracted marketplace/brand-ai-readiness-audit'
            output = temp/'audit output'
            subprocess.run([sys.executable, str(root/'skills/audit-orchestrator/scripts/run_audit.py'), f'http://127.0.0.1:{server.server_port}/', '--output-dir', str(output), '--max-pages', '3'], cwd=temp, check=True, capture_output=True)
            subprocess.run([sys.executable, str(root/'tests/validate_report.py'), str(output/'report.json')], cwd=temp, check=True, capture_output=True)
            report = json.loads((output/'report.json').read_text())
            assert report['coverage']['pages_checked'] == 3
            assert report['findings'] == []
            assert report['assessment']['mode'] == 'static_baseline'
            assert report['assessment']['visibility']['status'] == 'not_measured'
            assert (root/'scripts/package_submission.py').is_file()
            assert not list(root.rglob('*.zip'))
        print('PASS: extracted ZIP runs with no install/API key from a different cwd and preserves honest coverage')
    finally: server.shutdown()


if __name__ == '__main__': main()
