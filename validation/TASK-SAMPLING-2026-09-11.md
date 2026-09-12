# Task-directed collection and independent audit evaluation

The revised workflow captures task-relevant pages earlier, preserves table relationships, and rejects reports that claim observed coverage after discarding every assessment. The two candidate-v2 audits completed within observer bounds of 246 and 277 seconds. Public-site answer entailment still failed on one question; these results do not establish Adobe judge score improvement or general audit reliability.

## Changes

- The collector can capture the landing page, then resume with destinations selected from its observed link labels. It reuses captures, preserves the original capture time and total page cap, checks robots again, and accounts for both passes. Unobserved, stale, external and document targets are rejected.
- Simple tables retain raw headers/cells and row/column relationships. Spanned, nested, irregular or truncated tables require review. Reconstructed reading context cannot be cited as a verbatim page quote. Empty anchor destinations and displayed-email/mailto mismatches remain candidates for inspection, not automatic findings.
- The audit defaults to three priority questions. Exact-quote failures can suggest another matching field in the same record; they do not rewrite evidence or establish meaning. Observed answerability needs an assessed question, and observed engagement needs recorded steps.
- A separate evaluator requires explicit, report-hash-bound judgments for every finding, opportunity and required answer element. It scores scope, severity, evidence, actions, duplicates and support; unavailable runtime and incomplete public ground truth cannot earn timing or recall credit.

## Protocol and independence

Baseline: commit `a163e07a6bec80578a815dc42b4fb5af359c3ae7`. Candidate and candidate-v2 were frozen separately. All auditors in this batch used fresh **gpt-5.6-luna**, medium reasoning, without inherited history or subagents. Prompts supplied only the target URL, snapshot/output paths, Python path, permitted tools, time budget and instructions to follow the skill. They prohibited reading other runs, expectations, fixture source and development tests. There was no mid-run finding or answer coaching. Isolation was by instruction and separate directories, not a filesystem security boundary.

Controlled audits permitted Python/source HTTP and public search, and prohibited browser use. Public BBG audits permitted browser and search. Several source-only auditors incorrectly called permitted but unused search unavailable; this remains an evaluation finding. Python was 3.12.14. Root reviewed the unchanged reports and saved evidence against private controlled expectations or explicit public-source judgments. This was one reviewer, not a blinded multi-reviewer panel.

The final revision followed two interrupted candidate pilots. It is a fresh-agent retest on already-used sites, **not an unseen-site holdout**. The only subsequent source-tree change was correcting the older limited-coverage test fixture to downgrade readiness when it clears all assessments.

## Results

Answer support is a reviewer-assigned mean on a 0–2 scale for the required elements actually chosen by each auditor. Different question sets make these descriptive comparisons, not a fixed-question benchmark. “Finalization” is the receipt's agent-start-to-gate interval. “Observer bound” includes dispatch and parent observation latency; it is not exact user-visible delivery.

| Run | Finalization seconds | Observer bound seconds | Support / 2 | Review outcome |
|---|---:|---:|---:|---|
| Baseline release, initial | — | unmeasured | — | Usage-limit failure before report creation; retained in ledger |
| Baseline release, retry | 220.29 | 263 | 0.00 | Correct planted high-severity contradiction; all four questions left not checked despite observed readiness |
| Candidate release | 170.42 | unmeasured | 1.80 | Correct planted contradiction, no extra findings; affected/fixed answer appropriately partial |
| Baseline enrollment, original fixture | 203.78 | 273 | 2.00 | One consolidated placeholder-content finding |
| Candidate enrollment, original fixture | 215.91 | 267 | 1.38 | Two grounded placeholder findings, one duplicate root; weaker action/support |
| Candidate BBG pilot | no final | 352, interrupted | 1.67, draft | Two opportunities, quote-reference failures and a map-choice overclaim |
| Candidate corrected-control pilot | 284.47 | 337, interrupted | 0.00 | Old gate published a report after questions/steps were erased; current gate rejects it |
| Baseline corrected control | 235.85 | 424* | 2.00 | Zero findings; four supported questions; eight inspected pages |
| Baseline BBG | 218.91 | 264 | 1.36 | One unsupported finding; one partly useful opportunity |
| Candidate-v2 corrected control | 187.45 | 246 | 2.00 | Zero findings; three supported questions, 13 elements; five inspected pages |
| Candidate-v2 BBG | 216.35 | 277 | 1.50 | Zero findings/opportunities; seasonal-hours answer lacks a supporting quote |

