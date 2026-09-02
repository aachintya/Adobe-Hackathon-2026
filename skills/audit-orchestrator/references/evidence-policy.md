# Evidence cascade

## Stage 1 - reachability (always)

Fetch robots.txt, homepage, sitemap hints, canonical, meta robots, status/redirect chain, content type, language, title/H1, and visible text. A robots rule is a finding only when it applies to a named mainstream crawler or `*` and blocks representative valuable paths; merely missing robots.txt passes.

Resolve robots access per RFC 9309: request lowercase `/robots.txt` at the origin root directly; follow up to five redirects and apply the resulting rules to the original authority; parse at least the first 500 KiB; use every parseable rule despite malformed lines. A 4xx response means unavailable and permits crawling, while 5xx/network failure means unreachable and stops crawling unless a valid cached copy no older than 24 hours is explicitly available. Record redirects, status, content type, truncation, and whether rules were present. Never treat robots as authorization or probe paths that its applicable rules disallow.

## Stage 2 - bounded representative sample (always when allowed)

Discover same-site URLs from fetched sitemap inventory and links. Preserve a user-supplied starting path. Stratify by templates inferred from paths and markup: home, about/entity, product/service, article/news, help/contact. Prefer breadth over many URLs from one template. Normalize tracking parameters, reject cross-authority redirects, and stop new collection by 270 seconds. Default 20 pages and record denominator per check.

## Stage 3 - rendered differential (conditional)

When a browser is available, render a maximum of three task-representative pages: the starting/acquisition page and up to two distinct product, pricing, contact, or completion-path templates. This baseline supports engagement observations even when static HTML is substantial. Expand static/rendered comparison only when static HTML has fewer than 80 meaningful words, empty landmarks, script-heavy shell markers, or visible facts suspected to be client-injected. A JS-render gap requires important rendered content absent from static HTML, not merely a byte-count difference. If rendering is unavailable, mark interactive engagement and rendered extraction `not_checked` separately.

Never classify a capped/truncated response as thin. Retry with a larger safe cap or mark extractability `not_checked`.

## Stage 4 - off-site validation (conditional)

When search is available, run the compact baseline in [retrieval-validation.md](retrieval-validation.md): exact entity, one neutral category query, and up to three material claim lookups. Expand only for collisions, conflicts, or an explicit competitive request. Separate first-party repetition from independent corroboration. Search absence is weak evidence and cannot alone create a high-severity finding. Record query, locale, date, and source URLs.

## Finding gates

- Site-wide claims: at least two representative templates, unless robots/homepage makes broader sampling impossible and the limitation itself is observed.
- Template claims: at least 2 affected pages or all pages when only one exists; include affected/checked.
- Structured data: validate semantics, visible-text agreement, required properties, and parseability. Absence is a defect only where a supported schema would materially clarify an entity, product, article, event, FAQ, or breadcrumb.
- Engagement: infer friction from observable paths/content; do not claim bounce rate or user intent without analytics/research.
- Facts in images/PDF/video: only report when a material fact lacks an equivalent HTML text alternative.
