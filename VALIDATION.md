# Validation

The September 11 no-browser evaluation used fresh Luna agents on British Museum, Framework and PostgreSQL, followed by a Django run against the revised evidence gate. Original finalization times were 199–240 seconds; Django finalized in 168 seconds. It exposed search-excerpt coverage inflation and incomplete answer support, leading to stricter retrieval handling and required-element mappings. The complete local review and unchanged audit artifacts are under `validation/NO-BROWSER-2026-09-11.md` and `validation/no-browser-2026-09-11/` in the repository (excluded from the submission ZIP). The forward run still exposed a semantic mismatch between affected and fixed versions; consistency validation does not establish entailment.

The complete deterministic suite passed on Python 3.12.14 after these changes, including 30 evidence-gate tests, 8 answer-locality tests, 15 finalizer tests and the extracted-package test. The optional offline locality probe also ran on three captured PostgreSQL cases and the packaged synthetic before/proposed example; those word-window experiments do not establish citation uplift.

A second fresh Luna forward run detected both seeded defects in a newly served local tour-operator fixture (homepage noindex and reservation HTTP 404), with no additional findings, and finalized in 181 seconds. Source evidence, typed assertions, report hashes and the evaluator's private expectations are preserved with the no-browser batch. This is a controlled detection result, not a general recall estimate.

For actual host-agent execution with public browser journeys and independently reviewed reports, see [the September 8–10 live usage evaluation](https://github.com/aachintya/Adobe-Hackathon-2026/blob/main/validation/LIVE-USAGE-2026-09-09.md). It separates observed behavioral results and runtime overruns from the older deterministic checks below. Detailed evaluation artifacts are kept in the repository rather than the submission ZIP.

The [September 10 portability follow-up](https://github.com/aachintya/Adobe-Hackathon-2026/blob/main/validation/PORTABILITY-2026-09-10.md) records the HTTP 308 fix, optional-tool behavior and the full suite passing on Python 3.12.14. The statements below describe the earlier validation revision.

The subsequent [harder-site holdout](https://github.com/aachintya/Adobe-Hackathon-2026/blob/main/validation/HOLDOUT-2026-09-10.md) and [paired browser/no-browser tests](https://github.com/aachintya/Adobe-Hackathon-2026/blob/main/validation/PAIRED-USAGE-2026-09-10.md) preserve runtime overruns, unsupported findings and interrupted runs alongside corroborated observations. Three paired attempts completed, but the evidence review does not establish submission readiness or reliability on arbitrary websites. For independent reproduction, use [the manual testing guide](evals/MANUAL-TESTING.md).

Run `python3 tests/run_all.py` (or your Python 3.10+ executable) to reproduce the deterministic checks. The suite validates all four skills, local HTTP fixtures, report semantics and the actual extracted ZIP.

The evidence-verification update adds offline cases for captured-field contradictions, incomplete evidence, incorrect source references, coverage counts, broken-link resolution, external-source support and reading modes. Finalization tests exercise validation failures, deadline boundaries and artifact publication. These are consistency checks; passing them does not establish that arbitrary natural-language conclusions follow from the evidence or that fresh host-agent runs meet the five-minute delivery requirement. See the [verification contract](skills/audit-orchestrator/references/report-verification.md).

On 2026-09-11 (Asia/Kolkata), the complete suite passed on Python 3.12.14 with the new gates, including all 23 evidence tests, 15 finalization tests and the extracted-package test. The evidence suite includes a focused landing-redirect count correction. A separate agent then completed a neutral audit of a newly served three-page local pottery-studio fixture: three answered questions, two source routes, no findings or opportunities, and successful first-attempt finalization at 155.72 seconds. Artifact work ended at 170.15 seconds; user-visible delivery was not measured. This healthy control supports one source-only workflow, not browser/external-search behavior or general public-site accuracy. The agent had prior knowledge of the gate design but received no fixture verdict or mid-run coaching. Raw evidence, draft, review, final report, receipt, timing and parent hash checks are preserved under `validation/evidence-verification-2026-09-11/` in the repository and excluded from the ZIP.

Verified locally on 2026-09-05 with Python 3.12.6: the full suite passed, including 17 practical-audit tests and seven added edge-case tests. Four-page public collection checks on Plausible and Python.org completed in 7.56 and 8.36 seconds respectively, with no collection errors and valid reports.

## Coverage

- Skill frontmatter, reference paths, one marketplace entrypoint and the bundled report schema.
- Healthy and problem fixtures; robots status behavior, rule specificity, merged groups, wildcards, Allow ties and percent encoding.
- Deep paths, sitemap discovery, tracking parameter removal, content types and redirects blocked before reaching another authority.
- Material passages, nested link labels, repeated metadata, hidden/navigation exclusion and structured-data parsing.
- Separation of search and training controls; engine-specific indexing directives and repeated HTTP header scope.
- Recorded-answer metrics, own-domain citation matching, failed-run exclusion and separate provider/prompt cohorts.
- Evidence requirements, action fields, severity counts and honest measurement status.
- Building and extracting the ZIP into a path with spaces, then running the fallback and report validator from an unrelated working directory without installation or credentials.

## Issues reproduced and corrected

- Valueless HTML attributes could crash extraction. They are handled as empty attribute values.
- A malformed navigation URL could discard an otherwise readable page. Invalid links remain recorded and are skipped during navigation.
- Relative links ignored the page's first `<base href>` and URL normalization dropped path parameters. Collection now preserves both.
- Broken gzip robots responses and malformed chunked responses could terminate the audit. They now produce explicit unknown-policy or collection-error evidence.
- Reports could claim `agent_composed` coverage without question or journey records. Validation now requires 3-5 question records and two journey records, allowing explicit `not_checked` outcomes.
- One recorded answer could be counted in multiple visibility cohorts. Validation now rejects repeated run IDs across cohorts and duplicate cohorts.

These cases are exercised in `tests/test_edge_cases.py` alongside the existing suite.

## Limits

Deterministic tests establish collection, reporting and packaging behavior. They do not establish unseen-site precision/recall, live assistant citation rates, causal visibility uplift, accessibility conformance or behavioral outcomes. Browser and search reasoning still need full agent evaluation using `evals/README.md`.

The included example is a controlled synthetic case. Public-site smoke checks establish collection compatibility only, not detection accuracy or a runtime guarantee for every website.
