"""Narrow, dependency-free consistency checks for an audit's evidence review.

Public reports remain schema 1.2. The review sidecar has review_version "1",
observations [], claims {finding/opportunity ID: {assertions: [...]}}, answers [],
journeys [], and corroboration []. Findings also declare checked_refs and
affected_refs. Collector references are page:N, robots, sitemap:N, error:N;
host observations have explicit host:* IDs and provenance.

Assertions: quote(ref, field, quote), field_equals(ref, field, value),
field_absent(ref, field), broken_link(ref, href, destination_ref). Fields are
dot-separated paths into saved fields, e.g. links.0.text. A missing key means
unknown, never absent. Quotes are short exact excerpts, allowing only whitespace
normalization. Host fields supplement text/status and cannot override them.

This checks recorded facts, scope, and provenance, not natural-language
entailment, external-source independence, or authenticity of host observations.
A reviewer must still check that each material claim uses the appropriate typed
assertion and that the conclusion follows from it. A quote about generic copy
does not mechanically prove an unrelated missing metadata claim.
"""
from datetime import datetime
from urllib.parse import urldefrag, urljoin, urlparse


MISSING = object()
MODES = {"static", "rendered", "off_site", "retrieval"}


def _url(value):
    if not isinstance(value, str):
        return ""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
        return ""
    return urldefrag(value)[0]


def _field(data, path):
    if not isinstance(path, str) or not path:
        return MISSING
    value = data
    for part in path.split("."):
        if isinstance(value, dict):
            value = value.get(part, MISSING)
        elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        else:
            return MISSING
    return value


def _empty(value):
    return value is None or value == [] or value == {} or isinstance(value, str) and not value.strip()


def _quote(quote, value):
    return (isinstance(quote, str) and 0 < len(quote.strip()) <= 500
            and isinstance(value, str) and " ".join(quote.split()) in " ".join(value.split()))


def _record(data, mode="static", kind="resource", complete=False):
    aliases = {_url(data.get("url")), _url(data.get("final_url"))} - {""}
    for redirect in data.get("redirects", []):
        aliases.update({_url(redirect.get("from")), _url(redirect.get("to"))} - {""})
    status = data.get("status")
    success = type(status) is int and 200 <= status < 300
    return {"data": data, "aliases": aliases, "mode": mode, "kind": kind,
            "complete": complete, "success": success, "readable": success,
            "identity": _url(data.get("final_url")) or _url(data.get("url"))}


def validate_evidence(doc, evidence, review):
    """Return consistency error strings; call validate_report.validate separately.

    Malformed input fails closed rather than crashing a finalization command.
    """
    try:
        return _validate(doc, evidence, review)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError) as error:
        return [f"evidence review: malformed input ({error})"]


