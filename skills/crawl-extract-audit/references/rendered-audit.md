# Rendered and accessibility audit

Use only when a browser is available and the evidence cascade triggers rendering. Record URL, viewport, locale, timestamp, final URL, and whether a challenge/consent overlay prevented observation.

## Static/rendered differential

After load settles, extract visible main text, visible links with accessible names and destinations, headings, landmarks (native and ARIA roles), images and accessible alternatives, form controls and label relationships, canonical/meta robots, and JSON-LD. Normalize whitespace and boilerplate before comparison.

Escalate only when a material fact, primary path, or identity cue exists in the rendered DOM but not static HTML. A larger rendered word count alone is not a finding. If the static response was truncated, retry safely or mark the comparison unavailable.

## Deterministic accessibility checks

On task-relevant public pages check:

- images lacking an accessible alternative, excluding demonstrably decorative images;
- inputs without `label`, `aria-label`, `aria-labelledby`, or title fallback;
- links/buttons with empty accessible names;
- missing document language;
- absent main landmark and skipped heading levels;
- keyboard reachability and visible focus for primary navigation and primary action;
- overlays that obscure content or trap focus.

Automated absence of errors never proves WCAG conformance. Contrast, focus behavior, and semantics should be marked `not_checked` unless actually measured. Report an accessibility issue only when the affected element is visible/task-relevant or repeated systematically. Accessibility checks cover observed task barriers and do not constitute accessibility certification.

## Evidence handoff

Return counts plus exact selectors or compact element descriptions, affected/checked denominators, screenshots only when they clarify visible obstruction, and separate `static`, `rendered`, and `not_checked` fields.
