# Inspect whether an answer travels with its qualifiers

Use this optional offline experiment when material facts are separated in captured source text, or when demonstrating a proposed answer-card rewrite. Select two or more exact phrases from one page: the answer and its decision-changing conditions (such as plan, billing period, eligibility, release or expiry). A reviewer must select the relevant elements and judge their meaning. Do not add this work to every timed audit.

The standard-library helper uses the existing `evidence.json`. No browser, network, API key or model call is involved. A cases file has this shape:

```json
{"cases":[{"id":"price-terms","ref":"page:0","elements":[
  {"label":"price","quote":"The plan costs $12 per user each month."},
  {"label":"condition","quote":"Annual billing is required; taxes are extra."}
]}]}
```

Copy quotes from `pages[N].main_text`; use the exact words and punctuation, not paraphrases or search excerpts. Include the entity/variant where necessary so unrelated repeated facts cannot appear to answer the question. Run from the marketplace root:

```text
python3 skills/audit-orchestrator/scripts/probe_answer_locality.py OUTPUT/evidence.json OUTPUT/cases.json --output OUTPUT/answer-locality.json
```

The output identifies the shortest word span containing all selected quotes, its source location and excerpt, and whether all quotes occur together in 80-, 160- and 300-word windows at two fixed alignments. `--words 100 200` changes those experimental budgets. Repeated mentions are handled; a later compact restatement can preserve the answer. Input hashes identify the exact files. Existing output files are not overwritten.

Interpret `quote_not_found` as a capture or quote mismatch, never proof the site lacks an answer. Positive matches in a truncated capture describe only the saved text. A split is a review candidate: inspect headings, variant associations, nearby equivalent prose and linked conditions before proposing a change. Words are not model tokens, these windows are not an actual search provider's chunker, and locality does not predict citations or establish semantic completeness.

For a reproducible synthetic before/proposed example:

```text
python3 skills/audit-orchestrator/scripts/probe_answer_locality.py examples/answer-locality-evidence.json examples/answer-locality-cases.json
```

The proposed text is clearly labeled hypothetical and preserves the same selected facts. It illustrates a measurable editing objective: make the answer and its conditions travel together. It is not a live website change, verified visibility uplift, or an automatically accepted report finding. Keep any resulting recommendation evidence-backed under the normal report verification gates; the public report schema stays 1.2.
