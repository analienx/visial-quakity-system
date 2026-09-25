"""TMDL fact tests (WP-05 static subset): synthetic models only.

Live DAX, refresh, and RLS remain blocked (see `blocked_snapshot`); these
tests cover declaration inventory and binding resolution, never values.
"""
from pathlib import Path

from vqs.data import (
    blocked_snapshot,
    check_bindings,
    check_freshness,
    inventory_model,
    parse_tmdl,
    require_rls_identity,
)

MODEL = """table Dim Product
    column Brand
        dataType: string
    column Category
    measure Product Count = COUNTROWS('Dim Product')
    measure Bare Measure
table Fact Sales
    column Amount
        dataType: decimal
    measure Revenue = SUM('Fact Sales'[Amount])
"""


def _model(tmp_path: Path) -> Path:
    root = tmp_path / "Example.SemanticModel"
    root.mkdir()
    (root / "model.tmdl").write_text(MODEL, encoding="utf-8")
    return root


def test_loaded_synthetic_model_inventoried(tmp_path: Path) -> None:
    inventory = inventory_model(_model(tmp_path))
    assert inventory["issues"] == []
    tables = inventory["tables"]
    assert sorted(tables) == ["Dim Product", "Fact Sales"]
    assert tables["Dim Product"]["measures"]["Product Count"].startswith("COUNTROWS")
    assert tables["Dim Product"]["measures"]["Bare Measure"] == ""
    assert "Brand" in tables["Dim Product"]["columns"]


def test_missing_model_is_no_model_issue(tmp_path: Path) -> None:
    assert inventory_model(tmp_path / "absent")["issues"][0]["rule"] == "no_model"
    empty = tmp_path / "empty.SemanticModel"
    empty.mkdir()
    assert inventory_model(empty)["issues"][0]["rule"] == "no_model"


def test_bindings_resolve_or_fail_honestly(tmp_path: Path) -> None:
    inventory = inventory_model(_model(tmp_path))
    ok = check_bindings([{"query_ref": "Dim Product.Brand"},
                         {"query_ref": "Fact Sales.Revenue"}], inventory)
    assert [finding["status"] for finding in ok] == ["pass", "pass"]
    missing = check_bindings([{"query_ref": "Dim Ghost.Field"},
                              {"query_ref": "Dim Product.Nope"}], inventory)
    assert all(finding["rule"] == "missing_dimension_or_measure" for finding in missing)
    assert all(finding["status"] == "fail" for finding in missing)
    bare = check_bindings([{"query_ref": "Dim Product.Bare Measure"}], inventory)
    assert bare[0]["status"] == "unknown"


def test_absent_data_is_blocked_never_fabricated() -> None:
    snapshot = blocked_snapshot("No authorized DAX provider on this host")
    assert snapshot["status"] == "blocked" and snapshot["values"] is None


def test_orphan_declarations_become_issues() -> None:
    parsed = parse_tmdl("    measure Lonely = 1")
    assert any(row["rule"] == "orphan_declaration" for row in parsed["issues"])


REALWORLD = """/// Sales transaction fact table.
table 'Fact Sales'
\tlineageTag: 520533e2-e157-48b8-aaa1-cb539ef62b28

\t/// Total net sales in the current filter context.
\tmeasure 'Sales Amount' = SUM ( 'Fact Sales'[Net Sales] )
\t\tformatString: $#,0
\t\tdisplayFolder: Revenue

\tmeasure 'Margin?' = IF ( [A] = [B], 1, 0 )

\tcolumn 'Sales Order Number'
\t\tdataType: string
"""


def test_quoted_realworld_declarations_unquote_and_resolve() -> None:
    parsed = parse_tmdl(REALWORLD)
    assert parsed["issues"] == []
    tables = parsed["tables"]
    assert sorted(tables) == ["Fact Sales"]
    assert tables["Fact Sales"]["measures"]["Sales Amount"].startswith("SUM")
    assert tables["Fact Sales"]["measures"]["Margin?"] == "IF ( [A] = [B], 1, 0 )"
    assert "Sales Order Number" in tables["Fact Sales"]["columns"]
    assert "formatString" not in tables["Fact Sales"]["measures"]
    assert "lineageTag" not in tables["Fact Sales"]["measures"]
    ok = check_bindings([{"query_ref": "Fact Sales.Sales Amount"},
                         {"query_ref": "Fact Sales.Sales Order Number"}],
                        parsed)
    assert [finding["status"] for finding in ok] == ["pass", "pass"]


NON_TABLE = """model Model
\tculture: en-US

relationship factSales_customer
\tfromColumn: 'Fact Sales'.'Customer Key'
\ttoColumn: 'Dim Customer'.'Customer Key'

expression pStart = #date(2023, 1, 1)

\tannotation PBI_ResultType = Date

ref table 'Fact Sales'
"""


def test_non_table_objects_are_skipped_not_flagged() -> None:
    parsed = parse_tmdl(NON_TABLE)
    assert parsed == {"tables": {}, "issues": []}


def test_empty_table_name_is_flagged() -> None:
    parsed = parse_tmdl("table ''\n\tcolumn Orphaned\n")
    assert parsed["tables"] == {}
    assert [row["rule"] for row in parsed["issues"]] == ["empty_table_name"]


def test_out_of_date_source_fails_and_current_passes() -> None:
    assert check_freshness("a" * 64, "a" * 64, "report")["status"] == "pass"
    stale = check_freshness("a" * 64, "b" * 64, "model")
    assert stale["status"] == "fail" and stale["rule"] == "stale_source"
    assert check_freshness("", "b" * 64, "model")["status"] == "blocked"


def test_missing_rls_identity_blocks() -> None:
    assert require_rls_identity("viewer")["status"] == "pass"
    assert require_rls_identity("")["rule"] == "missing_rls_identity"
    assert require_rls_identity("   ")["status"] == "blocked"
