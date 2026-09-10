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

## Execution and output

- Use the helper only with Python 3.10+ and permission to execute it. It needs only the standard library. Resolve the actual interpreter name (`python3`, `python`, or `py -3` on Windows); examples use `python3`. If execution is prohibited, do not attempt it, install a runtime, or switch to another language to bypass the restriction.
- If an execution, network or output-directory failure prevents collection, retain any usable evidence and continue through other permitted tools. Distinguish local tool failures from website failures; do not evade site access controls.
- Use a host clock or a supplied UTC audit timestamp. If neither exists, request the missing timestamp rather than fabricate `audited_at`. A date alone does not establish the actual time of the audit.
- Save artifacts when the host offers a writable output location. Otherwise, return the composed JSON report directly in the response; file writing is not a prerequisite for reasoning through the skills.
- Run the Python report validator only when both execution and a saved report are available. Otherwise check the schema's required fields, counts, IDs, statuses and evidence manually, and disclose that automated validation was not run.
- `agent_composed` means the host performed the reasoning stages; it does not mean all tools or checks were available. Preserve unavailable lanes explicitly and keep visibility `not_measured` unless actual assistant runs were recorded.

## Manual report check when the validator cannot run

Read `report-schema.json` and use its exact enum values, not the host's tool names. In particular, `coverage.modes` accepts only `static`, `rendered`, `off_site`, and `retrieval`: public web fetching/search can be described as `retrieval`; use `static` for inspected source evidence, `rendered` only for actual browser observations, and `off_site` for checked external sources. Values such as `web_fetch` or `web_search` are not valid report modes.

Check required fields and nested objects against the schema, then verify each enum, finding/action ID, summary total and severity count. `answered` requires evidence for every required element; unobserved journeys use `not_checked`. Report this as manual review, never as a successful validator execution.
