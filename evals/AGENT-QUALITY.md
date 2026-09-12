# Agent report quality evaluator

`score_agent_reports.py` uses only explicit private adjudications. The expected file is `{ "expected_roots": [{"id":"R1", "severity":"critical"}] }`.
Set `ground_truth_complete: false` for public sites whose full defect set is unknown. Accepted findings may reference independently reviewed roots, but recall metrics stay null; reviewing reported findings is not a census of missed defects.
Every `findings` and `proactive_opportunities` item must have one entry in `adjudications`, identified by `item_id`, with `verdict` (`correct`, `partial`, `false`, `duplicate`, or `unsubstantiated`). Correct and partial findings need a known `root_id`; duplicate findings need an accepted sibling for that root. Opportunities may have a null root ID: a useful suggestion need not repair a defect. Only one accepted finding may claim a given root; mark additional reports of it as duplicates.

Finding entries require integer 0, 1, or 2 fields: `scope`, `evidence`, `severity`, `action_correctness`, `action_mechanism`, `action_specificity`, and `action_verification`. Opportunity entries require the same evidence and action fields (scope and severity may be omitted for opportunities). The `answer_support` object is indexed by `assessment.intent_tests` index and must contain every `required_elements` value with an explicit integer 0, 1, or 2.

Adjudications must include the exact `report_sha256`, and the API requires `report_path` or `report_bytes` so the hash is checked against report bytes. Runtime is independently adjudicated with timezone-aware `observer_start`, `delivery`, `completion` (`completed`, `failed`, or `interrupted`), and `timestamp_kind` (`exact_delivery` or `observed_completion_upper_bound`). Use `timestamp_kind: "not_measured"` with an explicit `reason` when an independent start or delivery time was not captured; duration remains null and no timing success is credited. A negative duration or malformed timestamp is invalid. Report runtime fields are never trusted.

Evidence and action means include findings and opportunities, including unsupported claims. Scores use 0–2 scales; finding precision and weighted recall give partial findings half credit. `root_recall_full` excludes partial matches; `root_recall_partial` includes them. These are reviewer judgments, not automatic truth verification.

Any missing, unknown, malformed, stale, or unreviewed entry returns `incomplete_run` with null quality metrics and CLI exit code 2. Zero findings is valid and gives null precision; zero expected roots gives null recall.
`complete` means the adjudication inputs are complete, not that the audit succeeded. Audit completion is reported separately under `runtime.completion`; exit code 0 certifies only a consistent evaluation record, not a passing quality threshold.

```sh
python3 evals/score_agent_reports.py report.json --expected private-roots.json --adjudications adjudications.json
```
