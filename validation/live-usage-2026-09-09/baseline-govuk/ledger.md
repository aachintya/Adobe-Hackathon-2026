# GOV.UK adult passport audit evidence ledger

Audit start: 2026-09-08T10:46:25Z, recorded with clock.curr_time before task actions.
Scope: https://www.gov.uk/renew-adult-passport
Runtime: host agent using skills/audit-orchestrator/SKILL.md and all three referenced sibling skills.
Assumptions: English-language UK adult renewal is the representative task; international, child, first-passport and expedited application flows are separate. No personal information was supplied.
Capabilities: Python 3 standard-library collector; live web.run search/open; dedicated background Codex in-app browser tab 1. Browser used its default viewport; dimensions and locale were not recorded. Search locale unknown.
No authentication, form answers, form submissions, payments, bot impersonation or site mutations occurred.

## Command record

Ran from <marketplace-root>:
`python3 skills/audit-orchestrator/scripts/run_audit.py https://www.gov.uk/renew-adult-passport --output-dir <raw-evidence-root>/baseline-govuk --max-seconds 120`

Exit code 0. Collector reported 24.86 seconds, 17 requests, 12 page responses of which 11 HTML and one Atom feed; max 2 requests/second. Evidence and static draft were successfully written. Final report replaces that explicitly partial draft.
Full collector observations are preserved in evidence.json. This includes complete target source passages, link labels/destinations, JSON-LD, applicable robots decisions, redirects and sample details.
No development unit-test suite or marketplace edits were performed.

## Question setup

Recorded before judging supporting routes:

1. Who can use the adult passport renewal service? Expected: adult age threshold; renewal versus first passport; UK versus overseas route.
2. What does an adult renewal cost online or on paper? Expected: online standard adult fee; paper standard adult fee; currency and application context.
3. How long should a UK applicant allow, and where is urgent guidance? Expected: routine processing guidance; conditions affecting timing; urgent-service route.
4. What is needed to renew and how do I begin? Expected: old passport requirement; online next step; preparation requirements.

## Static observations

- Supplied page: HTTP 200, final URL unchanged, language en, self-canonical. No robots/googlebot/bingbot meta restriction or X-Robots-Tag was recorded. Complete main_text, evidence_truncated=false.
- Named search policies permit the supplied path for Googlebot, bingbot, OAI-SearchBot, Claude-SearchBot and PerplexityBot. Actual provider IP access is not tested. Training/control and user-fetch policies remain separate in evidence.json.
- /print and /search/all have scoped wildcard restrictions; these utility policies were not called defects.
- Target has 3 parseable JSON-LD blocks, including Article, BreadcrumbList and FAQPage content. Material adult fees in Article/FAQ content agree with the visible overview. Old dateModified values were not used as evidence of stale current guidance.
- Processing-time source at https://www.gov.uk/government/organisations/hm-passport-office/about-our-services redirects to https://www.gov.uk/government/organisations/hm-passport-office/about/about-our-services and canonicals there. Main text is complete.
- Sitemap index returned 35 child references; the two bounded child fetches were truncated. General news extraction also capped. Neither is evidence that target content is missing.
- Static sampling included several general navigation documents. All 11 HTML source responses were checked for status/directives; business reasoning concentrated on the passport documents.

## Preserved browser observations

Observed between 10:46:50Z and 10:48:25Z on 2026-09-08 through the dedicated background tab. Times are bounding clock observations, not fabricated per-action timestamps.

B1. URL https://www.gov.uk/renew-adult-passport
Title: Renew or replace your adult passport: Overview - GOV.UK
Rendered accessibility tree showed overview purpose, adult eligibility, online and paper fees, child/overseas routes, processing-time link, urgent-service link and Renew guide link. Cookie consent was present and did not prevent reading or navigation.
Clicked the Renew link (initial AX index 34).

B2. URL https://www.gov.uk/renew-adult-passport/renew
Title: Renew or replace your adult passport: Renew - GOV.UK
Rendered Supporting documents section listed existing passport and valid foreign passports; Renew online listed photo, payment card and passport preparation. The online and paper amounts matched the overview.
Clicked Renew online (AX index 85).

B3. Exact final URL https://www.passport.service.gov.uk/filter/overseas
Title: Do you live in the UK? – Apply for a passport – GOV.UK
Public form entry appeared with Apply for a passport branding, HM Passport Office ownership, a location fieldset, explicitly named Yes/No radio choices and Continue. No answers entered. No submit performed.
This verifies only reaching the application entry.

B4. Returned to the exact supplied overview, then clicked Check how long it will take to get a passport (fresh AX index 52).
Final URL https://www.gov.uk/government/organisations/hm-passport-office/about/about-our-services
Title: About our services - HM Passport Office - GOV.UK
Rendered document gave the usual three-week period, additional-information/interview exceptions, receipt-of-documents start, overseas distinction and urgent-service signpost.
The How to apply paragraph linked a Post Office branch finder and mentioned an additional £16 without naming Check and Send. This was repeated in complete static source at p [source occurrence 19], under #how-to-apply.
The supporting Check and Send guide resolved which service the £16 refers to. No claim of a wrong passport fee is made.

No mobile, keyboard-focus, contrast, or performance check was performed. No screenshot or viewport-size measurement is claimed.

