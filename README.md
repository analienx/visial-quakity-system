# Visual Quality System (VQS)

**Design, repair and independently verify analytical experiences that answer the right questions.** VQS is a source-aware quality system for Power BI reports (first) and generated analytical documents (later). It checks whether the intended users can reach a useful, defensible conclusion—not merely whether a page renders, complies with PBIR schema, or looks attractive in an AI screenshot review. It proposes and, for supported transformations, applies changes to a disposable *real Power BI report*, then proves the result using current model/data, actual Desktop rendering and task-specific regression checks.

> **Status: pre-alpha / partial extraction.** This repository currently contains a portable PBIR inventory, observation policy, source/image evidence checks, a limited CLI and isolated quantitative design-rule primitives. **It does not yet run** the complete user-story engine, live data/refresh verification, effective-palette analyzer, user-journey test, AI-answer comparison, automated whole-report repair or paginated Word review. A more integrated single-report prototype remains in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12); it has not passed an unattended, unrelated-project acceptance test. The capabilities and roadmap below are product requirements, not claims of shipping functionality.

## Why VQS exists

AI can increasingly generate charts and report pages. The harder question is **whether the analytical product is appropriate, truthful, usable and still correct after it changes**. VQS owns an executable *decision-quality contract* shared by dashboard users, report creators, AI authoring tools and independent reviewers. Its primary initial workflow is **review an existing Power BI report → diagnose defects → safely redesign actual PBIR visuals and styling → reopen and independently validate the result**. Generating missing visuals and whole pages follows only when their analytical question and bindings are verified.

An evaluation starts with `persona → decision → question → expected evidence/answer → page, visual and interaction path → model query/filter scope → rendered communication → action`. User stories or a design profile supplied by the owner take precedence. Otherwise VQS proposes **conditional defaults from verified available data**, not fabricated business semantics: **what** happened; **compared with what**; **when**; **where/who/which**; **how** (contribution, decomposition, process); **why might it have happened** (tested alternatives, not assumed causation); **so what** (materiality); **how sure are we**; **what is missing**; **what if** (eligible scenario); **what might happen next** (validated forecast); and **what should be investigated or done next**. A missing date, benchmark, business definition, causal design or suitable prediction history results in `not applicable`, `unknown` or a question—not a speculative chart.

## What VQS evaluates

| Dimension | Evidence and expected result | Standalone status |
| --- | --- | --- |
| **Visual design and repair — P0** | Effective theme and overrides, palette harmony/semantic color consistency, distinguishable series, contrast, typography, hierarchy, gutters, whitespace, alignment, chart suitability, axes/labels, table occupancy and readability at target viewport; implement supported PBIR/theme edits and verify fresh Desktop output | PBIR inventory and isolated axis/contrast/label primitives extracted; integrated review and constrained repair remain in prototype |
| **Question and decision coverage — P1** | Persona/task contract; default evidence-supported story candidates; question-to-measure/visual/interaction traceability; missing, redundant or misleading answers; appropriate baselines, units, materiality, uncertainty and alternatives | Specified, not implemented |
| **Data and semantic truth** | Measure lineage and definitions, actual scoped query results, filter and RLS context, refresh/first-open health, population/period comparability, omissions and forecast validation | Portable source digest only; live validation pending |
| **User journey and AI-answer tests — P2** | Overview → exception → comparison → investigation → evidence → action/return; slicer/drillthrough state; task correctness and observable usability; compare dashboard and available AI answers under equivalent scope | Specified, not implemented |
| **Rendered and interpretive review** | Exact-source page and chart renders; detect clipping, scrollbars, blank data and perceptual/overall composition defects; independent, opt-in vision review grounded in PBIR and actual data | Hash/PNG and review policy extracted; Desktop/reviewer adapters in prototype |
| **Safe repair and regression** | Versioned finding → evidence-backed source plan → allowlisted isolated edit → model/PBIR revalidation → fresh whole-page render and task regression → pass/fail/blocked with rollback | Limited prototype only; not a general autonomous report designer |
| **Domain packs and change monitoring — P3** | Domain-specific questions, metrics, exceptions and forecasting eligibility; invalidate approved conclusions when data/model/report versions change | Planned |
| **Documents and other analytical surfaces** | OOXML plus rendered pagination, embedded-figure lineage and alignment with the report's question/answer contract | Shared policy only in this repo; full Word workflow pending |

