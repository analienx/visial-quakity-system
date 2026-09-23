# Default analytical stories and automated Power BI design

**Status:** product specification and staged implementation plan, not an implemented autonomous generator. Applies when a user provides no explicit stories; user-supplied intent and safety constraints take precedence. VQS is initially a **review-and-improve** system for existing PBIR reports and may also propose/generate new visuals in an isolated candidate. A story is a hypothesis about a useful question, not evidence that the data can answer it.

## 1. Derive useful default stories from the data, not from a fixed page template

Create a versioned semantic inventory: facts and measures, units, aggregation/additivity, time roles and grain, geography and hierarchies, entities, segment dimensions, targets/budgets, outcome variables, explanatory candidates, filters/security, freshness and provenance. Infer domain from field names, descriptions, measures and data distributions with **confidence and evidence**; ambiguous domains/metrics stay unknown and require user confirmation. Never publish a fabricated KPI, causal conclusion, target or prediction.

Generate a ranked *coverage backlog* by broadly reusable analytical question families when the required data exists. Rank by the user's stated task and data feasibility, **not** by an unconditional quota of visuals. All questions support a persona, an intended decision, a measure/dimension/filter specification, minimum data requirements, expected answer artifact, a navigation path and a test showing the report actually answers the question. Defaults are editable, and not-applicable questions are recorded with a reason.

| Family | Example question | Conditions and candidate Power BI experiences |
| --- | --- | --- |
| **What / status** | What happened? How much, how many, vs target/baseline? | Credible outcome measure; KPI/card with stated period, denominator and comparison; avoid invented targets. |
| **When / trend** | When did it change? What are trend, seasonality and outliers? | Date role and sufficient grain; line/small multiples with honest aggregation, comparisons and continuous axis where eligible. |
| **Where / distribution** | Which regions, locations, channels, cohorts or products account for it? | Meaningful segmentation or geography; ranked comparisons, maps only for valid location fields, purposeful drillthrough. |
| **Who / segment** | Which customers, teams, users or groups are affected? | Appropriate entity dimension and permitted visibility; segmentation without exposing sensitive rows. |
| **How / composition and process** | How is the outcome composed? How does a funnel or process change? | Additive parts or valid stages; decomposition, contribution bars, waterfall with reconciled totals, funnel only for ordered comparable stages. |
| **Why / drivers and hypotheses** | Which observed factors are associated with the outcome? What explanations need testing? | Candidate variables, sufficient data and model checks; decomposition tree, key influencers or explicit statistical analysis. Label associations as such, never assert causal explanations from correlation. |
| **Exceptions / action** | What is unexpectedly high/low, at risk, or needs attention? | Valid baseline, rules and operational threshold; variance, ranked exceptions, drill-to-evidence and owner/action context when available. |
| **What next / forecast** | What might happen if observed trends persist? | Sufficient clean time series, clear horizon, supported visual/configuration and backtest; forecast with uncertainty, actual-vs-forecast and explicit assumptions. Do not force a forecast from a handful of points or irregular/multiseries data. |
| **What if / scenario** | How might a controllable input change the outcome? | An explicit, validated relationship and assumptions; what-if parameters or a modeled sensitivity view. Do not present scenario output as a prediction. |

Use a **domain pack** only after generic coverage and data capability detection: retail (sales, units, margin, discount, returns, stock, budget), finance (actual/budget, cash flow, aging), operations (throughput, bottlenecks, SLA, defects), HR (headcount, attrition and cohorts with privacy checks), support (volume, response time, backlog), energy (generation, demand, export, efficiency). Each pack declares required fields/measures, units, time grain, known denominators, domain-safe comparisons, expected actions and explicit non-goals. Reuse the same question families rather than hardcoding five identical pages per domain.

## 2. Power BI's native analytical features are candidates, not unconditional defaults

- **Decomposition tree:** requires an analyzable measure/aggregate plus one or more meaningful `Explain by` dimensions; can support interactive high/low AI splits. Provide a clear starting measure, data-relevant dimensions and a return path. It explores contributors, not causal proof.
- **Key influencers:** evaluate model/storage compatibility, sample-size/feature limits and statistical interpretability before recommending or generating it; label reported influencers as associations. If unsupported, choose a transparent alternative rather than injecting a broken visual.
- **Forecast and anomaly detection:** require the supported line-chart configuration (single series, continuous X axis) and a suitable time series. Validate sampling, seasonality, forecast horizon, uncertainty and holdout error; otherwise mark `not_applicable` or `blocked` and retain a descriptive trend.
- **Drillthrough, report-page tooltips, bookmarks, field parameters, hierarchies and cross-filtering:** propose only where they advance an actual question-to-detail user journey. Test their context, navigation and return behavior. Avoid turning every report into an interaction-heavy demo.
- **Waterfall, variance, decomposition and Top N:** reconcile contributions and totals, preserve the denominator, state whether an `Other` group is shown, and avoid hiding critical exceptions through reduction.

