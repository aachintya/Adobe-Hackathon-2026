# External validation report

Date: 2026-09-02 UTC/IST. Historical observations for `brand-ai-readiness-audit` at that date; these are not validation of the current implementation.

## Benchmark design

Ground truth came from the CrawlIndex 2026-09-01 snapshot (`domains.jsonl`, probe 3.0.0, rubric 2.0.0). It archives raw observations rather than only scores and labels unavailable/partial measurements. The frozen source file is in `external/crawlindex-domains.jsonl` (CC BY 4.0, Fidget Labs BV).

Twelve unseen, recognizable sites were stratified across externally observed conditions: AI crawler blocking, generic noindex, thin server text, rich/absent JSON-LD, abnormal H1 counts, and healthy controls. The live collector ran on 2026-09-02 with one-page caps to make homepage signals comparable.

Sites: acrobat.com, amazon.com, apple.com, cloudflare.com, cnn.com, elevenlabs.io, europa.eu, github.com, microsoft.com, mozilla.org, wikipedia.org, wordpress.org.

## Results against snapshot observations

| Signal | Agreements | Comparable checks | Agreement |
|---|---:|---:|---:|
| Per-agent robots access | 132 | 132 | 100.0% |
| Generic meta noindex | 10 | 12 | 83.3% |
| JSON-LD presence | 11 | 12 | 91.7% |
| Thin SSR text (<150 chars) | 10 | 11 | 90.9% |
| Landmark set | 10 | 12 | 83.3% |
| Exact H1 count | 8 | 12 | 66.7% |
| Exact image count | 8 | 12 | 66.7% |

One large response (CNN) was excluded from the thin-text denominator after the revised collector correctly labeled it truncated. Exact DOM counts are the least stable comparisons because the benchmark and candidate ran one day apart, from different network vantage points and user agents; redirects, localization, experiments, and site releases are visible in the mismatches. These are agreement figures, not statistically powered population accuracy estimates.

## Bugs found and fixed

1. Unbounded robots fetch could hang past the five-minute budget. Fixed with an 8-second timeout and fail-closed `not_checked` behavior.
2. The collector checked only its own user-agent. Fixed by resolving 11 answer-surface crawler policies independently and adding a conditional GPTBot response probe.
3. Generic, Googlebot, and Bingbot meta directives were concatenated, permitting a bot-specific directive to become a false site-wide noindex. Fixed by separating directive scopes.
4. Responses capped at 2 MB were silently interpreted as complete, producing a false thin-page signal on CNN. Fixed by recording `response_truncated` and prohibiting thin classification on capped data.
5. JSON-LD types were extracted with regex. Fixed with recursive traversal of parsed objects/arrays.
6. The HTML parser lost heading context around nested tags. Fixed with a tag stack and suppression depth.
7. Sitemap declarations were not preserved. Fixed by extracting robots `Sitemap:` hints.
8. Robots HTTP outcomes were not modeled according to RFC 9309. Fixed with explicit `present`, `present_no_parseable_groups`, `unavailable_4xx`, `unreachable_5xx`, and `unreachable_network` states and a 500 KiB parse floor.

## Additional tests

Eight local HTTP scenarios pass: named-agent block, 401, 403, 404, 503, malformed rules, wildcard root block, and robots redirect. Direct `/robots.txt` access, final redirect URL, status, content type, truncation, sitemap hints, wildcard policy, and eleven named-agent policies are preserved independently.

Rendered checks were executed on two unseen production routes. ElevenLabs had 10,470 static-text characters and two raw H1 elements versus 9,612 visible rendered characters and one visible H1, demonstrating that raw and rendered structural evidence cannot be collapsed. Acrobat redirected to an app route with no visible body text in the selected browser; this was retained as route/environment-specific evidence, not called a defect.

## Remaining validation gaps

- CrawlIndex validates acquisition and extraction mechanics, not entity correctness, information scent, task completion, or real user engagement.
- WebAIM Million is a suitable next ground truth for rendered accessibility barriers. The marketplace now defines rendered checks, but it still depends on an available browser and does not bundle a complete WCAG engine.
- Human-rated usability datasets are mostly screenshots and perceived ratings, not site-level root-cause labels; they need a blinded annotation protocol before precision/recall can be claimed.
- The skill's agent-written final report still needs blinded evaluator scoring for evidence fidelity, duplicate-root-cause merging, severity calibration, and action quality.
- Retrieval/citation outcomes require a frozen query suite, provider/locale/date controls, repeated trials, and competitor passage comparison. A procedure was added, but no universal citation guarantee is possible.

## Decision

The collector is credible for robots, JSON-LD presence, and coarse static-text gating after fixes. It is not yet valid to claim that the entire marketplace is “proven” for engagement or citation outcomes. The next release should add rendered-DOM/accessibility measurements and an independently labeled report-quality evaluation set.
