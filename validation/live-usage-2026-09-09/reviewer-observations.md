# Independent live observations

Reviewer: parent agent, separate from neutral auditing sessions. This is an agent review, not human-labeled ground truth. Only the inspected tasks have known outcomes.

## Linear — 2026-09-08, approximately 10:47–10:50 UTC

Policy checked at https://linear.app/robots.txt: wildcard disallows /api/ and /cdn-cgi/, permits the inspected public routes. Browser: Codex in-app browser, fresh reviewer tab, desktop screenshot 1280 x 720; no login.

Observed journey: homepage navigation link “Pricing” → https://linear.app/pricing. The public destination loaded and showed Free, Basic, Business, Enterprise. Initial Basic $10 per user/month and Business $16 per user/month had “Billed yearly” checked. Clicking Basic's yearly checkbox changed both toggles to unchecked, Basic to $12 and Business to $18. This is functioning billing selection, not a contradictory-price defect. These observations are a dated UI sample, not pricing advice.

Observed extraction/accessibility gap: the “Code Intelligence” comparison row shows crosses for Free/Basic and checks for Business/Enterprise in the rendered screenshot. Each of its four plan cells has empty textContent and no aria-label; the only decision values are SVGs with aria-hidden="true". The accessibility tree exposes the row label without the four yes/no values. Same pattern independently checked on “Private teams” and “Agent platform” (12/12 sampled plan cells). Relevant locators: role=row filtered by the exact feature label, then role=cell with data-plan=free/basic/business/enterprise. Business's card also names Code Intelligence and private teams; this alternate prose reduces severity and prevents claiming that the information is absent site-wide. A bounded medium or low finding should identify lost comparison semantics for nonvisual/text readers, with literal included/not-included text associated with feature and plan as its acceptance test. No citation impact was measured.

Do not infer a pricing contradiction from abbreviated card bullets: “All Basic features +” and non-exhaustive summaries can coexist with a detailed matrix. Do not claim a missing answer merely because a pricing table has no JSON-LD.

## GOV.UK — 2026-09-08, approximately 10:49 UTC

Policy opened at https://www.gov.uk/robots.txt. Wildcard restrictions on print pages and site-search do not block the inspected overview, renewal and urgent-service routes. Fresh reviewer IAB tab, public English desktop pages, no authentication or form submission.

Observed steps: supplied /renew-adult-passport → “Renew” contents link → /renew-adult-passport/renew → “Get a passport urgently” related link → /get-a-passport-urgently. All destinations loaded. Overview and renewal text agree on online and paper prices in the observed response. Renewal supplies prerequisites and a “Renew online” action. Urgent service explains eligibility and timing before “Start now”; reviewer stopped at public instructions. No defect established on these inspected tasks. The cookie banner did not prevent reading or navigation. Multiple H1 elements and a robots-blocked print duplicate are not, by themselves, public-service failures. Website scope remains the supplied service, not every GOV.UK department.

## DuckDB — 2026-09-08, approximately 10:50 UTC and 15:48 UTC

Robots source in the collector evidence permits current and LTS documentation and installation routes; archived /docs/1.3 and older routes were not inspected. Public default desktop macOS IAB, no commands executed or software installed.

First reviewer journey: homepage → “Read the docs” → version selector “1.4 LTS” → LTS documentation → “Installation”. The installer selected 1.5.5 current, not 1.4.5 LTS. Choosing Python, then 1.4.5 LTS explicitly, changed the command to `pip install duckdb==1.4.5`, set `version=lts` in the URL, and changed “Client documentation page” to the LTS Python overview. That destination retained an LTS badge. The session interruption prevented the final return click in this first attempt.

After resume, a fresh reviewer tab opened the previously observed https://duckdb.org/docs/lts/clients/python/overview. Its LTS badge coexists with a latest-stable-version notice and an unpinned install command. Clicked the exact body “installation page” link (https://duckdb.org/install/?environment=python). The destination became https://duckdb.org/install/?environment=python&platform=macos, selected 1.5.5 current (`aria-checked=true`), left 1.4.5 LTS unselected, and displayed `pip install duckdb`. This corroborates the first auditor's scoped context-loss finding. A latest-stable notice on old docs is not automatically false; the actionable mechanism is losing the explicitly selected release in installation instructions. Medium severity is reasonable because the LTS control still offers a recovery route.

## IKEA India holdout preparation — approximately 15:50 UTC

This evidence is withheld from all auditors and is not a basis for tuning the baseline instructions. Robots permits the public Indian landing and delivery pages, while restricting search parameters, cart, checkout and profile routes. Those restricted paths were not visited. Default desktop IAB, English/India URL preserved.

Observed /in/en/ homepage with region heading, local currency and product/service links. Opened cookie preferences, disabled three optional cookie groups and confirmed; consent dialog closed. Followed “Delivery Service” in the footer to https://www.ikea.com/in/en/customer-service/delivery-service-pubd5889e60/. The destination retained /in/en/, exposed price slabs with readable weight/member/non-member labels and prices, service-area qualifications, and an explicit contact route for non-serviceable areas. No postal code, personal information or form response was entered. This public information journey works; individual delivery eligibility remains untested. No missing-shipping-information or lost-region finding is supported on these observations. The initial consent banner is a handled state, not a permanent navigation failure.

## Fastmail holdout — 2026-09-09, approximately 08:21 UTC

Independent reviewer IAB tab. Homepage → Pricing reaches https://www.fastmail.com/pricing/in/ with India selected and 12-month billing. Selected 1 month; it became checked, 12 months became unchecked, and the plan prices/annual-saving descriptions changed together. No signup, messages, personal data or purchase. The comparison table exposes explicit accessible image descriptions such as “Supported on Individual plan”, “Supported on Duo plan”, and “Supported on Family plan” beside the feature rows. This is a useful counterexample to an indiscriminate icon-only comparison warning. Displayed prices have a tax-inclusive qualifier. Cross-country price differences cannot be judged contradictory without preserving locale and billing period. No defect established on these inspected interactions.

## Standard Ebooks holdout — 2026-09-09, approximately 08:22 UTC

Independent reviewer IAB tab. Homepage → “browse our library of free ebooks” → catalogue → “The Final Count” → “Kobo FAQ” reaches https://standardebooks.org/help/how-to-use-our-ebooks#kobo-faq. Book detail provides title/author, format links with device-specific explanations, provenance/change history, and an explicit US-copyright scope notice. The linked help explains kepub for Kobo and other device alternatives. Catalogue keyword/filter forms were not submitted, book files or reading text were not fetched, and no donation/subscription was initiated. This verifies public catalogue-to-format guidance only, not file usability or legal rights in a user's jurisdiction. A generic help URL is not inherently lost book context. No defect established on these inspected routes.
