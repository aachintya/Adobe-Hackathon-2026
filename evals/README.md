# Generalization evaluation protocol

The cases in `evals.json` are forward-test specifications. They are not evidence that the marketplace has already generalized. Generalization is measured by running the entrypoint in fresh agent sessions against sites or fixtures that were not used to author the skills.

## Test set

Use a balanced set of controlled and public cases:

- At least 10 controlled sites with private ground-truth findings.
- At least 10 unseen public sites across different industries, architectures, and locales.
- Include healthy sites to measure false positives.
- Include runs with browser, search, or script execution unavailable.

Freeze the URL, collection time, capability set, and expected observations for each run. Do not reveal expected findings, suspected defects, or prior outputs to the auditing agent.

`evals.json` now separates neutral `prompt` text from `private_setup`, `expected_output` and assertions. Only give the auditing agent the prompt, target URL and ordinary user-provided artifacts; keep setup and expected outcomes with the evaluator. The 12 cases include training/search separation, material answer passages, recorded-answer denominators and noncommercial visitor tasks.

## Execution

1. Start a fresh agent session with this marketplace installed.
2. Provide only the public URL and a neutral request to audit AI discoverability and on-site engagement.
3. Allow no more than five minutes.
4. Save the emitted report without editing it.
5. Run `python tests/validate_report.py REPORT.json --evidence EVIDENCE.json --review REVIEW.json` when those artifacts exist; otherwise run schema-only validation and record that narrower scope. Preserve the finalization receipt if produced, but measure actual request-to-delivery independently.
6. Repeat important cases three times to measure output stability.
7. Have a reviewer who did not author the report match findings to the private ground truth.

Require observed question tests and journey steps in the composed report. Assess missing-in-sample conclusions against actual inspected coverage. Do not require a finding in both categories on every site: verified passes and explicit untested lanes are valid outcomes. For citation measurement, preserve raw assistant answers and evaluate cohorts separately; a search-tool result is not a consumer assistant-answer test.

Use the [agent quality evaluator](AGENT-QUALITY.md) to score hash-bound private adjudications of fresh reports. The older `tests/evaluate_report_quality.py` is an authored-example smoke test, not a general accuracy metric.

## Metrics

Record these values per case and in aggregate:

- Finding precision: correct findings divided by all reported findings.
- Overall recall and recall for high-severity ground-truth issues.
- Evidence fidelity: cited evidence directly supports the finding and its scope.
- Severity agreement with the reviewer.
- Action quality on a 0-2 scale for correctness, mechanism, specificity, and verification.
- Correct use of `coverage.not_checked`.
- Schema-valid report rate, completion rate, and runtime.
- Cross-run stability for core findings.

Suggested quality targets are at least 85% precision, 85% recall on high-severity issues, 95% evidence fidelity, 95% schema validity, zero false critical findings, no high/critical findings on healthy cases, and all typical runs below five minutes. These are evaluation targets, not measured results.

## Iteration rule

Change a skill when a failure repeats across cases or exposes a general mechanism. Do not encode a rule solely to make one evaluation site pass. After every change, rerun the complete frozen set and compare precision, recall, false positives, stability, and runtime with the previous results.
