# Severity and confidence

Severity combines impact and breadth:

- `critical`: verified site-wide exclusion, persistent 5xx, or essentially no accessible meaningful content.
- `high`: blocks discovery/extraction or task completion on a major template/material claim.
- `medium`: meaningfully weakens interpretation, trust, orientation, or continuity but has a viable alternate path.
- `low`: localized quality/accessibility issue with limited user or machine impact.

Confidence is `high` for direct repeated observation, `medium` for direct but limited/conditional evidence, and `low` for inference. Findings require medium or high confidence. Prefer lower severity or `not_checked` when scope is uncertain.

Priority normally follows severity, but raise broad low-effort fixes and lower expensive narrow ones. Each action must state change, location/scope, mechanism, owner hint, effort (`low`, `medium`, or `high`), and acceptance test.
