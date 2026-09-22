"""Measured, pure design rules. Never fabricate unavailable rendered/data values.

Input facts must come from a separately verified data/render/format adapter.
These are narrow building blocks, not an overall dashboard-design verdict.
"""
from __future__ import annotations

import math
from collections.abc import Sequence


def _finding(rule: str, status: str, **evidence: object) -> dict:
    if status not in {"pass", "fail", "unknown"}:
        raise ValueError("Invalid rule status")
    return {"rule_id": rule, "status": status, "evidence": evidence}


def axis_display_distinctness(
    numeric_ticks: Sequence[float] | None, displayed_labels: Sequence[str] | None,
) -> dict:
    """Detect distinct numeric tick positions with identical *actually rendered* labels."""
    rule = "axis.display_values_not_distinct"
    if numeric_ticks is None or displayed_labels is None:
        return _finding(rule, "unknown", reason="Numerical tick values and rendered labels must both be measured")
    if len(numeric_ticks) != len(displayed_labels) or len(numeric_ticks) < 2:
        return _finding(rule, "unknown", reason="Insufficient paired tick observations")
    if (any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in numeric_ticks) or
            any(not isinstance(s, str) or not s.strip() for s in displayed_labels)):
        return _finding(rule, "unknown", reason="Invalid or missing tick observations")
    collisions = []
    for i, (number, label) in enumerate(zip(numeric_ticks, displayed_labels, strict=True)):
        for j in range(i):
            if numeric_ticks[j] != number and displayed_labels[j].strip() == label.strip():
                collisions.append({"indices": [j, i], "numeric_ticks": [numeric_ticks[j], number],
                                   "displayed_label": label})
    return _finding(rule, "fail" if collisions else "pass",
                    tick_count=len(numeric_ticks), collisions=collisions)


def _srgb_luminance(hex_color: str) -> float:
    if not isinstance(hex_color, str) or len(hex_color) != 7 or hex_color[0] != "#":
        raise ValueError("Expected opaque #RRGGBB color")
    try:
        rgb = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    except ValueError as exc:
        raise ValueError("Expected opaque #RRGGBB color") from exc
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in rgb]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))


def text_contrast(foreground: str | None, background: str | None, *, large_text: bool = False) -> dict:
    """Compare two fully resolved opaque colors to WCAG 2.2 SC 1.4.3 thresholds.

    Passing this local calculation does not establish broader WCAG compliance.
    """
    rule = "typography.text_contrast"
    if foreground is None or background is None:
        return _finding(rule, "unknown", reason="Resolved colors are not both available")
    try:
        lighter, darker = sorted((_srgb_luminance(foreground), _srgb_luminance(background)), reverse=True)
    except ValueError:
        return _finding(rule, "unknown", reason="Unresolved, invalid or translucent color")
    ratio = (lighter + 0.05) / (darker + 0.05)
    threshold = 3.0 if large_text else 4.5
    return _finding(rule, "pass" if ratio >= threshold else "fail",
                    ratio=round(ratio, 3), required_ratio=threshold,
                    foreground=foreground, background=background, large_text=large_text)


def category_axis_space(label_widths_px: Sequence[float] | None,
                        available_width_px: float | None, *, gap_px: float = 8) -> dict:
    """A conservative label-space budget for a *specified* horizontal category axis.

    The caller must measure label widths at actual effective font and report zoom.
    Rotation, responsive layout or skipped ticks require a separate adapter.
    """
    rule = "axis.category_label_space"
    if label_widths_px is None or available_width_px is None or not label_widths_px:
        return _finding(rule, "unknown", reason="Measured label widths and plot width required")
    widths = list(label_widths_px)
    values = [*widths, available_width_px, gap_px]
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        return _finding(rule, "unknown", reason="Invalid layout measurements")
    if any(width <= 0 for width in widths) or available_width_px <= 0 or gap_px < 0:
        return _finding(rule, "unknown", reason="Invalid plot or label geometry")
    required = sum(widths) + gap_px * (len(widths) - 1)
    return _finding(rule, "pass" if required <= available_width_px else "fail",
                    labels=len(widths), required_px=round(required, 2), available_px=available_width_px,
                    assumptions="All labels visible, horizontal, nonoverlapping, measured at target zoom")
