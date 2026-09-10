# DuckDB audit source ledger

Started: 2026-09-08T15:47:28Z; epoch 1788882448. Tools: Python static collector, live web search/open, Codex IAB rendering. Locale: unknown for search; browser detected macOS.

## Frozen question tests (before inspecting task destinations)

1. What does DuckDB do, and who should use it? Expected: analytical SQL purpose, deployment model, representative data tasks.
2. Is DuckDB free and what license/governance applies? Expected: cost, license, governing entity.
3. What version should a new user install today? Expected: current stable release and distinction from alpha/development release.
4. How can a Python user get started? Expected: installation command, Python requirements, first-query or documentation route.

Assumed audience: developers and data analysts assessing a local/in-process analytical database. Default crawl cap 12. No private analytics or assistant citation runs available.

## Browser evidence

- Created one hidden IAB tab at https://duckdb.org/; rendered accessibility tree showed analytical database deployment, PostgreSQL-inspired query language, MIT licensing and independent DuckDB Foundation governance. Homepage states latest version 1.5.5 and links a separate v2.0-alpha blog post dated 2026-09-02.
- Homepage actions available: Get DuckDB -> https://duckdb.org/install; Python -> https://duckdb.org/docs/current/clients/python/overview.html. Next inspections use these two routes.
- Clicked Get DuckDB (AX 26), verified https://duckdb.org/install/?platform=macos&environment=cli: CLI/macOS, 1.5.5 current, 1.4.5 LTS, visible curl installation command and separate preview route. Journey 1 completed at instructions.
- Clicked Python radio (AX 27), verified URL environment=python and `pip install duckdb`; Client documentation page destination changed to Python overview.
- Clicked Client documentation page (AX 56), verified final https://duckdb.org/docs/current/clients/python/overview: stable 1.5.5, Python 3.9 or newer, Basic API Usage `SELECT 42`, file-reading examples, persistence and thread-safety guidance. Journey 2 completed. Three templates rendered. No forms, authentication, downloads or command execution.
- Browser default viewport, exact dimensions and locale not recorded. No blocking challenge/overlay in tested paths. Mobile, keyboard/focus, contrast and performance not exercised.

## Static evidence and reviewed candidates

Collector completed 22 requests in 13.07 seconds; 12 HTML pages; robots and sitemap 200. robots permits current paths with Allow: / and disallows only listed old docs paths; search/training/user-fetch roles separately preserved in evidence.json. Six page evidence records capped. Eight HTTP 308 errors are collection limitations, not site defects; installer redirect works in browser.

- Rejected static draft F-001: https://duckdb.org/design has `noindex`, `Redirecting…`, and canonical https://duckdb.org/design/manual/. Opened destination is a readable DuckDB Design Manual describing visual/communication standards. The utility redirect's exclusion does not establish a valuable page's exclusion.
- Retained composed F-001 (low): https://duckdb.org/docs/current/clients/overview has literal `{{ site.current_duckdb_version }}` and `{% include tooltip.html ... %}` in meta description and JSON-LD WebPage.description. Same response's body lists concrete support tiers and 1.5.5. Exactly 1/12 source pages affected; metadata descriptions inspected across all 12. JSON-LD parse errors total 0. Missing/short metadata elsewhere not treated as defects.
- Homepage SoftwareApplication schema price 0 and MIT URL agree with visible free/MIT offer. Sample noindex count 1/12; other 11 have empty meta and HTTP restrictions. No provider-IP or assistant citation access claims.

## Search ledger

Date 2026-09-08; tool web.run; locale unknown. One batch of four exact queries, output pooled by the tool (no individual rank attribution):

1. `DuckDB`
2. `embedded analytical SQL database query parquet python`
3. `DuckDB current stable release 1.5.5 September 2026`
4. `DuckDB MIT license independent Foundation`

Returned relevant source URLs included https://duckdb.org/, https://duckdb.org/faq, https://duckdb.org/install/, https://github.com/duckdb/duckdb/blob/main/LICENSE, https://github.com/duckdb/duckdb/releases/tag/v1.5.5, https://arxiv.org/abs/2603.02081, https://arxiv.org/abs/2502.05311, https://www.youtube.com/watch?v=uHm6FEb2Re4, https://ducklabs.com/about/, and Wikipedia. Search snippets were leads. Opened evidence:

- https://duckdb.org/faq — current first-party FAQ; free MIT components, Foundation/DuckLabs/MotherDuck distinctions; data science and engineering use cases. Quote: `there is no “enterprise version” of DuckDB.`
- https://github.com/duckdb/duckdb/blob/main/LICENSE — first-party project license, not independent despite external hostname. Quote: `Copyright 2018-2026 Stichting DuckDB Foundation`; grant free of charge visible. Supports license/entity consistency.
- https://github.com/duckdb/duckdb/releases/tag/v1.5.5 — first-party release; quote: `DuckDB v1.5.5 Bugfix Release`, labelled Latest, released `22 Jul 10:51`. Confirms current stable site statement as observed today.
- https://arxiv.org/abs/2603.02081 — independent primary research by Jiale Lao and Immanuel Trummer, submitted 2026-03-02. Quote: `We compare GenDB with state-of-the-art query engines, including DuckDB`. Corroborates DuckDB query-engine identity only; its benchmark superiority claim was not audited or adopted.
- https://arxiv.org/abs/2502.05311 — ParquetDB research, submitted 2025-02-07/revised 2025-04-21. Opened abstract describes another Python/Parquet system; not used to corroborate DuckDB or infer competitor causality.
- https://www.youtube.com/watch?v=uHm6FEb2Re4 — open failed with tool Internal Error; excluded from corroboration. Wikipedia and DuckLabs about page were returned but not independently opened/used for conclusions.
- https://duckdb.org/design/manual/ — opened to resolve noindex candidate, heading `DuckDB Design Manual`; destination content available.

## Same-entity claim ledger

Entity: DuckDB; canonical URL https://duckdb.org/; project identifier github.com/duckdb/duckdb. All claims observed 2026-09-08, locale unknown; no conflicts found in checked representations.

- C-001, subject DuckDB, predicate category, value analytical SQL/query engine; materiality high; first-party homepage and FAQ; independent source https://arxiv.org/abs/2603.02081 (arXiv authors, supports=true); status supported. Publication 2026-03-02 for research; first-party update date unrecorded.
- C-002, subject DuckDB, predicate license/cost, value free under MIT; materiality high; first-party homepage, FAQ and project LICENSE; independent sources none; status self_asserted (first-party consistency confirmed). Copyright 2018–2026; published/modified dates unrecorded.
- C-003, subject DuckDB, predicate governing entity, value DuckDB Foundation / Stichting DuckDB Foundation; materiality high; first-party homepage/FAQ/LICENSE; independent sources none; status self_asserted. Independent current governance verification not completed.
- C-004, subject DuckDB Python/current release, predicate stable version, value 1.5.5; materiality high; first-party installer, Python API and GitHub release; independent sources none; status self_asserted (three first-party representations agree). Release page displays 22 Jul, time 10:51.

No actual assistant answers, citation rates or behavioral measurements were collected. Suggested action is a proposal only. Audit stages completed as reasoning lanes; no delegation or development tests.
