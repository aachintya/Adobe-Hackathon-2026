# Brand AI Readiness Audit

Audit a public website for AI discoverability and on-site engagement. Load `marketplace.json` and invoke `audit-orchestrator` with a website URL to combine three focused skills into one evidence-backed JSON report.

| Skill | Responsibility |
|---|---|
| `audit-orchestrator` (entrypoint) | Shared time/evidence budget, visitor questions, composition, prioritization and output validation |
| `crawl-extract-audit` | Search access and indexing controls; readable facts; question answerability; structured-data contradictions |
| `entity-trust-audit` | Entity identity, material fact consistency, current evidence and independent source comparison |
| `engagement-context-audit` | Real visitor information routes, next steps, context continuity and observable task barriers |

The skills use the host agent's public fetch, browser and search tools as available. Optional helpers use Python 3.10+ and its standard library. No API keys, package installation or service setup is required. Reports disclose missing capabilities.

Commands below use `python3`; substitute your Python 3.10+ executable (for example, `py -3` on Windows) if it has another name.

## Invoke the marketplace

Ask the host agent:

> Use the entrypoint in `skills/audit-orchestrator/SKILL.md` to audit https://example.com for AI discoverability and on-site engagement. Return the composed JSON report.

The agent derives three priority visitor questions by default (up to five for specific needs), evaluates supporting facts, traces two safe public journeys, checks source credibility and returns prioritized fixes. It uses the same evidence across all skills. Paths resolve from the installed skill, so invocation does not depend on the working directory.

## Run the optional Python fallback

From the extracted marketplace root:

```text
python3 skills/audit-orchestrator/scripts/run_audit.py https://example.com --output-dir audit-output
python3 tests/validate_report.py audit-output/report.json
```

This writes `evidence.json` and a schema-valid **static baseline** `report.json`. It preserves page passages, link labels/destinations, structured-data values and scoped access controls. The host agent reviews and completes the baseline with question tests, trust reasoning and browser journeys. Python alone does not simulate a complete agent audit or measure live assistant citations.

For a composed audit, the agent saves `draft-report.json` and a compact `review.json` linking its claims to the captured evidence. The [verification workflow](skills/audit-orchestrator/references/report-verification.md) checks source references, quoted passages, captured-field contradictions, scope counts, link destinations and reading modes before publishing `final-report.json` with a hashed receipt. The finalizer also rejects publication at or beyond 300 seconds from the supplied invocation start. Schema-only validation remains available for baselines; it does not verify claims against evidence. A receipt checks recorded consistency, not semantic truth, source authenticity or user-visible delivery time. Tool-only hosts use explicit manual review instead.

The report includes findings, evidence, severity, suggested actions, coverage and an executive summary. See [the synthetic example](examples/problem-site-report.json). Actual visibility remains `not_measured` unless recorded assistant answers support it; [the measurement protocol](skills/audit-orchestrator/references/retrieval-validation.md) explains the optional helper.

An optional [answer-locality experiment](skills/audit-orchestrator/references/answer-locality.md) shows whether selected answer facts and their qualifiers fit together in short text windows. It runs offline on saved evidence and includes a reproducible synthetic before/proposed answer-card example. It measures exact-quote separation in words, not model tokens, semantic correctness or citation likelihood, and adds no mandatory work to the five-minute audit.

## Host environments

| Browser | Python | Supported behavior |
|---|---|---|
| Yes | Yes | Source collection plus real browser journeys; off-site corroboration also needs search/fetch. |
| No | Yes | Source audit and question analysis; rendered and interactive checks remain untested. |
| Yes | No | Direct fetch/browser audit; no Python collection or automated report validation. |
| No | No | Limited text-based audit if the host can fetch public pages; no interactive verification. |

Python means Python 3.10+ with permission to execute; an installed but prohibited runtime is unavailable. All paths require reachable site evidence. Without network tools or supplied evidence, a live audit cannot run. Search, source HTML/headers, a clock or supplied UTC timestamp, and writable output each have separate capability requirements. The host can return the JSON report in chat when it cannot write files. See [the capability and fallback rules](skills/audit-orchestrator/references/tool-availability.md).

Coverage and runtime depend on the host's permitted tools and the target site.

## Package contents

Keep the complete `brand-ai-readiness-audit/` folder together. It contains the manifest, four skills with their references and helpers, synthetic usage examples, this README and the license. The two files under `tests/` are runtime report validators used by the finalizer; retain them.

Standalone collection defaults to 12 pages, 2 requests/second and 120 seconds. The timed skill starts with 1 page/15 seconds, selects visitor questions and observed task links, then resumes to a total of 5 pages with up to 30 further seconds. It stops evidence gathering by 120 seconds, and targets 280 seconds through composition, verification and delivery. The finalization gate checks its own deadline; enforcing cancellation and the full request-to-delivery deadline requires host support. The audit respects robots, uses its own crawler identity and recommends changes without modifying live sites.
