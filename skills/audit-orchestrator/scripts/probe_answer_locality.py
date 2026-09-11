#!/usr/bin/env python3
"""Offline experiment: do selected answer quotes fit together in a word window?

This measures the locality of exact, reviewer-selected evidence, not semantic
answer quality, actual search chunks, model tokens, or citation probability.
"""
import argparse
from bisect import bisect_left, bisect_right
import hashlib
import json
from pathlib import Path
import re


def _occurrences(text, quote, starts):
    spans, offset = [], 0
    while True:
        index = text.find(quote, offset)
        if index < 0:
            return spans
        end = index + len(quote)
        # Do not accept an accidental substring of another word.
        if (index == 0 or text[index - 1].isspace()) and (end == len(text) or text[end].isspace()):
            spans.append((bisect_right(starts, index) - 1, bisect_right(starts, end - 1)))
        offset = index + 1


def probe(evidence, cases, budgets=(80, 160, 300)):
    if not isinstance(evidence, dict) or not isinstance(evidence.get("pages"), list):
        raise ValueError("evidence must contain a pages array")
    if not isinstance(cases, dict) or not isinstance(cases.get("cases"), list) or not 1 <= len(cases["cases"]) <= 20:
        raise ValueError("provide 1-20 cases")
    if not budgets or any(type(n) is not int or not 2 <= n <= 2000 for n in budgets) or len(set(budgets)) != len(budgets):
        raise ValueError("word budgets must be distinct integers between 2 and 2000")
    results, ids = [], set()
    for case in cases["cases"]:
        if not isinstance(case, dict):
            raise ValueError("each case must be an object")
        ident, ref, elements = case.get("id"), case.get("ref"), case.get("elements")
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            raise ValueError("each case needs a unique nonempty id")
        ids.add(ident)
        if not isinstance(ref, str) or not re.fullmatch(r"page:[0-9]+", ref):
            raise ValueError(f"{ident}: ref must be page:N")
        if not isinstance(elements, list) or not 2 <= len(elements) <= 12:
            raise ValueError(f"{ident}: provide 2-12 answer/qualifier elements")
        labels, quotes = [], []
        for element in elements:
            if not isinstance(element, dict) or any(not isinstance(element.get(k), str) or not element[k].strip() for k in ("label", "quote")):
                raise ValueError(f"{ident}: elements need nonempty label and exact quote")
            labels.append(element["label"])
            quotes.append(" ".join(element["quote"].split()))
        if len(set(labels)) != len(labels) or len(set(quotes)) != len(quotes) or any(len(q) > 500 for q in quotes):
            raise ValueError(f"{ident}: labels/quotes must be distinct; quotes at most 500 characters")
        index = int(ref.split(":")[1])
        result = {"id": ident, "ref": ref, "elements": elements, "status": "not_checked"}
        results.append(result)
        if index >= len(evidence["pages"]):
            result["reason"] = "Page reference was not captured."
            continue
        page = evidence["pages"][index]
        result["url"] = page.get("final_url") or page.get("url")
        if (type(page.get("status")) is not int or not 200 <= page["status"] < 300
                or page.get("parse_status") != "parsed_html" or not isinstance(page.get("main_text"), str)
                or not page["main_text"].strip() or page.get("error") or page.get("read_error")):
            result["reason"] = "Successful readable source HTML is unavailable."
            continue
        text = " ".join(page["main_text"].split())
        words = text.split()
        starts = [match.start() for match in re.finditer(r"\S+", text)]
        groups = [_occurrences(text, quote, starts) for quote in quotes]
        result["capture_complete"] = page.get("response_truncated") is False and page.get("evidence_truncated") is False
        result["source_text_sha256"] = hashlib.sha256(page["main_text"].encode()).hexdigest()
        missing = [label for label, spans in zip(labels, groups) if not spans]
        if missing:
            result.update(status="quote_not_found", unmatched_elements=missing,
                          reason="Selected quotes were not found exactly in this capture; this is not proof the website lacks the answer.")
            continue
        # Try every possible leftmost occurrence; use the first occurrence of
        # each other element at/after it. Duplicate mentions can shorten the span.
        best = None
        group_starts = [[span[0] for span in group] for group in groups]
        for left in sorted({span[0] for group in groups for span in group}):
            indices = [bisect_left(positions, left) for positions in group_starts]
            choices = [group[index] if index < len(group) else None for group, index in zip(groups, indices)]
            if any(span is None for span in choices):
                continue
            right = max(span[1] for span in choices)
            if best is None or right - left < best[1] - best[0]:
                best = (left, right)
        left, right = best
        excerpt = " ".join(words[left:right])
        result.update(status="measured", minimum_span_words=right-left,
                      span={"start_word": left, "end_word_exclusive": right},
                      excerpt=excerpt[:800], excerpt_truncated=len(excerpt) > 800, windows=[])
        for budget in budgets:
            phases = []
            for offset in (0, budget // 2):
                windows = [(start, min(start + budget, len(words))) for start in range(offset, len(words), budget)]
                if offset:
                    windows.insert(0, (0, min(offset, len(words))))
                containing = next(((a, b) for a, b in windows if all(any(a <= x and y <= b for x, y in group) for group in groups)), None)
                phases.append({"offset_words": offset, "all_elements_together": containing is not None,
                               "window": list(containing) if containing else None})
            result["windows"].append({"budget_words": budget, "fits_contiguous_window": right-left <= budget, "phases": phases})
    return {"probe_version": "1", "site": evidence.get("site"), "cases": results,
            "limits": ["Exact-quote locality only; a reviewer must select every material answer element and qualifier and check meaning.",
                       "Whitespace-delimited words are not model tokens. Two fixed non-overlapping chunk alignments are an experiment, not a search-engine simulation.",
                       "A split is a review candidate, not an automatic website defect. Missing, failed or truncated captures cannot establish absence.",
                       "No browser, network, live assistant answers, citation probability or visibility uplift is measured."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence")
    parser.add_argument("cases")
    parser.add_argument("--words", nargs="+", type=int, default=[80, 160, 300])
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try:
        inputs = [Path(path) for path in (args.evidence, args.cases)]
        if args.output != "-" and Path(args.output).resolve() in [p.resolve() for p in inputs]:
            raise ValueError("output must differ from the evidence and cases inputs")
        raw = [p.read_bytes() for p in inputs]
        result = probe(*(json.loads(value) for value in raw), budgets=args.words)
        result["input_sha256"] = dict(zip(("evidence", "cases"), (hashlib.sha256(value).hexdigest() for value in raw)))
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output == "-":
            print(payload, end="")
        else:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(payload)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.exit(1, f"Answer-locality probe failed: {error}\n")


if __name__ == "__main__":
    main()
