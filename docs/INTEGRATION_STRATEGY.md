# Integration strategy: one product, multiple specialized engines

**Status:** proposed adapters and ordering, not evidence that Fab Inspector, Draco 2, SemanticOps or Desktop Bridge are running from the standalone VQS package. See [product/design contract](PRODUCT_AND_DESIGN_CONTRACT.md), [architecture](ARCHITECTURE.md), [ecosystem research](RESEARCH.md) and [README](../README.md).

## Decision

VQS **is** the integration and judgment layer, but it must own the quality model, user-story/question graph, visual-design system, evidence reconciliation, safe repair and release gate. External engines are optional, version-pinned **capability providers**. Do not fork a mature governance engine merely to rebrand its rules; likewise, do not outsource overall quality to a tool that cannot know the user's decision, actual model data or rendered result. “Inspired by” means implement our own distinct design/journey rules where existing tools lack an interface; “integrate” means execute a supported upstream tool, normalize its output and retain original provenance. Do not copy third-party source without reviewing its license, NOTICE, version and API compatibility.

## Ownership and execution map

| Stage / question | Upstream or source | VQS-owned logic | Integration mode and current state |
| --- | --- | --- | --- |
| What is the required user journey and analytical question? | User-supplied persona, scenario, requirements, acceptance questions and design tokens | Requirement schema, question coverage, visual-to-story trace, default/filtered navigation tests, gap detection | **Build first**; no upstream tool can infer stakeholder intent from PBIR alone. Planned. |
| Is PBIR syntactically/structurally valid? | Microsoft published report schemas, supported PBIR Toolkit / authoring CLI | Capability checks, normalized source references and failure propagation | Optional validator subprocess, pinned build. Adapter pending. |
| Does it meet existing Power BI governance rules? | [Fab Inspector](https://github.com/NatVanG/fab-inspector) | Normalize its rule IDs/severity/evidence, de-duplicate against native checks, maintain policy exceptions | Optional subprocess/JSON adapter after verifying executable output/version. **Do not vendor or assume all proposed rule families exist upstream.** Pending. |
| Are the measures/filters/data ready and suitable for the question? | TMDL/PBIR plus read-only SemanticOps/modeling client and scoped DAX queries | Semantic fact graph, query/data provenance, cardinality, actual ranges, units, intent-to-encoding rules | Authorized opt-in connector; no arbitrary remote model probing. Pending in standalone package. |
| Is chart encoding appropriate? | Neutral chart/task facts; optionally [Draco 2](https://github.com/cmudig/draco2) | Power BI role mapping, task/semantic constraints, alternative chart candidate validation | Start with **inspiration and independent fixture-tested rules**. Add optional Draco bridge only for representable neutral specs; Power BI-only behaviors remain `unsupported`, not silently translated. Pending. |
| Is the visual language coherent? | PBIR/theme/base-theme/overrides/conditional formatting, viewport, rendered page | Effective token resolution, palette and semantic-color consistency, contrast, typography, spatial rhythm and page hierarchy | **VQS-owned design-system analyzer**; rendered checks supplement measurements. Planned beyond contrast primitive. |
| What did Power BI actually display? | Microsoft Desktop Bridge exact instance/path and native page capture | Saved-state/source/digest verification, entire-canvas calibration, crop-to-visual mapping, data-ready check | Optional Windows adapter, port from PBIPDocumenter prototype. Never mistake Bridge for a per-visual formatting/model API. |
| Does the result feel purposeful, readable and navigable? | Configurable image-capable reviewer; whole page plus focused crops + source facts + persona/questions | Versioned observed-defect contract, reviewer disagreement adjudication, avoid unsupported causal/root-cause claims | Optional opt-in cloud/local provider. **No screenshot-only quality verdict**. Port pending. |
| Can we fix it safely? | Constrained PBIR edits, theme changes, user-approved story/semantic changes | Source-bound plan, allowlist, isolation, invariants, rollback, whole-page and whole-journey regression | Build and port prototype recipes; substantial chart/measure changes require verified intent/data. Pending. |
| Is generated Word output equally usable? | OOXML and paginated DOCX rendering | Style/figure/page integrity, document narrative and trace to report question IDs | Independent document adapter sharing VQS core; full loop pending. |

## Concrete orchestration

`load user journey + design profile → import PBIR/theme/TMDL → validate schemas & existing governance → build question/visual/data fact graph → run measured design checks → query model only for required unknown data facts → capture verified, populated default and specified interaction states → run independent interpretive review → reconcile conflicting findings → produce question-aware repair plan → isolate, patch, validate, rerender, replay journey → approve / fail / blocked`.

A tool returns **facts or findings with its tool name, version, rule ID, source hash, page/visual locator, applicability and data/viewport context**. VQS decides whether a finding is verified, contradicted, a risk, or untestable. The same issue may originate in multiple engines; de-duplicate by source object and substantive defect, retain all supporting or conflicting evidence, and never count “two models said so” as proof of a data/causal claim. A missing optional adapter yields `not_run` for its declared coverage; a required adapter's absence blocks the corresponding acceptance gate rather than producing a synthetic pass.

## Design-system evaluation is a first-class engine

The visual identity contract contains brand and dashboard-profile tokens: background, surfaces, primary/secondary text, neutral/grid, categorical series, sequential/diverging scale, highlight/selected, positive/negative/alert/target, title/body/axis fonts, spacing scale, gutters, borders, interaction states, output viewport and device. Compare the **resolved** formatting for all page objects, not raw theme JSON alone; Power BI base/custom themes, per-visual overrides and conditional formatting may differ. When resolution is unsupported, check visible pixels where possible and record remaining effective-style uncertainty.

Rules include semantic color stability across pages; no accidental same-color/different-meaning collision; categorical distinguishability without hue alone; palette moderation relative to data/task (not a fixed universal color count); background/foreground and essential graphical contrast; accent use proportional to information importance; coherent hierarchy; consistent alignment/padding and intentional whitespace; logical page-to-page visual rhythm. An independent design reviewer evaluates non-quantifiable coherence and overall feeling **against the user's chosen style profile and intended audience**: enterprise-operational, executive-editorial, exploratory-analytical or a provided brand design. It reports concrete discordances, not a universal “beautiful/ugly” score. Design preference cannot override data correctness or required question coverage.

## Journey and question coverage is a first-class engine

Start from explicit user requirements. Every mandatory `what / when / where-or-who / how / why-or-next` question gets evidence targets and an answerability check. Coverage is many-to-many: one visualization can serve several questions, and one question may need a summary → detail route. VQS should test the actual navigation state machine (landing → recognition → compare → investigate → action/return) and context propagation through slicers, cross-highlights, bookmarks, drillthrough and export. For `why`, require adequate design and provenance; where only correlations are shown, report *candidate drivers / open hypotheses* rather than verified causes.

Run the question and story checks **before** proposing chart replacements. A bar chart cannot be accepted as a fix for a scatterplot if the user story requires exploring a genuine relationship, unless a user or owner approves the changed analytical intent. If requirements are absent, offer an exploratory profile, identify uncovered question families as recommendations, and report `requirements_missing`—do not invent a validated persona or fail all exploratory reports for lacking a standard five-question sequence.

## Build sequence and acceptance

1. Define and validate story, question and token profiles; implement an offline checker detecting missing mappings, contradictory units and inconsistent theme tokens on fixtures. Keep CI deterministic.
2. Port and verify PBIR schema/geometry; add a Fab Inspector adapter with real upstream output and contract tests. Compare overlap with native rules; do not copy its full ruleset.
3. Implement format resolution, semantic-data query provenance and data-aware chart/palette rules using independently checked fixtures.
4. Connect exact-instance Desktop rendering and focused visual crops; check default **and** user-story interaction states, not only a single screenshot.
5. Add interpretive model review and safe isolated repair, replay question coverage and rendered/page/data regressions. Benchmark against two unrelated PBIP projects and the generated Word document.
6. Publish capability and acceptance matrices: what ran, what did not, what failed, and why. No unconditional “quality approved” label from passing a structural check or a model-generated checklist.

## Sources

[Microsoft dashboard design](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips) · [Microsoft report requirements](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-migration-requirements) · [Microsoft themes and formatting](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes) · [Microsoft report drillthrough](https://learn.microsoft.com/en-us/power-bi/guidance/report-drillthrough) · [Tableau visual best practices](https://help.tableau.com/current/blueprint/en-us/bp_visual_best_practices.htm) · [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [Fab Inspector](https://github.com/NatVanG/fab-inspector) · [Draco 2](https://github.com/cmudig/draco2).
