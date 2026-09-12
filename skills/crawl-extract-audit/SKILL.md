---
name: crawl-extract-audit
description: Diagnose public-site crawl access, indexability, machine-readable extraction, structured data, and quotable fact issues without modifying the site.
license: MIT
allowed-tools: Read WebFetch Browser Bash
---

# Crawl and extraction audit

Use the shared evidence bundle and the orchestrator's visitor questions. Check access for named search crawlers, engine-specific meta and HTTP directives, redirects/canonical coherence, then whether a reader can extract the facts needed to answer those questions. Treat the Python report as technical candidates; review their business relevance and intentional restrictions before retaining them.

For each question, fill its `assessment.intent_tests` record using `main_text`, `passages`, table headers/cells, actual JSON-LD values, media alternatives and relevant linked pages. Table `records` provide derived reading context only; quote the actual header and value fields separately. Complex or truncated tables need contextual review. Cite a short quote and URL for each answer; record partial or untested coverage honestly. Check each required element, including its unit, variant or qualifier, before assigning status. A resolved answer is `answered` even if another passage warrants a separate localized finding; `partial` must name the still-missing or unresolved element. A long marketing page may lack the important answer; a short clear page may answer it fully. Compare rendered and source facts when a browser can resolve uncertainty. Review `evidence_truncated` before claiming absence.

Check schema syntax AND agreement with material visible facts; source schema values are evidence, not a higher truth than the page. Evaluate canonical destinations before claiming duplicate-content exclusion. Distinguish policy that blocks training from policy that blocks search; neither permission nor a successful local GET proves actual citation.

Read [checks.md](references/checks.md) for gates. When the cascade triggers rendering, read [rendered-audit.md](references/rendered-audit.md). Return finding candidates, passes, and `not_checked` items separately. Each candidate contains the exact observation, URLs, affected/checked counts, likely mechanism, and verification-ready fix. Never equate missing sitemap/schema with invisibility, use raw HTML size as content quality, or report JS use itself as a problem.

When a selected answer's qualifiers are separated in readable text, the optional [answer-locality experiment](../audit-orchestrator/references/answer-locality.md) can quantify the separation from saved evidence. Use it only for a relevant quotability investigation or a requested demonstration within the shared deadline; it is not required for routine audits.
