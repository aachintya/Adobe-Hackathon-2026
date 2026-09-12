# Verify evidence before publishing a composed report

Use this route when Python and saved artifacts are available. Keep the public report schema at 1.2. The collector's `report.json` is a static baseline; compose `draft-report.json`, retain evidence references in `review.json`, and publish `final-report.json` only through the finalizer. Start from a fresh output directory.

The validator checks recorded evidence and internal consistency. It cannot establish that a passage entails an arbitrary conclusion, authenticate host observations, or guarantee that a website has not changed. Review each claim's meaning, scope and counterevidence before finalization. A quoted heading does not establish the absence of content beneath it. Opportunities receive the same premise check as findings.

## Compact review sidecar

Refer to existing collector records by `page:0`, `page:1`, etc.; also supported are `robots`, `sitemap:0`, and `error:0`. Do not duplicate collected pages. Additional fetch, browser and opened external evidence uses `host:` IDs in `observations`. Keep only material passages and captured fields with the original tool-result reference.

```json
{
  "review_version": "1",
  "observations": [],
  "claims": {
    "F-001": {
      "assertions": [
        {"type": "field_equals", "ref": "page:0", "field": "meta_robots", "value": "noindex"}
      ],
      "checked_refs": ["page:0", "page:1"],
      "affected_refs": ["page:0"]
    },
    "O-001": {
      "assertions": [
        {"type": "quote", "ref": "page:1", "field": "main_text", "quote": "Exact material passage from the saved source."}
      ]
    }
  },
  "answers": [
    {"test_index": 0, "evidence_index": 0, "ref": "page:1", "field": "main_text", "element_indices": [0]}
  ],
  "journeys": [
    {
      "journey_index": 0,
      "mode": "source",
      "steps": [
        {
          "step_index": 0,
          "ref": "page:1",
          "assertions": [
            {"type": "quote", "ref": "page:1", "field": "links.0.text", "quote": "Learn more"}
          ]
        }
      ]
    }
  ],
  "corroboration": []
}
```

This illustrates the record format, not a complete report's evidence. Supply a claim entry for every retained finding and opportunity, an answer mapping for every reported answer quote, and journey mappings for the reported steps. Indices are zero-based; claim IDs must follow the final report's ranking. Use actual evidence references and values, never the illustrative values above. Finding scopes must identify the records actually checked and affected, with counts and cited URLs agreeing with the report. Reading the same page in two modes does not double its page count.

For each `answered` question, every answer mapping needs `element_indices`: the zero-based required elements supported by that quote. Together the mappings must cover all required elements; one quote may support several. Preserve dates, version names, units, conditions and exclusions in the actual quotes. A generic heading or a sentence clipped before its date cannot support the missing detail. For other statuses, mappings may omit these indices; any supplied indices are still checked. For each required element, check the quote’s subject, relationship, value, conditions and date. “Fixed in 7.2.9” cannot support “affected versions”; “120 per year” cannot support “120 per month.” Quote a table’s raw header and cell fields separately (for example `tables.0.rows.0.1.value` and `tables.0.rows.1.1.value`); `records.*.context` is reconstructed reading context, not a verbatim website quotation. The validator checks coverage of the mapping, not whether the selected quote semantically supports the assigned element. Apply the same material-qualifier review to opportunity premises and journey observations, including `not_checked` journeys.

Supported assertions:

| Type | Required fields | What it establishes |
|---|---|---|
| `quote` | `ref`, `field`, `quote` | A short contiguous passage exists in the named captured string field, allowing whitespace normalization. |
| `field_equals` | `ref`, `field`, `value` | The captured field matches the stated JSON value. |
| `field_absent` | `ref`, `field` | A captured field is empty in successful complete evidence. An uncaptured key, failed fetch, or truncated source cannot establish absence. |
| `broken_link` | `ref`, `href`, `destination_ref` | The literal href exists in the source, resolves using the final URL/base, and its recorded destination returns 404 or 410. |

Use the typed field assertion for a captured-field claim, including an opportunity's absence premise. Use `broken_link` for a broken-destination claim. A quote assertion only proves passage presence; do not use it to evade a contradictory field or to assert an untested destination. Broad missing-answer claims still need contextual inspection of the relevant material, not a keyword or empty-field shortcut.

