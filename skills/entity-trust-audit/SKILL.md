---
name: entity-trust-audit
description: Audit a public brand's entity clarity, factual consistency, freshness signals, and independent corroboration while separating absence of evidence from a defect.
license: MIT
allowed-tools: Read WebFetch WebSearch
---

# Entity and trust audit

Extract a claim ledger for legal/display name, description, offering, location/service area, contact, identifiers, leadership where relevant, and dated material claims using [claim-ledger-schema.json](references/claim-ledger-schema.json). Compare first-party pages before optional external search.

Reuse the orchestrator's bounded searches for exact-entity identity, neutral discovery and 1-2 decision-critical claims. Open relevant sources; snippets alone are leads. Prefer independent authoritative sources; directories copied from the brand are not independent. Record exact query, date, locale, URLs and short evidence quotes in the shared ledger, and summarize corroboration in `assessment.readiness`. Apply [trust-gates.md](references/trust-gates.md).

Return evidence-backed candidates plus passes and `not_checked`. Routine product capabilities can be established by current first-party documentation; independent corroboration is especially useful for contested, comparative or credential claims. No search result is not evidence of no reputation. Do not claim search-engine ranking, model knowledge, or lack of citation from search-result absence.
