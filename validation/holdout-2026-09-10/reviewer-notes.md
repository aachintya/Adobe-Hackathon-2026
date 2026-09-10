# Independent reviewer observations

Recorded without sending these observations to the auditors. This is targeted reviewer inspection, not a comprehensive human usability study or a complete defect inventory.

## Arngren

- Browser loaded https://www.arngren.net/. Sparse/dated styling and many products do not by themselves establish a defect.
- A rendered contact link displays the Gmail address for Frithjof Arngren but its actual `mailto:` destination is the older c2i.net address. The same mismatch occurs on the payment page reached from the homepage. No email was sent; mailbox validity is unknown. This supports a scoped contact-label/destination inconsistency, not a claim that contact is impossible; an alternative arngren.net contact link is present.
- The visible `Snøfreser` product link's literal href is `http://https://gratis-annonse.no/belte-kr-annonse.html`, which points at the wrong host. The malformed href was read from the DOM; it was not followed. This is a narrowly observed link-target defect, not an observed server failure.
- Clicking `Slik Betaler du` actually reached http://www.arngren.net/kjop.html. It exposes payment instructions, a shipping charge with product/large-item exceptions, delivery timing, and return instructions. Therefore a blanket finding that this site lacks ordering/shipping guidance would be unsupported. No payment, form submission or legal-compliance assessment was attempted.
- The public robots URL was unavailable through the reviewer's web-fetch tool. No subsequent crawler expansion or technical-policy conclusion was made from that failed fetch.

After the saved auditor report was available, the reviewer opened https://www.arngren.net/el-varer.html in a fresh browser tab. `GrÃ¸nmo` is genuinely visible in the rendered link text, so at least one encoding error is independently reproduced. The auditor's F-003 still combines this localized issue with mixed language and historical claims; those are not defects by themselves, and its affected count/severity are not established by this one verification.

## Saved Arngren report adjudication

The Luna auditor hit an account usage limit before delivering its final response/timing artifact. Its saved `agent_composed` report passes parent-side schema validation, but this is not a completed timed-run pass.

- F-001 (high, task organization): not accepted as written. It relies on catalogue breadth, image links and a price disclaimer without demonstrating failure of a relevant inspected task. Category links exist. High severity is not supported.
- F-002 (medium, purchase/availability handoffs): insufficiently supported as written. The report did not inspect the linked payment instructions, which the reviewer reached successfully. Contact-based selling or request-a-shipping-quote is not itself a defect. A product-specific unmet task could still exist but needs direct evidence.
- F-003 (medium, mixed encoding/language/history): partially corroborated, requiring narrower wording/scope/severity. Visible mojibake exists on one checked page; a language mixture or an old dated statement alone does not establish material staleness.
- The report did not identify the reviewer's contact-label/destination mismatch or malformed snow-blower link. These are observed misses in this sample, not a recall estimate for the entire site. Review compared the same public homepage; the payment-page second observation was outside the auditor's sample.
- The first question is labelled `answered`, but the cited evidence does not clearly support its own required audience/use-case element. Its four question records need semantic review despite passing the structural validator.

These adverse outcomes are retained. A schema-valid report is not evidence of correct detection or successful generalization.

## Municipal Corporation of Delhi

- Parent browser navigation initially timed out, but a later state inspection showed the actual page loaded at https://mcdonline.nic.in/portal/. A navigation-tool timeout alone is not evidence that the website is down.
- Rendered homepage exposes municipal identity, services including property tax and birth/death registration, a general help/contact route, and links to complaint services. Merely counting source text would not prove these journeys complete; they were not followed during this preliminary review.
- The footer's old update date is not by itself a material stale-fact defect. The historical maintenance notice seen in one search extraction was not visible in the current accessibility snapshot, so it is not yet a verified present-day UI problem.
- Some outgoing service links contain credential-like query values. Values are not reproduced here and were not used. Any saved audit publication will require a bounded sanitization review.

## Municipal report adjudication

The auditor reports browser observations and two completed public-information journeys, not a browserless trial. The parent independently saw the rendered landing page, but has not reproduced the two complete service journeys. The saved report passes parent-side schema validation. Its observed start/end clocks span 356 seconds (09:42:19 to 09:48:15 UTC), already over five minutes; delivery occurred later. Parent observed the final message by 09:49:06 UTC, at most 437 seconds after the pre-dispatch clock of 09:41:49. That upper bound includes dispatch/orchestration and notification delay and is not a precise audit duration.

- F-001 (medium, sessionized/mixed-protocol links): not established as an actionable discoverability defect by the supplied evidence. Observed URL patterns, separate subdomains and absent canonicals do not alone show exclusion, conflicting identity, indexed duplication or failed task completion. A narrower URL-maintenance recommendation could be considered; the present severity and causal claim need verification.
- The report's two public service destinations and working landing-page orientation are positive observations. Their existence is not proof that authenticated services, submission, payment or all navigation work.
- The engagement readiness record says a service choice was exercised, but journey details stop before selecting an event/type. Following a link to a distinct service is not evidence that a non-default material choice was retained across a handoff. Keep this check unverified.
- The fee/document question is marked fully answered with abbreviated examples rather than explicit support for every required band/document. The detailed source may contain them, but structural validation does not establish complete semantic coverage.

## Batch stop

After the Arngren usage-limit interruption, no further Luna runs were launched. Tamil University, boAt and Berkshire Hathaway remain selected but unexecuted. The completed MCD run is retained without mid-run coaching; no instruction revision was made after seeing either auditor result. The adverse sample is too small and incomplete for a generalization score. Resume remaining tests only when account capacity is available; do not silently replace interrupted runs with successes.
