"""Read-only PBIR visual facts. No Desktop, credentials, model query or image needed.

Adapted from PBIPDocumenter's source-bound quality gate and structured evidence.
Effective theme values, actual DAX values and pixel readability remain unknown.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .evidence import load


def source_digest(report: Path) -> str:
    """Fingerprint report plus sibling model *source*, excluding runtime binary caches."""
    report = Path(report).resolve()
    root = report.parent
    models = sorted(root.glob("*.SemanticModel"))
    digest = hashlib.sha256()
    for source in [report, *models]:
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".json", ".tmdl", ".pbism", ".pbir"}:
                # User-local runtime settings are not report/model design source.
                if ".pbi" in path.relative_to(source).parts:
                    continue
                digest.update(path.relative_to(root).as_posix().encode("utf-8"))
                digest.update(b"\0")
                digest.update(path.read_bytes())
                digest.update(b"\0")
    return digest.hexdigest()


def _literals(node: object, prefix: str = "", limit: int = 50) -> list[dict]:
    result: list[dict] = []
    def walk(value: object, key: str, depth: int) -> None:
        if len(result) >= limit or depth > 16:
            return
        if isinstance(value, dict):
            literal = value.get("Literal")
            if isinstance(literal, dict) and "Value" in literal:
                text = str(literal["Value"])
                if len(text) <= 180:
                    result.append({"path": key + ".Literal.Value", "value": text})
                return
            for name, child in value.items():
                walk(child, f"{key}.{name}" if key else name, depth + 1)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{key}[{index}]", depth + 1)
    walk(node, prefix, 0)
    return result


def visual_context(item: dict) -> dict:
    visual = item.get("visual", {})
    roles = visual.get("query", {}).get("queryState", {})
    bindings = {
        name: [{"query_ref": projection.get("queryRef", ""), "field": projection.get("field", {}),
                "active": projection.get("active", True)} for projection in spec.get("projections", [])]
        for name, spec in roles.items()
    }
    return {"visual_id": item["name"], "visual_type": visual.get("visualType", ""),
            "position": item["position"], "field_bindings": bindings,
            "sort_definition": visual.get("query", {}).get("sortDefinition"),
            "configured_visual_properties": _literals(visual.get("objects", {}), "visual.objects"),
            "configured_container_properties": _literals(
                visual.get("visualContainerObjects", {}), "visual.visualContainerObjects"),
            "evidence_limits": {"pixel_readability": "requires a fresh rendered image",
                                "data_values": "requires an authorized semantic-model query",
                                "missing_property": "may be inherited from theme or Desktop defaults"}}


def report_context(report: Path) -> dict:
    """Read native PBIR page/visual inventory without asserting design approval."""
    report = Path(report)
    pages_root = report / "definition" / "pages"
    pages = []
    for page_id in load(pages_root / "pages.json")["pageOrder"]:
        page_dir = pages_root / page_id
        page = load(page_dir / "page.json")
        visuals = [visual_context(load(path)) for path in sorted(
            (page_dir / "visuals").glob("*/visual.json"))]
        pages.append({"id": page_id, "display_name": page["displayName"],
                      "canvas": [page["width"], page["height"]], "visuals": visuals})
    return {"schema": 1, "kind": "PBIR source metadata, not visual or data approval",
            "source_sha256": source_digest(report), "pages": pages}
