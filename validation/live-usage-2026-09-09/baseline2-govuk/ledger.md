# GOV.UK passport renewal audit ledger

Started 2026-09-08T15:47:14Z (epoch 1788882434). Tools: Python standard-library collector, public web search/open, background IAB browser. Scope: supplied path and sampled public supporting pages. Assumed audience: UK-based adult renewing an existing British passport; overseas and urgent variants tested only as public guidance. No authentication or submission.

## Questions frozen before supporting-page inspection

1. Who can use adult passport renewal? Required: adult age threshold, existing-passport renewal context, overseas alternative.
2. What does standard renewal cost? Required: online and paper fees, UK scope.
3. How long does it take and what if travel is urgent? Required: normal processing expectation, caveat, urgent route.
4. What do I need and where do I start? Required: old passport/photo/payment preparation and explicit application destination.
5. Which public body runs the service and how can I track an application? Required: HM Passport Office identity and tracking route/reference requirement.

## Browser observations

- Opened supplied https://www.gov.uk/renew-adult-passport in own background IAB tab 1. Rendered H1 identifies renewal/replacement; overview shows £102 online, £115.50 paper; aged 16+ or turning 16 within three weeks; overseas alternative and processing-time, urgent and tracking links. Cookie banner contains accept/reject controls and did not prevent accessibility-tree inspection. Normal default viewport, exact dimensions and browser locale not yet measured.

## Executed browser journey ledger

- Clicked Renew (AX 34) on the overview; reached https://www.gov.uk/renew-adult-passport/renew. Read Supporting documents, Renew online and paper guidance: old passport, any other valid passports, photo and card requirements.
- Clicked Renew online (AX 85); reached https://www.passport.service.gov.uk/filter/overseas. The official service displayed Do you live in the UK?, labelled Yes/No radios, Continue and Built by HM Passport Office. Stopped without input or submission.
- Used browser Back twice, inspecting fresh accessibility state after each navigation, then clicked Check how long it will take to get a passport (AX 52). Reached https://www.gov.uk/government/organisations/hm-passport-office/about/about-our-services via the observed same-authority redirect.
- First processing-page accessibility snapshot was incomplete during navigation. A combined accessibility/screenshot observation then showed complete content. Screenshot dimensions were 1280 by 720. It showed an ordinary cookie banner above content, not a challenge. Browser locale remained unknown; collected page language was en.
- Processing guidance: normal expectation three weeks from receipt of documents; information/interview requests may take longer. Under How to apply, the paper-form sentence says: This costs an extra £16.00. Same statement is in untruncated static main text and Article JSON-LD.

## Retrieval ledger

Executed one four-query web search batch on 2026-09-08, English, UK task scope, tool locale unspecified:

1. `HM Passport Office`
2. `renew UK adult passport online requirements cost`
3. `UK passport fee 102 115.50 April 2026`
4. `UK passport renewal processing time three weeks 2026`

The batch returned GOV.UK passport guidance, HMPO identity sources, parliamentary material and anecdotal results. Only opened relevant sources were used for claims; no query-specific rank or assistant citation was inferred. Selected returned leads included https://www.gov.uk/government/organisations/hm-passport-office/about/about-our-services and https://publications.parliament.uk/pa/ld5901/ldselect/ldsecleg/292/292.pdf. Older parliamentary processing evidence and anecdotal social posts were not treated as current service guarantees.

Opened source facts, observed 2026-09-08:

- https://www.gov.uk/government/organisations/hm-passport-office: organisation description identifies HMPO as UK passport issuer and part of Home Office. First-party identity source.
- https://www.gov.uk/passport-fees: standard adult 34-page passport shows online £102 and paper £115.50. Other passport variants and overseas/urgent routes are distinguished.
- https://www.gov.uk/how-the-post-office-check-and-send-service-works: How much it costs identifies £16 for Check and Send on top of the passport fee; paper service excludes photos. This explains the likely intended service behind the ambiguous processing-page sentence without asserting an actual billing error.
- https://www.gov.uk/track-passport-application: tracking routes distinguish PEX, POD and paper references; no private reference was entered.
- https://www.gov.uk/get-a-passport-urgently: premium and fast-track guidance, preparation and restrictions available. Opened via web tool, not traced further in browser.
- https://publications.parliament.uk/pa/ld5901/ldselect/ldsecleg/292/292.pdf: House of Lords Secondary Legislation Scrutiny Committee, 57th Report, published 23 April 2026. Paragraph 23 (PDF page index 9) supports standard online fee rising from £94.50 to £102. Independent legislative scrutiny, not independent measurement of processing time.

## Claim ledger

Entity: HM Passport Office; canonical identity URL: https://www.gov.uk/government/organisations/hm-passport-office. Identifier: HMPO. Service scope: UK passports; public renewal guidance assumes domestic adults and directs overseas cases separately.

- C-001 — Standard adult online renewal fee GBP 102; materiality high; first-party sources overview, Renew and Passport fees, observed 2026-09-08; independent source parliamentary report published 2026-04-23, supports true; status supported; no fee conflict.
- C-002 — Standard adult paper renewal fee GBP 115.50, compared with GBP 16 Check and Send surcharge; materiality high; first-party sources Passport fees, Check and Send and About our services, observed 2026-09-08; independent sources none; status conflicted in presentation: About our services omits the optional-service qualifier. No evidence of incorrect actual charge. F-001.
- C-003 — Usual UK processing expectation three weeks from receiving documents, with caveats; materiality high; first-party source About our services, observed 2026-09-08; independent sources none; status self_asserted. Older parliamentary or anecdotal timelines were excluded as incomparable.
- C-004 — Service operated by HMPO; materiality high; first-party sources official service footer and organisation page, observed 2026-09-08; independent identity verification not checked; status self_asserted.

## Stage handoff and validation

- Crawl passes: landing HTTP 200, coherent canonical, permitted named search policy, readable facts, three valid JSON-LD blocks. Old metadata dates were not treated as defects. Unresolved: real provider access and capped inventory.
- Entity candidate: F-001, one ambiguous cost-bearing page of five inspected, shared root cause across readable text and structured data. Independent online-fee support found.
- Engagement passes: both public journeys completed. No observed navigation barrier. Mobile, keyboard/focus, contrast, metrics and submissions not checked.
- Collector: 17 requests, 14.86 seconds, deadline not reached; 11 HTML pages plus one Atom response. Two sitemap children and the news listing extraction capped. Required report validator returned valid=true, errors=[], exit 0. No unit tests run.
