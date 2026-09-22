"""Measured rules must fail on actual violations, not guessed inputs."""
from vqs.design_rules import axis_display_distinctness, category_axis_space, text_contrast


def test_repeated_percent_labels_do_not_pass() -> None:
    finding = axis_display_distinctness([0.096, 0.104], ["10%", "10%"])
    assert finding["status"] == "fail" and finding["evidence"]["collisions"]
    assert axis_display_distinctness([0.096, 0.104], ["9.6%", "10.4%"])["status"] == "pass"
    assert axis_display_distinctness(None, ["10%", "10%"])["status"] == "unknown"
    assert axis_display_distinctness([0.1, 0.2], None)["status"] == "unknown"


def test_contrast_is_measured_not_inferred() -> None:
    assert text_contrast("#000000", "#FFFFFF")["status"] == "pass"
    assert text_contrast("#888888", "#FFFFFF")["status"] == "fail"
    assert text_contrast("#777777", None)["status"] == "unknown"
    assert text_contrast("rgba(0,0,0,0.5)", "#FFFFFF")["status"] == "unknown"
    assert text_contrast("#777777", "#FFFFFF", large_text=True)["status"] == "pass"


def test_label_density_uses_actual_dimensions() -> None:
    assert category_axis_space([70, 70, 70], 300)["status"] == "pass"
    assert category_axis_space([70, 70, 70], 150)["status"] == "fail"
    assert category_axis_space(None, 300)["status"] == "unknown"
    assert category_axis_space([70, 70], None)["status"] == "unknown"
