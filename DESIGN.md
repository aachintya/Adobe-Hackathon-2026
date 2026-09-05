# Why version 2 changes the audit

The previous implementation preserved mostly HTML counts and a 1,200-character preview. It made search-citation validation optional, probed GPTBot as if it represented discovery, and its maintained example classified a training restriction as a high-severity discovery defect. It also accepted an image finding without verifying relevance. Those choices could reward a technically tidy report with weak practical conclusions.

Version 2 preserves facts and task evidence, separates search from training, requires question tests and visitor journeys in the agent workflow, and distinguishes observed readiness from actual answer citations. It keeps deterministic mechanics in Python and leaves contextual interpretation to the judging agent.

## Adobe requirements and the chosen implementation

Source: the user's downloaded **6a8ffdf33590a_round3-handout-updated.pdf**, pages 1-6, inspected on 2026-09-05. The [official event listing](https://api.unstop.com/hackathons/adobe-university-hackathon-2026-adobe-1715333) also confirms the marketplace ZIP submission.

| Handout requirement | Implementation |
|---|---|
| Agent Skills format with optional bundled scripts/references (p. 1) | Four SKILL.md files with frontmatter; dependency-free Python mechanics under the entrypoint skill |
| Marketplace manifest, exactly one invoked entrypoint (p. 3) | `marketplace.json`; `audit-orchestrator` reads and composes the three other concerns |
| Detect off-site discovery and on-site engagement causes (pp. 3-4) | Provider-specific access, question answerability, corroboration and two visitor journeys |
| Evidence, severity, prioritized fixes; proactive actions permitted (pp. 1-2) | Fixed report schema with exact scope, action owner, effort, mechanism, verification and optional opportunities |
| Portable, self-contained manifest (p. 5) | No service needed to resolve skills; Python optional, no pip/npm installation or API credentials |
| Recommend-only; respect robots; public safe access (pp. 2, 5) | No website edits, authentication, form submission or provider impersonation |
| ZIP <= 50 MB; typical audit < 5 minutes (p. 5) | Verified ZIP size; shared 280-second agent target, 120-second default collector budget |
| Unseen-site generalization and few false positives (pp. 1, 4) | Domain-independent evidence rules, healthy controls, meaningful regressions and forward-evaluation cases |

The handout does **not** publish a judge launcher command, installed Python version, provider/model or browser/search tool inventory. We therefore do not invent one. The judging interface remains the skill; the root README provides a portable Python smoke command and explains its partial coverage. A pure Python app would miss the requested skill composition, while prose-only skills would repeatedly reimplement fragile collection mechanics.

## How websites are evaluated

1. Establish what the business offers, whom the page serves, and the tasks that matter. Preserve locale and path.
2. Check whether search crawlers are permitted to reach the relevant pages, and whether engine-specific indexing/snippet controls limit use. Keep intentional controls scoped.
3. Test whether 3-5 relevant questions have clear, supported answers in source and/or rendered content. Keep passages, URLs and required answer elements.
4. Compare material same-entity claims across pages and independent sources. Require actual contradictions or confusion before reporting a trust defect.
5. Trace two public journeys. Record what the visitor knows, where the link leads, and what happens to that context. No imagined bounce or conversion numbers.
6. If actual assistant answer runs are available, compute mention and target-site citation rates separately, grouped by provider, surface, model, locale and branded/unbranded intent. Preserve raw answers; exclude failures; use null when nothing was measured.

No universal AI visibility score is inferred from robots, JSON-LD, H1 count, word count, llms.txt or a single search result. Useful content may be cited with minimal markup; an impeccably structured page may still not answer the user's question. [Google's current guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) specifically rejects special markup and fixed-length content as requirements. [OpenAI's crawler documentation](https://developers.openai.com/api/docs/bots) distinguishes search, training and user fetch.

## Engineering tradeoffs

- Standard-library source collection keeps the ZIP runnable. The browser-capable host agent supplies rendered review; the package does not download Chromium during judging.
- The source parser preserves explicit text and excludes obvious semantic navigation/hidden content, but cannot resolve external CSS or a full accessibility tree. Its output labels this limitation.
- Same-authority redirects and bounded sitemap indexes keep collection contained. The agent can inspect a clearly observed public apex/www destination after checking its policy and recording the scope change.
- Python reports only narrow technical observations, labelled `static_baseline`. The skills supply materiality, answerability, trust and task reasoning; an empty finding list is acceptable for a healthy or insufficiently observed site.
- Tests establish mechanics and false-positive controls. They do not establish a population-level precision or citation uplift. Fresh independent agent runs in Adobe's actual environment remain a separate evaluation.
