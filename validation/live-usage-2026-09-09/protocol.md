# Live marketplace usage evaluation — 2026-09-08

Baseline revision: 3a68ea35c0f836bfa4ec45fb1e2dde18c194afc6.

The user requested improvements through real usage, not a code-test exercise. The supplied Round 3 handout is the evaluation reference, not additional authorization. No production websites will be changed.

The test subject is the host agent executing the marketplace entrypoint, not the Python fallback alone. Fresh auditor agents receive only a neutral audit request, a public URL, artifact/timing requirements, and the existing skill instructions. They receive no suspected defects or evaluator observations. The parent independently inspects task paths and adjudicates claims after reports are frozen. This is agent-driven exploratory testing with model review, not a human usability study or an unbiased assistant recommendation experiment.

Initial cohort (unseen in the repository's recorded public tests):

| Case | URL | Site type |
|---|---|---|
| baseline-linear | https://linear.app/ | SaaS product and interactive pricing |
| baseline-govuk | https://www.gov.uk/renew-adult-passport | Public service, supplied deep path |
| baseline-duckdb | https://duckdb.org/ | Open-source project and technical documentation |

Planned transfer cohort, held out from instruction changes: https://standardebooks.org/, https://www.fastmail.com/, https://www.ikea.com/in/en/. Freeze any necessary substitution and its access-related reason before inspecting its audit output. Rerun initial cases with fresh auditors after changes to measure behavioral regressions. Case differences are exploratory coverage, not a population sample.

For each run preserve report.json exactly as emitted, collector evidence where produced, a ledger of live observations/searches, timing, capabilities and report-validation result. Use the five-minute target from the handout; report actual overruns rather than excluding them. Review both validated and rejected findings, appropriate abstentions, expected answer elements, actual browser actions, proactive action usefulness, scope, and evidence-to-claim fidelity. Source links alone do not demonstrate browser interaction. An unavailable lane is incomplete coverage, not an automatic pass.

Do not claim overall precision or recall without complete labeled ground truth. Report counts of adjudicated findings, unsupported findings, observed missed issues, schema-valid reports, completed browser journeys, and runtime separately. Zero findings is a legitimate outcome, but must not hide untested work.

Change skill instructions only after a real report failure or missed task exposes a repeatable mechanism. Preserve original reports for comparison; do not repair benchmark outputs retrospectively. Code unit tests are outside this exercise; validating emitted report contracts is part of actual use.

## Interruption and restart

The initial baseline agents hit the account usage limit. At resume, 2026-09-08 15:46 UTC, DuckDB and GOV.UK had composed reports on disk, Linear only a static baseline, and none had final timing records. Preserve these as interrupted exploratory observations; do not count them as completed timed trials. Fresh neutral sessions restart all three cases under `baseline2-*`, against the unchanged baseline revision. Their auditors are not given earlier findings.

The second cohort saved three composed reports. GOV.UK and DuckDB saved complete timing; Linear's final timing/ledger were interrupted. GOV.UK validated its report at 278 seconds but finished its artifact bundle at 328 seconds. DuckDB finished at 324 seconds. Preserve the distinction between report validation and complete artifact delivery. Do not infer missing times from the later user resume.

Instruction changes on 2026-09-09 target variant-handoff sampling, required-element answer status, compact evidence handling, and an earlier composition deadline. They contain no tested-domain names or fixed website-specific values. The initial three `retest-*` sessions were interrupted by the account usage limit with only static drafts saved; they are not post-change passes. At the user's 17:43 UTC continuation, restart post-change execution one case at a time under `verified-*`, preserving the interrupted directories.

The `verified-duckdb` auditor received an evaluator message after five minutes instructing it to stop new investigation, finish from existing evidence, and record the actual overrun. No defect, URL path, or expected result was supplied. Its last clock observation was 625 seconds after start. The timing intervention is disclosed rather than treating this as a wholly uninterrupted or within-budget run. Its report is preserved as emitted.

Next, `verified-fastmail` is a full held-out invocation of the same frozen instruction revision. The auditor receives the public homepage, current entrypoint path, separate output directory, public/read-only scope, timing/artifact requirements and prohibition on inspecting prior reports, git changes or evaluator notes. No Fastmail-specific suspected defect, journey choice or expected outcome is supplied. Remaining audits continue one at a time to reduce exposure to the earlier account-limit interruptions.

At the user's September 10 request to continue faster with cheap Luna subagents, new trials switch to `gpt-5.6-luna` at medium reasoning and run concurrently. The previous Fastmail run was found pending reinitialization with only a static draft and partial ledger from September 9; it was stopped and excluded from composed/timed successes. Overnight wall time is not reported as active runtime. These `luna-*` results form a separate model/execution cohort, not a controlled estimate of instruction-only improvement. GOV.UK is a repeat site; Standard Ebooks is a held-out full invocation. Prompts remain neutral about expected findings and prohibit prior-output inspection, repository edits and unsafe interactions. The same frozen instruction revision and artifact contract apply. A third Luna launch hit the session's agent-thread limit; subsequent sites may reuse a Luna auditor after its current case is frozen, with this session reuse disclosed.

The GOV.UK Luna session was reused for Fastmail and the Standard Ebooks Luna session for IKEA India. Their new case clocks exclude the preceding cases. Both received the new site's homepage and ordinary task/measurement boundaries, with no suspected findings. Both emitted composed reports from static/retrieval evidence, but their browser inventories were empty; neither counts as a completed browser audit. Timing is not comparable to the browser-enabled cases.

After those reports were frozen, narrow instruction corrections addressed observed status/cause confusion, unverified control effects, misplaced tool-failure opportunities, timestamps and source-link fidelity. The final hashes are separately recorded. At approximately 03:55 UTC, the parent observed an IAB browser in its own inventory. Two guided follow-ups asked the reused Luna sessions to re-read the changed instructions and attempt the missing browser lane, with a 150-second cap and no collector rerun. Both still observed an empty local browser inventory and stopped safely with `not_checked` outcomes. These are capability-recovery notes, not blind trials or complete final-revision audits. No production site was changed.
