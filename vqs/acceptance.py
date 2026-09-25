"""End-to-end acceptance adjudication (WP-11 core, issue #16).

Aggregates per-subject gate results into a release verdict. The rules encode
the acceptance contract itself: two unrelated PBIP subjects plus a DOCX
(a partial suite is never acceptance), every gate linked to evidence, all
named negative controls present and caught, reviewer different from editor,
and explicit user promotion approval. Anything short of that fails or
blocks — never passes.
"""
from __future__ import annotations

from typing import Any

REQUIRED_NEGATIVES: frozenset[str] = frozenset({
    "stale_image", "wrong_pid", "blank_first_open", "partial_canvas",
    "empty_model", "hallucinated_defect", "missing_word_font",
    "narrative_mismatch", "hidden_fifth_bar", "broken_slicer",
    "false_agent_approval",
})


def run_acceptance(record: dict[str, Any]) -> dict[str, Any]:
    """Adjudicate an acceptance record; see module docstring for the rules."""
    findings: list[dict[str, Any]] = []
    if not isinstance(record, dict):
        return {"verdict": "blocked", "findings": [{"rule": "record_not_an_object"}]}
    subjects = record.get("subjects", [])
    pbips = [s for s in subjects if isinstance(s, dict) and s.get("kind") == "pbip"]
    docxs = [s for s in subjects if isinstance(s, dict) and s.get("kind") == "docx"]
    layouts = {s.get("layout_digest") for s in pbips if s.get("layout_digest")}
    if len(pbips) < 2 or len(layouts) < 2 or len(docxs) < 1:
        findings.append({"rule": "partial_suite", "status": "blocked",
                         "reason": "Two unrelated PBIPs plus a DOCX are required"})
    gates = record.get("gates", [])
    if not isinstance(gates, list) or not gates:
        findings.append({"rule": "no_gates_evidence", "status": "blocked"})
        gates = []
    seen_negatives: set[str] = set()
    for gate in gates:
        if not isinstance(gate, dict):
            findings.append({"rule": "gate_not_an_object", "status": "blocked"})
            continue
        gate_id = gate.get("id", "?")
        ref = gate.get("evidence_ref", {})
        if not isinstance(ref, dict) or not ref.get("sha256"):
            findings.append({"rule": "missing_evidence_link", "status": "blocked",
                             "gate": gate_id})
        status = gate.get("status", "")
        if status not in ("pass", "fail", "blocked", "unknown", "not_run"):
            findings.append({"rule": "invalid_gate_status", "status": "blocked",
                             "gate": gate_id})
        elif status == "fail":
            findings.append({"rule": "gate_failed", "status": "fail", "gate": gate_id})
        elif status in ("blocked", "unknown", "not_run"):
            findings.append({"rule": "gate_not_green", "status": "blocked", "gate": gate_id,
                             "detail": status})
        control = gate.get("negative_control", "")
        if control:
            seen_negatives.add(control)
            if gate.get("caught", False) is not True:
                findings.append({"rule": "negative_uncaught", "status": "fail",
                                 "control": control})
    missing = REQUIRED_NEGATIVES - seen_negatives
    if missing:
        findings.append({"rule": "negative_controls_missing", "status": "blocked",
                         "missing": sorted(missing)})
    if record.get("reviewer_id", "") == record.get("editor_id", "") or not record.get("reviewer_id"):
        findings.append({"rule": "reviewer_not_independent", "status": "fail"})
    if record.get("user_approved", False) is not True:
        findings.append({"rule": "promotion_not_approved", "status": "blocked"})
    if not findings:
        return {"verdict": "pass", "findings": []}
    if any(finding.get("status") == "fail" for finding in findings):
        return {"verdict": "fail", "findings": findings}
    return {"verdict": "blocked", "findings": findings}
