# Retrieval and actual visibility are different tests

## Default audit: bounded retrieval and corroboration

Within the shared 45-second search allocation, run 3-4 queries: exact entity name; one neutral category/task query without the brand; and 1-2 material factual lookups derived from the question tests. Record exact queries, date, tool, locale (or unknown), returned source URLs and short evidence quotes from opened sources. Compare same-entity claims with the site's current statements. Store this ledger in the output directory and summarize findings/readiness with supporting URLs and query details.

Do not label these searches as observed ChatGPT/Claude/Gemini answers. A result in a search tool is a retrieval observation on that tool. Search absence is not a visibility defect, a noindex diagnosis, or proof of no independent support. A returned competitor is a lead to inspect, not evidence that its schema or word count caused it to win.

## Optional actual answer measurement

Only when a supported assistant surface is available within scope/budget, or the user supplies recorded runs, measure actual answers. Do not assume API credentials or create paid-service dependencies for the judging entrypoint. A search-enabled answer you compose while knowingly auditing the target is not an unbiased discovery test.

Freeze a small realistic prompt set before inspecting outcomes: include neutral category/constraint questions without the desired brand, plus separately labelled branded factual questions. Record fresh context, provider, actual surface (web product versus API), model or `unknown`, locale, UTC date, exact prompt, full response, citation URLs, and manually verified entity mention. For a fuller evaluation, repeat prompts in fresh sessions and report variability; the five-minute audit may only produce a clearly limited snapshot.

Input for `scripts/measure_visibility.py` (paths resolve from the orchestrator skill):

```json
{
  "site": "https://example.com",
  "runs": [{
    "id": "R-001", "provider": "record actual provider", "surface": "record actual product or API",
    "model": "unknown", "locale": "en-IN", "observed_at": "2026-09-05T10:00:00Z",
    "prompt": "Exact question used", "prompt_kind": "unbranded", "status": "ok",
    "response_text": "Exact returned answer", "brand_mentioned": false, "citation_urls": []
  }]
}
```

For a failure use `status: "error"` with `reason`; for an unexecuted prompt use `not_run`. Do not convert either to a successful omission. Capture only citations explicitly present in the returned answer, not links subsequently found by the auditor. Verify that a brand mention refers to the target entity, including negative mentions; recommendation quality/sentiment is a separate qualitative observation.

Run `python <skill-directory>/scripts/measure_visibility.py observations.json --output visibility.json` and copy its result into `assessment.visibility`. The helper separates provider/surface/model/locale and branded/unbranded cohorts, counts unique prompts, excludes errors from denominators, and computes per-run mention and target-domain citation rates. A third-party article mentioning the brand can count as a mention, but is not a citation of the target website. Keep the raw runs with the report so these numbers are reviewable. Do not merge before/after results from differing prompt sets or providers.

These rates describe this recorded sample, not universal visibility, rank, recommendation share or a causal improvement from a website change. With no successful actual runs, status stays `not_measured` and rates stay null. Recommend owner-provided analytics/Search Console reports only as later validation; the public audit does not claim to access them.
