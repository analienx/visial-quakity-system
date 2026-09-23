"""Read-only validator/reporter for roadmap/work_packages.json.

This checks *claims* in the planning ledger; it does NOT run Power BI, Word,
source-code tests, independent review, or release acceptance. No GitHub API is
required and it never changes a status or uploads evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "roadmap" / "work_packages.json"
VALID_STATES = {"planned", "ready", "active", "review", "blocked", "failed", "verified", "deferred"}
VALID_VERIFICATION = {"not_run", "partial", "failed", "blocked", "verified"}


def validate(data: dict) -> list[str]:
    """Validate IDs, graph, states and proof requirements; do not infer proof."""
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("schema_version") != "1.0.0":
        return ["unsupported or missing roadmap schema_version"]
    packages = data.get("packages")
    if not isinstance(packages, list) or not packages:
        return ["packages must be a non-empty list"]
    by_id: dict[str, dict] = {}
    issues: set[int] = set()
    for index, item in enumerate(packages):
        if not isinstance(item, dict):
            errors.append(f"package[{index}] is not an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"WP-\d{2,}", identifier):
            errors.append(f"package[{index}] has invalid id")
            continue
        if identifier in by_id:
            errors.append(f"duplicate work package {identifier}")
        by_id[identifier] = item
        issue = item.get("issue")
        if not isinstance(issue, int) or isinstance(issue, bool) or issue <= 0:
            errors.append(f"{identifier}: missing issue number")
        elif issue in issues:
            errors.append(f"{identifier}: duplicate issue number {issue}")
        issues.add(issue)
        state, verification = item.get("state"), item.get("verification")
        if state not in VALID_STATES:
            errors.append(f"{identifier}: invalid state {state!r}")
        if verification not in VALID_VERIFICATION:
            errors.append(f"{identifier}: invalid verification {verification!r}")
        if not isinstance(item.get("depends_on"), list) or any(
            not isinstance(dep, str) for dep in item.get("depends_on", [])
        ):
            errors.append(f"{identifier}: depends_on must be a list of IDs")
        if state == "verified" and (
            verification != "verified" or not item.get("verified_commit")
            or not item.get("evidence_uri") or not item.get("pull_request")
        ):
            errors.append(f"{identifier}: verified claim lacks independent evidence/merged commit/PR")
        if state == "deferred" and verification == "verified":
            errors.append(f"{identifier}: deferred cannot claim verified")
        if state == "blocked" and not item.get("blocker"):
            errors.append(f"{identifier}: blocked must include a blocker")
        if state in {"ready", "active", "review"} and verification == "verified":
            errors.append(f"{identifier}: workflow state contradicts verified evidence")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            errors.append(f"dependency cycle includes {identifier}")
            return
        if identifier in visited:
            return
        visiting.add(identifier)
        for dep in by_id[identifier].get("depends_on", []):
            if dep == identifier:
                errors.append(f"{identifier}: self dependency")
            elif dep not in by_id:
                errors.append(f"{identifier}: missing dependency {dep}")
            else:
                visit(dep)
                if by_id[identifier].get("state") in {"ready", "active", "review", "verified"} and (
                    by_id[dep].get("state") != "verified" or by_id[dep].get("verification") != "verified"
                ):
                    errors.append(f"{identifier}: prerequisite {dep} not independently verified")
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in by_id:
        visit(identifier)
    if data.get("first_ready_package") not in by_id:
        errors.append("first_ready_package does not exist")
    return sorted(set(errors))


def summarize(data: dict) -> dict:
    packages = data["packages"]
    initial = [item for item in packages if item["state"] != "deferred"]
    verified = [item for item in initial if item["state"] == "verified" and item["verification"] == "verified"]
    by_id = {item["id"]: item for item in packages}
    runnable = [item["id"] for item in initial if item["state"] in {"planned", "ready"} and all(
        by_id[dep]["state"] == "verified" and by_id[dep]["verification"] == "verified"
        for dep in item["depends_on"]
    )]
    return {"snapshot_utc": data.get("snapshot_utc"), "independently_verified": len(verified),
            "initial_release_packages": len(initial), "deferred": len(packages) - len(initial),
            "next_runnable": runnable, "packages": [
                {"id": item["id"], "issue": item["issue"], "stage": item["stage"],
                 "state": item["state"], "verification": item["verification"],
                 "depends_on": item["depends_on"], "evidence_uri": item.get("evidence_uri")}
                for item in packages]}


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
