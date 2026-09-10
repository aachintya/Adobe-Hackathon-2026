# Paired real-website usage tests — 10 September 2026

## Conclusion

Three of four audit attempts completed and passed the JSON schema validator. They were faster than the previous over-budget holdout, but factual interpretation remains unreliable. The university browser report found two independently corroborated issues with overstated severity/scope; the university text report made two insufficiently supported findings; the Arngren browser report's three findings were not accepted unchanged. The fourth attempt hit a model-usage limit and left invalid JSON. This is evidence of progress in bounded runtime, not evidence of submission readiness or accuracy on arbitrary websites.

## Design and version

Two public, less-polished sites were tested in paired fresh `gpt-5.6-luna` / medium sessions: Tamil University (a new completed target in this project) and Arngren (a repeat target, not a fresh holdout). Each auditor received the URL, package entrypoint, permitted capabilities, read-only boundaries, clock instructions and its own output folder. No prior reports, expected findings or mid-run coaching were supplied. The skill-creator independent-forward-testing procedure informed this isolation; findings were reviewed only after the runs.

Mode A permitted browser rendering, Python and public text fetch/search. Mode B permitted Python and text fetch/search but prohibited rendered-browser tools by instruction. This did not physically remove browser tools. No Python-absent mode was run in this batch. One run per mode, different sampling decisions and model variability prevent attributing every difference to browser access alone.

Base Git revision: `3f3eb64b8c68e9583b4176ca3cc34d5f8f40675f`, plus the preceding local runtime candidate. The tested skill remained frozen throughout this batch:

- Entrypoint SHA-256: `6132ecb0b8331d67cdb295dc3d3486313de3b566e24131856c7edbf71890ba51`.
- Evidence policy SHA-256: `a1797b7a8165594e2c15e67c2d6da064353ce62c1020d2a246c043dc7765b448`.
- Retrieval validation SHA-256: `bbc286375692f7ef02739839bb9dfae5adebe55c73c1640e158236bcf58ce6b8`.

The manual setup guide was added outside those frozen instructions and was not supplied to the auditors. The candidate and new documentation were local/unpushed when the tests and initial report were completed; this publication includes them together. Use the hashes above to identify the tested instructions. [Frozen protocol](paired-usage-2026-09-10/protocol.md).

## Results

| Site / permitted mode | Agent-recorded report time | Parent observed final, measured from agent start | Output and independent review |
| --- | ---: | ---: | --- |
| Tamil University / browser + Python | 206 s | ≤243 s | Valid JSON; 2 factual cores corroborated, both need severity/scope correction. |
| Tamil University / no browser + Python | ~147 s | ≤178 s | Valid JSON; 2 findings unsupported or insufficiently sampled as written. |
| Arngren / browser + Python | 190 s | ≤236 s | Valid JSON; 3 findings not accepted unchanged; sale interpretation, overbroad encoding/layout claim, and unproven ordering friction. |
| Arngren / no browser + Python | Unknown | No completed delivery | Usage-limit interruption; saved JSON invalid; no timing file. Not a pass. |

Agent times include instruction reading through the report/validation clock, not exact final delivery. Parent observations include notification delay, but exclude unknown dispatch-to-agent-start overhead. These are not exact user-request-to-delivery measurements. The three completed runs were observed under five minutes from their recorded agent starts; that does not prove Adobe's end-to-end requirement for other machines, hosts, permissions or sites. The previous MCD run at approximately 356 seconds remains an adverse result, not superseded by these faster runs. [Earlier holdout](HOLDOUT-2026-09-10.md), [timings and parent validation](paired-usage-2026-09-10/parent-checks.json).

## Evidence that changed the verdicts

### Tamil University

The parent independently opened the live site and followed the relevant navigation; no messages, applications or forms were submitted.

