# Luna audits without a browser

The September 11 batch tested the marketplace on public sites using fresh `gpt-5.6-luna` agents at medium reasoning effort. All browser automation, screenshots and rendered tools were prohibited. Python 3.12.14 and public text fetch/search were permitted. No website was modified. The original three runs used commit `fc6958c`; the [protocol and skill hashes](no-browser-2026-09-11/protocol.json) record the tested version. Auditors received no expected defects, previous reports or mid-run coaching.

## Original public-site results

| Site | Finalization elapsed | Auditor findings / opportunities | Important coverage limit |
|---|---:|---:|---|
| British Museum | 221.33 s | 0 / 0 | Collector homepage and sitemap returned 403; audit relied on search excerpts. |
| Framework | 239.58 s | 0 / 1 | Collector returned 403; opened text pages and search excerpts supplied fallback evidence. |
| PostgreSQL | 199.10 s | 0 / 1 | Four readable source pages; interactive and independent corroboration checks remained untested. |

All three passed the then-current finalizer. Parent checks confirmed the report, evidence and review hashes in each receipt. [Hash checks](no-browser-2026-09-11/parent-hash-checks.json). These timings run from auditor-recorded invocation start to the finalization gate, not exact user-request-to-delivery time. Exact per-run dispatch timestamps were not captured. Browser prohibition was an instruction, not physical removal of the tools.

The original reports, source evidence, review sidecars and receipts are preserved byte-for-byte under [the batch directory](no-browser-2026-09-11/). They are historical evidence, not corrected final reports or universal accuracy certificates. Evaluation material is excluded from the submission ZIP.

## Review findings about the marketplace

1. **Search excerpts could inflate inspected-page coverage.** British Museum reported four inspected pages and assigned HTTP 200 to search observations despite recording that direct page responses were unavailable. Search excerpts can establish retrieved text, not a current HTTP status or a successfully inspected live page.
2. **A receipt could validate quotes that omit material answer elements.** PostgreSQL's release question required version lines and a support-end date, but its quotes stopped before those details. Its manual-route question quoted an older-manual sentence without the available current-version text. The underlying source contained stronger evidence; this is report evidence selection, not a demonstrated website defect.
3. **Opportunity and journey prose could exceed the saved evidence.** Framework's opportunity relied partly on absence near a CTA, while its saved homepage excerpt did not preserve that surrounding region. Its corroboration records were labeled search results while the report described them as opened sources. British Museum's guide-journey prose mentioned filters and on-display guidance absent from its saved excerpt. Marking a journey untested does not exempt its observations from evidence review.

Independent Luna review and parent adjudication both contributed. Some reviewer suggestions were not adopted: an official domain and surrounding context can establish an entity without repeating its full name in every quote, and a source-only information journey may legitimately complete at an inspected public endpoint. Review should assess the claim in context, not mechanically downgrade every short quote.

