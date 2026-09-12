import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "evals"))
from score_agent_reports import evaluate_report

class AgentQualityTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"expected_roots": [{"id":"R1","severity":"critical"},{"id":"R2","severity":"medium"}]}
    def run_score(self, findings, opportunities=None, ads=None, support=None, runtime=None):
        report = {"findings": findings, "proactive_opportunities": opportunities or [], "assessment":{"intent_tests":[{"required_elements":["price"]}]}}
        raw = json.dumps(report).encode(); a={"report_sha256":hashlib.sha256(raw).hexdigest(),"adjudications":ads or [],"answer_support":support or {"0":{"price":2}},"runtime":runtime or {"completion":"completed","timestamp_kind":"exact_delivery","observer_start":"2026-01-01T00:00:00Z","delivery":"2026-01-01T00:01:00Z"}}
        return evaluate_report(report,self.expected,a,report_bytes=raw)
    def ad(self, iid, verdict, root=None):
        return {"item_id":iid,"verdict":verdict,"root_id":root,**{d:2 for d in ("scope","evidence","severity","action_correctness","action_mechanism","action_specificity","action_verification")}}
    def test_false_lowers_precision_and_abstention_recall(self):
        x=self.run_score([{"id":"F1"},{"id":"F2"}],ads=[self.ad("F1","correct","R1"),self.ad("F2","false")]); self.assertEqual(x["quality"]["finding_precision"],.5); self.assertEqual(x["quality"]["root_recall"],.5)
    def test_healthy_answered_zero_findings(self):
        x=self.run_score([]); self.assertIsNone(x["quality"]["finding_precision"]); self.assertEqual(x["quality"]["answer_requirement_support"],2)
    def test_opportunity_must_be_adjudicated(self):
        x=self.run_score([], [{"id":"O1"}], ads=[]); self.assertFalse(x["complete"]); self.assertIsNone(x["quality"]["finding_precision"])
    def test_duplicate_order_independent(self):
        x=self.run_score([{"id":"F1"},{"id":"F2"}],ads=[self.ad("F1","duplicate","R1"),self.ad("F2","correct","R1")]); self.assertTrue(x["complete"]); self.assertEqual(x["quality"]["duplicate_findings"],1)
    def test_multiple_accepted_assignments_and_duplicate_entries_are_rejected(self):
        x=self.run_score([{"id":"F1"},{"id":"F2"}],ads=[self.ad("F1","correct","R1"),self.ad("F2","correct","R1")])
        self.assertFalse(x['complete'])
        x=self.run_score([{"id":"F1"}],ads=[self.ad("F1","correct","R1"),self.ad("F1","correct","R1")])
        self.assertFalse(x['complete'])
    def test_opportunity_without_defect_and_false_claim_evidence(self):
        good=self.ad('O1','correct'); bad=self.ad('F1','false'); bad['evidence']=0
        x=self.run_score([{'id':'F1'}],[{'id':'O1'}],ads=[bad,good])
        self.assertTrue(x['complete'])
        self.assertEqual(x['quality']['evidence_fidelity'],1)
        self.assertEqual(x['quality']['finding_precision'],0)
    def test_unknown_answer_and_unreviewed_support_are_rejected(self):
        x=self.run_score([],support={'0':{'price':2,'invented':2}})
        self.assertFalse(x['complete'])
        x=self.run_score([],support={'0':{}})
        self.assertFalse(x['complete'])
    def test_partial_credit_and_healthy_recall_denominators(self):
        x=self.run_score([{'id':'F1'}],ads=[self.ad('F1','partial','R1')])
        self.assertEqual(x['quality']['finding_precision'],.5)
        self.assertEqual(x['quality']['root_recall'],.25)
        self.assertEqual(x['quality']['high_or_critical_recall'],.5)
        self.expected={'expected_roots':[]}
        x=self.run_score([])
        self.assertIsNone(x['quality']['root_recall'])
    def test_partial_public_ground_truth_and_unmeasured_clock(self):
        self.expected['ground_truth_complete']=False
        x=self.run_score([{'id':'F1'}],ads=[self.ad('F1','correct','R1')],runtime={'completion':'completed','timestamp_kind':'not_measured','reason':'Independent dispatch clock unavailable.'})
        self.assertTrue(x['complete'])
        self.assertEqual(x['quality']['finding_precision'],1)
        self.assertIsNone(x['quality']['root_recall'])
        self.assertIsNone(x['runtime']['duration_seconds'])
    def test_invalid_duration_and_hash(self):
        x=self.run_score([],runtime={"completion":"completed","timestamp_kind":"exact_delivery","observer_start":"2026-01-01T00:02:00Z","delivery":"2026-01-01T00:01:00Z"}); self.assertFalse(x["complete"])
        report={"findings":[]}; x=evaluate_report(report,{"expected_roots":[]},{"report_sha256":"bad","adjudications":[],"answer_support":{},"runtime":{"completion":"failed","timestamp_kind":"exact_delivery","observer_start":"2026-01-01T00:00:00Z","delivery":"2026-01-01T00:01:00Z"}},report_bytes=json.dumps(report).encode()); self.assertFalse(x["complete"]); self.assertIsNone(x["quality"]["root_recall"])
    def test_cli_malformed_report_is_recorded(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"; p.write_text("{"); e=Path(d)/"e.json"; e.write_text('{"expected_roots":[]}'); a=Path(d)/"a.json"; a.write_text('{}')
            script=Path(__file__).resolve().parents[1]/'evals/score_agent_reports.py'
            r=subprocess.run([sys.executable,str(script),str(p),"--expected",str(e),"--adjudications",str(a)],capture_output=True,text=True); self.assertEqual(r.returncode,2); self.assertIn("could not be loaded",r.stdout)

if __name__ == "__main__": unittest.main()
