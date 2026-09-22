# Product and design contract

**Status: proposed requirements and acceptance design, not implemented functionality.** This document defines what VQS must evaluate before it can claim to be an analytical-dashboard design gate. The current package supplies PBIR inventory, evidence validation, and a few isolated quantitative primitives; it does **not** yet establish user-journey coverage, resolve effective Power BI styling, query model data, or certify overall design quality. See [README](../README.md) and [architecture](ARCHITECTURE.md).

## Product purpose

VQS asks **whether a person can use an artifact to understand a business situation and make the intended decision**, not only whether the pixels are attractive or PBIR is valid. It unifies user stories, actual data, chart/task semantics, visual language, navigation, accessibility, and source-bound rendered evidence. Its outputs are itemized findings, coverage gaps, supported improvement proposals, and regression evidence—not a single ungrounded aesthetic score. A report can look polished and still fail because the audience cannot answer its required questions; a semantically correct report can fail because its information is illegible or visually incoherent.

The core quality contract has four independent gates: (1) **purpose and journey**: the intended audience, decisions and scenarios are evidenced; (2) **analytical correctness and coverage**: required questions are answerable from credible model data with the correct time, population, filters and units; (3) **visual communication and accessibility**: the chosen encodings, theme, hierarchy and page-level composition make the answers discoverable and readable; (4) **operational behavior**: navigation, interactions, refresh and rendered output work in realistic initial and filtered states. `pass` requires all applicable mandatory gates; `unknown` or missing requirements cannot silently become `pass`.

## Required input: a user-journey contract

For each persona, capture the role, domain vocabulary, decisions they actually control, usage context/device, frequency, data freshness needs and success criteria. Record user stories as *As [role], when [trigger], I need to answer [question] within [time/context], so I can [decision/action]*. Specify the initial landing view, recognition of an exception, comparison, investigation, supporting detail, return/navigation, and next action. The user defines intent; VQS can suggest missing questions but must not invent strategic goals or treat model-generated intent as confirmed.

Map each story to at least one required **question ID**, report page/visual or documented interaction, metric definition, relevant dimension, expected granularity, filter/time/population context, accepted evidence and action. A single overview page need not cover every analytical question: overview → focused page → drillthrough/detail is an acceptable journey when the user can discover, follow and return from it. Each important visual must contribute to a required question, a legitimate supporting context, or a deliberate exploration path; decorative chart variety alone is not a purpose.

### The five question families

These are *question families*, **not five compulsory charts on every page**. A report must explicitly declare which are required for each persona and why any family does not apply.

| Family | User's question | Typical evidence and checks |
| --- | --- | --- |
| **What** | What happened / what is the current state / how large is the deviation? | KPI and target/baseline, unit, period, relevant comparison and materiality; do not show an isolated number without context where the task requires context. |
| **When** | When did it start, change or recur? | Time series at appropriate grain, ordered dates, comparable periods, freshness, seasonality and defensible change-point claims. |
| **Where / who / which** | Which regions, segments, products, teams or entities account for the pattern? | Dimension breakdown, rank/share/distribution and useful navigation to the responsible population. `Where` may be geographic or organizational, not necessarily a map. |
| **How** | How does the result develop across the process, funnel, cohorts or contributing components? | Decomposition, process stages, flows, contribution and supported interaction; distinguish observed association/contribution from causation. |
| **Why / what next** | What evidence supports possible drivers, what remains uncertain, and what action is available? | Relevant driver comparisons, confounders, drillthrough to source evidence, documented hypotheses, uncertainty and action ownership. **A chart or LLM cannot prove cause from correlation; mark causal attribution unsupported unless design and evidence justify it.** |

An analytical sequence commonly runs `orient (what) → compare (to what) → locate (where/who) → follow change (when) → investigate (how/possible why) → decide/act → return or monitor`. Do not force this exact ordering or a visual for each question if the documented user journey differs. Distinguish **monitoring**, **diagnosis**, **exploration**, **operational action**, and **explanatory storytelling** profiles: they have different valid density and navigation patterns.

## Visual language: measurable rules plus interpretive review

A theme is a **semantic token system**, not a demand for a particular fashionable palette. Define a small set of roles: canvas/surface, foreground and secondary text, borders/gridlines, categorical series, sequential/diverging scales, neutral context, selected/highlighted, positive/negative/target and alert. Require consistent meaning for the same field and state across pages, legends, tooltips and exported documents; check that alert color is not also used casually as decoration. Respect brand and domain conventions while preserving accessibility; red is not universally bad, and a single hue must not be the only way to convey a state.