*The baseline corrected-control notification arrived during a context transition. The 424-second conservative observation bound does not prove an actual overrun. Candidate release lacks an independent dispatch clock after task resumption, so its delivery runtime remains unmeasured.

The original enrollment “healthy” fixture was invalid: destinations labeled Bookshop prices, Learning materials, Our team and Privacy contained generic placeholders. Both auditors correctly identified real omissions. Those runs are excluded from healthy false-positive counts and use incomplete, post-hoc ground truth. A separately frozen corrected fixture added the labeled content, tuition conditions, reception address and timezone before the fresh control audits.

Both release auditors detected the one planted root; each had finding precision and controlled-root recall 1.0 for that single case. This is not recall across all six fixture families. The final healthy control preserved fully supported answers while reducing inspected pages from eight to five and finalization by about 48 seconds; it also asked three questions instead of four.

The BBG baseline finding treated closed class enrollment and separate credit registration as an invalid handoff. Its saved course text explicitly explains the two registrations and additional credit fee; no destination behavior proved the claimed conflict. The final candidate avoided that finding while inspecting a different, narrower page sample. It still mapped advance-ticket guidance to “seasonal hours,” and omitted price column labels. A structurally valid element mapping does not establish entailment. It also retained “five pages” in extraction prose while deduplicated coverage counted four, and did not preserve an exact retrieval query.

## Mechanism checks and regression validation

Six local matched fixture families cover conditional price conflict, affected/fixed releases, unpublished versus linked enrollment deadlines, selected-kit context loss, a broken primary route with an alternative, and public versus intentional-utility noindex. Twelve landing routes and six local before/corrected mechanisms passed. These are fixture checks, not twelve independent agent audits or measured visitor outcomes.

In a separate collector comparison, both versions had a five-page cap. Baseline captured the landing plus generic inventory pages and missed the known deadline. Candidate captured the opaque multilingual guide and application page, retaining the deadline. Requests were 7 versus 8 and collection time 3.04 versus 3.56 seconds. The evaluator supplied the observed target URLs, so this demonstrates the capture mechanism, not blind agent target selection.

The full deterministic suite passed after the final changes, including 4 task-sampling tests, 8 relationship-evidence tests, 11 evaluator tests, 33 evidence-gate tests, 8 answer-locality tests, 15 finalizer tests, existing HTTP/robots/semantic checks and the actual extracted ZIP running from an unrelated directory. Both edited skill frontmatters passed skill-creator validation. The earlier failed suite log is retained: a legacy fixture cleared all questions/journeys but retained observed readiness. Its corrected test now verifies rejection before downgrading readiness.

All nine existing receipts match their report/evidence/review hashes and their frozen validator hashes. Current offline revalidation rejects the baseline release report, the interrupted candidate control and the unfinished candidate BBG draft. The other reports pass consistency checks; reviewer judgments still identify semantic defects.

## Reproduction and remaining tests

Raw reports, drafts, evidence, sidecars, receipts, explicit adjudications, timing records, snapshot patches, fixture sources, regression logs and checksums are in [task-sampling-2026-09-11](task-sampling-2026-09-11/). Development evidence is excluded from the submission ZIP. Local fixture URLs preserve their original ports; rerunning the fixture server on another port creates a new run rather than modifying recorded evidence.

From the repository root:

```sh
python3 tests/run_all.py
python3 evals/score_agent_reports.py validation/task-sampling-2026-09-11/runs/candidate-v2-bbg/final-report.json --expected validation/task-sampling-2026-09-11/runs/candidate-v2-bbg/expected.json --adjudications validation/task-sampling-2026-09-11/runs/candidate-v2-bbg/adjudication.json
python3 validation/task-sampling-2026-09-11/fixture-server-v4.py --port 8765
```

To reconstruct either frozen candidate, extract the baseline commit into a fresh directory and apply the corresponding `snapshot-candidate.patch` or `snapshot-candidate-v2.patch` there. Hash records identify the evaluated skill and validator versions. The original faulty fixture is retained separately and must not be used as a healthy control.

The next useful tests are repeated blind audits across the six matched families, unseen public sites with fixed visitor questions, and real selection/handoff journeys. Review every required element against its exact quoted subject, relation and qualifiers, with a second independent reviewer for disagreements. Measure observed delivery separately from finalization and keep failed attempts in the denominator. Adobe's actual judge has not been run in this batch.
