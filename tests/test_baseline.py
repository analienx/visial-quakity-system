"""WP-00 baseline honesty checks: BASELINE.md must exist and report truthfully.

These checks do not verify any work package; they verify the baseline
document itself follows issue #5 (capability blocked, never claimed).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "BASELINE.md"


def _text() -> str:
    return BASELINE.read_text(encoding="utf-8")


def test_baseline_document_exists_and_links_program() -> None:
    assert BASELINE.is_file()
    text = _text()
    assert "issues/4" in text
    assert "issues/5" in text
    assert "WP-00" in text


def test_baseline_records_capability_matrix_with_blocked() -> None:
    text = _text()
    assert "Capability matrix" in text
    assert text.count("blocked") >= 2
    assert "PBIDesktop.exe" in text
    assert "soffice" in text


def test_baseline_claims_no_verified_package() -> None:
    text = _text()
    assert "No work package is marked verified" in text
    assert "| **verified" not in text