def _validate(doc, evidence, review):
    errors, records = [], {}
    if not all(isinstance(x, dict) for x in (doc, evidence, review)):
        return ["report, evidence, and review must be JSON objects"]
    if review.get("review_version") != "1":
        errors.append("review_version must be '1'")
    for key, kind in (("observations", list), ("claims", dict), ("answers", list),
                      ("journeys", list), ("corroboration", list)):
        if not isinstance(review.get(key), kind):
            errors.append(f"review.{key} must be a {kind.__name__}")
    if errors:
        return errors
    if not _url(evidence.get("site")) or _url(doc.get("site")) != _url(evidence.get("site")):
        errors.append("collector site does not match report site")
    if not isinstance(evidence.get("pages"), list):
        return errors + ["collector pages must be an array"]
    for key, prefix in (("pages", "page"), ("sitemaps", "sitemap"), ("errors", "error")):
        for index, data in enumerate(evidence.get(key, [])):
            is_page = key == "pages" and data.get("parse_status") == "parsed_html"
            complete = (data.get("response_truncated") is False
                        and not data.get("read_error") and not data.get("error")
                        and (not is_page or data.get("evidence_truncated") is False))
            records[f"{prefix}:{index}"] = _record(data, kind="page" if is_page else "resource", complete=complete)
    if evidence.get("robots"):
        data = evidence["robots"]
        records["robots"] = _record(data, complete=data.get("response_truncated") is False and not data.get("read_error"))

    for index, observation in enumerate(review["observations"]):
        where = f"observations[{index}]"
        ref = observation.get("id")
        required = {"id", "url", "final_url", "mode", "kind", "status", "complete", "text", "provenance"}
        if not required <= observation.keys():
            errors.append(f"{where}: missing required observation fields")
            continue
        if not isinstance(ref, str) or not ref.startswith("host:") or ref in records:
            errors.append(f"{where}: unique host:* id required")
            continue
        if not _url(observation["url"]) or not _url(observation["final_url"]):
            errors.append(f"{where}: exact HTTP(S) request and final URLs required")
        if observation["mode"] not in MODES or observation["kind"] not in {"page", "resource", "external", "interaction"}:
            errors.append(f"{where}: invalid observation mode or kind")
        if not (observation["status"] is None or type(observation["status"]) is int and 100 <= observation["status"] <= 599):
            errors.append(f"{where}: HTTP status must be an integer or null when unavailable")
        if type(observation["complete"]) is not bool or not isinstance(observation["text"], str):
            errors.append(f"{where}: explicit completeness and captured text required")
        provenance = observation["provenance"]
        if not isinstance(provenance, dict) or not all(isinstance(provenance.get(k), str) and provenance[k].strip() for k in ("tool", "reference", "observed_at")):
            errors.append(f"{where}: tool, tool-output reference, and observed_at provenance required")
        else:
            try:
                if datetime.fromisoformat(provenance["observed_at"].replace("Z", "+00:00")).utcoffset() is None:
                    raise ValueError("timezone missing")
            except ValueError:
                errors.append(f"{where}: observed_at must include a timezone")
        fields = observation.get("fields", {})
        if not isinstance(fields, dict):
            errors.append(f"{where}: fields must be an object")
            continue
        data = {**fields, **{k: observation[k] for k in ("url", "final_url", "status", "text")}}
        records[ref] = _record(data, observation["mode"], observation["kind"], observation["complete"] is True)
        # Browser DOM and opened web-text tools may expose content without an
        # HTTP status. This supports positive text observations, not HTTP or
        # absence claims. Collector errors never receive this allowance.
        if observation["status"] is None and observation["text"].strip():
            records[ref]["readable"] = True

    def get(ref, where):
        if not isinstance(ref, str) or ref not in records:
            errors.append(f"{where}: unknown evidence ref {ref!r}")
            return None
        return records[ref]

    def assertions(items, where):
        if not isinstance(items, list) or not items:
            errors.append(f"{where}: nonempty typed assertions required")
            return
        for index, assertion in enumerate(items):
            label = f"{where}.assertions[{index}]"
            record = get(assertion.get("ref"), label)
            if record is None:
                continue
            data, kind = record["data"], assertion.get("type")
            value = _field(data, assertion.get("field"))
            if kind == "quote":
                if not record["readable"] or not _quote(assertion.get("quote"), value):
                    errors.append(f"{label}: quote is not a short verbatim excerpt from readable captured evidence")
            elif kind == "field_equals":
                expected = assertion.get("value", MISSING)
                if value is MISSING or type(value) is not type(expected) or value != expected:
                    errors.append(f"{label}: field value contradicts captured evidence or was not captured")
            elif kind == "field_absent":
                if value is MISSING:
                    errors.append(f"{label}: field was not captured; unknown is not absence")
                elif not _empty(value):
                    errors.append(f"{label}: missing-field claim contradicts a present field")
                if not record["success"] or not record["complete"] or record["mode"] == "retrieval":
                    errors.append(f"{label}: absence requires complete successful evidence in the stated reading mode")
                for other in records.values():
                    captured = _field(other["data"], assertion.get("field"))
                    if (other["success"] and other["mode"] == record["mode"] and other["aliases"] & record["aliases"]
                            and captured is not MISSING and not _empty(captured)):
                        errors.append(f"{label}: another observation of this URL contains the supposedly absent field")
                        break
            elif kind == "broken_link":
                destination = get(assertion.get("destination_ref"), label)
                href, final = assertion.get("href"), _url(data.get("final_url"))
                if not record["success"] or not final or "base_href" not in data:
                    errors.append(f"{label}: broken link requires successful source, observed final URL, and captured base_href")
                    continue
                if not isinstance(href, str) or not any(link.get("href") == href for link in data.get("links", [])):
                    errors.append(f"{label}: literal href was not captured in source links")
                    continue
                base = urljoin(final, data["base_href"] or "")
                resolved = _url(urljoin(base, href))
                if data.get("link_base_url", base) != base:
                    errors.append(f"{label}: saved link base contradicts final URL/base_href resolution")
                if not destination or resolved not in destination["aliases"] or destination["data"].get("status") not in {404, 410}:
                    errors.append(f"{label}: resolved destination needs an observed HTTP 404 or 410; tool errors and access restrictions are not broken links")
            else:
                errors.append(f"{label}: unsupported assertion type {kind!r}")

    aliases = set().union(*(r["aliases"] for r in records.values())) if records else set()
    site_hosts = {urlparse(doc["site"]).netloc.lower()}
    # Honor an actually observed landing redirect (e.g. apex -> www), without
    # treating arbitrary sibling hosts or merely discovered links as first party.
    for record in records.values():
        if record["readable"] and _url(record["data"].get("url")) == _url(doc["site"]):
            site_hosts.add(urlparse(record["identity"]).netloc.lower())
    checked_pages = {r["identity"] for r in records.values() if r["kind"] == "page" and r["readable"]
                     and urlparse(r["identity"]).netloc.lower() in site_hosts}
    if doc["coverage"]["pages_checked"] != len(checked_pages):
        errors.append(f"pages_checked disagrees with {len(checked_pages)} unique inspected first-party pages")
    supported_modes = {r["mode"] for r in records.values()}
    if set(doc["coverage"]["modes"]) - supported_modes:
        errors.append("coverage modes include an unobserved reading mode")

    def check_urls(value, path="report"):
        if isinstance(value, dict):
            for key, child in value.items():
                urls = [child] if key == "url" else child if key == "urls" else []
                for url in urls:
                    if _url(url) not in aliases:
                        errors.append(f"{path}.{key}: unobserved report URL {url}")
                check_urls(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                check_urls(child, f"{path}[{index}]")
    check_urls(doc)

    all_claims = doc["findings"] + doc["proactive_opportunities"]
    if set(review["claims"]) != {claim["id"] for claim in all_claims}:
        errors.append("claims must map every finding and opportunity ID exactly once")
    for claim in all_claims:
        ident = claim["id"]
        entry = review["claims"].get(ident, {})
        assertions(entry.get("assertions"), ident)
        if "evidence" not in claim:
            continue
        scopes = {}
        for key, count in (("checked_refs", "checked"), ("affected_refs", "affected")):
            refs = entry.get(key)
            if not isinstance(refs, list) or not refs:
                errors.append(f"{ident}: {key} requires the inspected scope")
                refs = []
            scope_records = [get(ref, f"{ident}.{key}") for ref in refs]
            scopes[key] = {r["identity"] for r in scope_records if r}
            if len(scopes[key]) != len(refs) or len(scopes[key]) != claim["evidence"][count]:
                errors.append(f"{ident}: {count} count disagrees with unique {key}")
        if not scopes["affected_refs"] <= scopes["checked_refs"]:
            errors.append(f"{ident}: affected scope exceeds checked scope")
        cited = {_url(url) for url in claim["evidence"]["urls"]}
        affected_records = [records[ref] for ref in entry.get("affected_refs", []) if ref in records]
        if any(not (r["aliases"] & cited) for r in affected_records) or cited - set().union(set(), *(r["aliases"] for r in affected_records)):
            errors.append(f"{ident}: evidence URLs disagree with affected scope")
        support_records = [records[a["ref"]] for a in entry.get("assertions", []) if a.get("ref") in records]
        if any(not any(r["aliases"] & support["aliases"] for support in support_records) for r in affected_records):
            errors.append(f"{ident}: every affected page needs its own supporting assertion")

    answer_map = {}
    for answer in review["answers"]:
        key = (answer["test_index"], answer["evidence_index"])
        if key in answer_map:
            errors.append("answers: duplicate evidence mapping")
        answer_map[key] = answer
    expected_answers = set()
    for index, test in enumerate(doc["assessment"]["intent_tests"]):
        for evidence_index, item in enumerate(test["evidence"]):
            key = (index, evidence_index)
            expected_answers.add(key)
            mapping = answer_map.get(key, {})
            record = get(mapping.get("ref"), f"answer {key}")
            if record:
                assertions([{"type": "quote", "ref": mapping["ref"], "field": mapping.get("field"), "quote": item["quote"]}], f"answer {key}")
                if _url(item["url"]) not in record["aliases"]:
                    errors.append(f"answer {key}: quote provenance URL mismatch")
                if test["status"] == "missing_in_sample" and (not record["complete"] or record["mode"] == "retrieval"):
                    errors.append(f"answer {key}: missing_in_sample cannot follow from incomplete evidence")
    if set(answer_map) != expected_answers:
        errors.append("answers must map every report answer excerpt exactly once")

    journey_map = {}
    for journey in review["journeys"]:
        index = journey["journey_index"]
        if index in journey_map:
            errors.append("journeys: duplicate journey mapping")
        journey_map[index] = journey
    expected_journeys = {index for index, journey in enumerate(doc["assessment"]["journeys"]) if journey["steps"]}
    if set(journey_map) != expected_journeys:
        errors.append("journeys must map every journey with observed steps exactly once")
    for index in expected_journeys:
        journey = doc["assessment"]["journeys"][index]
        entry = journey_map.get(index, {})
        mode = entry.get("mode")
        if mode not in {"source", "rendered"}:
            errors.append(f"journey {index}: explicit source or rendered mode required")
        steps = {step["step_index"]: step for step in entry.get("steps", [])}
        if set(steps) != set(range(len(journey["steps"]))) or len(steps) != len(entry.get("steps", [])):
            errors.append(f"journey {index}: every observed step needs one evidence mapping")
        for step_index, step in enumerate(journey["steps"]):
            label = f"journey {index} step {step_index}"
            mapping = steps.get(step_index, {})
            record = get(mapping.get("ref"), label)
            if f"[{mode}]" not in step["action"].lower():
                errors.append(f"{label}: report action must label its [{mode}] reading mode")
            if record:
                if _url(step["url"]) not in record["aliases"]:
                    errors.append(f"{label}: observation URL mismatch")
                if mode == "rendered" and record["mode"] != "rendered" or mode == "source" and record["mode"] == "rendered":
                    errors.append(f"{label}: interaction mode contradicts observed evidence")
                refs = {a.get("ref") for a in mapping.get("assertions", [])} | {a.get("destination_ref") for a in mapping.get("assertions", [])}
                if mapping.get("ref") not in refs:
                    errors.append(f"{label}: step assertions must support its mapped observation")
            assertions(mapping.get("assertions"), label)

    corroboration = next(r for r in doc["assessment"]["readiness"] if r["stage"] == "corroboration")
    if corroboration["status"] == "observed" and not review["corroboration"]:
        errors.append("observed corroboration needs captured external source support")
    external_aliases = set()
    for support in review["corroboration"]:
        record = get(support.get("ref"), "corroboration")
        if record:
            if (record["kind"] != "external" or record["mode"] not in {"off_site", "retrieval"}
                    or urlparse(record["identity"]).hostname == urlparse(doc["site"]).hostname):
                errors.append("corroboration requires an external source observation with off_site/retrieval mode")
            external_aliases.update(record["aliases"])
        assertions([{**support, "type": "quote"}], "corroboration")
    if corroboration["status"] == "observed" and not external_aliases & {_url(url) for url in corroboration["urls"]}:
        errors.append("observed corroboration must cite its actual external source URL")
    return errors
