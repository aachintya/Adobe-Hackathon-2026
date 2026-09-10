# Live marketplace usage evaluation

The marketplace was exercised by independent auditor agents against public websites, with a separate reviewer navigating the real sites and checking the emitted evidence. The user requested actual usage testing; Python collection and JSON validation alone were not treated as successful agent audits. The Round 3 handout supplied the evaluation priorities: detection, actionable fixes, generalization, read-only behavior and a typical runtime below five minutes.

Baseline: commit `3a68ea35c0f836bfa4ec45fb1e2dde18c194afc6`. Runs took place September 8–10, 2026. This field-evaluation pass is closed with the coverage gaps below; it is not a certification of benchmark readiness. Method, prompting boundaries and interruptions are preserved in [the protocol](live-usage-2026-09-09/protocol.md); both instruction revisions are in [the revision record](live-usage-2026-09-09/revision-tested.txt).

Publication note: repository artifacts are sanitized transcripts as documented in [publication notes](live-usage-2026-09-09/PUBLICATION-NOTES.md); raw local paths and two observed tracking parameters were removed. Findings, judgment errors, timestamps and counts were retained. The later user-authorized code cleanup and environment guidance are documented in [the portability follow-up](PORTABILITY-2026-09-10.md), separately from the historical instruction-only trials below.

## What was observed before changes

| Site | Real task and evidence | Agent outcome | Reviewer assessment |
|---|---|---|---|
| Linear | Compare plan features and switch annual/monthly billing. Visible availability icons in sampled pricing cells have no text/accessible equivalents. Nearby plan-card prose answers some comparisons. | Second baseline caught a scoped medium extraction issue. | Supported; the functioning price toggle is not a contradiction. |
| DuckDB | Choose Python LTS, follow its documentation, then use its installation link. The return drops LTS and selects current with an unpinned command. | First report caught medium context loss; the next fresh run tested current CLI/Python only and missed it. | Independently reproduced; useful evidence of sampling instability. |
| DuckDB | Inspect client-overview metadata versus visible client/version facts. | Second baseline found literal build-template tokens in description fields, rated low. | Supported by preserved source evidence; not a claim of missing body content or failed citations. |
| GOV.UK | Reach adult-renewal preparation and processing guidance; distinguish base passport fees from optional Check and Send. | First report made a wording opportunity; second called the same ambiguity a medium finding. | Ambiguity is supported, but classification varies. No incorrect amount actually charged was demonstrated. |

The second GOV.UK report marked the base-cost question `partial` even though its frozen required elements were supported and the optional charge was resolved by another inspected source. That is a reporting-status inconsistency, distinct from the legitimate localized wording concern.

No reviewed report asserted actual assistant citation rates or recommended modifying a production site. The reviewers did not submit applications, sales forms, purchases, messages or authenticated actions.

## Instruction improvements

- Make the second journey exercise a decision-changing non-default option and its handoff, when a safe public choice exists. Verify the destination's actual selection/instruction; a dropped query parameter alone is not a defect.
- Check required answer elements individually. A resolved answer stays `answered`; a separate wording issue does not automatically make the answer partial.
- Verify row/column/value relationships in decision-critical comparison tables, including nonvisual alternatives and nearby equivalent prose.
- Stop collecting by elapsed 180 seconds and reserve 100 seconds for concise composition, validation and delivery. The full invocation requests a 90-second static cap and reads relevant evidence instead of dumping the whole collection.
- Keep compact observation notes during the run and count distinct first-party pages once across reading modes.

The Luna runs then exposed additional reporting failures. Final narrow corrections make journey status depend on the observed cause, require an applied material result rather than a changed control label, keep tool failures out of website-owner opportunities, require clock-derived timestamps/durations, and check copied source URLs and prose totals. Original reports were not repaired to make these changes look successful.

Changes are instructions and references only. No collector, validator, application code or unit tests were changed. The skill-creator workflow guided focused changes and independent behavioral verification; its structural validator passed for all three edited SKILL.md files.

## Post-change behavioral evidence

The fresh [DuckDB audit](live-usage-2026-09-09/verified-duckdb/report.json) selected Python LTS, followed client documentation, followed the installation return link, observed current-version selection and exercised manual LTS recovery. Its single medium finding matches the separately recorded reviewer reproduction. All four frozen questions remained `answered`, with the version-specific journey issue recorded separately. This is one successful repeat of the revised sampling and answer-status behavior, not proof that every run will catch it. The metadata issue found in a different baseline was not reported by this run; the probes remain sampled rather than exhaustive.

The run did **not** meet the runtime target: report validation took 617 seconds and the last recorded clock was 625 seconds from start. Collection reportedly ended before 180 seconds, but composition and artifact-writing retries overran. The evaluator sent a finish-from-existing-evidence reminder after five minutes, without supplying a defect or hint. Treat this as an over-budget run with an evaluator timing intervention, not an uninterrupted within-budget success. [Ledger](live-usage-2026-09-09/verified-duckdb/ledger.md) and [timing](live-usage-2026-09-09/verified-duckdb/timing.json) preserve the details; the final timing-file write and response followed the last clock observation.

At the user's request, subsequent trials used `gpt-5.6-luna`, medium reasoning, in parallel. Model, session reuse and capabilities differ, so these cannot isolate the effect of the instructions.

