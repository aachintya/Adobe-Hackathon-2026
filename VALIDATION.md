# Validation record

Validated on 2026-09-02 with Python 3.12. Candidate: v1.4.0.

## Structural checks

- `marketplace.json` parses as JSON.
- All four listed skill directories contain `SKILL.md`.
- Exactly one skill is marked `entrypoint`.
- The report schema parses as JSON.
- The collector compiles without syntax errors.
- Every listed skill has valid required frontmatter and exactly one marketplace entrypoint is declared.
- Every skill name matches its folder, descriptions satisfy Agent Skills limits, declared references resolve, and each entrypoint stays below the progressive-disclosure size guidance.

## Behavioral simulations

The local test harness served two sites over HTTP and ran the real collector.

1. Healthy fixture: discovered all three linked pages, parsed structured data, and returned no transport errors.
2. Problem fixture: preserved direct evidence for `noindex`, detected the low static-text trigger that calls for rendered comparison, and retained rendered/off-site checks as `not_checked` when those capabilities were absent.

Result: PASS.

## Generalization regressions

The v1.4 collector suite verifies six previously uncovered invariants against local HTTP servers:

1. A supplied deep path remains the audit starting point.
2. Declared sitemap inventory is fetched and contributes otherwise undiscoverable pages.
3. Tracking parameters are removed and remaining query parameters are deterministically ordered.
4. Non-HTML responses are recorded but not parsed as pages.
5. Cross-authority redirects are rejected before any request reaches the other authority.
6. Named AI-agent robots decisions are preserved for each sampled path.

The collector also has a global deadline of 270 seconds by default, capped at 295 seconds, so report composition can remain within Adobe's five-minute limit. Result: PASS.

## Composed-report evaluation

The outcome-level case represents the problem fixture. It validates a complete report for four expected evidence concepts: named-agent exclusion, page-level `noindex`, weak offer orientation/information scent, and a missing image alternative. It also requires explicit `not_checked` disclosure for rendered, keyboard, and off-site checks; an executive conclusion; coverage of both Adobe problem halves; an evidence-linked proactive opportunity; and rejection of unsupported citation, engagement-impact, or accessibility-conformance claims.

The maintained example scored 100/100. Six negative contract mutations were correctly rejected: affected count above checked count, invalid timestamp, missing action owner, unsupported evidence mode, an unknown top-action ID, and an unstructured opportunity.

## Forward-evaluation matrix

`evals/evals.json` defines eight fresh-agent cases covering rendered engagement on complete server HTML, entity ambiguity and corroboration, deep-path preservation, sitemap-only inventory, multilingual variants, image/PDF-locked facts, healthy-site false-positive control, and slow/redirecting/non-HTML behavior. Each case has observable assertions and an expected outcome. The deterministic suite verifies that all dimensions remain present; honest model-level precision/recall still requires executing these prompts blindly in the target judging environment.

Run the complete suite with `python tests/run_all.py`.

## External benchmark

A 12-site unseen benchmark was run against the prior day's CrawlIndex raw-observation dataset. Agreement was 100% across 132 named-agent robots decisions, 91.7% for JSON-LD presence, and 90.9% for the comparable thin-server-text cases. Lower exact-count agreement (66.7% for H1 and images) exposed sensitivity to time, user-agent, redirects, and locale. The exercise found and fixed bounded-timeout, agent-policy, meta-directive scoping, truncation, JSON-LD traversal, parser nesting, and sitemap-hint issues. See the separately supplied external validation report for method and limitations.

Eight deterministic robots scenarios now pass: named-agent blocking, 401, 403, 404, 503, malformed rules, wildcard root blocking, and redirect-to-policy. These follow RFC 9309's distinction between unavailable 4xx and unreachable 5xx/network outcomes.

A rendered production check showed why static and rendered evidence must remain separate: ElevenLabs exposed two H1 elements in fetched HTML but one visible rendered H1. The rendered page had 9,612 visible-text characters, semantic landmarks, and no missing image alternatives; three empty-name actions remained candidates requiring element-level relevance review. Acrobat redirected to an app surface with no visible body text in the selected browser, so that observation was retained as environment/route-specific rather than declared a defect.

## What this proves - and does not prove

It proves deterministic collection, bounded crawling, path/sitemap handling, redirect containment, response-type safety, signal preservation, manifest composition, output-contract enforcement, and uncertainty handling for the simulated cases. It does not by itself prove agent-written report precision on a population of unseen sites or ranking/citation outcomes in a particular AI assistant. The marketplace therefore includes a forward-evaluation matrix and reports mechanisms and observed evidence, not promises of citation or lower bounce rate.
