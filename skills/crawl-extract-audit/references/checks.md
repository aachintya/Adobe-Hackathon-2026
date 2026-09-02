# Crawl/extraction checks

- Exclusion: evaluate wildcard and named-agent robots policies separately. Keep generic `robots`, `googlebot`, and `bingbot` meta directives separate; never let a bot-specific `noindex` become a site-wide `noindex`. Identify which valuable path/template is affected.
- Robots retrieval: distinguish `present`, `present_no_parseable_groups`, `unavailable_4xx`, `unreachable_5xx`, and `unreachable_network`. A direct browser visit proving `/robots.txt` is readable is evidence of presence, but rules must still be parsed for each agent/path and compared with an actual permitted-agent fetch to detect server-side blocking.
- Canonical: flag only invalid, conflicting, cross-entity, or systematic canonicalization that can remove valuable pages; self-canonical absence alone is not a defect.
- Extractability: meaningful text excludes nav/footer/cookie boilerplate. Escalate render only below 80 words or with shell evidence; require missing material facts in static mode.
- Quotability: sample material attributes. A defect needs an important answer stated only implicitly, split across UI fragments, or absent from readable HTML. Quote short evidence snippets.
- JSON-LD/microdata: parse every block; compare names, URLs, dates, availability, prices, and identifiers to visible text. Unsupported or cosmetic schema recommendations are opportunities, not defects.
- Media: inspect alt/transcript/equivalent nearby text. Decorative media is excluded.
- Links: orphaning requires sitemap/known inventory evidence; a deep click path alone is medium at most unless it blocks a major template.
- Sitemap: fetch declared sitemap files (or `/sitemap.xml` as a bounded fallback), use same-authority HTML URLs for representative discovery, and record parse/fetch limits. Merely publishing no sitemap is not a defect.
- Transport: preserve the requested path, reject redirects outside the audited authority, skip non-HTML parsing, normalize tracking parameters, bound decoded response size, and surface a global-deadline stop as partial coverage.
