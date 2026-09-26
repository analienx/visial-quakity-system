# VQS command reference (pre-alpha)

Install once (editable): `pip install -e .` — this exposes the `vqs`
entry point. Every command below was executed against synthetic fixtures
during development; see `tests/test_pipeline.py` and
`tests/test_validate_commands.py` for runnable shapes.

Exit codes: `0` pass, `1` demonstrated violation, `2` blocked
(environment, capability, or input prevents a verdict). Nothing here
renders pixels, queries live data, executes a repair, or approves a
release — those need leased backends plus owner promotion.

## vqs status

Read-only delivery-ledger snapshot; never modifies the ledger.

```console
vqs status
vqs status --format json --ledger roadmap/work_packages.json
```

## vqs inventory

Read a PBIR enhanced-format `*.Report` folder: pages, visuals, field
bindings, source hash. Read-only; not design approval.

```console
vqs inventory path/to/Example.Report
```

## vqs request-review

Build a review template from a report plus a renders directory.
`capture-manifest.json` must carry three keys: `source_sha256` equal to
the report digest (stale sources block), `page_images` mapping every
PBIR page id to a unique PNG filename, and `files` mapping every PNG
to its sha256 (unbound renders block). PNGs must be at least 450px on
each side.

```console
vqs request-review path/to/Example.Report path/to/renders --fixer-id agent-a
```

Minimal `capture-manifest.json`:

```json
{
  "source_sha256": "<digest from vqs inventory>",
  "page_images": {"p1": "p1.png"},
  "files": {"p1.png": "<sha256 of p1.png>"}
}
```

## vqs check

Run a measured-facts JSON document to a sealed verdict under
`.vqs-runs/<run-id>/` (gitignored): `manifest.json` carries the terminal
status plus a `verdict_sha256` digest, with `event_count` matching the
event log. Facts sections: `rules` (the six design rules),
`oracles` (question answerability, scope matching), `documents` (DOCX
well-formedness — structure only, never pagination), `models` (TMDL
inventory, binding resolution, optional freshness and RLS role).
Unknowns block; malformed entries block; duplicate `--run-id` is refused.

```console
vqs check facts.json
vqs check facts.json --run-root .vqs-runs --run-id check-01
```

Minimal passing `facts.json`:

```json
{
  "rules": {
    "typography.text_contrast": {"foreground": "#000000", "background": "#ffffff"}
  },
  "oracles": [{"oracle_scope": "a", "run_scope": "a"}]
}
```

## vqs validate-plan

Validate a repair plan *before* any execution. Any allowlist issue fails:
unknown or shell operations, unapproved model/DAX/RLS touches, writes
outside the disposable candidate root or to the original, dropped visual
ids, missing rollback.

```console
vqs validate-plan plan.json --original /orig/report --candidate-root /cand
vqs validate-plan plan.json --original /orig/report --candidate-root /cand --approve-change CHG-7
```

## vqs adjudicate-bundle

Adjudicate a review bundle on static checks only: reviewer separation,
image-capability presence, full-canvas calibration, per-page source
binding (stale images fail), observation completeness. Pixel judgment
itself needs a capable image reviewer plus real renders.

```console
vqs adjudicate-bundle bundle.json
vqs adjudicate-bundle bundle.json --run-id review-01
```
