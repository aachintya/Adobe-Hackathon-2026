# Publication sanitization

These repository copies are sanitized publication transcripts, not byte-identical copies of the raw field-evidence artifacts.

Sanitization was deliberately bounded to the following categories:

- Local filesystem paths were replaced with `<marketplace-root>` and `<raw-evidence-root>` in `baseline-govuk/ledger.md`, `baseline2-govuk/timing.json`, `baseline2-duckdb/timing.json`, and `verified-duckdb/timing.json`.
- The observed `_ga` query parameter was removed from the GOV.UK public-service URLs in `baseline-govuk/ledger.md`, `baseline-govuk/report.json`, `baseline2-govuk/ledger.md`, and `baseline2-govuk/report.json`.
- The observed Fastmail `u` query parameter was removed from the custom-domain URLs in `luna-fastmail/ledger.md` and `luna-fastmail/report.json`.

Functional query parameters and substantive URLs, findings, quotes, counts, timestamps, and judgment errors were not changed. Raw originals remain outside this repository. A bounded review found no credential-like secret or private personal-data value in the committed live-usage artifacts.
