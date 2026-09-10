# Paired-run reviewer evidence

The parent inspected public pages independently of the audit reports' authors. Observations below are bounded and are not a complete site audit or a user study. No instructions or suspected defects were sent to the auditors during their runs. Model language and judgement differences are confounders: one run per mode cannot prove that browser access alone caused differences.

## Tamil University: browser evidence

1. At https://www.tamiluniversity.ac.in/english/, the actual navigation exposes Academic, Admission, Learning Management System and Contact Us, plus the main heading identifying Tamil University, Thanjavur and its language/research purpose. This contradicts a blanket claim that relevant task routes or identity are absent from the landing page. The parent initially used the uppercase accessibility label in a case-sensitive locator; that selector failed, and the current DOM's title-case `Admission` locator worked. That was a reviewer selector error, not site friction.
2. Clicking `Admission` reached https://www.tamiluniversity.ac.in/english/admission/. The primary content lists PG/Diploma/Certificate material for 2021-22 and B.Ed/M.Ed/Ph.D material pointing to 2020-21 routes. One online application link has an empty href. The site homepage and contact-page news also expose 2026-27 application/prospectus notices. This establishes a stale primary admissions route and a narrowly observed empty application href, not that current documents are absent from the entire site. Current notices provide an alternative, so the auditor's `high` severity needs moderation or stronger scope evidence.
3. Clicking `Contact Us` reached https://www.tamiluniversity.ac.in/english/contact-us/. The Web Master row's visible address and `mailto:` address disagree. The parent read the literal href; it did not open a mail client or send email. This corroborates the browser auditor's observation, but it is localized contact/engagement friction with working alternative contacts, not demonstrated discovery exclusion. A low severity is more proportionate than the submitted medium absent evidence of greater impact.
4. On that contact page, a visible `Academic Fee` link points directly to https://www.tamiluniversity.ac.in/english/wp-content/uploads/2022/03/academic-fee-1.pdf. The parent checked visibility and href. The news permalink and actual document are distinct destinations; the text auditor inspected the permalink, not this PDF.
5. The PDF was downloaded, text-extracted and its entire single page rendered and viewed. It is a certificate-fee notification dated 2 March 2022, effective 3 March 2022, with four certificate types and rupee amounts. It contains fee information and readable English equivalents. It is not a tuition fee schedule for every course; whether it remains current was not independently established. Therefore the text auditor's proposed remedy to publish a fee document overlooks an existing document, and its prospective-student tuition question requires a programme prospectus or admissions source before alleging absence. No claim is made that all tuition questions are answered.

## Tamil University: adjudication

- Browser run F-001: factual core corroborated; severity/scope require narrowing because current notices offer another route.
- Browser run F-002: exact link-label mismatch corroborated; category/severity should be narrowed to localized contact friction.
- Text run F-001: unsupported as written. It infers above-the-fold orientation from static ordering and overlooks actual task navigation; old styling or a short title is not itself a medium defect.
- Text run F-002: insufficient sampling and wrong fee context. A reachable certificate-fee PDF was uninspected. The fee question remains partly untested, not an established missing-content finding.
- Text run marks one journey `friction` despite its no-browser limitation and incomplete document inspection. The unobserved portion should remain `not_checked`; it cannot establish rendered journey failure.
- The text run missed the verified Web Master mismatch even though it inspected the same contact page. It did not inspect the Admission page, so its failure to find that issue is also a sampling limit.
- Both original reports passed parent-side schema validation. They were not altered to fit the review.

## Arngren: browser report review

The parent inspected https://www.arngren.net/alkotester.html in a real browser and viewed a screenshot. The top product block prominently shows `139,-` beside `Tilbud !` (offer/sale). The DOM also contains a 399 price and separate wholesale quantity/tax qualifiers. These are not automatically mutually exclusive current prices. The browser report quotes the sale label itself; its high-severity price-conflict conclusion is not accepted without resolving the sale/regular/wholesale relationship. No purchase or payment was attempted.

- F-001: high-severity payable-price conflict insufficiently supported; the visible sale qualifier was not accounted for.
- F-002: combines layout breadth, a historic date, fragmentation and encoding into an overbroad medium finding. Actual localized mojibake was confirmed in the previous independent review, but `Kj ø p` is also a word split across separate links, not by itself proof of a decoding error. A historic date or a mixed catalogue is not a defect. Narrow reproduction and scope are needed.
- F-003: a manual bank-transfer/email ordering process and absence of a cart are not themselves a defect. The report establishes reachable purchase guidance and does not demonstrate an incorrect carried choice or an unmet permitted task. A product-specific summary could be an optional usability improvement, not a proven medium failure.
- The browser report's executive summary says two journeys completed while its records contain one `friction` and one `completed`; counts/status prose disagree.
- Off-site corroboration relied on a search result without opening the claimed independent source; the report discloses that limitation, but `observed` corroboration overstates the verification.
- Both older reviewer-observed contact-label mismatch and malformed snow-blower href remain unreported. This is a small set of observed misses, not site-wide recall.

## Arngren: no-browser attempt

The worker stopped with a model-usage-limit error before delivering a final report. The saved `report.json` is not valid JSON: parent validation returns `Extra data: line 1 column 9805 (char 9804)`. It contains an initial JSON object followed by an extra closing brace and another report-like object. No `timing.json` was saved. The parent did not repair, select one object as the answer, or restart the worker after the quota error. There is no valid delivered report or trustworthy end-to-end timing for this attempt; exclude it from accuracy comparisons and count it as an incomplete run, not a pass.

## Publication handling

Raw report files remain unchanged in the test directory. The Arngren browser report unnecessarily reproduces a public bank account and payment phone number; repository/publication copies will replace those with descriptive redaction tokens. Timing copies will replace local interpreter/validator paths with portable placeholders. These redactions do not repair or change the audit's findings, counts, severities, timestamps or methodological errors.
