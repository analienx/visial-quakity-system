"""Review adjudication tests (WP-07 static half): synthetic bundles only.

No pixels, models, or renders involved; perceptual judgment itself remains
the job of a capable image reviewer on real evidence.
"""
from vqs.review import adjudicate_bundle

SOURCE = "c" * 64


def _bundle(**overrides):
    base = {
        "source_sha256": SOURCE,
        "reviewer": {"id": "reviewer-1", "role": "independent_visual_reviewer"},
        "fixer_id": "executor-1",
        "image_capability": {"available": True, "provider": "synthetic-test"},
        "calibration": {"full_canvas": True, "viewport": "1440x1000", "scale": 1},
        "pages": [{
            "id": "page-1",
            "image_sha256": "d" * 64,
            "image_source_sha256": SOURCE,
            "observations": [{
                "criterion": "text_legibility",
                "status": "pass",
                "reason": "All labels legible at target size on the fresh render",
            }],
        }],
    }
    base.update(overrides)
    return base


def test_clean_bundle_passes() -> None:
    assert adjudicate_bundle(_bundle()) == {"verdict": "pass", "findings": []}


def test_same_reviewer_and_editor_fails() -> None:
    result = adjudicate_bundle(_bundle(reviewer={"id": "executor-1"}))
    assert result["verdict"] == "fail"
    assert any(row["rule"] == "own_review_forbidden" for row in result["findings"])


def test_stale_image_and_missing_capability() -> None:
    stale = _bundle()
    stale["pages"][0]["image_source_sha256"] = "e" * 64
    result = adjudicate_bundle(stale)
    assert result["verdict"] == "fail"
    assert any(row["rule"] == "stale_image" for row in result["findings"])
    nocap = _bundle(image_capability={"available": False})
    result = adjudicate_bundle(nocap)
    assert result["verdict"] == "blocked"
    assert any(row["rule"] == "missing_image_capability" for row in result["findings"])


def test_missing_calibration_and_reasonless_verdicts_block() -> None:
    nocal = _bundle(calibration={"full_canvas": False})
    assert adjudicate_bundle(nocal)["verdict"] == "blocked"
    noreason = _bundle()
    noreason["pages"][0]["observations"][0] = {"criterion": "text_legibility",
                                               "status": "pass", "reason": ""}
    result = adjudicate_bundle(noreason)
    assert result["verdict"] == "blocked"
    assert any(row["rule"] == "incomplete_observation" for row in result["findings"])


def test_failing_observation_and_unknown_verdicts() -> None:
    bad = _bundle()
    bad["pages"][0]["observations"][0]["status"] = "fail"
    assert adjudicate_bundle(bad)["verdict"] == "fail"
    unknown = _bundle()
    unknown["pages"][0]["observations"][0]["status"] = "unknown"
    assert adjudicate_bundle(unknown)["verdict"] == "blocked"
    assert adjudicate_bundle("not-a-bundle")["verdict"] == "blocked"