**Palette evaluation**: extract theme colors, explicit visual overrides and conditional formatting; resolve *effective* Power BI settings where supported, otherwise mark unknown. Check perceptual separation of categorical swatches, ordered lightness for sequential scales, appropriate divergent midpoint, saturation/accent budget and inconsistent mappings. Do not enforce arbitrary universal limits such as “only three colors”; categorical charts can legitimately need more, while five indistinguishable blues are worse than five well-separated colors. Check state and pairwise contrast against the actual adjacent canvas. Use WCAG 2.2 text contrast guidance (normally 4.5:1 for normal text, with applicable exceptions), non-text contrast where essential graphical elements or controls convey information, and non-color cues. WCAG numeric thresholds are measurable requirements **when the applicable foreground/background roles are known**, not blanket certification of a complete Power BI experience.

**Typography and hierarchy**: evaluate resolved title/subtitle/KPI/axis/table fonts at the actual target viewing size; truncation, competing emphasis, label density, numeric format and useful unit/period context. Define a constrained type scale and consistent alignment but permit justified exceptions such as dense operational tables. **Layout and rhythm**: page grid, outer/inner padding, gutters, grouping by proximity, alignment, whitespace distribution, navigation placement and predictable reading order. Aesthetics are judged in service of communication: visual hierarchy, compositional balance, coherent visual identity, restrained decoration, appropriate salience, and whether pages feel like one product. A vision-capable independent reviewer may assess these interpretive properties from the **whole page plus crops and structured facts**, with required observable examples; it may not overrule measured violations or assert an unverified root cause.

**Chart/task matching**: declare the analytical task (rank, compare, trend, distribution, part-to-whole, relationship, flow, detail) and input roles/grain. Validate actual category cardinality, numeric variation, sort, axis/tick formatting, data marks, baselines, percentage/percentage-point semantics, scales and table usefulness. A scatter→bar conversion changes the question from relationship to ranking; it needs an explicit intent decision, not only a cosmetic reviewer suggestion. Check table widths against content and whether its panel area is justified; core charts must not hide material categories behind scrollbars unless the scenario explicitly calls for browsing long lists.

## Traceable acceptance checks

- **Question coverage**: required question has a correct visual/interaction and data provenance; visible titles and units match the question; missing “why” evidence must be described as an open hypothesis, not manufactured. An optional coverage graph links `persona → story → question → page → visual → semantic field/measure → interaction → evidence → intended action`.
- **Journey simulation**: test the default view, realistic slicer states, click/filter/highlight, drillthrough, return, empty/error/loading states and cross-page context preservation. A screenshot of the landing page cannot certify navigation.
- **Visual system**: token/override consistency, accessible foreground/background roles, categorical distinction, color-meaning stability, typography hierarchy, spacing, alignment and crop-level legibility; record unknown effective theme properties rather than guessing.
- **Regression**: require source-bound captures and model readiness. An allowed repair must clear the original question/design defect and leave neighboring visuals, numbers, interactions, page composition and Word figures intact. An independent final review considers the whole page and the user's original scenario; a pleasant-looking image alone is not release approval.

## Example illustrative contract (not accepted by a parser yet)

```yaml
profile: sales-manager-weekly-review
persona: regional-sales-manager
trigger: weekly performance review
usage: desktop, 15-minute meeting
decision: identify material shortfalls and choose who investigates
questions:
  - id: sales.what.gap
    family: what
    prompt: How much did this week differ from target and last year?
    metric: net_sales
    comparisons: [weekly_target, prior_year_same_week]
    evidence: [summary_kpi, weekly_trend]
  - id: sales.where.shortfall
    family: where
    prompt: Which regions and categories contribute most to the shortfall?
    evidence: [ranked_contribution, drillthrough]
  - id: sales.why.hypotheses
    family: why
    prompt: Which observed factors warrant investigation?
    evidence: [mix_and_returns, supporting_detail]
    causal_claims_allowed: false
journey: [overview, select_shortfall, compare_segments, inspect_detail, return_to_overview]
style_profile: executive-light
review_context:
  viewport: desktop-1280x720
  brand_tokens: required_from_user_or_org
```

The schema, thresholds and fixture corpus are a future implementation task; the example must not be mistaken for currently supported CLI input.

## Research basis and limitations

- [Microsoft: dashboard design](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips) emphasizes audience, decision metrics, a legible overview, hierarchy and suitable visual choices; its article targets Power BI *service dashboards*, so apply principles rather than assuming they define every multi-page report.
- [Microsoft: requirements](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-migration-requirements) includes purpose, audience, expected action and the consumer's analytical workflow.
- [Tableau Blueprint: visual best practices](https://help.tableau.com/current/blueprint/en-us/bp_visual_best_practices.htm) discusses reading flow, purposeful color, whitespace, contrast, hierarchy and device context; it is design guidance, not Power BI API documentation.
- [Microsoft: themes](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes) explains base/custom themes and per-visual overrides; checking only theme JSON cannot prove effective rendered colors.
- [Microsoft: drillthrough](https://learn.microsoft.com/en-us/power-bi/guidance/report-drillthrough) explains summary → investigation → return and filter-context design.
- [Microsoft: accessibility](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) and [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) ground contrast, non-color cues, alt text and interaction accessibility; a few contrast calculations do not establish complete WCAG conformance.
