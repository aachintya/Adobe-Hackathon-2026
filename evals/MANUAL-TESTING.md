# Run the marketplace yourself

This package is a set of agent instructions plus optional Python helpers, not a standalone chatbot. A host agent must read the entrypoint, inspect the website, apply the sibling skills and compose the report. Running Python alone produces only a `static_baseline`.

## 1. Get the same version

For the published repository:

```sh
git clone https://github.com/aachintya/Adobe-Hackathon-2026.git
cd Adobe-Hackathon-2026
git rev-parse HEAD
```

Alternatively, extract the submission ZIP and open its `brand-ai-readiness-audit` folder. Keep the complete folder structure: `marketplace.json`, all four skill folders, references, scripts and tests. Do not copy only the entrypoint's SKILL.md.

Record the commit ID, or the ZIP's SHA-256 if testing an archive. A locally shared candidate ZIP may differ from GitHub's published version. Do not compare runs from different revisions as though only the tools changed.

## 2. Open it in Cursor or another file-capable agent

In Cursor, open the extracted/cloned root folder and start a fresh Agent conversation. Cursor documents Agent file/terminal capabilities and a built-in browser, subject to permissions and enterprise controls. Confirm what is actually enabled in your installation; keep approval safeguards for unfamiliar websites. [Cursor Agent](https://cursor.com/docs/agent/overview), [browser and permissions](https://cursor.com/docs/agent/tools/browser).

For this manual test, explicitly point the agent at `skills/audit-orchestrator/SKILL.md`; you do not need to rearrange the submission into an app-specific directory. `marketplace.json` is the contest's manifest, not a promise that Cursor automatically imports a marketplace. Cursor's automatic skill discovery uses designated skill directories; that is a separate installation option. [Cursor skill discovery](https://cursor.com/docs/skills).

Before the timed audit, check only the environment, not the target website:

```text
Confirm that you can read marketplace.json and locate all four declared
SKILL.md files. Do not run an audit or modify the package yet.
List your actual public web-fetch/search, browser automation, file-write,
clock and Python-execution capabilities. Distinguish installed tools from
permitted tools. Tell me if any required files cannot be read.
```

If using Python helpers, check that your available interpreter is Python 3.10+:

```sh
python3 --version
```

On Windows this may be `py -3 --version`; some systems use `python`. The helper uses only the standard library; no `pip install` or API key is needed by this repository. Your host agent still needs its own account/model access. If the host cannot read local files, use a supported attachment/import mechanism for the complete package; do not assume that uploading a ZIP makes every linked reference accessible.

## 3. Send the audit prompt

Replace `TARGET_URL` and `OUTPUT_FOLDER` with a real public URL and a writable folder outside the marketplace. Use a fresh output folder for each run. Attach or @-mention the entrypoint if your host supports file context.

```text
Use skills/audit-orchestrator/SKILL.md in this workspace to audit TARGET_URL
for AI discoverability and on-site engagement. Apply its referenced sibling
skills and return the composed report, not just the Python static baseline.
Save report.json in OUTPUT_FOLDER.

Infer realistic visitor questions from the site. Use only permitted public,
read-only inspection. Do not log in, submit forms, buy anything, send messages,
change the site, or bypass controls. Do not edit the marketplace or read its
validation reports, evaluation answers, or previous audit outputs.

Follow the package's shared time budget. Record observed UTC start and report
completion times, actual tools used and untested checks. Deliver the report
promptly; do not write a separate narrative ledger. Never invent a timestamp
or claim a tool ran when it did not.
```

Append exactly one capability instruction from the next section. Start your own stopwatch when sending this audit prompt, not when Python starts. Stop it when the completed report is delivered. Record approval waits, tool errors and rate-limit interruptions separately, but retain the raw end-to-end time. The handout does not say approval waits can be excluded.

## 4. Compare the two main modes

Use the same URL, package, host/model and locale in two fresh conversations. Do not show one report to the other auditor.

**A — browser plus Python, when permitted:**

```text
You may use public browser automation, text web fetch/search, and the bundled
Python helpers. Verify actual browser availability and use it for the safe
journeys. If browser use fails, disclose the failure; do not label the run
browser-verified without actual rendered observations.
```

**B — no browser, Python permitted:**

```text
Do not use browser automation, screenshots, Playwright, Selenium, or other
rendered-browser tools. You may use the bundled Python collector and public
text web fetch/search. Mark interactive/rendered checks not_checked. Do not
use another tool or runtime to work around the browser restriction.
```

For a stronger restriction test, disable the relevant capability in the host where supported and record the configuration. A prompt restriction alone tests instruction following; it does not prove the tools were removed.

Optional additional runs: append `Do not execute Python or any other code; do not run bundled scripts or the validator` to A or B. The agent must then use permitted browser/text evidence and manual schema review. Permit ordinary file reading/writing if available. If there is neither network access nor supplied site evidence, the correct outcome is that a live audit cannot be performed, not a fabricated report.

## 5. Check the delivered report yourself

After preserving the original report, run the validator if you have Python:

```sh
python3 tests/validate_report.py /absolute/path/to/output/report.json
```

On Windows, substitute `py -3` and your Windows path. Validation performed by you after delivery is a separate evaluator check; do not claim the auditing agent performed it.

Then do the checks that a JSON validator cannot do:

- Is `assessment.mode` actually `agent_composed`? Are 3-5 question tests and two journey records present?
- Open each finding's cited page. Does the quote, element or link exist, and does it support the claimed problem and severity?
- For a missing-answer claim, inspect the obvious supporting route. A missing-in-sample answer is not proof the site lacks it.
- Repeat the safe journey yourself. Record starting context, clicked label, destination and observed result. Do not submit or authenticate.
- For every `answered` question, check every required element, not just the headline answer.
- Reject deductions based only on old styling, absent schema, a training opt-out, another subdomain or a failed tool call.
- Record any real problem the auditor missed. A few reviewer-discovered issues are not a complete recall denominator.
- Compare A and B: does A add real observed interaction evidence, while B honestly leaves it untested?
- Was the report delivered in under 300 seconds? Was it still useful and evidence-backed?

Keep a small record per run: revision/hash, URL, UTC date, host/model, permitted and actual tools, raw elapsed seconds, schema result, accepted/unsupported findings, missed observations and coverage limits. Preserve failed and interrupted runs. If you give corrective feedback, save the correction separately and label it guided rather than an independent pass.

Do not read the project's earlier site results into the auditing conversation. Use different business types, languages and architectures, including healthy controls and less-polished sites. Appearance alone must not predetermine the expected findings. This is a reproducible approximation of the handout's requirements, not a claim to replicate Adobe's undisclosed host configuration.
