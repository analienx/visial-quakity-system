"""OOXML structure inspection (WP-08 static half, issue #13).

Stdlib only (`zipfile` + `xml`). Reports part inventory — paragraphs,
headings, tables, style ids, relationships, embedded-image hashes — and
structural issues (missing required parts, unresolvable rel targets).

DOC-01 boundary, stated plainly: a structure-only pass is NOT pagination
acceptance. Orphaned headings, split tables, and page geometry need a real
paginated render in the declared backend (spike #9); this module only proves
the package is well-formed and its references resolve.
"""
from __future__ import annotations

import hashlib
import posixpath
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
RELS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

REQUIRED_PARTS = ("[Content_Types].xml", "word/document.xml")


def _parse(xml_bytes: bytes) -> ET.Element | None:
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None


def inspect_docx(path: Path) -> dict:
    """Inventory a DOCX package; corrupt content yields issues, never raises."""
    path = Path(path)
    try:
        archive = zipfile.ZipFile(path)
        names = set(archive.namelist())
    except (zipfile.BadZipFile, OSError) as exc:
        if not path.is_file():
            raise
        return {"inventory": {}, "issues": [{"rule": "invalid_package",
                                             "detail": f"{type(exc).__name__}"}]}
    with archive:
        issues: list[dict] = []
        for required in REQUIRED_PARTS:
            if required not in names:
                issues.append({"rule": "missing_required_part", "part": required})
        if issues:
            return {"inventory": {"parts": sorted(names)}, "issues": issues}
        document = _parse(archive.read("word/document.xml"))
        if document is None:
            return {"inventory": {"parts": sorted(names)},
                    "issues": [{"rule": "unparseable_document"}]}
        paragraphs = document.findall(f".//{W}p")
        headings = [p for p in paragraphs
                    if p.find(f"{W}pPr/{W}pStyle") is not None
                    and str(p.find(f"{W}pPr/{W}pStyle").get(f"{W}val", "")).startswith("Heading")]
        tables = document.findall(f".//{W}tbl")
        embeds = [blip.get(f"{R}embed") for blip in document.findall(f".//{A}blip")
                  if blip.get(f"{R}embed")]
        rels_name = "word/_rels/document.xml.rels"
        targets: dict[str, str] = {}
        if rels_name in names:
            rels = _parse(archive.read(rels_name))
            if rels is None:
                issues.append({"rule": "unparseable_relationships"})
            else:
                for rel in rels.findall(f"{RELS}Relationship"):
                    rid, target = rel.get("Id"), rel.get("Target")
                    if rid and target:
                        resolved = posixpath.normpath(posixpath.join("word", target))
                        targets[rid] = resolved
        images: list[dict] = []
        for rid in embeds:
            target = targets.get(rid)
            if target is None or target not in names:
                issues.append({"rule": "broken_relationship", "id": rid, "target": target})
                continue
            digest = hashlib.sha256(archive.read(target)).hexdigest()
            images.append({"id": rid, "part": target, "sha256": digest})
        styles: list[str] = []
        if "word/styles.xml" in names:
            root = _parse(archive.read("word/styles.xml"))
            if root is not None:
                styles = sorted({s.get(f"{W}styleId", "") for s in root.findall(f"{W}style")})
        inventory = {"parts": sorted(names), "paragraphs": len(paragraphs),
                     "headings": len(headings), "tables": len(tables),
                     "style_ids": styles, "images": images}
        return {"inventory": inventory, "issues": issues}
