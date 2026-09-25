# WP-00 baseline — environment, tools, and fixture inventory

**Program:** [#4](https://github.com/analienx/visual-quality-system/issues/4).
**Work package:** WP-00, [issue #5](https://github.com/analienx/visual-quality-system/issues/5).
** kind:** baseline audit. **Status:** planned; this document records observations only.
No work package is marked verified by this baseline.

**Probed:** 2026-09-24. **Base:** `main` at `52ca11c` (plus untracked `tests/e2e/`).
**Host:** Windows 10.0.26200. **Python:** 3.12.10. **Node:** 24.19.0. **npm:** 11.17.0.
**git:** 2.55.0.windows.3. **pytest:** 8.4.2. **ruff:** 0.16.7.
**Repo tests at base:** 21 passed (`python -m pytest -q`), run from source checkout.

## Capability matrix

| Tool / capability | State | Evidence |
| --- | --- | --- |
| Pure-Python VQS core (`vqs inventory`, `request-review`, ledger validator) | available | 72/72 tests pass; `python scripts/roadmap_report.py --check` VALID; installed `vqs status` entry point verified |
| Packaged install (`pip install -e '.[test]'`) | available | 0.0.1a0 installs; installed `vqs status` entry point works incl. from outside the checkout (ledger logic moved to `vqs/ledger.py`; verified 2026-09-24) |
| Power BI Desktop binary | present (2.157.1354.0), automation unknown | `PBIDesktop.exe` verified 2026-09-24 under Program Files; Bridge CLI still absent, no instance running, open/save state unverified |
| Desktop Bridge CLI (`powerbi-desktop`) | available (1.0.0) | `@microsoft/powerbi-desktop-bridge-cli` installed globally 2026-09-24; `status/open/reload/screenshot` commands present |
| PBIR authoring/schema tooling, Fab Inspector, Draco 2 | blocked (missing) | none on PATH; first probed 2026-09-24 |
| Semantic-model query provider (DAX, refresh identity) | blocked (none authorized) | no provider configured; `cache.abf` must never enter the repo |
| Word automation backend (interactive Word) | present (16.0.20326.20158) | `WINWORD.EXE` verified 2026-09-24 after owner install; exact pagination runs need an exclusive lease per spike #9 |
| Headless pagination backend (LibreOffice `soffice`, PDF rasterizer) | blocked (missing) | `libreoffice`/`soffice` not on PATH |
| `python-docx` (OOXML inspection candidate) | blocked (OS policy) | Installed but unusable: Application Control blocks the `lxml` native DLL; stdlib `zipfile`+`xml` inspection stands instead |
| GitHub Actions CI for this repo | not configured | `.github/` holds templates only; no workflows directory |

Missing capability yields `blocked`, never a claim of availability
(acceptance negative of issue #5).

## Per-component baseline status

| Component | State |
| --- | --- |
| Portable PBIR inventory, policy observations, image integrity, axis/contrast/category primitives | extracted, unverified in this program |
| Ledger validator + STATUS snapshot + program e2e (`tests/e2e/`) | implemented, unverified (awaiting independent review + PR) |
| Desktop capture/data spike (#8), Word pagination spike (#9) | not run (blocked on backends/lease above) |
| Contracts (#6), runner/ledger (#7), all downstream stages | planned / not run |

## Fixture inventory and privacy

- No `fixtures/` directory exists yet; no customer report, cache (`cache.abf`),
  screenshot, credential, or Bearing [REDACTED] found in the public tree.
- Synthetic fixtures only: inline JSON + stdlib-generated PNGs under `tmp_path`
  in tests. Nothing binary or customer-derived is committed.
- Plan: two legally distributable synthetic PBIR examples plus a private-path
  plan for real reports and a sanitized DOCX fixture plan land with #6/#8/#9;
  real run evidence stays under ignored private `runs/` (see `.gitignore`).

## Risks and rollback

- Risk: Desktop binary present but automation path unknown — do not assume the
  preview/bridge commands exist; spike #8 must pin exact CLI capability first.
- Risk: single shared checkout — GUI spikes serialize on one exclusive host
  lease; pure source/rules work stays parallel-safe in separate worktrees.
- Rollback: this baseline touches only `docs/BASELINE.md`, `tests/test_baseline.py`
  on branch `work/wp00-baseline`. No `main` writes, no production report edits,
  no migration to undo. Delete the branch to roll back.

## Next action

Independent verifier reproduces `python -m pytest -q` and the capability probes
from the pinned commit, then #6 contracts freeze before parallel #7/#8/#9.
