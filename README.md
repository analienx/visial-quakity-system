# Visual Quality System (VQS)

**A user-journey-led, source-aware design checker and repair framework for Power BI dashboards and generated documents.** VQS asks whether a report answers the *right questions for its users*, conveys correct and appropriately scoped data, has a coherent and accessible visual identity, and supports the intended investigation and action. It correlates the actual report definition and model data with rendered evidence, identifies concrete defects, proposes constrained source repairs and checks the result. It is **not** a screenshot-to-AI taste prompt or a collection of disconnected linters.

> **Status: pre-alpha; partial extraction.** A portable Python package with PBIR visual inventory, versioned observation policy, source/image provenance checks, an initial CLI and isolated quantitative design-rule primitives is present. User-journey coverage, effective theme resolution, whole-report color/composition analysis, external tool adapters and the full autonomous Desktop → review → repair loop **are not yet operational in this repository**. The tested prototype remains in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12). No production-ready visual-quality release is claimed.

## Product contract: purpose → insight → design → action

Each evaluation begins with a **persona and analytical task**: who uses this, in what context, which decisions they need to make, and how they recognize, investigate and act on an interesting signal. Map `persona → user story → question → page/visual/interaction → actual measure and filters → evidence → action`. A page can be beautiful and still fail because the business question is unanswerable; it can be statistically correct but fail because labels or color obscure the finding. Never fabricate business intent from a screenshot or claim a causal “why” without supporting evidence.

The question families are **what** (state/deviation), **when** (timing/trend), **where / who / which** (affected segments or entities), **how** (process/contribution) and **why / what next** (evidence for possible drivers and the supported decision). These are configurable user-story needs, **not five mandatory charts per page**. Typical journeys are `overview → exception → comparison → focused investigation → supporting detail → action/return`; exploratory and operational use cases can differ. The system must check missing questions, redundant visuals and broken drillthrough/filter context as well as the appearance of each chart.

VQS evaluates a **visual language**, not a prescribed palette. It must analyze effective Power BI theme and visual overrides, meaningful category/alert/highlight color assignments, categorical separation, sequential/diverging scale semantics, text/mark contrast, fonts, salience, spacing, whitespace, grouping, alignment, balance, reading order and consistent interaction states. The overall *feeling* should be deliberate, brand-aligned and suitable for the audience: a restrained executive overview, dense operational monitor and exploratory analysis legitimately have different style profiles. Interpretive vision review tests this coherence against the explicit profile; measurable rules and actual data remain independent release requirements.

**Detailed requirements:** [product and design contract](docs/PRODUCT_AND_DESIGN_CONTRACT.md) · [tool integration strategy](docs/INTEGRATION_STRATEGY.md) · [technical architecture](docs/ARCHITECTURE.md).

## What is evaluated, and what works today?

| Quality dimension | Intended evidence and decision | State in standalone VQS |
| --- | --- | --- |
| User journeys and questions | Audience, decisions, required what/when/where/how/why questions, page/visual coverage, drillthrough and return paths | **Specified; not implemented** |
| Report and semantic facts | PBIR types, positions, bindings, sorting, themes/overrides, actual scoped data distributions and measure units | PBIR read-only inventory extracted; effective theme resolution and live model query **pending** |
| Data-aware design rules | Chart-task compatibility, duplicate axis values, category/label budget, numeric precision, scale/encoding correctness | Isolated measured axis/contrast/category-space primitives present; **no complete rule engine** |
| Visual identity and accessibility | Brand/design tokens, palette roles, consistency, effective color contrast, typography, whitespace, alignment, page coherence | Initial opaque-color contrast primitive and observation policy only; **comprehensive analyzer pending** |
| Rendered behavior | Exact-instance native Power BI capture, complete canvas/crops, clipping, scrollbars, populated values and target-size readability | Portable PNG/source integrity present; Windows Desktop Bridge adapter remains in prototype |
| Independent interpretation | Whole-page and visual-crop review **with** user story, PBIR/data facts and specific observations | Versioned 25 Power BI / 23 Word question sets present; model adapters remain in prototype |
| Safe repairs and regression | Isolated source changes, semantic/interaction integrity, fresh rerender and independent re-review | Constrained prototype recipes not yet ported or independently accepted |
| Generated Word output | OOXML and every paginated page, narrative/figure consistency with the corresponding report revision | Shared policy/evidence present; complete document loop pending |

Outputs should be **source-linked findings and question-coverage gaps**, not an ungrounded global visual score. Every rule records applicable context, evidence, violated expectation, affected visual/story, supported repair and verification plan. `unknown`/`blocked` are different from `pass`.

## Integrate tools, rather than fork a monolith

VQS **owns the decision and design-quality layer**. Existing tools are version-pinned, optional capability providers: use Fab Inspector for supported PBIR/Fabric governance findings; Microsoft schemas/authoring tooling for definition validation; read-only semantic-model tools for actual query evidence; Desktop Bridge for real rendering; optionally map chart/task constraints to Draco 2 where representable; and use an explicitly configured image-capable model for interpretive review. **The user-journey graph, purpose-driven chart assessment, palette/overall composition assessment, evidence arbitration and safe repair contract are VQS-owned.** Do not copy or vendor upstream code merely for convenience. See [integration strategy](docs/INTEGRATION_STRATEGY.md) and [research](docs/RESEARCH.md) for boundaries, licenses and what is not yet integrated.

## Executable pre-alpha surface

```bash
python -m pip install -e '.[test]'
vqs inventory /path/to/Example.Report
python -m pytest
```

`vqs inventory` reads a PBIR project, outputs page/visual IDs, geometry, bindings, stored formatting and a source SHA-256. It does not resolve all theme defaults, query the model or approve visual design. `vqs request-review REPORT RENDERS --fixer-id EXECUTOR` accepts a manifest binding each report page to a fresh, verifiable PNG and emits an **unapproved** observation request; it cannot capture, repair or approve a dashboard on its own. These commands are not substitutes for the planned full journey/design gate.

## Planned workflow and acceptance

`user stories + design profile → report/model and required data facts → structural/governance checks → question coverage + quantitative design + visual-language rules → saved, populated render at target viewport and journey states → source-grounded independent interpretive review → evidence adjudication → bounded isolated repair → full data/page/journey/document regression → pass | fail | blocked`.

Release acceptance requires tests on **at least two unrelated PBIP projects**, realistic default and filtered journeys, accurate color/axis/cardinality fixture findings, a real before/after repair with no neighboring visual regression, and all-page generated Word validation. Cloud image or model-data transfer is opt-in. A missing tool, stale screenshot, unsupported question or absent model data cannot be silently approved.

## Ownership and migration

This independent repository is now [analienx/visual-quality-system](https://github.com/analienx/visual-quality-system). PBIPDocumenter will become a pinned VQS consumer; its draft PR remains intact until the standalone package has equivalent verified coverage. Do not move Contoso cached data, screenshots, personal machine configuration, credentials or third-party binaries into this public repository. Extracted source keeps [Apache-2.0 attribution](NOTICE), and third-party tools retain their own licenses. Remaining work is tracked in [issue #1](https://github.com/analienx/visual-quality-system/issues/1).
