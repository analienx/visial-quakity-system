"""Private run-evidence store: append-only events plus atomic manifests (WP-02).

Layout per run (under a private root that Git ignores)::

    <root>/<run-id>/events.jsonl    # appended JSON lines, fsynced per write
    <root>/<run-id>/manifest.json   # written atomically via tmp + os.replace

The store never executes, renders, or approves anything. A killed run simply
stops appending; reopening replays every event written before the kill, and an
attempt without a terminal event reads back as ``blocked``, never green.
Artifact claims use exclusive lock files: a second claimant is refused (it
must queue), so two agents can never own one artifact or Desktop PID.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

TERMINAL_EVENTS = frozenset({"completed", "failed", "blocked"})


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def create_run(root: Path, run_id: str, manifest: dict) -> Path:
    """Create a run directory with an atomic manifest; fail if it exists."""
    run_dir = Path(root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = dict(manifest)
    payload.setdefault("run_id", run_id)
    payload.setdefault("status", "active")
    _atomic_write(run_dir / "manifest.json", json.dumps(payload, indent=2))
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")
    return run_dir


def append_event(run_dir: Path, event: dict) -> None:
    """Append one JSON event line and fsync; raises if the run is unknown."""
    log = Path(run_dir) / "events.jsonl"
    if not log.is_file():
        raise FileNotFoundError(f"Unknown run directory: {run_dir}")
    with log.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def read_events(run_dir: Path) -> list[dict]:
    """Replay every event in order; corrupt lines raise instead of skipping."""
    events = []
    for line in (Path(run_dir) / "events.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Corrupt event line in {run_dir}")
            events.append(value)
    return events


def seal_run(run_dir: Path, status: str, artifacts: dict | None = None,
             environment: dict | None = None) -> dict:
    """Atomically seal a run manifest with terminal status and pinned evidence.

    Records ``status`` (completed/failed/blocked), artifact digests, backend
    versions, and the event count so the manifest never contradicts the log.
    """
    manifest_path = Path(run_dir) / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = status
    manifest["artifacts"] = dict(artifacts or {})
    manifest["environment"] = dict(environment or {})
    manifest["event_count"] = len(read_events(run_dir))
    _atomic_write(manifest_path, json.dumps(manifest, indent=2))
    return manifest


def run_status(run_dir: Path) -> str:
    """Terminal event kind, or ``blocked`` when the run never terminated."""
    kinds = [event.get("kind") for event in read_events(run_dir)]
    for kind in reversed(kinds):
        if kind in TERMINAL_EVENTS:
            return str(kind)
    return "blocked"


def claim_artifact(lock_dir: Path, artifact_id: str, owner: str) -> bool:
    """Claim exclusive ownership; False means another owner holds it (queue)."""
    Path(lock_dir).mkdir(parents=True, exist_ok=True)
    lock = Path(lock_dir) / (artifact_id + ".lock")
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps({"artifact": artifact_id, "owner": owner}))
    return True


def release_artifact(lock_dir: Path, artifact_id: str, owner: str) -> bool:
    """Release a claim; False when held by someone else or not held."""
    lock = Path(lock_dir) / (artifact_id + ".lock")
    try:
        record = json.loads(lock.read_text(encoding="utf-8"))
    except OSError:
        return False
    if record.get("owner") != owner:
        return False
    lock.unlink()
    return True


def digest_bytes(data: bytes) -> str:
    """SHA256 helper for pinning source/model/contract bytes."""
    return hashlib.sha256(data).hexdigest()