A feature can have valid JSON yet still be misleading or unusable. Power BI's versioned visual schemas and real Desktop rendering are acceptance evidence. Some feature configurations will need validated authoring templates or explicit Desktop-host actions; unsupported configurations must not be represented as implemented.

## 3. Visual-language and user-journey contract

Define a *default but overridable* design profile: target form factor and minimum readable size; typography scale; spacing rhythm; compact/comfortable density; background/surface/text, categorical, sequential, diverging, status and focus palettes; permitted brand colors; color semantics; contrast targets; legend and axis rules; table style; motion/interaction rules. Resolve Power BI theme plus per-visual overrides before checking effective appearance. Evaluate both measurable contrasts/spacing and rendered perceptual cohesion; no single model taste score can override hard failures.

Each proposed or existing visual maps to a `story_id` and one of `overview → detect exception → compare → decompose/investigate → evidence/detail → action/return`. Score **coverage separately from visual quality**: a beautiful unrelated chart fails story alignment, while a relevant but unreadable chart fails visual design. Prefer one readable chart that answers the question over filling every canvas cell. Personalize no unrequested political or sensitive inferences.

## 4. Three actionable modes and practical feasibility

**A. Review (first milestone):** inspect existing PBIR, theme and semantic facts; map visuals to questions and journeys; run deterministic rules and render verification; provide exact visual-ID findings and suggested source changes. Entirely offline when input/data permit; missing data or unrendered effects stay `unknown`.

**B. Improve (first practical write mode):** make an isolated working copy; apply validated theme/palette, format/label, padding/alignment, sorting, category reduction, layout and supported visual-type transformations. Never change the business question, aggregation, units or data security merely to improve appearance. Validate PBIR schemas, reload in Desktop, check values and recapture every affected page. Require fresh independent review and compare newly introduced defects; preserve rollback.

**C. Generate (template-constrained write mode):** use a verified visual-template registry by PBIR schema version and chart family. From approved story + semantic roles + measured data + design profile, instantiate native visuals and optional new pages, calculated measures and drillthrough only when bindings/semantics are proven. Reserve stable IDs, prevent collisions, validate all dependencies and Desktop render/interactions. Generation starts from vetted examples; no claim of arbitrary native/custom visual or AI feature support. A request for a correlation chart cannot silently turn into a ranking chart. Advanced visuals (decomposition, influencers, forecast) need their **own validated authoring and round-trip fixtures** before automated creation is enabled.

Pipeline: `PBIP/PBIR + semantic model → capability/intent discovery → default story candidates and feasibility → existing-story coverage map → measurable design findings → proposal (before/after and semantic-impact report) → isolated PBIR/TMDL changes → static validation → Desktop reload + fresh populated render → data and interaction checks → independent high-resolution visual review → repeat or block → user-approved promotion`. A planned feature is not an implemented feature; no unconditional 'always improve until green' loop when model, renderer or user intent is unknown.

## 5. Implementation order and tests

1. Implement read-only capability graph and editable default story proposal with traceability; test ambiguous metric names, missing date/geography, nonadditive percentages, targets, partial data and privacy.
2. Implement effective theme resolver, color-semantic consistency/contrast and a validated layout/axis rule kernel; use visual crops for perceptual exceptions.
3. Implement **review existing report → safe styling/layout repair → Desktop rerender → regression** end-to-end on two unrelated PBIR projects. This is the priority before automated page generation.
4. Add versioned PBIR visual templates: cards, ranked bars, line trends, matrix/detail, waterfall, supported tooltips/drillthrough, with field-role contracts and visual-data tests. Then add scenario/AI-native features one by one behind capability checks.
5. Publish domain packs and prediction eligibility/backtesting fixtures, plus a user-journey simulator with expected slicer/drillthrough/filter states. Test both Word output and mobile/desktop viewports where supported.

**Present status:** none of the default story proposer, complete visual generator, semantic query adapter or unattended all-page repair gate is yet operational in this standalone repository. Current portable code provides policy, PBIR inventory, evidence primitives and narrow measured-rule helpers; the earlier partial repair/capture prototype remains in PBIPDocumenter draft PR #12.

## References

- Microsoft, [enhanced report format (PBIR)](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format) — programmatic, schema-validated report edits.
- Microsoft, [line charts](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-line-chart) — continuous single-series analytics feature requirements.
- Microsoft, [decomposition tree](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-decomposition-tree) and [key influencers](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-influencers) — native explanation tools and limitations.
- Microsoft, [drillthrough report design](https://learn.microsoft.com/en-us/power-bi/guidance/report-drillthrough) and [report design tips](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tips-and-tricks-for-creating-reports) — question-driven navigation and visual hierarchy.
