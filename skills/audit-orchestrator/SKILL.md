---
name: audit-orchestrator
description: Run and compose a read-only website audit for AI discoverability and on-site engagement. Use for a public brand URL when the output must be one evidence-backed, prioritized report.
license: MIT
allowed-tools: WebFetch WebSearch Browser Bash
---

# Audit orchestrator

## Input

A public `http` or `https` URL. Optional crawl cap (default 20, maximum 40) and material locales.

## Non-negotiable boundaries

Audit only public pages with GET/HEAD. Respect robots.txt. Stay same-site, throttle to at most 2 requests/second, and do not authenticate, submit forms, evade controls, or change a site. Recommendations are proposals only.

## Procedure

1. Normalize the supplied URL without discarding its path and record UTC start time. Run `python scripts/collect_site.py URL --output evidence.json`. If execution is unavailable, collect equivalent fields manually. Stop new work at 270 seconds so the report can be composed within five minutes.
2. Apply the cascade in [evidence-policy.md](references/evidence-policy.md). Render up to three representative task pages when a browser exists; reserve broader static/rendered comparison for pages whose static response is suspicious. When search exists, run the bounded off-site baseline in [retrieval-validation.md](references/retrieval-validation.md); expand it only when competitive or citation testing is explicitly requested.
3. Route collected evidence through the three sibling marketplace skills: `../crawl-extract-audit/SKILL.md`, `../entity-trust-audit/SKILL.md`, and `../engagement-context-audit/SKILL.md`. Read only the referenced rubric relevant to observed page types.
4. Merge candidates by root cause. Preserve page counts, URLs, selectors or snippets, response modes, and tool failures. Never turn missing capability, a blocked request, or a small sample into a defect.
5. Score severity and confidence using [severity.md](references/severity.md). Suppress candidates below the skill's finding gate; put unresolved tests in `coverage.not_checked`.
6. Rank actions by severity, breadth, confidence, and effort. Tie every action to the mechanism it repairs and a verification step. Add at most three evidence-relevant proactive opportunities using the same owner, effort, mechanism, and verification discipline; do not add generic best practices.
7. Emit valid JSON conforming to [report-schema.json](references/report-schema.json), including `schema_version: "1.1"`. Recompute counts from findings. IDs are stable in sorted order (`F-001`, ...). Include an executive conclusion and top action IDs a non-expert can use first. Do not include prose outside the JSON unless requested.
8. When the package test harness is available, save the report and run `python tests/validate_report.py REPORT.json`. For maintained evaluation cases, also run `python tests/evaluate_report_quality.py REPORT.json EXPECTATIONS.json`. Correct contract or evidence-fidelity failures before returning the report.

## Completion checks

- Both discoverability and engagement have coverage or an explicit `not_checked` reason.
- At least one representative acquisition or task page is rendered when a browser is available; otherwise the limitation is explicit.
- The off-site baseline is checked when search is available; otherwise the limitation is explicit.
- Every finding has observed evidence, affected/checked counts, confidence, and a prioritized action.
- `critical` is reserved for site-wide near-total exclusion or unusability.
- No claim says an assistant does or does not cite the brand unless directly tested.
- No claim asserts bounce, conversion impact, accessibility conformance, or user sentiment without direct supporting measurement.
- `audited_at` is ISO-8601 UTC; all severity counts match.
