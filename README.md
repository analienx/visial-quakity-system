# Visual Quality System (VQS)

**Design, repair and independently verify analytical experiences that answer the right questions.** VQS is a source-aware decision-quality system for Power BI Desktop reports **first**, rendered Word/DOCX documents **in the same initial delivery program**, and Fabric Apps/Rayfin **later**. It checks whether intended users can reach a defensible conclusion, whether data and visual design communicate it truthfully, and whether a source-level repair improves the *actual working artifact* without altering answers or hiding adjacent content. It is **not** a screenshot-to-AI taste prompt, a substitute for semantic-model validation, or a generic AI report creator.

> **Status: pre-alpha / partial extraction.** This repository currently contains a portable PBIR inventory, versioned observation policy, source/image integrity checks, a limited CLI and isolated quantitative rule primitives. The full Power BI Desktop review→repair loop, live data/refresh tests, comprehensive theme/palette engine, question/journey benchmarks and all-page Word pagination/repair acceptance **do not yet run end to end in this standalone package**. A one-report prototype remains in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12). Product goals and a planning issue are not evidence of implementation.

## Implementation program and honest status (start here)

**[Detailed staged implementation plan](docs/IMPLEMENTATION_PROGRAM.md)** · **[per-component status ledger](roadmap/STATUS.md)** · **[machine-readable dependency and verification ledger](roadmap/work_packages.json)** · **[agent/issue/PR reporting protocol](docs/LEDGER_AND_AGENT_PROTOCOL.md)** · **[falsifiable acceptance matrix](docs/ACCEPTANCE_MATRIX.md)** · **[program issue #4](https://github.com/analienx/visual-quality-system/issues/4)** · **[AGENTS.md](AGENTS.md)**.

First runnable work is [WP-00 / issue #5](https://github.com/analienx/visual-quality-system/issues/5): independently verify the baseline, available tools and fixtures. Freeze shared contracts; run a **real Desktop capture/data spike and genuine Word pagination spike in parallel**; then build semantic/style facts, measured design rules, independent visual review, typed isolated source repair, minimal question oracles and cross-surface end-to-end acceptance. A bounded set of implementation issues [#5–#18](https://github.com/analienx/visual-quality-system/issues/4) tracks owners, dependencies and exit evidence. Fabric Apps is explicitly deferred to [#18](https://github.com/analienx/visual-quality-system/issues/18), not an initial release blocker. As of this planning snapshot **0/13 initial-release work packages are newly independently verified**; existing extracted code and the older prototype require fresh assessment.

## What makes VQS different?

AI can increasingly generate reports and apps. VQS's durable responsibility is an executable **decision-quality contract**: `persona → decision → analytical question → scoped expected evidence → page/visual/document section and interaction → actual data/answer → perceived communication → action`. A user-provided task or brand profile takes precedence. Otherwise, propose only evidence-supported candidates from the model: **what** happened; **compared with what**; **when**; **where/who/which**; **how** (composition or decomposition); **why might it have happened** (hypotheses, not asserted causes); **so what** (materiality); **how sure**; **who/what is missing**; **what if** (eligible scenario); **what might happen next** (validated forecast); and **what should be investigated or done next**. If dates, targets, definitions, permissions or prediction history are absent, do not invent them to fill a template.

**P0 is pragmatic:** review an existing Power BI report, diagnose specific visual/semantic defects, improve palette, typography, spacing, labeling or a supported chart configuration in a disposable PBIP, and independently verify actual Desktop output and unchanged data/task answers. In parallel, assess a real generated DOCX through OOXML **and every rendered page**, checking report figure and narrative revision consistency; apply only safe, testable document repairs. New Power BI visuals use validated templates only after the analytical purpose and field bindings are confirmed. Human approval controls promotion to the original project.

## Scope, evidence and current implementation

| Dimension | Intended evidence and outcome | Standalone state |
| --- | --- | --- |
| Visual design and safe repair | Effective colors/theme/overrides, palette roles, accessible contrast, fonts, hierarchy, whitespace, bounds, axes, label/category fit, table completeness and user-viewing size; source-bound real PBIR repair and fresh independent Desktop regression | Inventory/isolated axis/contrast/category-space primitives extracted; whole-report loop unverified |
| Semantic/model truth | PBIR/TMDL facts, actual scoped DAX query and filters/RLS, loaded data, first-open vs fresh refresh, stable measure definitions and units | Source digest only; no standalone live data/refresh acceptance |
| Question/decision coverage | User stories or conditional defaults, question-to-page/visual/interaction mapping, comparable baselines, uncertainty, alternative explanations and expected answers | Specified, not operational |
| User journey and AI-answer testing | Overview→exception→comparison→investigation→action/return, supported interaction replay and answer consistency at identical population/filters | Planned; unavailable interactions must be declared unsupported |
| Independent perceptual review | Correctly calibrated full page and chart crops, current source/data/design profile; capable image reviewer reports located observable symptoms and overall visual coherence | Review policy/image integrity extracted; full reviewer/Bridge adapter remains in prototype |
| Word/DOCX quality | OOXML styles/relationships/figures plus backend-pinned actual pagination of every page and current report image/narrative lineage | Policy/evidence shared; real independent Word backend and all-page repair not verified |
| Safe source changes and evidence | Typed allowlisted edits in disposable candidate, diff+rollback, source/data/render hashes, independent reviewer not the editor, fail/blocked kept distinct | Limited prototype; no standalone general repair engine |
| Fabric Apps/Rayfin | Same question/design/evidence contract with separate React/TypeScript/Playwright and staged Fabric environment | Deferred until initial PBI+Word release and separate approval |

A screenshot is evidence of what rendered, **not the sole design evaluator**. PBIR/semantic data and quantified design rules provide verifiable causes; a multimodal reviewer is useful for visual hierarchy, overall palette cohesion, legibility and storytelling when actual appearance matters. A successful JSON parse or model-generated approval cannot override a blank data model, stale figure, mis-scoped answer, clipped table, missing Word page or untested interaction.

## How it would run

The target runtime is one local Python coordinator with typed versioned contracts, reproducible run/evidence storage and optional tool adapters. A Windows worker uses installed Microsoft Power BI Desktop Bridge, validated PBIR tooling and authorized semantic-model queries. A separate document worker uses OOXML inspection and a **declared** pagination backend (e.g. isolated LibreOffice/PDF rasterization, with independently assessed Word compatibility). The planner proposes narrow typed source edits; the executor writes only to an isolated worktree/DOCX copy; an independent verifier checks real output and test oracles. No mandatory cloud-model upload, server-side Word COM automation, public-repo self-hosted runner on a private workstation, or production/Fabric deployment. See [execution architecture](docs/EXECUTION_ARCHITECTURE.md), [technical architecture](docs/ARCHITECTURE.md), and [implementation program](docs/IMPLEMENTATION_PROGRAM.md).

## Existing pre-alpha commands

```bash
python -m pip install -e '.[test]'
vqs inventory /path/to/Example.Report
python -m pytest
```

`vqs inventory` emits PBIR page/visual IDs, layout/bindings, explicitly stored properties and source SHA. `vqs request-review REPORT RENDERS --fixer-id EXECUTOR` checks a source-bound capture manifest and emits an **unapproved** observation template; it does not capture, repair or certify a report. The proposed `vqs run`, `vqs improve`, `vqs status` and independent Word renderer CLI are **not implemented** in this pre-alpha. Refer to the ledger for the implementation phase and do not cite these examples as a successful current E2E run.

## Integrate existing tools; own the quality decision

Use optional pinned [Fab Inspector](https://github.com/NatVanG/fab-inspector) findings for supported PBIR governance, [Microsoft PBIR authoring and schema tooling](https://github.com/microsoft/skills-for-fabric) and [Desktop Bridge](https://www.npmjs.com/package/@microsoft/powerbi-desktop-bridge-cli) for actual Power BI artifacts, an authorized separate model-query provider for DAX facts, and optionally a tested [Draco 2](https://github.com/cmudig/draco2) bridge for representable chart-design constraints. None supplies the complete decision/question/visual/Word evidence contract or is permitted to silently approve its own fix. See [integration strategy](docs/INTEGRATION_STRATEGY.md), [research](docs/RESEARCH.md), [default stories](docs/DEFAULT_STORIES_AND_AUTOMATED_DESIGN.md) and [product/design contract](docs/PRODUCT_AND_DESIGN_CONTRACT.md).

## Reuse, security and migration

VQS is a standalone Apache-2.0 package with [source extraction attribution](NOTICE). PBIPDocumenter becomes a pinned consumer **only after** two unrelated PBIPs and a real paginated generated DOCX pass independently verified end-to-end acceptance; the old draft PR remains intact until owner approval. Never move customer/Contoso cached data, real report images, credentials, local Desktop PID/config or third-party binaries into this public repository. The default run is local/private and source changes are candidate-only; external model transmission and publishing require explicit authorization. See [security and agent protocol](docs/LEDGER_AND_AGENT_PROTOCOL.md).