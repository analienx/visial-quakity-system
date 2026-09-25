"""Review-bundle adjudication (WP-07 static half, issue #12).

Decides a structured review bundle without looking at pixels: reviewer
separation (CORE-06), image-capability presence (DES-10), capture calibration
(full-canvas at target scale), per-page source binding (stale images fail),
and observation completeness (every verdict carries its reason). Verdict
aggregation never coerces ``unknown`` into ``pass``. Model disagreement,
hallucination detection, and perceptual judgment itself need a capable image
reviewer plus real renders — explicitly out of scope here.
"""
from __future__ import annotations

from typing import Any

from vqs.contracts import adjudicate as adjudicate_status


def adjudicate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Adjudicate a review bundle; empty findings means release-pass."""
    findings: list[dict[str, Any]] = []
    if not isinstance(bundle, dict):
        return {"verdict": "blocked", "findings": [{"rule": "bundle_not_an_object"}]}
    source = bundle.get("source_sha256", "")
    reviewer = bundle.get("reviewer", {})
    reviewer_id = reviewer.get("id", "") if isinstance(reviewer, dict) else ""
    if reviewer_id and reviewer_id == bundle.get("fixer_id"):
        findings.append({"rule": "own_review_forbidden", "status": "fail"})
    capability = bundle.get("image_capability", {})
    if not isinstance(capability, dict) or capability.get("available") is not True:
        findings.append({"rule": "missing_image_capability", "status": "blocked",
                         "reason": "A capable image reviewer is required; text-only cannot assess pixels"})
    calibration = bundle.get("calibration", {})
    if (not isinstance(calibration, dict) or not calibration.get("full_canvas")
            or not calibration.get("viewport") or not calibration.get("scale")):
        findings.append({"rule": "calibration_missing", "status": "blocked",
                         "reason": "Full-canvas calibration at target scale required"})
    pages = bundle.get("pages")
    if not isinstance(pages, list) or not pages:
        findings.append({"rule": "no_pages_evidence", "status": "blocked"})
        pages = []
    for page in pages:
        if not isinstance(page, dict):
            findings.append({"rule": "page_not_an_object", "status": "blocked"})
            continue
        page_id = page.get("id", "?")
        if page.get("image_source_sha256", "") != source or not source:
            findings.append({"rule": "stale_image", "status": "fail", "page": page_id})
        observations = page.get("observations")
        if not isinstance(observations, list) or not observations:
            findings.append({"rule": "observations_missing", "status": "blocked",
                             "page": page_id})
            continue
        for obs in observations:
            if not isinstance(obs, dict):
                findings.append({"rule": "observation_not_an_object", "status": "blocked",
                                 "page": page_id})
                continue
            status = obs.get("status", "")
            if status not in ("pass", "fail", "blocked", "unknown", "not_applicable"):
                findings.append({"rule": "invalid_observation_status", "status": "blocked",
                                 "page": page_id, "criterion": obs.get("criterion")})
            elif not obs.get("reason", ""):
                findings.append({"rule": "incomplete_observation", "status": "blocked",
                                 "page": page_id, "criterion": obs.get("criterion"),
                                 "reason": "Every verdict states its observed evidence"})
            elif status != "pass":
                findings.append({"rule": "observation_not_pass", "status": status,
                                 "page": page_id, "criterion": obs.get("criterion")})
    if not findings:
        return {"verdict": "pass", "findings": []}
    verdict = "pass"
    for finding in findings:
        verdict = {"fail": "fail", "blocked": "blocked"}.get(
            adjudicate_status(finding.get("status", "unknown")), verdict)
        if verdict == "fail":
            break
    if verdict == "pass":
        verdict = "blocked"
    return {"verdict": verdict, "findings": findings}