1. **Stale main admissions route: corroborated, but narrower than the report.** Clicking Admission from the homepage reaches a page listing 2021–22 and 2020–21 material. One application href is empty. However, the homepage/contact-page news also link 2026–27 application and prospectus notices. The defect is the stale primary route, not absence of current admissions information everywhere. The submitted high severity needs moderation or stronger impact evidence. [Admission page](https://www.tamiluniversity.ac.in/english/admission/).
2. **Contact link-label mismatch: corroborated, localized.** The Web Master row displays `karthickanandbabu.ab@gmail.com` but its literal href is `mailto:sbaskarantj@gmail.com`. No email link was activated. This supports a contact-routing defect, not demonstrated discovery exclusion; other working contacts make low severity more proportionate on the observed evidence. [Contact page](https://www.tamiluniversity.ac.in/english/contact-us/).
3. **The text-only fee conclusion overlooked a document.** The text auditor inspected an Academic Fee news permalink. The visible Academic Fee link on the contact page instead reaches a readable, one-page certificate-fee PDF. It gives certificate types, amounts and a 2022 effective date. It is not a programme tuition schedule, and current validity was not established. A prospective student's tuition question needs the relevant programme/admissions source; the inspected sample cannot prove site-wide absence. The PDF was independently extracted and fully rendered/viewed. [Official certificate-fee PDF](https://www.tamiluniversity.ac.in/english/wp-content/uploads/2022/03/academic-fee-1.pdf).
4. **The text-only homepage conclusion overreached.** The rendered homepage visibly offers Academic, Admission, LMS and Contact Us navigation and identifies the university and its purpose. Static extraction order did not justify an above-the-fold orientation claim. Its unfinished, non-rendered journey should not be presented as proven rendered friction. [Homepage](https://www.tamiluniversity.ac.in/english/).

The text auditor missed the contact mismatch on a page it inspected. It did not sample the Admission page. This is an observed miss/sampling limit, not a complete recall measurement.

### Arngren

The parent opened the alcohol-tester product page in a real browser and inspected its DOM and screenshot. The prominent `139,-` price appears next to `Tilbud !` (offer/sale); other amounts include a regular-looking price and explicitly quantity/tax-qualified wholesale prices. The report quoted the sale label but still called the prices an unresolved high-severity conflict. That conclusion needs to account for the qualifiers first. It is not accepted on the submitted evidence. [Product page](https://www.arngren.net/alkotester.html).

The other findings also need correction: a historic date, broad catalogue and fragmented link text are not themselves defects; localized mojibake needs its own narrow evidence. Manual payment/email ordering and absence of a cart are not automatically failures when purchase guidance is reachable and no incorrect handoff is demonstrated. No payment was attempted. The executive summary also claims two completed journeys while the structured records show one completed and one with friction. A search snippet was used without opening the claimed independent corroborating page.

The failed no-browser attempt is preserved as found, not repaired into a second Arngren result. Parent validation returned `Extra data: line 1 column 9805 (char 9804)`. Its partial contents are excluded from quality comparisons.

## What to do next

Prioritize finding precision over additional output volume: verify sale/quantity qualifiers; inspect obvious linked documents before alleging missing information; distinguish unfamiliar design/workflows from demonstrated task failure; calibrate severity to observed impact; and keep unobserved interaction steps `not_checked`. These are candidate improvements suggested by this batch, not changes already proven effective.

After any focused change, use fresh uncoached runs and unseen sites across several business types, plus healthy controls. Preserve interrupted runs and both unsupported findings and independently observed misses. Measure dispatch-to-delivery with an external stopwatch. Test browser/no-browser and Python/no-Python configurations separately, with actual permissions recorded. Neither a tool declaration nor this experiment establishes Adobe's undisclosed browser/Python availability.

Your friend can use [the manual testing guide](../evals/MANUAL-TESTING.md) in Cursor or another file-capable agent. Clone the revision publishing this report, or share a ZIP with matching skill hashes, to reproduce the tested instructions. The earlier base commit alone does not contain the candidate changes. This guide was reviewed for setup clarity and packaged-link integrity; Cursor itself was not operated in an end-to-end test.

At batch completion, the pre-publication submission ZIP was rebuilt, extracted into a path containing spaces, and its Python collector and validator successfully executed from an unrelated working directory. This is a packaging/portability check, not another live-site agent-quality pass. That archive's SHA-256 was `c79f1b557c9cf1d5f640a50c047772c72432388e39d1dc7bdcf1673d5dfc3a2b`; later documentation-only publication updates can change the ZIP hash without changing the tested skill hashes. The ZIP includes the manual guide; evaluation reports under `validation/` stay outside the submission ZIP.

## Artifacts and limits

- [Tamil browser report](paired-usage-2026-09-10/tamil-browser/report.json) and [timing](paired-usage-2026-09-10/tamil-browser/timing.json).
- [Tamil text report](paired-usage-2026-09-10/tamil-text/report.json) and [timing](paired-usage-2026-09-10/tamil-text/timing.json).
- [Arngren browser report](paired-usage-2026-09-10/arngren-browser/report.json) and [timing](paired-usage-2026-09-10/arngren-browser/timing.json).
- [Arngren text file at interruption — intentionally invalid JSON](paired-usage-2026-09-10/arngren-text/report-at-interruption.json).
- [Detailed independent reviewer notes](paired-usage-2026-09-10/reviewer-notes.md) and [publication/redaction notes](paired-usage-2026-09-10/PUBLICATION-NOTES.md).

This is bounded AI-agent usage testing with independent parent review, not a human user study, comprehensive ground truth, measured population precision/recall, proof of search-engine visibility, or a guarantee for “any website.” Original audit conclusions are preserved even when this review rejects them. Valid JSON demonstrates structural compliance only.
