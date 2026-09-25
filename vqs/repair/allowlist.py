"""Typed repair-plan allowlist (WP-09 static half, issue #14).

Two-stage plan validation *before* any execution: every operation must be
allowlisted, model/DAX/RLS and intent changes need an explicit owner approval
id, the write target must be a disposable candidate (never the original
source), and a rollback recipe is mandatory. FIX-02 (shell/DAX smuggling),
FIX-08 (original overwrite), and DES-07 (intent change without approval) are
rejected here; live render, data, and regression gates belong downstream.
"""
from __future__ import annotations

import posixpath
import re
from typing import Any

ALLOWED_OPS: frozenset[str] = frozenset({
    "theme.set", "palette.assign", "typography.size", "axis.tick_format",
    "axis.title", "axis.precision", "label.format", "chart.resize",
    "spacing.adjust", "sort.set", "chart.replace",
})
MODEL_TARGETS: frozenset[str] = frozenset({"model", "dax", "rls", "dataset", "measure"})
SHELL_OPS: frozenset[str] = frozenset({"shell", "exec", "command", "run", "script"})


def _seps(path: str) -> str:
    return path.replace("\\", "/")


def _resolve(candidate_root: str, target: str) -> str:
    """Resolve a write target: absolute stays absolute, relative joins the root."""
    candidate = posixpath.normpath(_seps(candidate_root))
    cleaned = _seps(target)
    if posixpath.isabs(cleaned) or re.match(r"^[A-Za-z]:", cleaned) or cleaned.startswith("//"):
        return posixpath.normpath(cleaned)
    return posixpath.normpath(posixpath.join(candidate, cleaned))


def _inside(candidate_root: str, target: str) -> bool:
    """Strict containment: the target must be a file inside the root.

    The root directory itself (from empty, ".", or equivalent targets) is
    not a writable artifact and is rejected.
    """
    root = posixpath.normpath(_seps(candidate_root))
    resolved = _resolve(candidate_root, target)
    if resolved == root:
        return False
    return resolved.startswith(root.rstrip("/") + "/")


def _touches_model(target: str) -> bool:
    """Case/whitespace-qualified match, including qualified refs like Dataset.T[col]."""
    norm = target.strip().casefold()
    delimiters = (".", "[", "(", " ", "/", ":")
    return any(norm == word or norm.startswith(word + mark)
               for word in MODEL_TARGETS for mark in delimiters + ("",))


def validate_plan(plan: dict[str, Any], original_path: str, candidate_root: str,
                 approved_semantic_change: str | None = None) -> list[dict[str, Any]]:
    """Validate a repair plan; empty list means it may proceed to execution."""
    issues: list[dict[str, Any]] = []
    if not isinstance(plan, dict):
        return [{"rule": "plan_not_an_object"}]
    operations = plan.get("operations")
    if not isinstance(operations, list) or not operations:
        return [{"rule": "plan_has_no_operations"}]
    for index, op in enumerate(operations):
        if not isinstance(op, dict):
            issues.append({"rule": "operation_not_an_object", "index": index})
            continue
        op_type = op.get("type", "")
        if op_type in SHELL_OPS:
            issues.append({"rule": "plan_rejected_shell", "index": index, "type": op_type})
            continue
        if op_type not in ALLOWED_OPS:
            issues.append({"rule": "plan_rejected_unknown_op", "index": index,
                           "type": op_type})
            continue
        target = str(op.get("target", ""))
        if _touches_model(target) and not approved_semantic_change:
            issues.append({"rule": "dax_rls_unapproved", "index": index,
                           "remediation": "Declare an owner-approved semantic change id"})
            continue
        if op_type == "chart.replace" and not (
                op.get("identical_intent") is True or approved_semantic_change):
            issues.append({"rule": "intent_change_unapproved", "index": index})
    original = posixpath.normpath(_seps(original_path))
    for target in plan.get("write_targets", []):
        if not isinstance(target, str) or not _inside(candidate_root, target):
            issues.append({"rule": "write_guard_violation", "target": target,
                           "remediation": "Write only inside the disposable candidate root"})
        elif _resolve(candidate_root, target) == original:
            issues.append({"rule": "write_guard_violation", "target": target,
                           "remediation": "The original source is read-only"})
    if plan.get("removed_ids") and not approved_semantic_change:
        issues.append({"rule": "id_not_preserved", "removed": plan.get("removed_ids")})
    if not plan.get("rollback"):
        issues.append({"rule": "missing_rollback"})
    return issues


def rollback_ok(before_digest: str, after_rollback_digest: str) -> dict:
    """Pass only when rollback restores the exact input hash."""
    if not before_digest or not after_rollback_digest:
        return {"rule": "rollback_unverifiable", "status": "blocked"}
    if before_digest == after_rollback_digest:
        return {"rule": "rollback_restored", "status": "pass"}
    return {"rule": "rollback_mismatch", "status": "fail"}
