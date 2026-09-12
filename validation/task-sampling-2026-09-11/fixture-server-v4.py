#!/usr/bin/env python3
"""Deterministic local public sites; private expectations are never served."""
import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

CASES = {f'c{i:02d}-{v}': {'kind': i, 'defect': v == ('a' if i in (3, 4, 5, 6) else 'b')}
         for i in range(1, 7) for v in ('a', 'b')}
NAMES = {1: 'Northwind Field Supplies', 2: 'Harbor Metrics', 3: 'Mosaic Learning',
         4: 'Cedar Trail Outfitters', 5: 'Juniper Studio', 6: 'Saffron Civic Archive'}

def render(case, path, query):
    info = CASES[case]; kind, bad = info['kind'], info['defect']; prefix = '/' + case + '/'
    def link(target, label): return f'<a href="{html.escape(prefix + target, quote=True)}">{html.escape(label)}</a>'
    body, status, noindex = '', 200, False
    if path == 'index.html':
        body = '<h1>' + NAMES[kind] + '</h1>'
        if kind == 1:
            body += '<p>On-site equipment inspection for small workshops. A single visit costs 240 credits, excluding local tax. Annual plans include two visits for 400 credits, excluding local tax.</p>'
            body += link('terms.html', 'Prices, taxes and cancellation') + link('contact.html', 'Arrange a visit')
        elif kind == 2:
            body += '<p>Harbor Metrics is open-source monitoring software. Administrators should review the current security bulletin and update affected installations.</p>'
            body += link('r/72.html', 'Security bulletin: affected and fixed releases') + link('install.html', 'Installation instructions')
        elif kind == 3:
            body += '<p>Autumn evening language courses for adult learners at 12 Orchard Lane, Exampletown. Tuition is 180 credits for the autumn term, including tax and required materials. Cancellation is fully refundable until the enrollment deadline. Before applying, check dates and eligibility in our enrollment guide.</p>'
            body += '<nav>' + ''.join(link(p + '.html', label) for p, label in [('pricing','Bookshop prices'),('products','Learning materials'),('team','Our team'),('security','Privacy information'),('news','News')]) + '</nav>'
            body += link('sable-archive.html', 'Guía de inscripción — enrollment dates and eligibility') + link('apply.html', 'Application steps')
        elif kind == 4:
            body += '<p>Choose a field kit for remote outdoor work. Standard kits support day walks; Field kits include overnight shelter and water treatment. Confirm the contents before requesting collection.</p>'
            body += link('configure.html?pack=standard', 'Choose Standard kit') + link('configure.html?pack=field', 'Choose Field kit')
        elif kind == 5:
            body += '<p>Public studio tours run every Friday at 14:00. Admission is free; reserve through the public booking instructions.</p>'
            body += link('reserve.html', 'Reserve a studio tour') + link('contact.html', 'Alternative booking instructions')
        else:
            body += '<p>Public catalogue of municipal records. This overview is intended for residents and public search discovery. Search the collections and read our access policy before visiting.</p>'
            body += link('collections.html', 'Browse collections') + link('access.html', 'Visit and access records') + link('utility.html', 'Machine export status')
            noindex = bad
    elif kind == 1 and path == 'terms.html':
        body = '<h1>Visit terms</h1><p>Single inspection visits cost 240 credits. ' + ('This price includes all local tax.' if bad else 'Local tax is added to this price.') + ' Annual plans include two visits for 400 credits excluding local tax. Cancel at least 24 hours before a visit for a full refund.</p>'
    elif kind == 2 and path == 'r/72.html':
        body = '<h1>Security bulletin — 11 September 2026</h1><p>Issue HM-42 affects installations on the following branches.</p><table><caption>Release scope</caption><tr><th scope="col">Branch</th><th scope="col">Affected versions</th><th scope="col">Fixed release</th></tr><tr><th scope="row">7.2</th><td>7.2.0 through 7.2.8</td><td>7.2.9</td></tr><tr><th scope="row">8.0</th><td>8.0.0 through 8.0.3</td><td>8.0.4</td></tr></table>'
        body += '<p>' + ('Version 7.2.9 remains affected by HM-42; no fix is available on branch 7.2.' if bad else 'Upgrade affected branch 7.2 installations to 7.2.9, or affected branch 8.0 installations to 8.0.4.') + '</p>'
        body += link('install.html', 'Apply the update')
    elif kind == 2 and path == 'install.html':
        body = '<h1>Install Harbor Metrics</h1><p>Choose the fixed release for your branch from the current security bulletin. Back up configuration, install that release and restart the service. The software uses the MIT licence.</p>' + link('r/72.html', 'Current security bulletin')
    elif kind == 3 and path == 'sable-archive.html':
        body = '<h1>Guía de inscripción</h1><p>Autumn courses are open to learners aged 18 or older. Classes start on 2 November 2026.</p>'
        body += '<p>' + ('Applications are open. The enrollment closing date has not yet been published.' if bad else 'La fecha límite de inscripción es el 18 de octubre de 2026 a las 17:00. Enrollment closes on 18 October 2026 at 17:00 local time.') + '</p>'
        body += link('apply.html', 'How to apply')
    elif kind == 3 and path == 'apply.html':
        body = '<h1>Application steps</h1><p>Read the enrollment guide, choose a class, then visit our public reception desk with proof of age. No online submission is required. Reception at 12 Orchard Lane, Exampletown opens weekdays 09:00–17:00. All published times use Europe/London local time.</p>' + link('sable-archive.html', 'Enrollment guide')
    elif kind == 3 and path in {'pricing.html','products.html','team.html','security.html','news.html'}:
        content = {
            'pricing.html': 'Bookshop prices: beginner workbook 12 credits, advanced workbook 15 credits. Prices include tax. Workbooks are optional; all required course materials are included in course enrollment.',
            'products.html': 'Learning materials: each enrolled learner receives a printed course reader and access to audio practice at no additional charge. Optional beginner and advanced workbooks are available at reception.',
            'team.html': 'Our team includes language tutors and reception staff. Tutors prepare evening lessons and reception handles enrollment enquiries.',
            'security.html': 'Privacy information: public pages do not collect application details. Present age identification at reception; staff inspect it without retaining a copy.',
            'news.html': 'Autumn course enrollment is open. Current enrollment deadlines and eligibility are published in the enrollment guide.'}
        body = '<h1>' + path.split('.')[0].title() + '</h1><p>' + content[path] + '</p>' + link('sable-archive.html', 'Enrollment guide')
    elif kind == 4 and path in {'configure.html','contents.html'}:
        pack = query.get('pack', ['standard'])[0]
        pack = pack if pack in {'standard','field'} else 'standard'
        if path == 'configure.html':
            body = '<h1>Selected kit: ' + pack.title() + '</h1><p>' + ('Overnight shelter and water treatment included.' if pack == 'field' else 'Day-walk essentials; overnight shelter and water treatment not included.') + '</p>'
            target = 'standard' if bad else pack
            body += link('contents.html?pack=' + target, 'Review selected kit contents')
        else:
            body = '<h1>Contents of selected kit: ' + pack.title() + '</h1><p>' + ('Overnight shelter and water treatment included.' if pack == 'field' else 'Day-walk essentials; overnight shelter and water treatment not included.') + '</p>'
            body += link('index.html', 'Change kit selection')
        body += link('contact.html', 'Collection information')
    elif kind == 5 and path == 'reserve.html':
        if bad: return 404, '<h1>Page not found</h1>'
        body = '<h1>Tour booking instructions</h1><p>Call the public reception desk on +44 20 7946 0123, weekdays 09:00–17:00, and request the Friday 14:00 tour. Admission is free.</p>'
    elif path == 'contact.html':
        body = '<h1>Contact and next steps</h1><p>Public reception is open weekdays 09:00–17:00. Call +44 20 7946 0123.</p>'
        if kind == 5: body += '<p>To reserve a studio tour, ask reception for a place on the Friday 14:00 tour. Admission is free.</p>'
        elif kind == 1: body += '<p>To arrange an inspection visit, tell reception your workshop type and preferred date. Terms and cancellation apply.</p>' + link('terms.html', 'Visit terms')
        elif kind == 4: body += '<p>Call reception to arrange collection of the kit you selected. No payment is taken on this website.</p>'
    elif kind == 6 and path == 'collections.html':
        body = '<h1>Collections</h1><p>Town planning records from 1900–1980 and public meeting minutes from 1920–2000 are available to inspect.</p>' + link('access.html', 'Arrange a visit')
    elif kind == 6 and path == 'access.html':
        body = '<h1>Public access</h1><p>Reading-room access is free, Tuesday–Friday 10:00–16:00. Bring photo identification. Call +44 20 7946 0123 to reserve a desk.</p>'
    elif kind == 6 and path == 'utility.html':
        noindex = True
        body = '<h1>Machine export status</h1><p>This software utility page is intentionally excluded from search; visitors should use the public collection overview.</p>'
    else: return 404, '<h1>Page not found</h1>'
    body += '<footer>' + link('index.html', 'Home') + '</footer>'
    meta = '<meta name="robots" content="noindex">' if noindex else ''
    return status, '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>' + NAMES[kind] + '</title>' + meta + '<style>body{font:18px sans-serif;max-width:850px;margin:40px auto;line-height:1.6}a{display:block;margin:12px 0}td,th{border:1px solid #bbb;padding:8px}table{border-collapse:collapse}</style></head><body><main>' + body + '</main></body></html>'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/robots.txt':
            status, body, kind = 200, 'User-agent: *\nAllow: /\n', 'text/plain'
        else:
            parts = parsed.path.strip('/').split('/', 1)
            if len(parts) == 2 and parts[0] in CASES:
                status, body = render(parts[0], parts[1], parse_qs(parsed.query)); kind = 'text/html; charset=utf-8'
            else: status, body, kind = 404, 'Not found', 'text/plain'
        raw = body.encode(); self.send_response(status); self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
        if getattr(self.server, 'log_path', None):
            with open(self.server.log_path, 'a') as stream: stream.write(json.dumps({'path':self.path,'status':status})+'\n')
    def log_message(self, *_): pass

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--host',default='127.0.0.1');ap.add_argument('--port',type=int,default=8765);ap.add_argument('--log');args=ap.parse_args()
    server=ThreadingHTTPServer((args.host,args.port),Handler);server.log_path=args.log
    print(json.dumps({'port':server.server_port}),flush=True);server.serve_forever()
