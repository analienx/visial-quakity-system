"""Emitter tests (WP-19): exact extraction from the committed mini fixture."""
from pathlib import Path

import pytest

from vqs.powerbi.measure import measure_report

FIXTURES = Path(__file__).parent / "fixtures"
REPORT = str(FIXTURES / "mini_report")
MODEL = str(FIXTURES / "mini_model" / "definition")


def test_contrast_picks_weakest_text_run_pair() -> None:
    rules = measure_report(REPORT)["rules"]
    assert rules["typography.text_contrast"] == {"foreground": "#52617A",
                                                 "background": "#FFFFFF"}


def test_palette_assigns_theme_colors_per_page() -> None:
    rules = measure_report(REPORT)["rules"]
    assert rules["palette.semantic_consistency"] == {"assignments": [
        {"state": "series-index-0", "color": "#6C8FF0", "page": "P1"},
        {"state": "series-index-1", "color": "#6B7280", "page": "P1"}]}


def test_cohorts_carry_declared_values_and_default_nulls() -> None:
    rules = measure_report(REPORT)["rules"]
    assert rules["typography.format_declaration_consistency"] == {"readings": [
        {"cohort": "card/labels.fontSize", "page": "P1", "value": 24,
         "visual": "cardx"},
        {"cohort": "slicer/header.textSize", "page": "P1", "value": None,
         "visual": "slicera"},
        {"cohort": "slicer/header.textSize", "page": "P1", "value": 11,
         "visual": "slicerb"}]}


def test_model_sections_needs_model_dir() -> None:
    facts = measure_report(REPORT, MODEL)
    assert facts["rules"]["encoding.metric_unit_consistency"] == {"readings": [
        {"measure": "Fact Sales.Revenue", "page": "P1", "unit": "USD"}]}
    assert facts["models"] == [{"bindings": [{"query_ref": "Dim Date.Year"},
                                             {"query_ref": "Fact Sales.Revenue"}],
                                "model_dir": MODEL}]
    bare = measure_report(REPORT)
    assert "encoding.metric_unit_consistency" not in bare["rules"]
    assert "models" not in bare


def test_missing_report_dir_raises() -> None:
    with pytest.raises(OSError):
        measure_report(str(FIXTURES / "absent"))


def test_missing_theme_omits_theme_rules(tmp_path: Path) -> None:
    import shutil
    clone = tmp_path / "report"
    shutil.copytree(REPORT, clone)
    for path in (clone / "StaticResources").rglob("*.json"):
        path.unlink()
    rules = measure_report(str(clone))["rules"]
    assert "typography.text_contrast" not in rules
    assert "palette.semantic_consistency" not in rules
    assert "typography.format_declaration_consistency" in rules


def test_emitted_facts_pass_pipeline_shape(tmp_path: Path) -> None:
    from vqs.pipeline import run_check
    facts = measure_report(REPORT, MODEL)
    facts["rules"].pop("typography.format_declaration_consistency")
    result = run_check(facts, tmp_path, run_id="emitter-shape")
    assert result["verdict"] == "pass"
    assert result["findings"]
