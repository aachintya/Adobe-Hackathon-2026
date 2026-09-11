# Adapt to the host's available tools

The manifest selects skills; `allowed-tools` declares tool needs. Neither installs tools, grants permission, nor guarantees a particular provider's tool names. Map the host's actual capabilities before collecting. A prohibited capability is unavailable even if its executable or tool definition exists.

| Browser | Python execution | Audit path |
|---|---|---|
| Available | Available | Use the optional collector for source evidence and the browser for actual journeys. Use web search for off-site corroboration when available. |
| Unavailable | Available | Collect source evidence and assess questions and linked information. Interactive journeys and rendered behavior remain `not_checked`. |
| Available | Unavailable | Use public fetch and browser tools directly. Inspect relevant passages, rendered controls and safe handoffs; do not execute the Python helpers or validator. |
| Unavailable | Unavailable | Use the host's public text-fetch/search tools. Assess only facts and routes actually inspected; interactive journeys remain `not_checked`. |

Every path still needs a way to obtain website evidence. Python needs permitted network access; browser/fetch tools need access to the target public pages. If no permitted route works and no site evidence is supplied, report that the audit could not be performed. Do not substitute remembered facts for inspection. If search is unavailable, disclose the narrower off-site coverage separately.

## Source evidence without Python

Use public fetch to inspect the supplied page and origin's robots policy before expanding to allowed supporting pages. Keep the exact URL, reading mode, short material passages, link destinations and relevant qualifiers for each inspected source. Share these notes across the sibling skills instead of requiring a Python-produced `evidence.json`.

Record HTTP headers, source HTML, canonical tags and structured-data values only when the tool actually exposes them. A search snippet or cleaned page-text response cannot establish absent schema, an absent header, or a source/rendering gap. A browser's rendered DOM is not the original response HTML. Mark unavailable technical checks `not_checked`; do not invent the missing collector fields.

Search excerpts are retrieval observations, not inspected live pages: exclude them from `pages_checked`, leave HTTP status unknown, and do not call them opened external corroboration. An opened page-text result counts as inspection but still cannot establish source HTML fields or a status the tool did not expose. Retain useful snippets when direct access fails without upgrading their evidentiary scope.

## Execution and output

- Use the helper only with Python 3.10+ and permission to execute it. It needs only the standard library. Resolve the actual interpreter name (`python3`, `python`, or `py -3` on Windows); examples use `python3`. If execution is prohibited, do not attempt it, install a runtime, or switch to another language to bypass the restriction.
- If an execution, network or output-directory failure prevents collection, retain any usable evidence and switch promptly to other permitted tools within the same deadline. Do not repeat an unchanged failing capability probe or wait for new permission to complete the timed audit. Distinguish local tool failures from website failures; do not evade site access controls. Record unavailable lanes when no permitted route works.
- Use a host clock or a supplied UTC audit timestamp. If neither exists, request the missing timestamp rather than fabricate `audited_at`. A date alone does not establish the actual time of the audit.
- Save artifacts when the host offers a writable output location. Otherwise, return the composed JSON report directly in the response; file writing is not a prerequisite for reasoning through the skills.
- Use [report verification](report-verification.md) when execution, saved artifacts and an observed invocation start are available. If the collector was unavailable but Python can validate files, keep a minimal evidence object with `site` and an empty `pages` list and put actual host observations in `review.json`; do not synthesize a crawl. If timing alone is missing, the evidence-aware validator can still run without a timing receipt. Otherwise check the schema and factual support manually, and disclose that automated evidence verification and/or runtime verification were not run. Tool-only reports remain supported; never imply they have an automated receipt.
- `agent_composed` means the host performed the reasoning stages; it does not mean all tools or checks were available. Preserve unavailable lanes explicitly and keep visibility `not_measured` unless actual assistant runs were recorded.

## Manual report check when the validator cannot run

Read `report-schema.json` and use its exact enum values, not the host's tool names. In particular, `coverage.modes` accepts only `static`, `rendered`, `off_site`, and `retrieval`: use `retrieval` for search excerpts, `static` for inspected first-party source or opened page-text evidence, `rendered` only for actual browser observations, and `off_site` for opened external sources. An opened page-text observation still does not prove access to its original HTML. Values such as `web_fetch` or `web_search` are not valid report modes.

Check required fields and nested objects against the schema, then verify each enum, finding/action ID, summary total and severity count. `answered` requires evidence for every required element; unobserved journeys use `not_checked`. Report this as manual review, never as a successful validator execution.

For each finding AND opportunity, compare its premise with the exact observed source and any material qualifier. Confirm a captured field is actually absent rather than omitted by the tool. Count unique inspected first-party pages across tools; use only observed URL aliases. Keep external corroboration tied to opened external sources, and label source information routes separately from rendered interaction. Delete unsupported conclusions or state the unresolved check in coverage. With no file tools, keep these short references in working context instead of requiring a sidecar file.
