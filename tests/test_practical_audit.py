#!/usr/bin/env python3
"""Regressions for material evidence, provider roles and honest measurements."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/audit-orchestrator/scripts"))
from page_evidence import page_fields
from robots_policy import RobotsPolicy
from run_audit import baseline, indexing_directives
from measure_visibility import summarize
from validate_report import validate


class PracticalAuditTests(unittest.TestCase):
    def test_material_evidence_survives_beyond_old_preview(self):
        html = '<html lang="fr"><head><title>Offer</title><meta name="robots" content="index"><meta name="robots" content="nosnippet"></head><body><nav>menu noise</nav><main><h1>Hosting</h1><p>' + 'intro ' * 260 + '</p><h2>Constraints</h2><p id="answer">Hosted only in Paris; export supported.</p><a href="/terms">Read <strong>terms</strong></a><p hidden>secret hidden text</p><script>junk</script></main><footer>footer noise</footer></body></html>'
        _, p = page_fields(html)
        self.assertNotIn('Paris', p['text_sample'])
        self.assertIn('Paris', p['main_text'])
        self.assertNotIn('menu noise', p['main_text'])
        self.assertNotIn('secret hidden', p['main_text'])
        self.assertEqual(p['title'], 'Offer')
        self.assertEqual(p['language'], 'fr')
        self.assertEqual(p['links'][0]['text'], 'Read terms')
        self.assertEqual(p['meta_robots'], 'index, nosnippet')
        self.assertTrue(any(x['selector'] == '#answer' and x['heading'] == 'Constraints' for x in p['passages']))

    def test_structured_values_and_parse_errors_are_preserved(self):
        _, p = page_fields('<script type="application/ld+json">{"@type":"Product","offers":{"price":42}}</script><script type="application/ld+json">{bad}</script>')
        self.assertEqual(p['jsonld']['data'][0]['offers']['price'], 42)
        self.assertEqual(p['jsonld']['parse_errors'], 1)

    def test_main_text_without_semantic_main_is_not_dropped(self):
        _, p = page_fields('<div><div>Clinic open Monday.</div></div>')
        self.assertIn('Clinic open Monday.', p['main_text'])

    def test_noscript_fallback_is_readable_source_evidence(self):
        _, p = page_fields('<noscript><p>Open Monday to Friday.</p></noscript>')
        self.assertIn('Open Monday to Friday.', p['main_text'])

    def test_robots_specificity_merging_wildcards_and_ties(self):
        rules = RobotsPolicy('User-agent: *\nDisallow: /\nUser-agent: OAI-SearchBot\nDisallow: /docs/*\nAllow: /docs/public\nUser-agent: OAI-SearchBot\nAllow: /docs/exact$\nDisallow: /tie\nAllow: /tie\n')
        for path in ['/docs/public/a', '/docs/exact', '/tie']:
            self.assertTrue(rules.can_fetch('OAI-SearchBot', 'https://example.com' + path))
        self.assertFalse(rules.can_fetch('OAI-SearchBot', 'https://example.com/docs/private'))
        self.assertFalse(rules.can_fetch('OAI-SearchBot', 'https://example.com/docs/exact/more'))
        self.assertFalse(rules.can_fetch('BrandAIReadinessAudit', 'https://example.com/docs/public'))

    def test_robots_percent_encoded_unreserved_and_reserved(self):
        rules = RobotsPolicy('User-agent: *\nDisallow: /%62locked\nDisallow: /a%2Fb\n')
        self.assertFalse(rules.can_fetch('*', 'https://x.test/blocked'))
        self.assertFalse(rules.can_fetch('*', 'https://x.test/a%2fb'))
        self.assertTrue(rules.can_fetch('*', 'https://x.test/a/b'))

    def test_crawl_delay_respects_collector_group(self):
        rules = RobotsPolicy('User-agent: *\nCrawl-delay: 5\nUser-agent: BrandAIReadinessAudit\nCrawl-delay: 2\n')
        self.assertEqual(rules.crawl_delay('BrandAIReadinessAudit/2.0'), 2)
        self.assertEqual(rules.crawl_delay('Other'), 5)

    def test_training_block_and_missing_schema_are_not_defects(self):
        _, fields = page_fields('<h1>Library opening times</h1><p>Open Monday to Friday, 9 to 5.</p>')
        evidence = {'site':'https://library.test/','collected_at':'2026-09-05T10:00:00Z','robots':{'url':'https://library.test/robots.txt','ai_agent_allowed':{'GPTBot':False,'OAI-SearchBot':True}},'pages':[{'url':'https://library.test/','parse_status':'parsed_html',**fields}],'errors':[],'coverage':{}}
        report = baseline(evidence)
        self.assertEqual(report['findings'], [])
        self.assertEqual(report['assessment']['visibility']['status'], 'not_measured')
        self.assertEqual(validate(report), [])

    def test_http_and_meta_indexing_scopes(self):
        p = {'meta_robot_directives':{'googlebot':'noindex'},'x_robots_tag':'bingbot: noindex, nofollow, otherbot: nosnippet'}
        d = indexing_directives(p)
        self.assertNotIn('noindex', d['robots'])
        self.assertIn('noindex', d['bingbot'])
        self.assertIn('noindex', d['googlebot'])
        self.assertNotIn('nosnippet', d['bingbot'])

    def test_repeated_http_headers_reset_engine_scope(self):
        d = indexing_directives({'x_robots_tags':['googlebot: noindex','nofollow']})
        self.assertEqual(d['googlebot'], {'noindex'})
        self.assertEqual(d['robots'], {'nofollow'})

    def make_run(self, **changes):
        return {'id':'R1','provider':'test','surface':'test-api','model':'test-model','locale':'en-IN','observed_at':'2026-09-05T10:00:00Z','prompt':'A neutral question','prompt_kind':'unbranded','status':'ok','response_text':'Captured answer','brand_mentioned':False,'citation_urls':[],**changes}

    def test_errors_excluded_and_mentions_not_conflated_with_citations(self):
        runs = [self.make_run(brand_mentioned=True, citation_urls=['https://independent.test/about-brand']), self.make_run(id='R2',citation_urls=['https://docs.example.com/help']), self.make_run(id='R3',status='error',reason='timeout')]
        c = summarize({'site':'https://example.com','runs':runs})['cohorts'][0]
        self.assertEqual((c['valid_runs'], c['failed_runs'], c['mention_rate'], c['citation_rate']), (2, 1, .5, .5))

    def test_citation_hostname_must_match_not_just_contain_brand(self):
        runs = [self.make_run(citation_urls=['https://example.com.evil.test/', 'https://notexample.com/', 'https://else.test/?q=example.com'])]
        self.assertEqual(summarize({'site':'https://example.com','runs':runs})['cohorts'][0]['citation_rate'], 0)

    def test_failed_only_runs_are_unknown_not_zero_visibility(self):
        result = summarize({'site':'https://example.com','runs':[self.make_run(status='error',reason='unavailable')]})
        self.assertEqual(result['status'], 'not_measured')
        self.assertIsNone(result['cohorts'][0]['citation_rate'])

    def test_branded_and_different_surfaces_do_not_share_denominator(self):
        result = summarize({'site':'https://example.com','runs':[self.make_run(),self.make_run(id='R2',prompt_kind='branded'),self.make_run(id='R3',surface='web-product')]})
        self.assertEqual(len(result['cohorts']), 3)

    def test_missing_raw_answer_and_duplicate_runs_are_rejected(self):
        for runs in [[self.make_run(response_text='')], [self.make_run(), self.make_run()]]:
            with self.assertRaises(ValueError): summarize({'site':'https://example.com','runs':runs})

    def test_unmeasured_report_cannot_claim_measured_visibility(self):
        doc = json.loads((ROOT/'tests/fixtures/valid-report.json').read_text())
        doc['assessment']['visibility']['status'] = 'measured_sample'
        self.assertTrue(validate(doc))

    def test_journey_and_question_outcomes_need_evidence(self):
        original = json.loads((ROOT/'tests/fixtures/valid-report.json').read_text())
        for field, key in [('journeys','steps'), ('intent_tests','evidence')]:
            doc = copy.deepcopy(original); doc['assessment'][field][0][key] = []
            self.assertTrue(validate(doc))


if __name__ == '__main__': unittest.main()
