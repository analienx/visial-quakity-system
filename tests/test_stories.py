"""WP-10 story oracles: scoped answers preserved, ambiguous ones clarified.

DES-08 (never fabricate) and DES-09 (same scope or no pass). Synthetic
inputs only; no model query is exercised.
"""
from vqs.stories import ambiguity_check, oracle_matches, scope_digest


def test_oracle_requires_identical_scope() -> None:
    scope = scope_digest({"Year": "2024"}, role="viewer", period="2024", measure="Revenue")
    assert scope_digest({"Year": "2024"}, role="viewer", period="2024", measure="Revenue") == scope
    assert scope_digest({"Year": "2023"}, role="viewer", period="2024", measure="Revenue") != scope
    assert oracle_matches(scope, scope)["verdict"] == "pass"
    assert oracle_matches(scope, scope_digest({}))["verdict"] == "fail"
    assert oracle_matches("", scope)["verdict"] == "blocked"


def test_ambiguous_questions_need_clarification() -> None:
    assert ambiguity_check("Revenue trend?", ["Revenue"])["verdict"] == "answerable"
    assert ambiguity_check("Why did it happen?", ["Revenue"])["verdict"] == "needs_clarification"
    assert ambiguity_check("Revenue vs target?", ["Revenue"])["verdict"] == "needs_clarification"
    assert ambiguity_check("Revenue vs Q1 target?", ["Revenue"], ["Q1 target"])["verdict"] == "answerable"
    assert ambiguity_check("", ["Revenue"])["verdict"] == "blocked"
