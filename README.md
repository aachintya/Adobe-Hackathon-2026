# Brand AI Readiness Audit

Audit a public website for AI discoverability and on-site engagement. Load `marketplace.json` and invoke `audit-orchestrator` with a website URL to combine three focused skills into one evidence-backed JSON report.

| Skill | Responsibility |
|---|---|
| `audit-orchestrator` (entrypoint) | Shared time/evidence budget, visitor questions, composition, prioritization and output validation |
| `crawl-extract-audit` | Search access and indexing controls; readable facts; question answerability; structured-data contradictions |
| `entity-trust-audit` | Entity identity, material fact consistency, current evidence and independent source comparison |
| `engagement-context-audit` | Real visitor information routes, next steps, context continuity and observable task barriers |

The skills use the host agent's public fetch, browser and search tools as available. Optional helpers use Python 3.10+ and its standard library. No API keys, package installation or service setup is required. Reports disclose missing capabilities.

## Invoke the marketplace

Ask the host agent:

> Use the entrypoint in `skills/audit-orchestrator/SKILL.md` to audit https://example.com for AI discoverability and on-site engagement. Return the composed JSON report.

The agent derives 3-5 relevant visitor questions, evaluates supporting facts, traces two safe public journeys, checks source credibility and returns prioritized fixes. It uses the same evidence across all skills. Paths resolve from the installed skill, so invocation does not depend on the working directory.

## Run the optional Python fallback

From the extracted marketplace root:

```text
python skills/audit-orchestrator/scripts/run_audit.py https://example.com --output-dir audit-output
python tests/validate_report.py audit-output/report.json
```

This writes `evidence.json` and a schema-valid **static baseline** `report.json`. It preserves page passages, link labels/destinations, structured-data values and scoped access controls. The host agent reviews and completes the baseline with question tests, trust reasoning and browser journeys. Python alone does not simulate a complete agent audit or measure live assistant citations.

The report includes findings, evidence, severity, suggested actions, coverage and an executive summary. See [the synthetic example](examples/problem-site-report.json). Actual visibility remains `not_measured` unless recorded assistant answers support it; [the measurement protocol](skills/audit-orchestrator/references/retrieval-validation.md) explains the optional helper.

## Verify and package

```text
python tests/run_all.py
python scripts/package_submission.py
```

Submit `dist/brand-ai-readiness-audit.zip`. It contains one folder, `brand-ai-readiness-audit/`, with the manifest, skills, references, helpers, examples and validation tools. The package excludes caches, live crawl outputs and other archives. Both compressed and uncompressed sizes are checked against a 50 MB cap.

Collection defaults to 12 pages, 2 requests/second and 120 seconds. The skill shares a 280-second target across collection, browser, search and composition. It respects robots, uses its own crawler identity and recommends changes without modifying live sites. See [design](DESIGN.md) and [validation](VALIDATION.md).
