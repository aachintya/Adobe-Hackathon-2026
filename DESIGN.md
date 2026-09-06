# Audit design

The marketplace combines four skills around one shared evidence bundle. Python handles collection and validation; the host agent interprets the evidence and composes the report.

## Evaluation

1. Establish what the site offers, whom it serves and which visitor tasks matter. Preserve the supplied locale and path.
2. Check published search-crawler access and engine-specific indexing controls. Keep intentional restrictions scoped to the affected pages and providers.
3. Test 3-5 relevant questions against saved passages, linked pages and rendered content. Record expected answer elements and the evidence for each outcome.
4. Compare material claims across first-party pages and independent sources. Require an observed contradiction or entity confusion before reporting a trust defect.
5. Trace two public journeys and record observed steps, destinations and retained context.
6. When recorded assistant answers are available, measure mentions and target-site citations separately. Group observations by provider, surface, model, locale and prompt intent; exclude unsuccessful runs from rates.

No overall AI visibility score is inferred from HTML counts, markup, training controls or a single search result. Every finding needs evidence, a clear scope and a verifiable action. Healthy sites can have no findings.

## Implementation

- Standard-library helpers keep the package portable. A browser-capable host agent supplies rendered review.
- Source extraction retains material passages, link labels and destinations, structured values and indexing directives. External CSS and JavaScript behavior require a browser.
- Requests use a dedicated crawler identity, respect applicable robots rules and stay within bounded public navigation. Redirects to another authority are left for explicit agent review of the destination's policy and scope.
- The Python report is a `static_baseline`. The agent completes answerability, trust and visitor-journey analysis and records unavailable checks explicitly.
- The collector defaults to 120 seconds. The full skill targets 280 seconds across collection, browser review, search and composition; missing coverage remains visible when time expires.
- The ZIP has one marketplace root and includes its validators and controlled fixtures. Tests run the extracted fallback from an unrelated working directory.

Schema and collector identifiers are machine-readable compatibility metadata. Package names and documentation do not carry release numbers.