## Host observations

When a tool supplies evidence beyond the collector, add a compact observation:

```json
{
  "id": "host:institution",
  "url": "https://institution.example/clubs",
  "final_url": "https://institution.example/clubs/",
  "mode": "off_site",
  "kind": "external",
  "status": 200,
  "complete": false,
  "text": "Exact relevant passage copied from the opened source.",
  "provenance": {
    "tool": "actual public fetch tool",
    "reference": "actual tool-result or saved capture reference",
    "observed_at": "2026-09-10T10:00:30Z"
  }
}
```

Use `mode` from `static`, `rendered`, `off_site`, `retrieval`; use `kind` from `page`, `resource`, `external`, `interaction`. Status is the observed integer or null when not exposed. Set `complete` false for excerpts or capped observations; a successful fetch alone does not establish complete source capture. Optional `fields` contains only actually captured collector-shaped fields, addressed by their names in assertions. Cleaned text cannot establish the absence of a source HTML meta tag or header. Never invent status codes, tool references, timestamps or completeness to satisfy validation.

Search-result excerpts use `mode: "retrieval"`, `status: null` and `complete: false`, even when they link to a first-party page. They support quoted retrieval observations, but do not count in `coverage.pages_checked`, establish a live response, complete a journey, or provide opened-source corroboration. Opening a result successfully is a separate `static` or `off_site` observation with its own capture reference; do not relabel the search excerpt. Public text-fetch tools that omit HTTP status also use null, never an assumed 200. Save verbatim passages with their qualifiers; do not reconstruct text from memory or paraphrase a capture to make a quote assertion pass.

External corroboration entries are `{ "ref": "host:institution", "field": "text", "quote": "Exact relevant passage" }`. An observed corroboration stage must cite its opened external sources. The validator checks source provenance and quotes; the auditor must still establish independence and that the source supports the claimed relationship.

For each journey, choose `mode: "source"` or `"rendered"`; label each report step's action `[source]` or `[rendered]` respectively. A source route can establish readable information and observed link destinations. A rendered journey needs corresponding browser evidence. Keep steps already inspected even when the journey remains `not_checked`; do not convert a capability failure into website friction.

## Validation and finalization

For evidence checking without publication or timing verification:

```text
python3 <marketplace-root>/tests/validate_report.py OUTPUT/draft-report.json --evidence OUTPUT/evidence.json --review OUTPUT/review.json
```

For finalization, pass the unchanged, observed invocation start from before instruction reading:

```text
python3 <skill-directory>/scripts/finalize_report.py --report OUTPUT/draft-report.json --evidence OUTPUT/evidence.json --review OUTPUT/review.json --output OUTPUT/final-report.json --started-at ORIGINAL_UTC_START
```

The finalizer requires a composed report, validates its schema and evidence, checks elapsed time before publication, and refuses an existing output or receipt. Success writes the final report and `final-report.json.receipt.json`, binding the checked report, evidence and review with hashes. Keep these artifacts together. If publication fails, retain the draft/evidence and actual diagnostics. Quote failures may name another field in the same record containing the exact quote; inspect its context before changing the reference. These are locator hints, not permission to paraphrase a quote or assume semantic support. Keep correctly completed assessment records when narrowing an unsupported item. All-not-checked questions or empty journeys cannot support an observed readiness stage. Correct evidence or narrow unsupported conclusions within the original budget; do not repeatedly relabel or regenerate timestamps to obtain success.

The strict time gate rejects elapsed time at or beyond 300 seconds. Target 280 seconds to leave delivery headroom. This does not authenticate the caller-supplied start, cancel the host agent's operations, or measure user-visible message delivery. The host must enforce its own full-run deadline if that guarantee is required. A schema-only validation result is explicitly a different scope from an evidence check; neither is a certificate of factual truth.

When Python, files or the clock are unavailable, follow [tool availability](tool-availability.md). A manually checked report remains supported with explicit limits; never claim automated evidence or timing verification for that path.