The parent separately opened [Framework's homepage](https://frame.work/) and [configurator](https://frame.work/products/laptop13pro-diy-intel-ultra-3/configuration/new) using text retrieval. Their relationship supports considering a low-priority availability cue before configuration. This later observation does not retroactively repair the original auditor's capture or establish visual placement. Neither public-site opportunity demonstrates a confirmed site defect, causal visibility improvement, or detection recall.

## Implemented corrections

- Retrieval observations must have unknown HTTP status and incomplete capture. They no longer count as inspected pages, expand first-party scope through a supposed redirect, establish completed/friction journeys, or serve as opened-source corroboration.
- Every quote for an `answered` question maps to the required elements it supports. The gate rejects missing, invalid or incomplete mappings. Documentation asks auditors to retain dates, units, variants and conditions in their actual quotes and to review opportunity/journey premises equally carefully.
- The validator remains a consistency check. A false element assignment or an incorrectly labeled observation can still pass; semantic support and source authenticity require review. No heuristic is presented as an entailment verifier.
- The public report schema remains 1.2. Review sidecars for answered questions now need `element_indices`. Historical sidecars lacking these mappings fail the stricter gate; [post-run checks](no-browser-2026-09-11/revised-gate-checks.json) preserve that distinction. Their rejection is not evidence that every historical answer was false.

## Demonstrable addition: answer and qualifier locality

The new optional [answer-locality probe](../skills/audit-orchestrator/references/answer-locality.md) runs offline against saved source evidence. A reviewer chooses exact answer/qualifier quotes; the helper finds their shortest enclosing word span and tests fixed word-window alignments. It preserves input hashes and makes no network requests.

An independent Luna selected three cases from the saved PostgreSQL evidence. With 20-, 40- and 80-word budgets, the release/support relationship needed a 200-word span, a nearby open-source/extensibility pair needed 9 words, and the selected current-documentation pair needed 72 words. The last fits some 80-word window but neither tested alignment, illustrating why a single arbitrary boundary is not proof of a site defect. [Cases](no-browser-2026-09-11/answer-locality/cases.json), [results](no-browser-2026-09-11/answer-locality/result.json).

The packaged synthetic before/proposed example preserves the same selected price and billing terms while reducing their separation from 197 words to 15 words. This is a reproducible editing demonstration, not a live site change. The probe uses whitespace-delimited words, not model tokens; it does not simulate a real retrieval engine, measure semantic completeness, or predict citations. It is optional and adds no mandatory phase to the five-minute audit.

## Fresh runs after the changes

A new, uncoached Luna audited Django using the revised instructions and gate. It finalized in **167.93 seconds**, with five source pages, four question records, two source information journeys and no defect findings or opportunities. Every answer quote supplied the new element mapping, and the revised gate passed. [Report](no-browser-2026-09-11/django-forward/final-report.json), [receipt](no-browser-2026-09-11/django-forward/final-report.json.receipt.json).

Parent semantic review still found a meaningful limitation: the security question mapped the titles of fixed releases to an `affected versions` requirement, although the saved page separately listed affected branches. That mapping is structurally valid but supports the wrong relationship. Its date was available in the URL and full source but omitted from the chosen quote. This forward test demonstrates that the new workflow is executable within the time budget; it does **not** demonstrate complete semantic reliability. The auditor also described search as unavailable although text search was permitted in its prompt; record this as unused coverage, not proof that the host lacked the tool.

A second fresh Luna inspected a newly created three-page local tour-operator fixture through HTTP only, with no access to its source or private expected outcomes. It finalized in **181.02 seconds**, detecting both planted roots: the homepage's explicit `noindex` directive and the reservation CTA's HTTP 404 destination. The report used a captured-field assertion for the former and a literal-href/destination assertion for the latter, retained correct price, age and cancellation qualifiers, and made no extra findings. Parent schema/evidence validation and all receipt hashes passed. This supports two controlled detections, not population precision or recall. [Report](no-browser-2026-09-11/controlled-forward/final-report.json), [parent checks](no-browser-2026-09-11/controlled-parent-checks.json), [private expectations revealed after the run](no-browser-2026-09-11/controlled-expectations.json).

The fixture source is preserved in `no-browser-2026-09-11/controlled-fixture/`; its temporary local HTTP server was stopped after the run. The revised package hashes used by the fresh runs are preserved in [the forward protocol](no-browser-2026-09-11/forward-protocol.json). The complete deterministic suite passed, including 30 evidence tests, 8 locality tests, 15 finalizer tests and the extracted-package test. The skill frontmatter check also passed; its development-only YAML dependency was installed outside the marketplace.

## Remaining evaluation needs

The problem-statement priorities are taken from the user's earlier supplied Round 3 analysis and the repository's documented interpretation: useful detection, actionable and non-obvious suggestions, generalization, read-only execution and typical runtime below five minutes. The original PDF is not present in this workspace; this batch is not a new certification against every rubric clause.

Broader unseen-site coverage, repeated runs, actual end-to-end delivery timing and semantic evidence fidelity remain necessary. No-browser testing cannot establish rendered-content parity, interactive state retention or visual usability. Actual assistant citations still require separately recorded assistant answers. Zero public-site defect findings does not establish recall or site health.
