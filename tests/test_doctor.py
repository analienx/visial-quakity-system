"""Doctor tests: shape-only; presence values depend on the machine."""
import json

from vqs.cli import main as vqs_main
from vqs.doctor import report


def test_report_shape() -> None:
    data = report()
    assert data["status"] == "ok"
    checks = data["checks"]
    assert set(checks) == {"pbir", "desktop_bridge", "modeling_mcp",
                           "desktop_process", "adomd"}
    for name in ("pbir", "desktop_bridge", "modeling_mcp"):
        assert checks[name]["status"] in ("present", "missing")
    assert checks["adomd"]["required_by_vqs"] is False


def test_doctor_command_exits_zero(capsys) -> None:
    assert vqs_main(["doctor"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "ok"
