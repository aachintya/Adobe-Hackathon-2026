# Audit design

The marketplace combines four skills around shared evidence. When execution is permitted, optional Python helpers handle source collection and report validation. The host agent interprets the evidence and composes the report; without Python it collects notes through available public fetch/browser tools and checks the report structure manually.

## Evaluation

1. Establish what the site offers, whom it serves and which visitor tasks matter. Preserve the supplied locale and path.
2. Check published search-crawler access and engine-specific indexing controls. Keep intentional restrictions scoped to the affected pages and providers.
3. Test 3-5 relevant questions against saved passages, linked pages and rendered content. Record expected answer elements and the evidence for each outcome.
4. Compare material claims across first-party pages and independent sources. Require an observed contradiction or entity confusion before reporting a trust defect.
5. Trace two public journeys and record observed steps, destinations and retained context.
6. When recorded assistant answers are available, measure mentions and target-site citations separately. Group observations by provider, surface, model, locale and prompt intent; exclude unsuccessful runs from rates.

No overall AI visibility score is inferred from HTML counts, markup, training controls or a single search result. Every finding needs evidence, a clear scope and a verifiable action. Healthy sites can have no findings.

## Implementation

- Standard-library helpers keep the package portable. A browser-capable host agent supplies rendered review.
- Capability declarations do not provision tools. Select the available collection path before starting; source fetch, search, browser interaction, execution, a trustworthy clock and writable output are separate capabilities. Return the report in chat if files cannot be written, and disclose any unavailable check.
- The timed collector captures the landing page before the agent chooses its questions. Resumption reuses captured pages and prioritizes observed task destinations within the total page cap, with fresh robots checks and cumulative request/time records.
- Source extraction retains material passages, link labels and destinations (including empty/missing targets), structured values and indexing directives. Simple table records preserve row/column relationships; complex tables remain explicit review cases. Literal email-recipient mismatches and empty CTA anchors are candidates for review. External CSS and JavaScript behavior require a browser.
- Requests use a dedicated crawler identity, respect applicable robots rules and stay within bounded public navigation. Redirects to another authority are left for explicit agent review of the destination's policy and scope.
- The Python report is a `static_baseline`. The agent completes answerability, trust and visitor-journey analysis and records unavailable checks explicitly.
- The composed draft keeps schema 1.2. A compact review sidecar references collector records and additional host observations; typed assertions check factual fields, exact quotes and observed broken destinations. Finding scopes, answer quotes, reading modes and external corroboration are checked against those records. Semantic entailment, source independence and observation authenticity remain reviewer responsibilities.
- Answered questions map their quotes to every required element, so omitted units, conditions and dates are easier to review. Search excerpts remain retrieval evidence with unknown HTTP status; they do not count as inspected pages, completed journeys or opened-source corroboration.
- The optional offline answer-locality probe measures the shortest span containing reviewer-selected answer/qualifier quotes and tests two word-window alignments. It preserves capture limits and input hashes; its results are review candidates, not automated visibility scores or website defects.
- When Python, files and an observed invocation start are available, `finalize_report.py` publishes a distinct final report and a receipt only after schema/evidence checks and the strict 300-second finalization gate pass. Failed drafts remain available. Hashes bind the checked artifact versions. The command cannot enforce the host's collection cutoff or user-visible delivery deadline; tool-only/manual paths disclose their validation limits.
- The collector defaults to 120 seconds. The full skill targets 280 seconds across collection, browser review, search and composition; missing coverage remains visible when time expires.
- The ZIP has one marketplace root containing the runtime skills, validators and synthetic usage examples. Development tests, controlled test fixtures, evaluations, design notes and validation history stay in the repository. Tests run the extracted fallback and composed-report finalizer from an unrelated working directory.

Schema and collector identifiers are machine-readable compatibility metadata. Package names and documentation do not carry release numbers.

## Repository development

Run `python3 tests/run_all.py` to verify the implementation, then `python3 scripts/package_submission.py` to rebuild `dist/brand-ai-readiness-audit.zip`. The package builder uses an explicit file allowlist and checks both compressed and uncompressed size against 50 MB.

The [manual testing guide](evals/MANUAL-TESTING.md), [evaluation protocol](evals/README.md) and [validation history](VALIDATION.md) document development checks and their limitations. These files are not shipped in the submission ZIP.
