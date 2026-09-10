#!/usr/bin/env python3
"""Validate and publish an audit with an evidence receipt before 300 seconds.

The supplied start must be the observed host-task start, not collector startup.
This gate checks elapsed time at finalization; it cannot enforce host delivery.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
DEADLINE_SECONDS = 300


class FinalizationError(ValueError):
    """The inputs cannot be published as a successful finalization."""


def _utc(value, label):
    if not isinstance(value, datetime) or value.utcoffset() != timedelta(0):
        raise FinalizationError(f"{label} must be an aware UTC datetime")
    return value


def _start(value):
    if not isinstance(value, str) or "T" not in value:
        raise FinalizationError("started_at must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError as error:
        raise FinalizationError("started_at must be an ISO-8601 UTC timestamp") from error
    return _utc(parsed, "started_at")


def _elapsed(started, observed):
    elapsed = (_utc(observed, "clock") - started).total_seconds()
    if elapsed < 0:
        raise FinalizationError("started_at is in the future")
    if elapsed >= DEADLINE_SECONDS:
        raise FinalizationError(f"Finalization deadline exceeded: {elapsed:.6f}s; must be under 300s")
    return elapsed


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FinalizationError(f"Cannot load bundled validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate(report, evidence, review):
    schema = _module("_audit_finalizer_schema", ROOT / "tests/validate_report.py")
    errors = schema.validate(report)
    if errors:
        return ["report schema: " + error for error in errors]
    if report["assessment"]["mode"] != "agent_composed":
        return ["Finalization requires assessment.mode=agent_composed; a static baseline is not a completed audit"]
    gate = _module("_audit_finalizer_evidence", ROOT / "tests/report_evidence.py")
    return ["evidence review: " + error for error in gate.validate_evidence(report, evidence, review)]


def _read(path, label):
    raw = path.read_bytes()
    def reject_constant(value):
        raise ValueError(f"non-finite JSON value {value}")
    try:
        value = json.loads(raw, parse_constant=reject_constant)
    except (ValueError, UnicodeError) as error:
        raise FinalizationError(f"{label} is not valid JSON: {error}") from error
    if not isinstance(value, dict):
        raise FinalizationError(f"{label} must contain a JSON object")
    return raw, value


def _stage(destination, content):
    """Write fully before publishing; use the same filesystem as destination."""
    descriptor, name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _remove_owned(destination, temporary):
    # Do not remove a replacement another process created after publication.
    try:
        if destination.samefile(temporary):
            destination.unlink()
    except FileNotFoundError:
        pass


def finalize(report_path, evidence_path, review_path, output_path, started_at, *, clock=None):
    """Return the saved receipt; raise on failure, leaving draft inputs intact.

    ``clock`` is an injectable callable returning an aware UTC datetime. The
    receipt records the final observation after validation and report staging,
    immediately before publishing. It is not a whole-host timeout guarantee.
    """
    clock = clock or (lambda: datetime.now(timezone.utc))
    started = _start(started_at)
    _elapsed(started, clock())
    paths = {"report": Path(report_path), "evidence": Path(evidence_path), "review": Path(review_path)}
    output = Path(output_path)
    receipt_path = output.with_name(output.name + ".receipt.json")
    for destination in (output, receipt_path):
        if os.path.lexists(destination):
            raise FinalizationError(f"Refusing existing output or receipt: {destination}")
        if any(destination.resolve() == source.resolve() for source in paths.values()):
            raise FinalizationError(f"Output must differ from every input: {destination}")

    records = {name: _read(path, name) for name, path in paths.items()}
    errors = _validate(*(records[name][1] for name in ("report", "evidence", "review")))
    if errors:
        raise FinalizationError("Validation failed:\n" + "\n".join(errors))

    hashes = {name: hashlib.sha256(raw).hexdigest() for name, (raw, _) in records.items()}
    output.parent.mkdir(parents=True, exist_ok=True)
    staged = []
    published = []
    try:
        report_temp = _stage(output, records["report"][0])
        staged.append(report_temp)
        observed = _utc(clock(), "clock")
        elapsed = _elapsed(started, observed)
        receipt = {
            "receipt_version": "1",
            "status": "validated",
            "started_at": started.isoformat().replace("+00:00", "Z"),
            "finalized_at": observed.isoformat().replace("+00:00", "Z"),
            "elapsed_seconds": elapsed,
            "deadline_seconds": DEADLINE_SECONDS,
            "sha256": hashes,
            "validator_sha256": {
                name: hashlib.sha256((ROOT / "tests" / name).read_bytes()).hexdigest()
                for name in ("validate_report.py", "report_evidence.py")
            },
            "limits": [
                "Validation checks structural and evidence consistency, not semantic truth.",
                "Elapsed time ends at the observed finalization gate before publication; it excludes final receipt writing and host delivery.",
                "The deadline is checked again during and immediately after publication; a failed check removes this invocation's output and receipt.",
                "This command does not enforce or prove an end-to-end host delivery deadline, and cannot verify the supplied host-task start.",
                "Report and receipt are individually atomic; consumers must require both files with matching report hashes.",
            ],
        }
        receipt_temp = _stage(receipt_path, (json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
        staged.append(receipt_temp)
        # A hard link publishes a complete same-filesystem file and fails if a
        # destination appeared concurrently. os.replace would silently clobber it.
        for temporary, destination in ((report_temp, output), (receipt_temp, receipt_path)):
            _elapsed(started, clock())
            os.link(temporary, destination)
            published.append((destination, temporary))
        _elapsed(started, clock())
        return receipt
    except BaseException:
        for destination, temporary in reversed(published):
            _remove_owned(destination, temporary)
        raise
    finally:
        for temporary in staged:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("report", "evidence", "review", "output", "started-at"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        receipt = finalize(args.report, args.evidence, args.review, args.output, args.started_at)
    except (FinalizationError, OSError, ImportError) as error:
        print(json.dumps({"finalized": False, "errors": [str(error)]}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps({"finalized": True, "output": str(Path(args.output)),
                      "receipt": str(Path(args.output).with_name(Path(args.output).name + ".receipt.json")),
                      "elapsed_seconds": receipt["elapsed_seconds"], "limits": receipt["limits"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
