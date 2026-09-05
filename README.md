# Brand AI Readiness Audit

Adobe University Hackathon 2026, Round 3: **Speak to Agents: The New Language of Brand Visibility**. Version 2.0.0.

Submit this marketplace as a ZIP. The judging agent loads `marketplace.json` and invokes the single `audit-orchestrator` entrypoint with a website URL. It composes three focused skills into one evidence-backed JSON report:

| Skill | Responsibility |
|---|---|
| `audit-orchestrator` (entrypoint) | Shared time/evidence budget, visitor questions, composition, prioritization and output validation |
| `crawl-extract-audit` | Search access and indexing controls; readable facts; question answerability; structured-data contradictions |
| `entity-trust-audit` | Entity identity, material fact consistency, current evidence and independent source comparison |
| `engagement-context-audit` | Real visitor information routes, next steps, context continuity and observable task barriers |

**Skills plus Python helpers are allowed.** Adobe's updated Round 3 handout explicitly permits optional `scripts/` and `references/`. The submission is a skill marketplace; its Python helpers support the host agent. No API keys, model weights, package installation, server or paid service is required. Python 3.10+ is optional; public fetch, browser and search tools are used by the agent as available. Missing capabilities are disclosed.

## Invoke the marketplace

Ask the judging/general agent:

> Use the entrypoint in `skills/audit-orchestrator/SKILL.md` to audit https://example.com for AI discoverability and on-site engagement. Return the composed JSON report.

The agent derives 3-5 relevant visitor questions, evaluates supporting facts, traces two safe public journeys, checks source credibility and returns prioritized fixes. It uses the same evidence across all skills. Paths resolve from the installed skill, so invocation does not depend on the working directory.

## Run the optional Python fallback

From the extracted marketplace root:

```text
python skills/audit-orchestrator/scripts/run_audit.py https://example.com --output-dir audit-output
python tests/validate_report.py audit-output/report.json
```

This writes `evidence.json` and a schema-valid **static baseline** `report.json`. It preserves page passages, link labels/destinations, structured-data values and scoped access controls. The host agent reviews and completes the baseline with question tests, trust reasoning and browser journeys. Python alone does not simulate a complete agent audit or measure live assistant citations.

The report includes Adobe's required findings, evidence, severity, suggested actions and summary, plus `assessment`, explicit coverage, an executive conclusion and relevant proactive opportunities. See [the composed synthetic example](examples/problem-site-report.json). Actual visibility remains `not_measured` unless recorded assistant answers support it; [the measurement protocol](skills/audit-orchestrator/references/retrieval-validation.md) explains the optional helper.

## Verify and package

```text
python tests/run_all.py
python scripts/package_submission.py
```

The ZIP is `dist/brand-ai-readiness-audit-v2.0.0-submission.zip`, containing one marketplace root. Tests include running its extracted Python fallback from an unrelated working directory with spaces in its path. Build scripts, validators and fixtures are included; caches, live crawl outputs, previous ZIPs and model weights are excluded. Both compressed and uncompressed sizes must stay below 50 MB.

Collection defaults to 12 pages, 2 requests/second and 120 seconds. The skill shares a 280-second target across collection, browser, search and composition. It respects robots, uses its own crawler identity, follows only bounded public navigation and recommends changes without modifying live sites. See [design and Adobe requirement mapping](DESIGN.md) and [validation limits](VALIDATION.md).