**Design is not a single aesthetic score.** Measured violations and unsupported/misleading encodings are deterministic findings; a capable independent multimodal reviewer examines whole-page cohesion, visual emphasis, narrative flow and subjective fit to the declared design profile. The reviewer reports *visible symptoms*, not imaginary root causes. Missing data, unresolved disagreements and unverified changes cannot become a pass. A pixel image is necessary evidence of what users see, not the sole source of truth.

## Practical Power BI editing scope

VQS should use validated PBIR/theming operations to restyle or rearrange supported visuals, adjust safe formatting, change tested chart types without silently changing the business question, and add visuals from version-pinned templates **only after validating field roles and story intent**. The execution layer may use Microsoft report-authoring tooling, Desktop Bridge, semantic-model tools and independent editor models; it must not assume every native visual, forecast, AI visual, filter interaction or Desktop API is programmatically supported. Complex visuals and predictions require feature-specific round-trip tests. Edits are made to disposable project copies, with source diffs, semantic-impact checks and an approval/promotion boundary.

## How existing tools fit

**VQS is the coordinator and evaluator, not a fork of every upstream tool.** Optional version-pinned adapters consume Fab Inspector governance findings, Microsoft PBIR/schema/authoring and semantic tooling, Desktop Bridge captures, and supported Draco 2 chart-design constraints. VQS itself owns user/decision contracts, neutral evidence IDs, purpose-driven design and palette rules, cross-tool adjudication, safe repair specifications, task regression and release evidence. A text-only model may plan repairs from verified data; **only an image-capable reviewer can evaluate actual pixels**. No provider receives report images or business data without explicit configuration and authorization. See [architecture](docs/ARCHITECTURE.md), [integration strategy](docs/INTEGRATION_STRATEGY.md) and [ecosystem research](docs/RESEARCH.md).

## Current executable surface

```bash
python -m pip install -e '.[test]'
vqs inventory /path/to/Example.Report
python -m pytest
```

`inventory` returns PBIR visual IDs/types, geometry, bindings, explicitly stored formatting and source SHA-256; **it does not certify appearance, loaded data or analytical quality**. `vqs request-review REPORT RENDERS --fixer-id EXECUTOR` validates provided source-bound PNG evidence and emits an *unapproved* review request; it neither captures images nor repairs the report independently. No end-to-end standalone acceptance or independent second-project test is claimed.

## Delivery roadmap and release contract

**P0 — working Power BI design repair:** complete effective-theme/palette/style facts and measured visual design rules, port verified Desktop capture and image reviewer, apply safe PBIR changes, then pass a real before/after task and full-page regression on two unrelated reports. **P1 — decision contracts:** generate evidence-supported story/questions, establish metric semantics, baselines, materiality, uncertainty and missing-question coverage. **P2 — journey and AI-answer tests:** validate interactions, scope-equivalent responses and task success, with representative-user testing where human usability is asserted. **P3 — domain packs and ongoing monitoring:** conditional industry questions, predictive eligibility and change-triggered revalidation. Unknown/blocked is never green; a model cannot approve its own edit.

PBIPDocumenter will be a pinned VQS consumer, not a permanently duplicated implementation. Keep [its draft PR](https://github.com/analienx/pbidocumenter/pull/12) intact until this package has independently matched its useful capabilities. Do not commit Contoso ABF data, private screenshots, credentials, local calibration, third-party binaries or other users' datasets. License: [Apache-2.0 with extraction attribution](NOTICE). Track initial migration in [issue #1](https://github.com/analienx/visual-quality-system/issues/1) and auto-design in [issue #2](https://github.com/analienx/visual-quality-system/issues/2).