| Luna case | Actual scope and report outcome | Reviewer decision |
|---|---|---|
| [GOV.UK](<live-usage-2026-09-09/luna-govuk/composed report.json>) | Fresh session; four answered questions; standard renewal and overseas public handoff completed; zero findings. | Supported sampled outcomes. One malformed supporting URL; no repeat adjudication of the optional-fee ambiguity. |
| [Standard Ebooks](live-usage-2026-09-09/luna-ebooks/report.json) | Fresh session; catalogue-to-title completed; four questions answered, one partial; reading destination client-blocked; zero findings. | Incorrectly calls the tool block `friction` and assigns a website-owner opportunity. Changed sort label does not prove an applied constraint handoff. Reported 249 s is actually 289 s from timestamps. |
| [Fastmail](live-usage-2026-09-09/luna-fastmail/report.json) | Reused GOV.UK session; four answered questions from static/retrieval evidence; both journeys `not_checked` because no browser was exposed. | Appropriate abstention, not an interactive pass. Future manually entered audit timestamp and prose count mismatch. |
| [IKEA India](live-usage-2026-09-09/luna-ikea/report.json) | Reused Ebooks session; four answered questions, one not checked; both journeys unrendered; zero findings. | Appropriate journey limits, but proposed delivery-guidance work is unsupported by the sampled pages. Future audit timestamp. |

[Detailed adjudication](live-usage-2026-09-09/reviewer-adjudication.md) separates supported findings, reporting errors, missed checks and overly speculative opportunities. The final instruction corrections were made only after these reports were frozen. Two guided browser-recovery rechecks still exposed no browser in the Luna sessions and stopped safely. They test abstention, not complete final-revision behavior.

## Timing and completeness

| Run | Report validation | Last recorded elapsed | Treatment |
|---|---:|---:|---|
| baseline2-govuk | 278 s | 328 s | Report met five minutes; final evidence/timing bundle exceeded it. |
| baseline2-duckdb | Completed, separate time unrecorded | 324 s | Exceeded five minutes. |
| baseline2-linear | Parent validation available | Final timing missing | Report can be reviewed; runtime is unknown. |
| verified-duckdb | 617 s | 625 s | Revised instructions; over budget, with evaluator timing reminder. |
| luna-govuk | 259.306 s | 288.447 s | Below five minutes at last clock; above the internal 280 s target. |
| luna-ebooks | 289 s from timestamps | 289 s from timestamps | Original 249 s field is incorrect; below five minutes at last clock, above 280 s. |
| luna-fastmail | 89.938 s | Same clock as validation | No browser; no separate final-delivery timestamp. |
| luna-ikea | 118 s | Same clock as validation | No browser; no separate final-delivery timestamp. |

None of these clocks measures a later final-response delivery event. Browser-unavailable durations are not comparable to full browser audits. Token billing was not measured; using Luna is not a measured cost-saving percentage.

The initial three baseline sessions and first three revised sessions were interrupted by account usage limits. Saved static drafts are not composed-report successes. Untimed saved reports are not used to claim runtime performance. The interruptions and complete outputs remain preserved separately.

The September 9 Fastmail trial also stopped with a static draft and partial ledger before the September 10 continuation. Its overnight interruption is excluded from active runtime estimates and it is not a completed composed audit. At the user's request, subsequent trials use Luna medium in parallel; report these separately from the earlier inherited-model sessions.

## Independent holdout reviewer checks

Before the holdout trials, the reviewer navigated Fastmail, Standard Ebooks and IKEA India without giving these observations to auditors or using them to author the first instruction revision. Fastmail's pricing matrix supplies accessible availability labels and its monthly toggle works; Standard Ebooks routes a reader from catalogue to book to device-specific help; IKEA's Indian delivery guidance retains region and exposes readable service/fee conditions. These are targeted reviewer observations, distinct from the later Luna audits. [Reviewer evidence](live-usage-2026-09-09/reviewer-observations.md) records exact routes, limits and dates. Do not credit the reviewer journeys to browser-unavailable auditors.

## Evidence counts and final checks

- Ten preserved composed reports across six public sites pass `tests/validate_report.py`. Eight report rendered evidence; Fastmail and IKEA's Luna reports explicitly do not. Interrupted static drafts are excluded.
- The reports contain five finding instances representing four underlying issues, including the repeated DuckDB LTS issue. Their scoped observations are supported; the GOV.UK ambiguity's classification remains variable. Two Luna opportunities promote inadequate coverage/tool problems into website-owner work and are not accepted as demonstrated improvements.
- Emitted journey statuses total 13 completed, 3 friction and 4 not checked. One of the 3 friction records is the misclassified Standard Ebooks tool block; reviewer adjudication makes that an additional not-checked journey. These are recorded outcomes, not a population completion rate.
- Emitted question statuses total 40 answered, 2 partial and 1 not checked. The earlier GOV.UK partial result is a known status inconsistency. Questions differ across runs, so counts do not measure improved accuracy.
- All seven revised instruction files are fingerprinted; the final three-file correction has separate hashes. Structural skill validation and `git diff --check` pass. No collector/application/validator code, unit suite, website, account or production data was changed.

The portable reports, ledgers and timings are in [the evidence directory](live-usage-2026-09-09/). Raw collector bundles and interrupted artifacts remain outside the repository in the local sibling `field-testing-2026-09-08/` directory.

## Limits

This is agent-driven field evaluation with model review, not a human usability study. The site set is small and selected for diversity; there is no exhaustive labeled ground truth, so overall precision/recall and population generalization cannot be claimed. No consumer-assistant recommendation/citation experiment, conversion measurement, full accessibility audit, mobile study or causal uplift measurement was performed. Changing skill instructions has no effect on the audited websites themselves.

Remaining validation gaps: no completed post-change Linear rerun; no complete fresh end-to-end run after the final instruction correction; no browser-enabled Luna Fastmail/IKEA audit; runtime and optional-fee severity stability are unresolved. The final guided rechecks verify safe stopping only. These limits are retained instead of presenting a universal pass or claiming that instruction changes alone solved runtime.
