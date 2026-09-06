# Limited field observations, 2026-09-05

This is source research and a collection smoke check, not a cited-versus-uncited benchmark. No live consumer-assistant response experiment was conducted. The observations inform general checks; no domains are encoded in the audit logic.

## Retrieval sample

The web-search query `privacy friendly website analytics no cookies EU hosting pricing` returned several first-party services, including Snorklee, Tallytics, Countaclick, Pomelo and others. Plausible's homepage was not among the returned first-party results in this sample, although an informational result about it was present. Tool: web search in this session; date: 2026-09-05; search-engine locale not exposed. This is not a test of ChatGPT citations or market share.

Direct inspection of [Plausible's homepage](https://plausible.io/) nevertheless showed clear product positioning, cookie/hosting statements and links to pricing, documentation and a trial. Its source HTML provided those facts. Therefore absence from one neutral search sample cannot establish an extraction defect or lack of relevant content.

## Public collection checks

| Site | Inspected sample | Result |
|---|---|---|
| Plausible | Homepage, publishers page, docs, about | Four HTML pages; no transport errors; 8.12 seconds; schema-valid static report |
| Python.org | Homepage, about, blogs, PSF | Four HTML pages; no transport errors; 8.11 seconds; schema-valid static report |

On [Python.org](https://www.python.org/), a source fallback notice accompanied useful introductory information and links. The notice alone does not establish that important facts are missing or that browser users see a broken page. Rendered behavior needs separate inspection.

Local evidence for these runs is in `tmp/live-plausible/` and `tmp/live-python/` (development-only output; deliberately excluded from the ZIP). The smoke checks preceded the final addition of explicit noscript fallback retention and repeated HTTP-header scope preservation; those changes are covered by deterministic regressions.

## General decisions

- Inspect answer-bearing passages and relevant link destinations before claiming a content gap.
- Separate retrieval observations from actual assistant answers and citations.
- Treat script/fallback markers as a reason to compare reading modes, not a defect.
- Preserve successful first-party evidence even when a small unbranded search sample omits the domain.

Real generalization still requires the forward-evaluation protocol and independent unseen-site agent runs. These two sites cannot establish precision, recall or causal visibility effects.
