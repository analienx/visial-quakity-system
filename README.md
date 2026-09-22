# Visual Quality System (VQS)

**Source-aware design-quality analysis for Power BI dashboards and generated documents.** VQS is intended to determine *why* a visual is hard to read or analytically misleading, produce a verifiable source-level repair, and check that the rendered result improves. It is **not** a screenshot-to-LLM taste prompt, a Power BI custom visual, or a substitute for validating the data model.

> **Status: extraction / pre-alpha.** This repository is a new, independently maintained home for VQS. The proven Power BI/Word prototype is still in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12) (prototype commit `99ae076`); do not infer that every capability described below already works here. No production-ready package, CI-quality release, unattended full-report remediation, or independent second-project validation is claimed. The target repository name retains its original spelling, `visial-quakity-system`.

## What will be evaluated?

The central artifact is a **source-linked design finding**, not an overall AI quality score. Every applicable rule has an ID, measured or observed evidence, affected page/visual, reason, confidence/limits, proposed repair, and a verification requirement. A missing input is `unknown` or `blocked`, never an implicit pass.

| Layer | Evidence | Example decisions | Status |
| --- | --- | --- | --- |
| Report definition | PBIR page and visual JSON, theme, formatting, geometry, IDs and field bindings | Bounds, margin/gutter consistency, grouping, explicit title/axis settings | Prototype in PBIPDocumenter; extraction in progress |
| Semantic model and actual data | TMDL, partition/refresh state, authorized read-only DAX queries, category cardinality and numeric ranges | Meaningful axis precision; excessive categories; degenerate scatter data; percent vs percentage-point misuse | Model context in prototype; comprehensive quantitative design rules **not implemented** |
| Deterministic design rules | Configurable constraints on joined definition/data evidence and chart intent | Repeated formatted ticks, label-space budget, encoding/task compatibility, contrast, table utilization | Geometry-only prototype; broader rule engine **planned** |
| Rendered behavior | Real Power BI Desktop output, page and chart images bound to exact source digest | True clipping, scrollbars, visible tick labels, blank KPIs, legibility at target size | Desktop Bridge and crop prototype tested in PBIPDocumenter; independent port pending |
| Independent visual interpretation | Opt-in vision model receives whole page, focused crop, source facts and testable observations | Hierarchy, composition, storytelling; propose candidate explanations, not unchecked root causes | Opt-in Pi/Cline reviewer tested on Contoso; inconsistent findings still require adjudication |
| Repair and regression | Allowlisted PBIR edits in an isolated candidate, tool validation, reload, recapture, repeat | Eliminate a duplicate-axis defect without hiding a category or shortening the action table | Constrained scatter→bar and geometry prototype; whole-report unattended loop **not proven** |
| Generated documents | OOXML styles/structure plus *all* paginated rendered Word pages | Minimum font sizes, figure fidelity, page breaks, table splits and report/document consistency | Structural prototype; end-to-end rendered repair **not proven** |

An image is final *rendered evidence*, not the sole design evaluator. Structural correctness also cannot approve poor visuals; the release gate requires successful data/refresh, source evidence, deterministic checks and supported independent review together.

## Intended use

1. Import a PBIP/PBIR report and its semantic-model reference; construct an explicit visual inventory and design-intent contract.
2. Run offline PBIR validation and independent configurable design rules; optionally query a **specified and authorized** local/remote semantic model for ranges, cardinalities and measure semantics.
3. Open a disposable copy in Power BI Desktop on Windows; select the exact instance by PID, require saved state, render all pages and validate the entire canvas and source hashes.
4. Evaluate deterministic findings first; send the page/crop plus structured evidence to an **explicitly configured image-capable** reviewer for remaining interpretive judgments. Never upload sensitive data or images without permission.
5. Have a separate planner diagnose findings against PBIR and real data. Apply narrowly allowlisted changes only to an isolated candidate; validate/reopen/rerender the **whole affected page** and check for new failures.
6. Continue within an explicit iteration budget; return `pass`, `fail` or `blocked` with durable evidence. Never convert timeout, model disagreement, absent data, missing review or stale screenshot into a pass.
7. Apply the analogous process to a generated DOCX using document structure and paginated render evidence.

**Example planned finding (illustrative, not a current computed result):** `axis.display_values_not_distinct` identifies two different underlying ticks that both format as `10%`, links to the exact PBIR visual and measure, proposes a precision or chart-encoding change, and requires a fresh Desktop render proving the labels are distinguishable.

## Design and reuse decisions

We will **not fork another tool wholesale**. [Fab Inspector](https://github.com/NatVanG/fab-inspector) already provides extensive PBIR/JSONLogic policy checks; VQS should consume its machine-readable findings via an optional adapter instead of rebuilding its existing governance rules. [Draco 2](https://github.com/cmudig/draco2) offers formal visualization constraints; a Power BI-to-neutral-chart-spec bridge can reuse its concepts or engine without claiming native PBIR support. Microsoft's [Power BI report authoring tools](https://github.com/microsoft/skills-for-fabric) and [Desktop Bridge CLI](https://www.npmjs.com/package/@microsoft/powerbi-desktop-bridge-cli) provide metadata validation and real Desktop capture; semantic-model tools are separate. Detailed trade-offs, links and license caveats are in [research](docs/RESEARCH.md) and [architecture](docs/ARCHITECTURE.md).

## Repository boundaries and migration

VQS owns the **portable engine, evidence schemas, quality rules, adapters, and safe remediation loop**. PBIPDocumenter remains a consumer that supplies its report and generated Word document and receives structured findings and release decisions. Do not move its application, Contoso-specific PBIP/ABF cache, generated screenshots, source data, tokens, profile paths, local PID/calibration, or unrelated tests here. Preserve its draft PR while extracted interfaces are independently tested; do not delete the prototype until the new package has equivalent test coverage and a migration release.

The original prototype is [here](https://github.com/analienx/pbidocumenter/tree/99ae076/pbip_documenter/visual_quality); its 109-test repository run and single-page repair trial applied to the *original project*, not to this new repo. See [migration and milestones](docs/ARCHITECTURE.md#extraction-plan-and-acceptance) for the exact work remaining.

## License and dependencies

The original PBIPDocumenter project is Apache-2.0. Respect its copyright and attribution when extracting source. Fab Inspector and Draco 2 are MIT-licensed, but **their code has not been copied into VQS**. Microsoft's modeling MCP has an MIT repository license and also publishes preview EULA terms: confirm the terms for a chosen distribution/runtime before bundling. Third-party CLI executables, models, credentials and licenses are **not vendored**.
