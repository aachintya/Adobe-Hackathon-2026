#!/usr/bin/env python3
"""Build the actual ZIP, extract to a path with spaces and run from an unrelated cwd."""
import json
import hashlib
import re
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone

from test_report_evidence import fixture as composed_fixture

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
            assert {p.name for p in root.iterdir()} == {
                'marketplace.json', 'README.md', 'LICENSE', 'skills', 'examples', 'tests'}
            assert {p.name for p in (root/'tests').iterdir() if p.is_file()} == {
                'validate_report.py', 'report_evidence.py'}
            assert not list(root.rglob('*.zip'))
            # Exercise the composed-report path from the actual cleaned archive;
            # a collector-only smoke test would miss removed finalizer dependencies.
            composed, evidence, review = composed_fixture()
            inputs = [temp/name for name in ('draft.json', 'evidence.json', 'review.json')]
            for path, value in zip(inputs, (composed, evidence, review)):
                path.write_text(json.dumps(value), encoding='utf-8')
            final = temp/'final-report.json'
            command = [sys.executable, str(root/'skills/audit-orchestrator/scripts/finalize_report.py'),
                       '--report', str(inputs[0]), '--evidence', str(inputs[1]), '--review', str(inputs[2]),
                       '--started-at', datetime.now(timezone.utc).isoformat()]
            subprocess.run(command + ['--output', str(final)], cwd=temp, check=True, capture_output=True)
            receipt = json.loads(final.with_name(final.name + '.receipt.json').read_text())
            assert final.read_bytes() == inputs[0].read_bytes()
            assert receipt['sha256']['report'] == hashlib.sha256(final.read_bytes()).hexdigest()
            review['claims']['F-001']['assertions'][0]['value'] = 'index'
            inputs[2].write_text(json.dumps(review), encoding='utf-8')
            rejected = temp/'rejected-report.json'
            result = subprocess.run(command + ['--output', str(rejected)], cwd=temp, capture_output=True)
            assert result.returncode != 0 and not rejected.exists()
            for document in root.rglob('*.md'):
                for target in re.findall(r'\[[^]]+\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                    target = target.strip('<>')
                    if '://' in target or target.startswith('#'):
                        continue
                    destination = target.split('#', 1)[0]
                    assert (document.parent/destination).exists(), f'Broken packaged link in {document.relative_to(root)}: {target}'
        print('PASS: clean ZIP excludes development files; collection and evidence-gated finalization run from a different cwd')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__': main()
