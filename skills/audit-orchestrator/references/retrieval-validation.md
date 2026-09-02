# Differentiating retrieval validation

Use the baseline whenever web search is available. It tests off-site discoverability without confusing variable search outcomes with causes.

## Baseline

Run three to five dated queries: exact entity name; one neutral category/discovery query that omits the brand; and up to three material factual lookups derived from the site. Record locale, returned source URLs, and whether an independent source resolves identity or supports the claim. Search absence alone is not a defect and never proves that an assistant will not cite the brand.

## Expanded competitive or citation validation

1. Derive 6-10 neutral queries from the site's own material claims: exact entity, category discovery, comparison, factual lookup, location/audience, and recent-status query. Do not put the desired brand into category-discovery queries.
2. Run each query once in a documented locale/date and record returned sources. Do not infer universal ranking from a small query set.
3. For each cited/competing page, compare answer-bearing passage quality: directness, freshness, entity disambiguation, structured facts, and independent corroboration.
4. Link every observed retrieval miss to a mechanism already evidenced by the audit. If no mechanism is supported, report it as an experiment result, not a defect.
5. Preserve the query set as a regression suite so later site changes can be compared under the same tool, locale, and date window.

Run the expanded layer only when the user requests competitive or citation validation. This is an experiment, not a promise: search and assistant outputs vary with provider, index, personalization, and time.
