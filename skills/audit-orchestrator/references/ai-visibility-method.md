# Practical AI visibility method

## Mechanism and measurement

An assistant may answer from model knowledge or retrieve fresh sources. Retrieval can involve query rewriting, search indexes, source selection and extraction; the answer may mention a brand, cite its own site, cite a third party about it, or omit it. These are distinct outcomes. An on-site audit can identify obstacles and test answerability; it cannot infer a provider's private ranking, live bot IP access, personalized answers or overall citation probability.

Use five diagnostic stages and keep actual visibility in a separate measurement lane:

| Stage | Evidence to collect | Actionable failure gate |
|---|---|---|
| Access | Named search policy per valuable path; status, redirects, engine-specific meta and X-Robots-Tag; snippet restrictions | Applicable observed restriction on a page intended for discovery; preserve engine/path scope and intentional controls |
| Extraction | Short material fact quotes from source HTML and, where possible, the rendered page; media alternatives | A decision-critical visible fact is unavailable to the tested reader; do not diagnose from word count alone |
| Answerability | 3-5 site-specific questions, required answer elements, inspected URLs and supporting passages | A user cannot resolve an important question on the inspected relevant pages; distinguish ambiguous, missing-in-sample and untested |
| Corroboration | Same-entity claim ledger with first-party and independent sources, dates, locale and variants | Material contradiction or observed name collision; search absence and first-party-only routine facts are not defects |
| Engagement | Two safe visitor journeys with starting context, links, destination and observed outcomes | An observed dead end, unexplained destination, lost selected context or verified task barrier |

For example, an analytics buyer might ask about cookie consent, hosting location, traffic limits and the next step. A university visitor might ask about programme eligibility, deadlines and application guidance. Infer relevant tasks from evidence; don't impose a SaaS checklist on every site. Record expected answer elements before examining all supporting pages, and judge passages semantically rather than by keyword matching.

`assessment.intent_tests` records `question`, `required_elements`, `status` (`answered`, `partial`, `missing_in_sample`, `not_checked`), `evidence` (URL and short quote), and `reason`. Only use `missing_in_sample` after inspecting relevant untruncated evidence. It never means the whole web lacks an answer. Structured data may help resolve an actual ambiguous fact, but its absence is not an automatic finding.

`assessment.journeys` records `task`, `starting_context`, `steps` (URL, action and observation), `status` (`completed`, `friction`, `not_checked`), and `reason`. Completion means reaching a public information/next-step destination; stop before a form submission, purchase or authentication. A brand cannot be expected to receive a visitor's private assistant conversation. Test retention of context the website itself knows, such as selected plan, region or product, only when safely observable.

## Provider distinctions

- OAI-SearchBot concerns ChatGPT search. GPTBot concerns training. ChatGPT-User is user-initiated access and does not determine search inclusion. A training opt-out is not a discoverability defect.
- Googlebot and relevant indexing/snippet controls affect Google's Search pipeline. Google-Extended is a different control. Google Search Console also has owner-only generative-AI controls/reporting; public crawling cannot inspect these settings.
- Record Claude/Perplexity search and user agents independently. If a provider's current behavior is unclear, limit the conclusion to the published rule and verify its official documentation before prescribing changes.
- A request carrying a bot-like User-Agent from a local machine does not establish that a provider's real crawler can access the site. Use actual provider logs/inspection when supplied; otherwise mark that check unavailable.

## Sources verified 2026-09-05

- [OpenAI crawler roles](https://developers.openai.com/api/docs/bots): independent search, training and user-fetch controls.
- [Google generative AI optimization guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide): relevant useful content and existing search systems; no special AI schema, ideal word count, chunking or llms.txt requirement; provider measurement is distinct from third-party guesses.
- [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html): robots matching and retrieval behavior. The collector restricts redirects to the audited authority as a deliberate safety/coverage limit; it does not claim to reproduce every provider's crawler.
- [Anthropic crawler roles](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) and [Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers): provider-specific search, training and user-request purposes.

Provider behavior changes. Use the current official source when a conclusion depends on it. These sources explain mechanisms, not a promise that any checklist will cause citations.
