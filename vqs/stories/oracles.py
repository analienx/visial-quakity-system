"""Minimal question/answer oracles (WP-10, issue #15, offline subset).

A repair preserves the answer to the same scoped question. Scope equality is
checked on a stable digest of filters, role, period, and measure — an
apparently equal answer under a different scope can never pass (DES-09), and
a question with no known measure, date, or target needs clarification instead
of a fabricated claim (DES-08). No model query or render is performed here.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence


def scope_digest(filters: dict[str, str] | None, role: str = "",
                 period: str = "", measure: str = "") -> str:
    """Stable digest of an answer scope; empty scope digests honestly, not equally."""
    canonical = json.dumps(
        {"filters": filters or {}, "role": role, "period": period, "measure": measure},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def oracle_matches(oracle_scope: str, run_scope: str) -> dict:
    """Pass only when the run reproduced the oracle under the identical scope."""
    if not oracle_scope or not run_scope:
        return {"verdict": "blocked", "reason": "Both oracle and run scopes required"}
    if oracle_scope == run_scope:
        return {"verdict": "pass", "scope": run_scope}
    return {"verdict": "fail", "reason": "Answer scope differs from the oracle scope",
            "oracle": oracle_scope, "run": run_scope}


def ambiguity_check(question: str | None, known_measures: Sequence[str] | None,
                    known_targets: Sequence[str] | None = None) -> dict:
    """Decide whether a question is answerable from known model context.

    Returns ``answerable`` only when the question names a known measure.
    Anything else returns ``needs_clarification`` — never a fabricated
    trend, target, or causal claim.
    """
    if not question or not question.strip():
        return {"verdict": "blocked", "reason": "A question is required"}
    measures = list(known_measures or [])
    targets = list(known_targets or [])
    lowered = question.lower()
    if not any(measure.lower() in lowered for measure in measures):
        return {"verdict": "needs_clarification",
                "reason": "Question names no known measure; do not invent one"}
    mentions_target = any(target.lower() in lowered for target in targets)
    if "target" in lowered and not mentions_target:
        return {"verdict": "needs_clarification",
                "reason": "Question implies a target with no target evidence"}
    return {"verdict": "answerable", "question": question}
