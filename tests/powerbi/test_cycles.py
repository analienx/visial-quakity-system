"""Cycle-gate tests: synthetic TMDL with known loops and clean controls."""
import json
from pathlib import Path

import pytest

from vqs.powerbi.cycles import check_model

FIXTURES = Path(__file__).parent / "fixtures"
LOOPY = str(FIXTURES / "cycle_model")
CLEAN = str(FIXTURES / "clean_model")


def test_dax_cycle_reports_both_measures() -> None:
    result = check_model(LOOPY)
    assert result["acyclic"] is False
    assert result["dax_cycles"] == [
        ["measure:Loop.A", "measure:Loop.B", "measure:Loop.A"]]
    assert all("Clean" not in node for cycle in result["dax_cycles"]
               for node in cycle)


def test_m_query_cycle_found() -> None:
    result = check_model(LOOPY)
    assert result["m_cycles"] == [["Q1", "Q2", "Q1"]]
    assert result["m_queries"] == 5


def test_within_let_cycle_names_query() -> None:
    result = check_model(LOOPY)
    assert result["let_cycles"] == [
        {"query": "Loopy", "cycle": ["a", "b", "a"]}]


def test_clean_model_is_acyclic() -> None:
    result = check_model(CLEAN)
    assert result == {"model_dir": CLEAN, "dax_objects": 2, "m_queries": 1,
                      "dax_cycles": [], "m_cycles": [], "let_cycles": [],
                      "acyclic": True}


def test_missing_model_dir_raises() -> None:
    with pytest.raises(OSError):
        check_model(str(FIXTURES / "absent"))


def test_cycles_command_exit_codes(capsys) -> None:
    from vqs.cli import main as vqs_main
    assert vqs_main(["cycles", LOOPY]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["acyclic"] is False
    assert vqs_main(["cycles", CLEAN]) == 0
    assert vqs_main(["cycles", str(FIXTURES / "absent")]) == 2
