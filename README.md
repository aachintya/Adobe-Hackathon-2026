# Brand AI Readiness Audit

Adobe University Hackathon marketplace submission for **Speak to Agents: The New Language of Brand Visibility**. It audits a public website without changing it and returns one evidence-backed report.

[![Validate marketplace](https://github.com/aachintya/Adobe-Hackathon-2026/actions/workflows/validate.yml/badge.svg)](https://github.com/aachintya/Adobe-Hackathon-2026/actions/workflows/validate.yml)

The `audit-orchestrator` entrypoint composes three focused skills:

- `crawl-extract-audit`: access, indexability, static-vs-rendered extractability, structured data, fact quotability, and important facts trapped in media.
- `entity-trust-audit`: entity identity, claim freshness, first-party consistency, and independent corroboration.
- `engagement-context-audit`: orientation, information scent, dead ends, continuity, accessibility friction, and task completion paths.

## Run

Invoke `skills/audit-orchestrator` with a public URL. The agent uses available browser/search tools and can run the bundled deterministic collector:

```text
python skills/audit-orchestrator/scripts/collect_site.py https://example.com --output evidence.json
```

The entrypoint emits one JSON report conforming to `skills/audit-orchestrator/references/report-schema.json`. It includes an executive conclusion, prioritized finding actions, and evidence-linked proactive opportunities. It is recommend-only and preserves unavailable evidence as `coverage.not_checked` instead of inventing a failure. See `examples/problem-site-report.json` for a composed example.

The collector preserves a supplied path, consumes bounded sitemap inventory, normalizes tracking URLs, evaluates named-agent policy per sampled path, rejects cross-authority redirects before fetching them, skips non-HTML parsing, bounds decoded responses, and stops new collection before the five-minute limit. When capabilities exist, the skill renders representative task pages and runs a compact off-site discovery baseline.

## Validate

Run the complete deterministic suite from this directory:

```text
python tests/run_all.py
```

Build the contest-ready ZIP, with one `brand-ai-readiness-audit/` root and no generated cache files:

```text
python scripts/package_submission.py
```

The verified archive is written to `dist/` and checked against Adobe's 50 MB limit, manifest, skill paths, and single-entrypoint rule.

The suite checks healthy/problem collection, robots edge cases, report-contract failures, and outcome-level report quality. To score a new composed report against a maintained case:

```text
python tests/evaluate_report_quality.py REPORT.json tests/fixtures/problem-expectations.json
```

`evals/evals.json` contains eight forward-evaluation prompts spanning rendered engagement, entity ambiguity, path-specific audits, sitemap discovery, multilingual sites, media-locked facts, healthy-site false-positive control, and deadline/redirect safety. These cases are intended for blinded fresh-agent runs; the deterministic suite validates their coverage and all mechanics that can be checked without model judgment.

See [`evals/README.md`](evals/README.md) for the blinded generalization protocol, metrics, capability-degradation matrix, and internal release gates. The project does not present the maintained example's synthetic score as proof of unseen-site performance.

## Cascading design

The audit spends its evidence budget in stages: robots/homepage/sitemap, then a diverse bounded crawl, then optional rendering for suspicious pages, then optional off-site corroboration for material claims. Each later stage is triggered only when it can resolve uncertainty. This keeps typical runs under five minutes while reducing false positives.

## Safety defaults

Public GET/HEAD only; no login, forms, mutation, bypass, or high-rate crawling. Robots directives are respected. Default cap: 20 pages, two requests per second, same-site URLs only.

## Accessibility scope

Accessibility is a directly observed engagement evidence lane, not a conformance certification. The audit reports task-relevant barriers it can verify and marks rendered interaction, focus, keyboard, overlay, or contrast checks as `not_checked` when those capabilities were not exercised.
