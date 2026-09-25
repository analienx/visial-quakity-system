"""Static semantic-model facts from TMDL declarations (WP-05 subset, issue #10).

Parses `table` / `column` / `measure` declarations from `*.tmdl` text and
cross-checks PBIR field bindings (`queryRef`) against the declared model:
unknown tables or fields become fail findings, measures without a recorded
expression become ``unknown``. Live values, refresh identity, RLS scoping,
and DAX execution are NOT performed here — absent data facts are reported
``blocked`` via :func:`blocked_snapshot`, never fabricated.
"""
from __future__ import annotations

from pathlib import Path


def parse_tmdl(text: str) -> dict:
    """Parse TMDL declarations; malformed lines become issues, never raises."""
    tables: dict[str, dict[str, dict]] = {}
    issues: list[dict] = []
    current: str | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if not raw.startswith((" ", "\t")):
            if line.startswith("table "):
                current = line[len("table "):].strip()
                tables.setdefault(current, {"measures": {}, "columns": {}})
            else:
                current = None
            continue
        if current is None:
            issues.append({"rule": "orphan_declaration", "line": lineno})
            continue
        if line.startswith("measure "):
            name, _, expression = line[len("measure "):].partition("=")
            tables[current]["measures"][name.strip()] = expression.strip()
        elif line.startswith("column "):
            tables[current]["columns"][line[len("column "):].strip()] = ""
    return {"tables": tables, "issues": issues}


def inventory_model(model_dir: Path) -> dict:
    """Inventory every `*.tmdl` file under a model directory."""
    model_dir = Path(model_dir)
    if not model_dir.is_dir():
        return {"tables": {}, "issues": [{"rule": "no_model", "path": str(model_dir)}]}
    try:
        files = sorted(model_dir.rglob("*.tmdl"))
    except OSError as exc:
        return {"tables": {}, "issues": [{"rule": "no_model", "detail": str(exc)}]}
    if not files:
        return {"tables": {}, "issues": [{"rule": "no_model", "path": str(model_dir)}]}
    merged: dict[str, dict[str, dict]] = {}
    issues: list[dict] = []
    for file in files:
        try:
            parsed = parse_tmdl(file.read_text(encoding="utf-8-sig"))
        except OSError as exc:
            issues.append({"rule": "unreadable_model_file", "part": file.name,
                           "detail": str(exc)})
            continue
        issues.extend({**row, "part": file.name} for row in parsed["issues"])
        for table, content in parsed["tables"].items():
            target = merged.setdefault(table, {"measures": {}, "columns": {}})
            target["measures"].update(content["measures"])
            target["columns"].update(content["columns"])
    return {"tables": merged, "issues": issues}


def check_bindings(bindings: list[dict], inventory: dict) -> list[dict]:
    """Resolve PBIR `queryRef` bindings against the declared model.

    Each binding needs ``query_ref`` like ``"Dim Product.Brand"``. Unknown
    tables/fields fail; measures without a recorded expression are
    ``unknown`` — their values require a live authorized query (blocked).
    """
    tables = inventory.get("tables", {})
    findings = []
    for binding in bindings:
        ref = binding.get("query_ref", "") if isinstance(binding, dict) else ""
        table, _, field = ref.rpartition(".") if isinstance(ref, str) else ("", "", "")
        if not table or not field or table not in tables:
            findings.append({"rule": "missing_dimension_or_measure", "status": "fail",
                             "query_ref": ref})
            continue
        content = tables[table]
        if field in content["columns"]:
            findings.append({"rule": "binding_resolved", "status": "pass", "query_ref": ref})
        elif field in content["measures"]:
            if content["measures"][field]:
                findings.append({"rule": "binding_resolved", "status": "pass",
                                 "query_ref": ref})
            else:
                findings.append({"rule": "measure_without_expression", "status": "unknown",
                                 "query_ref": ref,
                                 "reason": "Values require a live authorized query"})
        else:
            findings.append({"rule": "missing_dimension_or_measure", "status": "fail",
                             "query_ref": ref})
    return findings


def blocked_snapshot(reason: str) -> dict:
    """Explicit blocked data snapshot: no live query, no fabricated values."""
    return {"status": "blocked", "reason": reason, "values": None}


def check_freshness(bound_sha256: str, current_sha256: str, label: str) -> dict:
    """Fail findings bound to an out-of-date source or model snapshot.

    Covers the out-of-date-source and stale-cache legs: a fact recorded
    against one digest is invalid once the source moves, even when the
    fact itself was once correct.
    """
    if not bound_sha256 or not current_sha256:
        return {"rule": "freshness_unknown", "status": "blocked", "label": label,
                "reason": "Bound and current digests are both required"}
    if bound_sha256 != current_sha256:
        return {"rule": "stale_source", "status": "fail", "label": label,
                "bound": bound_sha256, "current": current_sha256}
    return {"rule": "freshness_ok", "status": "pass", "label": label}


def require_rls_identity(role: str) -> dict:
    """Block scoped facts without an explicit RLS identity (missing-role leg)."""
    if not isinstance(role, str) or not role.strip():
        return {"rule": "missing_rls_identity", "status": "blocked",
                "reason": "An explicit RLS role is required before scoped answers"}
    return {"rule": "rls_identity_present", "status": "pass", "role": role}
