"""Repair allowlist tests (WP-09 static half): plans validated pre-execution.

FIX-02 (shell/DAX smuggling), FIX-08 (original overwrite), DES-07 (intent
change without approval). No execution, render, or data is involved.
"""
from vqs.repair import rollback_ok, validate_plan

ORIGINAL = "/reports/original.Report"
CANDIDATE = "/candidate/worktree-1"


def _plan(**overrides):
    base = {
        "operations": [{"type": "theme.set", "target": "visual", "value": "#0F2A44"}],
        "write_targets": ["/candidate/worktree-1/report.Report"],
        "rollback": "git checkout -- report.Report",
    }
    base.update(overrides)
    return base


def test_allowed_theme_change_passes() -> None:
    assert validate_plan(_plan(), ORIGINAL, CANDIDATE) == []


def test_shell_and_unknown_ops_rejected() -> None:
    shell = _plan(operations=[{"type": "shell", "target": "os", "value": "rm -rf /"}])
    assert any(row["rule"] == "plan_rejected_shell" for row in validate_plan(shell, ORIGINAL, CANDIDATE))
    weird = _plan(operations=[{"type": "teleport", "target": "visual"}])
    assert any(row["rule"] == "plan_rejected_unknown_op"
               for row in validate_plan(weird, ORIGINAL, CANDIDATE))
    assert validate_plan({"operations": []}, ORIGINAL, CANDIDATE)[0]["rule"] == "plan_has_no_operations"


def test_dax_mutation_needs_owner_approval() -> None:
    dax = _plan(operations=[{"type": "axis.tick_format", "target": "dax", "value": "0.0"}])
    assert any(row["rule"] == "dax_rls_unapproved"
               for row in validate_plan(dax, ORIGINAL, CANDIDATE))
    assert validate_plan(dax, ORIGINAL, CANDIDATE, approved_semantic_change="owner-7") == []


def test_chart_replace_needs_identical_intent_or_approval() -> None:
    swap = _plan(operations=[{"type": "chart.replace", "target": "visual"}])
    assert any(row["rule"] == "intent_change_unapproved"
               for row in validate_plan(swap, ORIGINAL, CANDIDATE))
    same = _plan(operations=[{"type": "chart.replace", "target": "visual",
                              "identical_intent": True}])
    assert validate_plan(same, ORIGINAL, CANDIDATE) == []


def test_write_guard_blocks_original_and_escapes() -> None:
    outside = _plan(write_targets=["/etc/passwd"])
    assert any(row["rule"] == "write_guard_violation"
               for row in validate_plan(outside, ORIGINAL, CANDIDATE))
    direct = _plan(write_targets=[ORIGINAL])
    assert any(row["rule"] == "write_guard_violation"
               for row in validate_plan(direct, ORIGINAL, ORIGINAL))
    dropped = _plan(removed_ids=["vis1"])
    assert any(row["rule"] == "id_not_preserved"
               for row in validate_plan(dropped, ORIGINAL, CANDIDATE))
    assert any(row["rule"] == "missing_rollback"
               for row in validate_plan({**_plan(), "rollback": ""}, ORIGINAL, CANDIDATE))


def test_model_target_variants_need_approval() -> None:
    for target in ("DAX", "dax ", "dataset.table[col]", " RLS", "Measure.X"):
        probing = _plan(operations=[{"type": "axis.tick_format", "target": target}])
        assert any(row["rule"] == "dax_rls_unapproved"
                   for row in validate_plan(probing, ORIGINAL, CANDIDATE)), target


def test_windows_and_alias_escapes_blocked() -> None:
    for target in ("..\\evil.Report", "C:\\Windows\\evil.Report",
                   "//server/share/evil.Report"):
        probing = _plan(write_targets=[target])
        assert any(row["rule"] == "write_guard_violation"
                   for row in validate_plan(probing, ORIGINAL, CANDIDATE)), target
    root_original = "/candidate/worktree-1/report.Report"
    for target in ("report.Report", "sub/../report.Report"):
        probing = _plan(write_targets=[target])
        assert any(row["rule"] == "write_guard_violation"
                   for row in validate_plan(probing, root_original, CANDIDATE)), target
    for target in ("", ".", "/candidate/worktree-1"):
        probing = _plan(write_targets=[target])
        assert any(row["rule"] == "write_guard_violation"
                   for row in validate_plan(probing, ORIGINAL, CANDIDATE)), target


def test_rollback_restores_exact_hash() -> None:
    assert rollback_ok("a" * 64, "a" * 64)["status"] == "pass"
    assert rollback_ok("a" * 64, "b" * 64)["status"] == "fail"
    assert rollback_ok("", "b" * 64)["status"] == "blocked"
