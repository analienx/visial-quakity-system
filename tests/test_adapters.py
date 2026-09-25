"""Spike-harness tests (WP-03/WP-04 offline subset): probe honesty.

PBI-04 (exact PID/path), DOC-06 (no Word-exact claims from another backend),
and the acceptance negatives: missing backends yield ``blocked`` with the
exact missing piece. No Desktop run, render, or model query is performed.
"""
from vqs.document import check_backend_equivalence, word_spike_readiness
from vqs.powerbi import check_target_match, desktop_spike_readiness


def test_desktop_spike_ready_with_binary_and_bridge() -> None:
    report = desktop_spike_readiness()
    assert report["gate"] == "G1-desktop-spike"
    assert report["verdict"] == "ready"
    assert report.get("missing", []) == []
    assert any("powerbi-desktop" in cap["reason"] for cap in report["capabilities"])


def test_wrong_pid_or_path_fails_before_pixels() -> None:
    assert check_target_match(1, "a.pbip", 1, "a.pbip")["verdict"] == "pass"
    assert check_target_match(1, "x/../a.pbip", 1, "a.pbip")["verdict"] == "pass"
    assert check_target_match(2, "a.pbip", 1, "a.pbip")["verdict"] == "fail"
    assert check_target_match(1, "b.pbip", 1, "a.pbip")["verdict"] == "fail"
    assert check_target_match(1, "", 1, "a.pbip")["verdict"] == "blocked"


def test_word_spike_ready_with_interactive_word() -> None:
    report = word_spike_readiness()
    assert report["gate"] == "G1-word-spike"
    assert report["verdict"] == "ready"
    assert "interactive-word" in report["backends"]


def test_renderer_mismatch_cannot_pass() -> None:
    assert check_backend_equivalence("word", "word")["verdict"] == "pass"
    failed = check_backend_equivalence("word", "libreoffice")
    assert failed["verdict"] == "fail"
    assert "Word-exact" in failed["reason"]
    assert check_backend_equivalence("", "word")["verdict"] == "blocked"
