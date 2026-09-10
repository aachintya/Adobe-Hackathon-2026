# DuckDB public audit ledger

Start: 2026-09-09T17:43:34Z; epoch 1788975814. Output belongs to a fresh audit, with no prior-run inspection. Read and applied orchestrator and three sibling skills with required references. Python collector executed with --max-seconds 90: 12 HTML pages, 22 requests, 14.65 seconds. Six capped records and eight HTTP 308 errors retained in evidence.json. Only the report validator was executed; no development tests or repository edits.

Questions frozen before supporting-page judgment and search: analytical SQL + local/in-process deployment + integrations; free/license + governance; current stable version + install instruction; Python command + corresponding client docs. LTS was a separate journey constraint, not a retroactive question requirement.

## Actual browser navigation

Background IAB tab 1; English page, macOS detected; observed screenshot 1280 x 720. Actions observed 17:44–17:46 UTC; exact individual action times were not recorded.

1. Opened https://duckdb.org/. Read analytical/in-process and MIT/Foundation facts. Clicked Get DuckDB (AX 26).
2. Reached /install/ and inspected settled https://duckdb.org/install/?platform=macos&environment=cli. CLI selected, 1.5.5 current selected; curl https://install.duckdb.org | bash. This completed the default task; no software executed.
3. Selected Python (AX 97): https://duckdb.org/install/?platform=macos&environment=python; pip install duckdb; Python documentation link.
4. Selected 1.4.5 (LTS) (AX 116): https://duckdb.org/install/?platform=macos&environment=python&version=lts; pip install duckdb==1.4.5; documentation href /docs/lts/clients/python/overview.html.
5. Clicked Client documentation page (AX 126), final https://duckdb.org/docs/lts/clients/python/overview. Visible 1.4 LTS; Installation prose uses unpinned pip install duckdb; note separately describes latest stable 1.5.5. The latest-stable note alone is not treated as a contradiction.
6. Clicked installation page in that prose (AX 128), final https://duckdb.org/install/?environment=python&platform=macos. Python remained selected, but 1.5.5 current selected and unpinned command shown. Settled screenshot verified.
7. Manually selected 1.4.5 LTS (AX 43), final https://duckdb.org/install/?environment=python&platform=macos&version=lts. Pinned 1.4.5 command restored. One non-default combination checked. No authentication, forms, downloads or command execution.

## Exact retrieval queries and sources

web.run search, 2026-09-09, approximately 17:44:23 UTC, locale unknown. One four-query batch returned an aggregate pool, with no per-query rank mapping inferred:

- DuckDB
- embedded analytical SQL database query parquet local Python
- DuckDB current stable release September 2026
- DuckDB Foundation MIT license governance

Relevant returned pool: https://duckdb.org/ ; https://duckdb.org/faq ; https://duckdb.org/install/ ; https://duckdb.org/release_calendar ; https://duckdb.foundation/ ; https://github.com/duckdb/duckdb ; https://ducklabs.com/about/ ; https://duckdb.org/2026/08/26/ducklabs-to-join-aws ; https://duckdb.org/history/ ; https://en.wikipedia.org/wiki/DuckDB . Additional secondary articles and Reddit results were not used to substantiate findings. Search results do not measure assistant citation rates.

Opened-source claim ledger, all observed 2026-09-09:

- https://duckdb.foundation/: associated first-party entity. “The non-profit Foundation holds the core intellectual property”. MIT and named board statements agree with home/FAQ. Not independent endorsement.
- https://github.com/duckdb/duckdb: first-party repository. “DuckDB is a high-performance analytical database system.” CLI, Python, R, Java and Wasm clients listed. Supports entity/offer/integrations. Page instructions were not executed.
- https://duckdb.org/release_calendar: 2026-07-22 / 1.5.5 in past releases; 2026-09-16 / 1.5.6 upcoming. Supports current versus planned distinction.
- https://duckdb.org/docs/lts/clients/python/overview: fetched as well as rendered. Installation text gives pip install duckdb under 1.4 LTS; confirms scoped continuity evidence.
- https://en.wikipedia.org/wiki/DuckDB: opened as lead; Foundation section relies on first-party sources. Not treated as independent proof or basis of technical findings.
- https://www.aboutamazon.com/news/company-news/aws-ducklabs: found in collected https://duckdb.org/library/aws-ducklabs-about-amazon/ link. Opened Amazon statement says “We are not acquiring the DuckDB open source project”. It says project remains MIT under the independent Foundation. Interested counterparty, corroborates entity boundary but not independent endorsement or completed transaction.

## Stage decisions and limits

Crawl: robots 200, wildcard allows sampled current paths for named search agents; old documentation disallows recorded separately. /design noindex candidate discarded because it is an explicit Redirecting stub with canonical /design/manual/. No JSON-LD parse errors in 12 collected pages; home SoftwareApplication price 0/MIT agrees with copy. Source install main text lacks dynamic command but rendered browser supplies it and home includes current commands; no site-wide extraction failure asserted.

Entity: home/FAQ/Foundation/Amazon agree on tested license/governance boundary. Four frozen questions answered. No material conflict established. No citation-rate inference.

Engagement: default journey completed. LTS Python instruction and return-link drift merged into F-001. Recovery directly exercised. Not checked: other client/version combinations, mobile, keyboard/focus, contrast, performance, analytics, provider IPs or actual assistant citations.

Artifact authoring required retry after apply_patch rejected a combined delete/add for the same path; the rejected call performed no write. Report was then replaced with separate allowed patch operations and validated. Timing records actual overrun.
