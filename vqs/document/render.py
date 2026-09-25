"""Word pagination spike harness (WP-04, issue #9): probe, never claim.

`word_spike_readiness` reports whether this host can attempt real pagination:
a headless backend on PATH and/or an interactive Word lease. DOC-06 applies
at the evidence layer: `check_backend_equivalence` fails any result whose
observed renderer differs from the declared backend, so LibreOffice output
can never be presented as Word-exact acceptance.
"""
from __future__ import annotations

from dataclasses import asdict

from vqs.adapters.ports import Capability, probe_executable, probe_file, readiness

WORD_PATHS = (
    r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
    r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
)


def _probe_word() -> Capability:
    found = probe_executable("interactive-word", "winword")
    if found.status == "available":
        return found
    for candidate in WORD_PATHS:
        probed = probe_file("interactive-word", candidate)
        if probed.status == "available":
            return probed
    return probe_file("interactive-word", WORD_PATHS[0])


def word_spike_readiness() -> dict:
    """Probe pagination-backend capability on this host.

    Either backend suffices: headless (reproducible automation) or
    interactive Word (exact pagination under an exclusive lease).
    """
    capabilities = [
        probe_executable("headless-pagination-backend", "soffice", "libreoffice"),
        _probe_word(),
    ]
    if any(cap.status == "available" for cap in capabilities):
        present = [cap.component for cap in capabilities if cap.status == "available"]
        return {"gate": "G1-word-spike", "verdict": "ready", "backends": present,
                "capabilities": [asdict(cap) for cap in capabilities]}
    return readiness("G1-word-spike", capabilities)


def check_backend_equivalence(declared_backend: str, observed_renderer: str) -> dict:
    """Fail when the observed renderer is not the declared pagination backend."""
    if not declared_backend or not observed_renderer:
        return {"verdict": "blocked", "reason": "Declared backend and observed renderer required"}
    if declared_backend != observed_renderer:
        return {"verdict": "fail",
                "reason": "Renderer mismatch: do not claim Word-exact acceptance",
                "declared": declared_backend, "observed": observed_renderer}
    return {"verdict": "pass", "backend": declared_backend}
