---
name: engagement-context-audit
description: Audit observable on-site orientation, information scent, continuity, accessibility friction, and task paths without inventing behavioral analytics.
license: MIT
allowed-tools: Read WebFetch Browser
---

# Engagement and context audit

Use the shared visitor questions to choose two realistic journeys, such as understanding an offer then finding cost/eligibility, and verifying suitability then reaching contact/application instructions. Identify the actual starting context, expected public destination, labels, URLs and observed result. Return the `assessment.journeys` records with candidates, passes and `not_checked`. Use context-appropriate tasks, not a universal pricing/signup checklist. Follow safe links; never submit forms.

Assign journey status by the observed cause: `completed` when the chosen public endpoint is reached, `friction` for demonstrated website-side interference, and `not_checked` when an essential remaining step is unobserved because of tool availability, a client/policy block or the time budget. Keep successful earlier steps in the record, but do not turn a tool error into site friction or a website-owner recommendation.

Use [engagement-gates.md](references/engagement-gates.md). When a browser is available, render the starting/acquisition page and up to two distinct task templates even if static HTML is complete; inspect navigation, primary actions, overlays and context continuity. Check mobile layout, accessible names, keyboard reachability and visible focus when the tools and shared time budget permit; otherwise mark these separately `not_checked`. Without a browser, source links can establish information routes, but not successful interactive behavior. Do not require the site to know a user's private assistant conversation or to offer personalization without demonstrated need. Describe observed friction rather than asserting bounce, conversion loss, or sentiment.

For the second journey, prioritize one decision-changing choice exposed by the site: a supported release, billing period, product variant, service eligibility or locale. Use a safe public control and follow its next-step link; if the page offers a return to the selected task, inspect that handoff too. Read [choice-and-handoff.md](references/choice-and-handoff.md) when such a choice exists. A label or parameter alone does not prove retained state: verify the destination's selected value and material instruction. If no safe choice exists, use a distinct information task and state why context retention was not applicable.
