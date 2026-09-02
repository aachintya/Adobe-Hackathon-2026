---
name: engagement-context-audit
description: Audit observable on-site orientation, information scent, continuity, accessibility friction, and task paths without inventing behavioral analytics.
license: MIT
allowed-tools: WebFetch Browser
---

# Engagement and context audit

For each sampled template, identify the likely page purpose from title/H1/intro, primary next step, supporting proof, and routes for common tasks. Follow only safe links; never submit forms.

Use [engagement-gates.md](references/engagement-gates.md). When a browser is available, render the starting/acquisition page and up to two distinct task templates even if static HTML is complete; inspect navigation, primary actions, overlays, context continuity, mobile layout, accessible names, keyboard reachability, and visible focus. Return candidates, passes, and `not_checked`; describe observable friction rather than asserting bounce, conversion loss, or user sentiment.
