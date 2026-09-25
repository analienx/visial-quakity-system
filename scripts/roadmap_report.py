"""Read-only validator/reporter for roadmap/work_packages.json.

This checks *claims* in the planning ledger; it does NOT run Power BI, Word,
source-code tests, independent review, or release acceptance. No GitHub API is
required and it never changes a status or uploads evidence.

Validation logic lives in :mod:`vqs.ledger` (shared with the installed
``vqs status`` command); this module keeps the file-based CLI and the
historical import surface.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vqs.ledger import (
    SCHEMA_VERSION,
    VALID_STATES,
    VALID_VERIFICATION,
    summarize,
    validate,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "roadmap" / "work_packages.json"

__all__ = ["DEFAULT_LEDGER", "ROOT", "SCHEMA_VERSION", "VALID_STATES",
           "VALID_VERIFICATION", "summarize", "validate"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and report planned VQS work; never modifies ledger")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--check", action="store_true", help="Only validate the claims and graph")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8-sig"))
        errors = validate(data)
        if errors:
            print("INVALID ROADMAP:\n" + "\n".join(f"- {err}" for err in errors), file=sys.stderr)
            return 2
        summary = summarize(data)
    except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
        print(f"INVALID ROADMAP: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    if args.check:
        print(f"VALID ROADMAP: {len(data['packages'])} packages; validation does not prove tests passed")
        return 0
    if args.format == "json":
        print(json.dumps(summary, indent=2))
        return 0
    print(f"# VQS work-package status (snapshot {summary['snapshot_utc']})\n")
    print(f"Independently verified: {summary['independently_verified']}/{summary['initial_release_packages']}"
          f" initial-release packages; deferred: {summary['deferred']}.")
    print("This view does not inspect code, GitHub issue closure, tests, Desktop, or Word evidence.\n")
    print("| Package | Issue | Phase | Workflow | Verification | Prerequisites | Evidence |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for item in summary["packages"]:
        print(f"| {item['id']} | #{item['issue']} | {item['stage']} | {item['state']} | "
              f"{item['verification']} | {', '.join(item['depends_on']) or '—'} | "
              f"{item['evidence_uri'] or 'none'} |")
    print(f"\nRunnable by dependency only: {', '.join(summary['next_runnable']) or 'none'}."
          " Capability, privacy, resource lease and owner approval must also be checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
