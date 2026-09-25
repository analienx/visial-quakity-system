"""Adapter ports: capability probes shared by Desktop and document workers.

A probe reports what is installed and reachable; it never runs a capture,
query, or render. Missing capability yields ``blocked`` with the exact
missing piece, never a claim of availability.
"""
from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Capability:
    """One probed capability: available, unavailable, or unknown, with reason."""

    component: str
    status: str
    reason: str = ""
    versions: dict[str, str] = field(default_factory=dict)


def probe_executable(component: str, *names: str) -> Capability:
    """Look for a CLI on PATH; unavailable names the missing tool."""
    for name in names:
        found = shutil.which(name)
        if found:
            return Capability(component, "available", f"found {name} at {found}")
    return Capability(component, "unavailable", f"none of {', '.join(names)} on PATH")


def probe_file(component: str, path: str) -> Capability:
    """Check a well-known install path exists; unavailable otherwise."""
    if Path(path).exists():
        return Capability(component, "available", f"present at {path}")
    return Capability(component, "unavailable", f"absent at {path}")


def readiness(gate: str, capabilities: list[Capability]) -> dict:
    """Overall spike verdict: ``ready`` only when every probe is available."""
    missing = [cap.component for cap in capabilities if cap.status != "available"]
    if missing:
        return {"gate": gate, "verdict": "blocked", "missing": missing,
                "capabilities": [asdict(cap) for cap in capabilities]}
    return {"gate": gate, "verdict": "ready",
            "capabilities": [asdict(cap) for cap in capabilities]}
