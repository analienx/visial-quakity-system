"""WP-11 acceptance adjudication: every rule must fail or block independently."""
from __future__ import annotations

from vqs.acceptance import REQUIRED_NEGATIVES, run_acceptance


def _gate(gate_id, control=None, caught=None, status="pass", sha="a" * 64):
    gate = {"id": gate_id, "status": status, "evidence_ref": {"sha256": sha}}
    if control:
        gate["negative_control"] = control
        gate["caught"] = caught
    return gate


def _subjects():
    return [{"kind": "pbip", "id": "contoso", "layout_digest": "1" * 16},
            {"kind": "pbip", "id": "other", "layout_digest": "2" * 16},
            {"kind": "docx", "id": "report"}]


def _record(**overrides):
    gates = [_gate("baseline")]
    for control in sorted(REQUIRED_NEGATIVES):
        gates.append(_gate(f"neg-{control}", control=control, caught=True))
    record = {"subjects": _subjects(), "gates": gates,
              "editor_id": "agent-a", "reviewer_id": "agent-b", "user_approved": True}
    record.update(overrides)
    return record


def test_full_record_passes():
    verdict = run_acceptance(_record())
    assert verdict == {"verdict": "pass", "findings": []}


def test_single_pbip_is_not_acceptance():
    subjects = [s for s in _subjects() if s["id"] != "other"]
    verdict = run_acceptance(_record(subjects=subjects))
    assert verdict["verdict"] == "blocked"
    assert {"rule": "partial_suite", "status": "blocked",
            "reason": "Two unrelated PBIPs plus a DOCX are required"} in verdict["findings"]


def test_identical_layouts_are_not_unrelated():
    subjects = _subjects()
    subjects[1]["layout_digest"] = subjects[0]["layout_digest"]
    verdict = run_acceptance(_record(subjects=subjects))
    assert verdict["verdict"] == "blocked"
    assert "partial_suite" in _rules(verdict)


def test_missing_negative_control_blocks():
    gates = [gate for gate in _record()["gates"]
             if gate.get("negative_control") != "hidden_fifth_bar"]
    verdict = run_acceptance(_record(gates=gates))
    assert verdict["verdict"] == "blocked"
    missing_finding = next(f for f in verdict["findings"]
                           if f["rule"] == "negative_controls_missing")
    assert missing_finding["missing"] == ["hidden_fifth_bar"]


def test_uncaught_negative_fails():
    gates = _record()["gates"]
    gates[2]["caught"] = False
    verdict = run_acceptance(_record(gates=gates))
    assert verdict["verdict"] == "fail"
    assert verdict["findings"][0]["rule"] == "negative_uncaught"


def test_same_reviewer_and_editor_fails():
    verdict = run_acceptance(_record(reviewer_id="agent-a"))
    assert verdict["verdict"] == "fail"
    assert "reviewer_not_independent" in _rules(verdict)


def test_missing_user_approval_blocks():
    verdict = run_acceptance(_record(user_approved=False))
    assert verdict["verdict"] == "blocked"
    assert "promotion_not_approved" in _rules(verdict)


def test_unknown_gate_status_blocks():
    gates = [_gate("odd", status="skipped")]
    verdict = run_acceptance(_record(gates=gates))
    assert verdict["verdict"] == "blocked"
    assert "invalid_gate_status" in _rules(verdict)


def _rules(verdict):
    return {finding["rule"] for finding in verdict["findings"]}


def test_missing_evidence_link_blocks():
    gates = _record()["gates"]
    gates[0] = {"id": "noev", "status": "pass", "evidence_ref": {}}
    verdict = run_acceptance(_record(gates=gates))
    assert verdict["verdict"] == "blocked"
    assert "missing_evidence_link" in _rules(verdict)


def test_failed_gate_fails():
    verdict = run_acceptance(_record(gates=[_gate("bad", status="fail")]))
    assert verdict["verdict"] == "fail"
    assert "gate_failed" in _rules(verdict)


def test_not_green_gate_blocks():
    for status in ("blocked", "unknown", "not_run"):
        verdict = run_acceptance(_record(gates=[_gate("grey", status=status)]))
        assert verdict["verdict"] == "blocked", status
        assert "gate_not_green" in _rules(verdict), status


def test_empty_gates_block():
    verdict = run_acceptance(_record(gates=[]))
    assert verdict["verdict"] == "blocked"
    assert "no_gates_evidence" in _rules(verdict)


def test_non_object_gate_blocks():
    verdict = run_acceptance(_record(gates=["not-a-gate"]))
    assert verdict["verdict"] == "blocked"
    assert "gate_not_an_object" in _rules(verdict)


def test_non_object_record_blocks():
    verdict = run_acceptance("not-a-record")
    assert verdict == {"verdict": "blocked",
                       "findings": [{"rule": "record_not_an_object"}]}
