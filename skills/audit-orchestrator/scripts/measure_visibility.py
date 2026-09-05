#!/usr/bin/env python3
"""Summarize actual recorded assistant runs. Makes no API calls or ranking claims."""
import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def http_url(value):
    if not isinstance(value, str): return False
    p = urlparse(value)
    return p.scheme in {"http", "https"} and bool(p.hostname) and not p.username


def summarize(document):
    target = document.get("site", "")
    if not http_url(target): raise ValueError("site must be an HTTP(S) URL")
    host = urlparse(target).hostname.lower().rstrip(".")
    if host.startswith("www."): host = host[4:]
    runs = document.get("runs")
    if not isinstance(runs, list): raise ValueError("runs must be a list")
    grouped, ids = defaultdict(list), set()
    for run in runs:
        if not isinstance(run, dict): raise ValueError("each run must be an object")
        for field in ("id", "provider", "surface", "model", "locale", "prompt", "prompt_kind", "observed_at", "status"):
            if not isinstance(run.get(field), str) or not run[field].strip(): raise ValueError(f"run needs {field}")
        if run["id"] in ids: raise ValueError("duplicate run id")
        ids.add(run["id"])
        timestamp = datetime.fromisoformat(run["observed_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None: raise ValueError("observed_at needs a timezone")
        if run["prompt_kind"] not in {"branded", "unbranded"}: raise ValueError("prompt_kind must be branded or unbranded")
        if run["status"] not in {"ok", "error", "not_run"}: raise ValueError("invalid run status")
        if run["status"] == "ok":
            if not isinstance(run.get("response_text"), str) or not run["response_text"].strip(): raise ValueError("successful runs need raw response_text")
            if type(run.get("brand_mentioned")) is not bool: raise ValueError("brand_mentioned must be manually verified boolean")
            if not isinstance(run.get("citation_urls"), list) or any(not http_url(u) for u in run["citation_urls"]): raise ValueError("citation_urls must be HTTP(S) URLs from the answer")
            cited = False
            for url in run["citation_urls"]:
                cited_host = urlparse(url).hostname.lower().rstrip(".")
                cited |= cited_host == host or cited_host.endswith("." + host)
            run = {**run, "target_cited": cited}
        elif not run.get("reason"): raise ValueError("unsuccessful runs need a reason")
        key = tuple(run[k] for k in ("provider", "surface", "model", "locale", "prompt_kind"))
        grouped[key].append(run)
    cohorts = []
    for key, group in sorted(grouped.items()):
        valid = [r for r in group if r["status"] == "ok"]
        cohort = dict(zip(("provider", "surface", "model", "locale", "prompt_kind"), key))
        cohort.update({"valid_runs": len(valid), "failed_runs": sum(r["status"] == "error" for r in group),
                       "not_run": sum(r["status"] == "not_run" for r in group),
                       "distinct_prompts": len({r["prompt"] for r in valid}),
                       "mentioned_runs": sum(r["brand_mentioned"] for r in valid),
                       "cited_runs": sum(r["target_cited"] for r in valid),
                       "mention_rate": sum(r["brand_mentioned"] for r in valid) / len(valid) if valid else None,
                       "citation_rate": sum(r["target_cited"] for r in valid) / len(valid) if valid else None,
                       "run_ids": [r["id"] for r in group]})
        cohorts.append(cohort)
    return {"status": "measured_sample" if any(c["valid_runs"] for c in cohorts) else "not_measured",
            "detail": "Observed answer samples only. Rates are per successful run, separately by provider/surface/model/locale and branded intent. Errors are excluded. No causal or population inference; preserve the raw run file and prompt set.",
            "cohorts": cohorts}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("observations"); parser.add_argument("--output", default="-")
    args = parser.parse_args()
    try: result = summarize(json.loads(Path(args.observations).read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError) as error: parser.error(str(error))
    payload = json.dumps(result, indent=2)
    if args.output == "-": print(payload)
    else: Path(args.output).write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__": main()
