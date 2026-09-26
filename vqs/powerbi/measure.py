"""PBIR/TMDL facts emitter (WP-19): read-only measurement, no renders.

`measure_report` walks a ``*.Report`` folder (plus an optional
``*.SemanticModel`` definition dir) and returns a facts document shaped
for `vqs check`: text contrast, palette assignments, metric units, TMDL
bindings, and format-declaration cohorts. Anything the sources cannot
prove is omitted — never inferred, never defaulted.
"""
from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter
from typing import Any


def _read_json(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _walk(node: Any, path: str = "") -> Any:
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, f"{path}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, f"{path}[{index}]")
    else:
        yield path, node


def _theme(report_dir: str) -> dict | None:
    candidates = sorted(glob.glob(os.path.join(
        report_dir, "StaticResources", "RegisteredResources", "*.json")))
    for path in candidates:
        theme = _read_json(path)
        if theme and isinstance(theme.get("background"), str):
            return theme
    return None


def _pages(report_dir: str) -> list[dict]:
    found = []
    for path in sorted(glob.glob(os.path.join(
            report_dir, "definition", "pages", "*", "page.json"))):
        page = _read_json(path)
        if page is not None:
            page["_dir"] = os.path.basename(os.path.dirname(path))
            found.append(page)
    return found


def _visuals(report_dir: str, page_dir: str) -> list[dict]:
    found = []
    pattern = os.path.join(report_dir, "definition", "pages", page_dir,
                           "visuals", "*", "visual.json")
    for path in sorted(glob.glob(pattern)):
        visual = _read_json(path)
        if visual is not None:
            visual["_id"] = os.path.basename(os.path.dirname(path))
            found.append(visual)
    return found


def _page_background(page: dict, theme: dict | None) -> str | None:
    try:
        color = (page["objects"]["outspace"][0]["properties"]["color"]
                 ["solid"]["color"]["expr"]["Literal"]["Value"])
    except (KeyError, IndexError, TypeError):
        color = None
    if isinstance(color, str) and re.fullmatch(r"'#[0-9A-Fa-f]{6}'", color):
        return color.strip("'").upper()
    if theme is not None:
        return str(theme["background"]).upper()
    return None


def _text_run_colors(report_dir: str) -> Counter:
    colors: Counter = Counter()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            paragraphs = node.get("paragraphs")
            if isinstance(paragraphs, list):
                for index, para in enumerate(paragraphs):
                    runs = para.get("textRuns") if isinstance(para, dict) else None
                    for run in runs or []:
                        color = (run.get("textStyle") or {}).get("color")
                        if isinstance(color, str):
                            colors[(index, color.upper())] += 1
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    for page in _pages(report_dir):
        for visual in _visuals(report_dir, page["_dir"]):
            visit(visual.get("visual", {}).get("objects", {}))
    return colors


def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in rgb]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def _ratio(foreground: str, background: str) -> float:
    first, second = sorted((_luminance(foreground), _luminance(background)),
                           reverse=True)
    return (first + 0.05) / (second + 0.05)


def _contrast(report_dir: str, theme: dict | None) -> dict | None:
    colors = _text_run_colors(report_dir)
    titles = Counter({c: n for (i, c), n in colors.items() if i == 0})
    subtitles = Counter({c: n for (i, c), n in colors.items() if i == 1})
    if not titles and not subtitles:
        return None
    candidates = []
    for page in _pages(report_dir):
        background = _page_background(page, theme)
        if background is None:
            continue
        if titles:
            candidates.append((titles.most_common(1)[0][0], background))
        if subtitles:
            candidates.append((subtitles.most_common(1)[0][0], background))
    if not candidates:
        return None
    foreground, background = min(candidates, key=lambda pair: _ratio(*pair))
    return {"foreground": foreground, "background": background}


def _palette(theme: dict | None, pages: list[dict]) -> list[dict] | None:
    if theme is None or not isinstance(theme.get("dataColors"), list):
        return None
    assignments = []
    for page in pages:
        for index, color in enumerate(theme["dataColors"]):
            assignments.append({"state": f"series-index-{index}",
                                "color": str(color).upper(),
                                "page": page["_dir"]})
    return assignments or None


def _measure_formats(model_dir: str) -> dict[tuple[str, str], str]:
    formats: dict[tuple[str, str], str] = {}
    pattern = os.path.join(model_dir, "**", "*.tmdl")
    for path in sorted(glob.glob(pattern, recursive=True)):
        try:
            with open(path, encoding="utf-8-sig") as handle:
                text = handle.read()
        except OSError:
            continue
        table = re.search(r"^table '(.+)'$", text, re.MULTILINE)
        if table is None:
            table = re.search(r"^table (\S+)$", text, re.MULTILINE)
        if table is None:
            continue
        name = table.group(1)
        blocks = re.finditer(r"^\tmeasure ('([^']+)'|([^\s=]+)) =(.*?)(?=^\t\S|\Z)",
                             text, re.MULTILINE | re.DOTALL)
        for match in blocks:
            measure = match.group(2) or match.group(3)
            found = re.search(r"formatString: (.*)$", match.group(4), re.MULTILINE)
            formats[(name, measure)] = found.group(1).strip() if found else ""
    return formats


def _unit_of(format_string: str) -> str:
    if "%" in format_string:
        return "percent"
    if format_string.startswith("$"):
        return "USD"
    if "#,0" in format_string or format_string == "0":
        return "count"
    if "pp" in format_string:
        return "pp"
    return "raw:" + format_string


