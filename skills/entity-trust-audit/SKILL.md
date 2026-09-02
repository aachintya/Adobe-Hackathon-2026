---
name: entity-trust-audit
description: Audit a public brand's entity clarity, factual consistency, freshness signals, and independent corroboration while separating absence of evidence from a defect.
license: MIT
allowed-tools: WebFetch WebSearch
---

# Entity and trust audit

Extract a claim ledger for legal/display name, description, offering, location/service area, contact, identifiers, leadership where relevant, and dated material claims using [claim-ledger-schema.json](references/claim-ledger-schema.json). Compare first-party pages before optional external search.

Trigger search only for name ambiguity, conflicting material claims, or 3-5 claims central to discovery. Prefer independent authoritative sources; directories copied from the brand are not independent. Record dates and URLs. Apply [trust-gates.md](references/trust-gates.md).

Return evidence-backed candidates plus passes and `not_checked`. Do not claim search-engine ranking, model knowledge, or lack of citation from search-result absence.
