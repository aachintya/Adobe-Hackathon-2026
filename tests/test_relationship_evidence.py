import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/audit-orchestrator/scripts"))
from page_evidence import page_fields


class RelationshipEvidenceTests(unittest.TestCase):
    def test_table_preserves_row_column_value_and_qualifiers(self):
        html = """<table><caption>Plans</caption>
          <tr><th scope=col>Plan</th><th scope=col>Price</th><th scope=col>Billing</th></tr>
          <tr><th scope=row>Pro</th><td>$10</td><td>Monthly</td></tr>
          <tr><th scope=row>Pro annual</th><td>$100</td><td>Annual</td></tr>
        </table>"""
        _, fields = page_fields(html)
        table = fields["tables"][0]
        annual = next(record for record in table["records"] if record["value"] == "Annual")
        self.assertEqual(annual["row_header"], "Pro annual")
        self.assertEqual(annual["column_header"], "Billing")
        self.assertEqual(annual["qualifiers"], ["Pro annual", "Billing"])
        self.assertEqual(annual["context"], "Pro annual | Billing | Annual")
        self.assertTrue(annual["context_is_derived"])
        self.assertEqual(table["caption"], "Plans")
        self.assertFalse(table["truncated"])

    def test_empty_and_missing_href_are_retained_but_healthy_link_is_unchanged(self):
        _, fields = page_fields('<a href="">Buy monthly</a><a>Apply annually</a><a href="mailto:sales@example.test">Email sales</a>')
        links = fields["links"]
        self.assertEqual([link["href"] for link in links], ["", None, "mailto:sales@example.test"])
        self.assertEqual(links[2]["text"], "Email sales")
        self.assertEqual(fields['links_count'], 1)
        self.assertEqual(fields['anchor_count'], 3)
        kinds = [candidate["type"] for candidate in fields["relationship_candidates"]]
        self.assertIn("empty_cta_link", kinds)
        self.assertNotIn("email_label_mismatch", kinds)

    def test_complex_or_oversized_table_is_bounded_and_explicit(self):
        rows = "".join("<tr><th>Row %d</th><td>value</td></tr>" % i for i in range(45))
        _, fields = page_fields("<table>" + rows + "</table><table><tr><td rowspan=bad>x</td></tr></table>")
        self.assertEqual(len(fields["tables"]), 2)
        self.assertTrue(fields["tables"][0]["truncated"])
        self.assertIn("invalid_span", fields["tables"][1]["ambiguities"])
        self.assertLessEqual(len(fields["tables"][0]["records"]), 200)

    def test_fixed_and_affected_are_distinct_relationships(self):
        _, fields = page_fields('<table><tr><th>Branch</th><th>Fixed release</th><th>Affected versions</th></tr>'
                               '<tr><th>7.2</th><td>7.2.9</td><td>7.2.0 through 7.2.8</td></tr></table>')
        records = fields['tables'][0]['records']
        self.assertEqual([(r['row_header'], r['column_header'], r['value']) for r in records],
                         [('7.2', 'Fixed release', '7.2.9'), ('7.2', 'Affected versions', '7.2.0 through 7.2.8')])

    def test_hidden_script_and_caption_do_not_pollute_values(self):
        _, fields = page_fields('<table><caption>Fees</caption><tr><th>Plan</th><th>Cost</th></tr>'
                               '<tr><th>Annual</th><td><span hidden>999</span>120<script>500</script></td></tr></table>'
                               '<table hidden><tr><td>secret</td></tr></table>')
        self.assertEqual(len(fields['tables']), 1)
        table = fields['tables'][0]
        self.assertEqual(table['caption'], 'Fees')
        self.assertEqual(table['records'][0]['value'], '120')
        self.assertNotIn('999', str(table))

    def test_span_nested_and_unclosed_tables_do_not_infer_headers(self):
        for html in [
            '<table><tr><th rowspan=2>Branch</th><th>Version</th></tr><tr><td>7.2</td></tr></table>',
            '<table><tr><th>Plan</th><td><table><tr><th>Inner</th><td>20</td></tr></table></td></tr></table>',
            '<table><tr><th>Plan</th><td>20',
        ]:
            with self.subTest(html=html):
                _, fields = page_fields(html)
                self.assertTrue(fields['tables'])
                self.assertTrue(all(t['ambiguities'] and not t['records'] for t in fields['tables']))

    def test_truncated_cell_is_not_complete_evidence(self):
        _, fields = page_fields('<table><tr><th>Plan</th><th>Terms</th></tr><tr><th>A</th><td>' + 'x' * 1001 + '</td></tr></table>')
        self.assertTrue(fields['evidence_truncated'])
        self.assertTrue(fields['tables'][0]['truncated'])
        self.assertEqual(fields['tables'][0]['records'], [])

    def test_literal_email_mismatch_and_healthy_controls(self):
        _, fields = page_fields('<a href="mailto:other@example.test">help@example.test</a>'
                               '<a href="mailto:help%40example.test?subject=Question">help@example.test</a>'
                               '<a href="/support">Email support</a>')
        candidates = fields['relationship_candidates']
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['type'], 'email_address_mismatch')
        self.assertEqual(candidates[0]['href'], 'mailto:other@example.test')


if __name__ == "__main__":
    unittest.main()
