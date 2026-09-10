# Portability and cleanup follow-up

This follow-up implements the user's request for code cleanup and GitHub publication after the earlier field evaluation. It does not rewrite the historical findings or establish Adobe's unknown tool configuration.

## Changes

- Fixed HTTP 308 handling in the optional collector for older urllib implementations. The original status stays in redirect evidence; the existing authority, robots, throttling and redirect-loop guards remain active. A local HTTP regression failed before the completed fix and passed afterward.
- Added explicit host-capability instructions for browser/Python combinations, direct web-evidence collection without a script-generated bundle, prohibited execution, missing source/headers, absent search, trustworthy timestamps and returning JSON when files cannot be written.
- Documented interpreter-name differences while retaining the declared Python 3.10+ minimum and standard-library-only helpers.
- Fixed repository-only evaluation links in the packaged README and validation guide. The actual extracted-ZIP check now verifies local Markdown link destinations.
- Sanitized publication copies of field transcripts as documented in `live-usage-2026-09-09/PUBLICATION-NOTES.md`; raw originals remain outside the repository.

## Checks completed

- Full deterministic suite passed on Python 3.12.14, including extraction of the real ZIP into a path with spaces and invocation from an unrelated working directory.
- The new HTTP 308 regression also passed on the machine's Python 3.9.6. This is a compatibility observation, not a change to the declared minimum version.
- Redirect cases cover an allowed same-authority target, an external target never contacted, a robots-blocked target never contacted, and a bounded redirect loop.
- A public one-page collection of `https://duckdb.org/install` followed its HTTP 308 to `/install/`, returned parsed HTML with status 200, and recorded zero errors (3 requests, collector time 2.70 seconds). This is a source-collection check, not a full agent audit.

## No-Python, no-browser behavioral trial

A reused Luna medium session audited `https://www.python.org/about/` with web fetch/search and file tools permitted, while Python/helper execution and browser automation were prohibited. This was an instruction restriction rather than removal of the tools from the host. The auditor returned four answered question records, two `not_checked` journeys, and no website findings. It explicitly disclosed unavailable source metadata, browser checks and automated validation.

The preserved [initial report](no-runtime-2026-09-10/initial/report.json) failed parent-side contract validation because `coverage.modes` used `web_fetch` and `web_search`, which are host tool descriptions rather than schema enum values. A focused manual-check clarification was then added to the capability reference. The auditor's approximately 90-second runtime was not backed by separate start/end clocks, so it is not used as measured performance. It also wrote outside the requested artifact directory; the parent preserved the records in the evaluation directory without altering the initial report.

After explicit feedback about those enum errors, the same auditor manually produced a [corrected report](no-runtime-2026-09-10/corrected/report.json) without browsing again or executing Python. Parent-side validation of that corrected report passed. The [correction note](no-runtime-2026-09-10/corrected/correction.md) discloses the intervention. This demonstrates a usable restricted-tool path after guided correction, not reliable unattended schema compliance across models.

## Environment expectations

| Browser | Python execution | Expected result | Evidence boundary |
|---|---|---|---|
| Yes | Yes | Collector-assisted audit with actual journeys when fetch/search and site access are available. | Earlier field runs exercised this path; the latest complete revision has not had a fresh full browser trial. |
| No | Yes | Source facts and question/trust reasoning; interaction checks explicitly unavailable. | Collector and extracted-package execution verified; earlier Luna audits exercised reasoning without browsers. |
| Yes | No | Direct fetch/browser audit with manual schema review. | Instruction-supported path; no complete isolated trial of this combination is claimed. |
| No | No | Limited text-based audit using the host's fetch/search tools. | Luna trial answered four questions and left two journeys untested; its initial format error required guided correction. |

No browser means less observable engagement coverage. No Python means no bundled collector or automated validator. No permitted network/evidence route means a live audit cannot be performed. These statements describe capability-dependent behavior, not equal detection accuracy, equal coverage, or a guaranteed five-minute runtime.

## Reviewed implementation fingerprints

- `skills/audit-orchestrator/SKILL.md`: `956714267f7b9396c9271a35bebfea79311c013050bb52f98147a4de1301f822`
- `skills/audit-orchestrator/references/tool-availability.md`: `664a17c781373b1239e4534d8d08c454dd16cb5d6c93402c8c36bd8bbfe89d7d`
- `skills/audit-orchestrator/scripts/collect_site.py`: `3b36bae76b6996045a4a42bb36afa8dee1ad8eeb2a850bb62a585519a01f1f37`
