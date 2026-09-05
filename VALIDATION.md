# Version 2.0.0 validation

Validated locally on 2026-09-05 with Python 3.12.6. Run `python tests/run_all.py` to reproduce deterministic checks.

## What is checked

- Four valid skill folders, resolved references, one marketplace entrypoint and a fixed JSON report schema.
- Healthy/problem HTTP fixtures, robots status behavior, deep-path preservation, sitemap discovery, tracking URL normalization, non-HTML handling and redirects blocked before reaching another authority.
- Material passages beyond the old 1,200-character preview, nested link labels, language, repeated metadata, hidden/navigation exclusion, JSON-LD values and parse errors.
- Robots rule specificity, combined named groups, wildcards, Allow ties and percent encoding.
- Training opt-out and absent schema produce no discovery finding on a healthy control. HTTP and meta indexing directives retain engine scope.
- Actual answer metrics separate mentions from own-domain citations, reject lookalike domains, exclude failures, preserve unknown values and separate provider surfaces/branded intent.
- Report validation rejects unsupported measurements and question/journey outcomes without evidence, as well as inconsistent counts and missing action fields.
- The actual submission ZIP is built, extracted into a temporary directory with spaces, and its fallback and report validator run from an unrelated working directory without installation or API keys.

## Public-site smoke checks

The portable fallback collected four HTML pages each from `https://plausible.io/` and `https://www.python.org/` on 2026-09-05. Each run took approximately eight seconds in this environment and produced a schema-valid report. The sample is deliberately small and proves only collection/report mechanics, not unseen-site detection accuracy or a five-minute bound for every website.

The pages exposed useful material text even with interactive features. This supports testing actual answers before treating JavaScript or short/static content as an issue. See `validation/FIELD-NOTES-v2.md` in the development repository for the limited research observations; full live crawl outputs are not bundled in the submission ZIP.

## Honest limits

No independent full agent benchmark was completed in Adobe's unpublished judging environment. No live ChatGPT/Claude/Gemini citation rates, causal visibility uplift, accessibility conformance, bounce or conversion results are claimed. The default report explicitly distinguishes static coverage from agent reasoning and actual answer measurement.

The maintained synthetic example now excludes the old GPTBot training finding and unverified image relevance finding. Its quality checks are regression checks for that controlled case, not evidence of performance on unseen websites. Historical v1 benchmark documents in the development repository describe prior code and are not current release validation.

The forward-evaluation protocol in `evals/README.md` covers full agent reasoning and capability degradation. Run those cases in fresh sessions on frozen unseen sites before reporting generalization precision/recall.
