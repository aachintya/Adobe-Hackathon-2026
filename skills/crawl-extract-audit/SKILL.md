---
name: crawl-extract-audit
description: Diagnose public-site crawl access, indexability, machine-readable extraction, structured data, and quotable fact issues without modifying the site.
license: MIT
allowed-tools: WebFetch Browser Bash
---

# Crawl and extraction audit

Use the orchestrator evidence bundle. Check, in order: response/status and redirect integrity; applicable robots rules and page-level indexing directives; canonical coherence; sitemap discovery; meaningful static text; conditional static/rendered difference; headings/landmarks; structured-data parseability and agreement with visible content; material facts available only in media; and internal-link discoverability.

Read [checks.md](references/checks.md) for gates. When the cascade triggers rendering, read [rendered-audit.md](references/rendered-audit.md). Return finding candidates, passes, and `not_checked` items separately. Each candidate contains the exact observation, URLs, affected/checked counts, likely mechanism, and verification-ready fix. Never equate missing sitemap/schema with invisibility, use raw HTML size as content quality, or report JS use itself as a problem.