## Exact search queries and retrieval record

Tool: web.run search_query, one four-query batch executed on 2026-09-08, completed before 10:47:17Z. Locale unknown. No domain filters or recency filters.

- Q1 exact: `HM Passport Office`
- Q2 exact: `renew British adult passport online cost`
- Q3 exact: `UK passport renewal £102 £115.50 2026`
- Q4 exact: `UK passport renewal processing time 3 weeks September 2026`

The tool returned a pooled result set. Per-query source membership/rank was not separately exposed, so no per-query position is asserted.
Relevant returned source URLs included:
- https://www.gov.uk/government/organisations/hm-passport-office/about
- https://www.gov.uk/passport-fees
- https://www.gov.uk/renew-adult-passport/renew
- https://www.gov.uk/government/news/new-fees-for-passport-applications
- https://www.gov.uk/government/publications/uk-passport-fees-transparency-data/uk-passport-fees-transparency-data-30-june-2026-accessible
- https://www.gov.uk/government/publications/application-fees-and-refunds/passport-fees-accessible
- https://www.passport.service.gov.uk/help/passport-offices
- https://moneyweek.com/spending-it/travel-holidays/uk-passport-renewal
- https://www.gov.im/categories/travel-traffic-and-motoring/news?altTemplate=ViewCategorisedNews&id=205635&iomg-device=Desktop

Other returned leads included maps, encyclopedic material, old fee documents and user anecdotes. These were not used to establish current facts. Search snippets were treated as leads, not checked-source evidence.

## Opened source ledger

Sources below were opened through web.run on 2026-09-08 before 10:48:25Z, in addition to static/browser evidence. Exact short quotes below use at most 25 words per webpage across this ledger; the JSON report has additional evidence from local collection/rendering.

S1. https://www.gov.uk/government/organisations/hm-passport-office/about
First party, HM Passport Office; update date not relied upon.
Quote: “HM Passport Office is the sole issuer of UK passports”
Meaning: Official entity/role supports attribution of the application service. Contact/leadership/reputation claims were not needed for these tasks.

S2. https://www.gov.uk/passport-fees
First party, GOV.UK; current observation.
Checked adult standard 34-page table row: online 102 GBP and paper 115.50 GBP. Also distinguishes frequent-traveller, overseas, urgent and optional-service contexts.
Evidence agrees with the landing and renewal instructions.

S3. https://moneyweek.com/spending-it/travel-holidays/uk-passport-renewal
Independent publisher MoneyWeek/Future; article by Oojal Dhanjal, last updated 24 July 2026.
Quote: “Adult (16 and over) standard 34-page passport”
The opened article table shows the same 102 GBP online and 115.50 GBP paper fees. It links GOV.UK as source, so this is editorial repetition consistent with current first-party facts, not an independent measurement of fees or processing performance. Only this narrow corroboration is used.

S4. https://www.gov.uk/government/organisations/hm-passport-office/about/about-our-services
First-party processing-time guidance. The linked legacy path redirects here.
Quote: “This costs an extra £16.00.”
The same paragraph refers to a paper form from a post office without naming Check and Send. Browser and static evidence agree.
The timing facts and exceptions are recorded in report.json.

S5. https://www.gov.uk/how-the-post-office-check-and-send-service-works
First-party supporting guide reached from an observed renewal-page link.
Quote: “It costs £16.00 on top of the passport application fee”
The opened page explicitly separates digital and paper Check and Send charges from the passport fee. This resolves the £16 service context and prevents a false contradiction finding.

## Claim ledger summary

C-001. HM Passport Office provides the official UK passport service. First-party entity page plus rendered service branding agree. Independent verification not needed for this routine identity inference; no observed collision.
C-002. Standard adult UK fee is 102 GBP online / 115.50 GBP paper. Landing, renewal, fee table and MoneyWeek's dated editorial table agree. Status: supported in the inspected sample.
C-003. Normal UK processing is usually three weeks from receiving documents, subject to stated exceptions. First-party source and rendered document agree. Actual completion performance not measured.
C-004. Check and Send is a separate 16 GBP charge. Explicit supporting guide resolves the unnamed charge in About our services. Status: supported; localized wording opportunity O-001, no proved conflicting fee.

## Composition decisions

Crawl/extraction: passes for supplied-path public policy, source readability, canonical behavior and material source/rendered agreement. No missing-schema, short-page, date-age or citation claim.
Entity/trust: consistent sampled current fees and official ownership; separate service variant explains apparent surcharge discrepancy.
Engagement: both public journeys completed; no verified dead end or lost site-selected context.
Finding count: 0. Opportunity O-001: name and link Check and Send next to the additional £16, preserving the distinction from base passport fees.
Actual assistant citations: not_measured. Search observations do not constitute an unbiased assistant citation experiment.

## Coverage arithmetic

11 static HTML documents (one processing-time redirect counted by canonical destination)
+ 2 new rendered documents (renewal instructions and application entry)
+ 3 other first-party web-open documents (fees, HM Passport Office about, Check and Send)
+ 1 opened independent editorial document (MoneyWeek)
= 17 distinct inspected HTML documents.
The Atom response and search-only leads are excluded.

Report validation command and final timing are preserved in timing.json.