def _literal(raw: Any) -> Any:
    if not isinstance(raw, str):
        return raw
    text = raw.strip()
    if len(text) >= 2 and text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    match = re.fullmatch(r"(-?\d+(?:\.\d+)?)D", text)
    if match:
        number = float(match.group(1))
        return int(number) if number.is_integer() else number
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        number = float(text)
        return int(number) if number.is_integer() else number
    if text == "true":
        return True
    if text == "false":
        return False
    return text


def _bindings_and_cohorts(report_dir: str) -> tuple[list[dict], list[dict], list[dict]]:
    bindings: dict[str, dict] = {}
    units: list[dict] = []
    cohorts: dict[str, dict[str, Any]] = {}
    for page in _pages(report_dir):
        for visual in _visuals(report_dir, page["_dir"]):
            node = visual.get("visual", {})
            visual_type = node.get("visualType", "?")
            state = node.get("query", {}).get("queryState", {})
            for role, content in state.items() if isinstance(state, dict) else []:
                for projection in (content or {}).get("projections", []):
                    ref = projection.get("query_ref") or projection.get("queryRef")
                    if isinstance(ref, str) and ref and ref not in bindings:
                        bindings[ref] = {"query_ref": ref, "measure": None}
                    field = projection.get("field", {}).get("Measure", {})
                    entity = (field.get("Expression", {}).get("SourceRef", {})
                              or {}).get("Entity", "")
                    prop = field.get("Property", "")
                    if entity and prop:
                        units.append({"measure": f"{entity}.{prop}",
                                      "page": page["_dir"]})
            objects = node.get("objects", {})
            for path, value in _walk(objects):
                segments = [s.split("[")[0] for s in path.split("/") if s]
                if "Value" not in segments:
                    continue
                size = [s for s in segments if re.fullmatch(r"(fontSize|textSize)", s)]
                if not size:
                    continue
                if not segments:
                    continue
                owner = segments[0]
                cohort = f"{visual_type}/{owner}.{size[0]}"
                slot = cohorts.setdefault(cohort, {})
                slot[f'{page["_dir"]}/{visual["_id"]}'] = _literal(value)
    readings: list[dict] = []
    for cohort in sorted(cohorts):
        for key in sorted(cohorts[cohort]):
            page_id, visual_id = key.split("/", 1)
            readings.append({"cohort": cohort, "visual": visual_id,
                             "page": page_id, "value": cohorts[cohort][key]})
    return list(bindings.values()), units, readings


def _cohort_nulls(report_dir: str, readings: list[dict]) -> list[dict]:
    """Add explicit nulls for cohort members that leave a property default."""
    names = sorted({reading["cohort"] for reading in readings})
    nulls = []
    members: dict[str, list[tuple[str, str]]] = {}
    for page in _pages(report_dir):
        for visual in _visuals(report_dir, page["_dir"]):
            visual_type = visual.get("visual", {}).get("visualType", "?")
            members.setdefault(visual_type, []).append((page["_dir"], visual["_id"]))
    seen = {(r["cohort"], r["page"], r["visual"]) for r in readings}
    for cohort in names:
        visual_type = cohort.split("/", 1)[0]
        for page_id, visual_id in members.get(visual_type, []):
            if (cohort, page_id, visual_id) not in seen:
                nulls.append({"cohort": cohort, "visual": visual_id,
                              "page": page_id, "value": None})
    return sorted(readings + nulls,
                  key=lambda item: (item["cohort"], item["page"], item["visual"]))


def measure_report(report_dir: str, model_dir: str | None = None) -> dict:
    """Measure check-ready facts for a PBIR report (plus optional model).

    Returns a facts document for `vqs check`. Rules the sources cannot
    prove are omitted. Raises OSError when the report folder is unreadable.
    """
    if not os.path.isdir(report_dir):
        raise OSError(f"report folder not found: {report_dir}")
    theme = _theme(report_dir)
    pages = _pages(report_dir)
    rules: dict[str, dict] = {}
    # Contrast and palette are theme rules: without a theme the color
    # roles cannot be proven, so both stay omitted.
    contrast = _contrast(report_dir, theme) if theme is not None else None
    if contrast is not None:
        rules["typography.text_contrast"] = contrast
    palette = _palette(theme, pages)
    if palette is not None:
        rules["palette.semantic_consistency"] = {"assignments": palette}
    bindings, unit_refs, cohort_readings = _bindings_and_cohorts(report_dir)
    cohorts = _cohort_nulls(report_dir, cohort_readings)
    if cohorts:
        rules["typography.format_declaration_consistency"] = {"readings": cohorts}
    facts: dict[str, Any] = {"rules": rules}
    if model_dir is not None:
        formats = _measure_formats(model_dir)
        readings = [{"measure": ref["measure"],
                     "unit": _unit_of(formats.get(tuple(ref["measure"].split(".", 1)), "")),
                     "page": ref["page"]} for ref in unit_refs]
        if readings:
            facts["rules"]["encoding.metric_unit_consistency"] = {"readings": readings}
        ordered = sorted(bindings, key=lambda item: item["query_ref"])
        facts["models"] = [{"model_dir": model_dir,
                            "bindings": [{"query_ref": b["query_ref"]}
                                         for b in ordered]}]
    return facts
