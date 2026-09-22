# Visual Quality System (VQS)

**A source-aware design-quality checker and repair framework for Power BI dashboards and generated documents.** VQS is being built to determine *why* a visual is hard to interpret, correlate rendered defects with report configuration and real data, produce constrained source changes and demonstrate measurable improvement. It is **not** another screenshot-to-AI taste prompt.

> **Status: pre-alpha, partial extraction.** A standalone Python package with policy, PBIR visual inventory, source hashes, PNG/review integrity checks and a few measured design-rule primitives now lives here. The full Desktop-render → multi-model review → safe repair loop remains in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12) (source prototype `99ae076`) and has **not** yet been ported or verified end to end here. Do not treat this repository as a production-ready visual-quality gate. The repository URL retains its original spelling, `visial-quakity-system`.

## What does VQS evaluate?

A VQS finding is identified by a versioned rule, the exact page and visual, the underlying source revision, *measured* evidence, the observable symptom, hypotheses versus verified causes, repair options and required regression checks. Missing model data or unmeasured effective formatting must be `unknown`/`blocked`, never guessed from pixels.

| Layer | Purpose | Current status |
| --- | --- | --- |
| **Report definition** | Inspect PBIR visual types, positions, field bindings, sorting and explicit formatting; resolve effective theme and report design intent | **Portable read-only inventory extracted**; theme resolution and full geometry rules pending |
| **Data-aware design** | Assess distinct tick labels, category/label-space budgets, chart suitability, actual model cardinality, units and filter context | **Pure axis-distinctness, opaque-text contrast and measured category-space primitives present**; no live model-query integration or whole-report rule engine yet |
| **Rendered reality** | Certify complete, source-bound Power BI page images and chart crops; detect actual clipping, scrollbars and blank visuals | Portable PNG/hash checks extracted; Windows Desktop Bridge and calibrated crop remain in prototype |
| **Independent interpretive review** | Evaluate hierarchy, composition and business storytelling using whole-page/crop images plus source facts; adjudicate unsupported claims | Versioned **25 Power BI / 23 Word observation contract** extracted; Pi/model adapters remain in prototype |
| **Safe remediation** | Trace findings to exact PBIR/DAX/Word source, apply allowlisted edits in isolation and rerender entire affected pages to catch regressions | Source-bound scatter→ranked-bar and fit recipes tested in prototype; not ported or approved for general autonomous use |
| **Word output** | Inspect OOXML and actual paginated DOCX rendering, tables, figures, typography and cross-output consistency | Policy/evidence shared; renderer, document checks and repair loop remain in prototype |

A screenshot is **necessary rendered evidence**, not a substitute for semantic analysis. Valid PBIR is not visual approval. A model opinion cannot override a failed quantitative test or a data-refresh blocker.

## What is executable here today?

The pre-alpha CLI reads a PBIR project without Power BI Desktop, external accounts or downloading a vision model:

```bash
python -m pip install -e '.[test]'
vqs inventory /path/to/Example.Report
python -m pytest
```

`vqs inventory` outputs page/visual IDs, types, geometry, query roles, sort information, explicitly stored formatting and a report-plus-model **source SHA-256**. It does **not** resolve default theme formatting, query measures or decide that a dashboard looks good. The pure rules in `vqs.design_rules` accept independently verified tick values/labels, resolved opaque colors or measured label widths; they return `pass`, `fail` or `unknown` for that *individual rule*.

A second command, `vqs request-review REPORT RENDERS --fixer-id EXECUTOR`, accepts a capture manifest with `source_sha256`, `files` (PNG filename → SHA-256), and an explicit `page_images` mapping (PBIR page ID → PNG filename). It requires **every** PBIR page to map uniquely to a verified current image and outputs an *unapproved* observation template. It cannot create images or approve a report. Render/repair/model adapters must be separately integrated and tested. The status and test code are in [the implementation and acceptance plan](docs/ARCHITECTURE.md#extraction-plan-and-acceptance).

## Intended end-to-end flow (not yet operational in this repo)

1. Load and validate PBIR, effective theme and associated semantic-model facts; obtain authorized, scope-bound read-only DAX values where needed.
2. Apply testable design rules for axis precision/density, task/encoding suitability, color semantics and contrast, typography, spacing, alignment, table utilization and narrative hierarchy. Preserve `unknown` for missing evidence.
3. Open a disposable PBIP in Desktop, require the exact PID/path and saved state, capture all pages through the Bridge and independently verify full-canvas calibration and loaded data.
4. Let an independent vision reviewer inspect actual images with structured facts; require locations and source-grounded diagnoses rather than accepting unsupported aesthetic suggestions.
5. Generate bounded repair plans, validate/execute only safe source operations in an isolated candidate, reload/rerender and check both the original defect and newly introduced page-level problems.
6. Repeat within a recorded iteration budget. Return `pass`, `fail` or `blocked` with reproducible evidence, never a silent AI approval. Apply analogous checks to every paginated Word document page.

## Why a new repository rather than a fork?

[Fab Inspector](https://github.com/NatVanG/fab-inspector) already supplies extensive configurable PBIR/Fabric governance checks and JSON/CI output, while [Draco 2](https://github.com/cmudig/draco2) supplies formal chart-design constraints. We will **integrate** those as optional, version-pinned engines rather than copy their code or make an unrelated governance tool our primary architecture. Microsoft's [report-authoring tools](https://github.com/microsoft/skills-for-fabric) and [Desktop Bridge CLI](https://www.npmjs.com/package/@microsoft/powerbi-desktop-bridge-cli) supply metadata validation and real renders, not an overall design evaluator. See the evidence-backed [ecosystem research](docs/RESEARCH.md) and [architecture](docs/ARCHITECTURE.md), including limitations, licenses, security and acceptance tests.

## Ownership and migration

VQS owns reusable rules, evidence, interfaces, adapters and the repair loop. PBIPDocumenter will consume VQS as a pinned package/CLI and supply the report plus generated Word document. Its existing PR stays **draft and intact** until the independent package passes equivalent and second-project tests. This repository intentionally excludes Contoso sample data, ABF cache, screenshots, personal machine paths, Desktop PIDs, cloud credentials and third-party binaries. Extracted code retains [Apache-2.0 licensing and attribution](NOTICE); optional upstream dependencies remain under their own terms. The current source is **not** a fork of Fab Inspector or Draco 2.
