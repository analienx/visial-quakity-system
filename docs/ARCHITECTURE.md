# VQS architecture: a verifiable decision-quality system

**Status:** proposed target architecture with a pre-alpha portable core. The complete Windows/vision/repair prototype remains in PBIPDocumenter PR #12. This document is an implementation contract, **not a list of capabilities already delivered**.

## Design principle and ownership

Use a **modular monolith with strict typed ports**, not microservices, separate AI agents for every rule, or a monolithic fork of another analyzer. Ship one Python package/CLI, an optional Windows Power BI executor and opt-in provider adapters. VQS owns the *question/decision contract, normalized evidence, rule decisions, conflict adjudication, repair safety and before/after acceptance*. Upstream tools and LLMs are replaceable capabilities, never the source of the final green status. Keep the artifact's source and data local by default.

**P0 user experience:** `vqs improve path/to/report.pbip --profile profile.yaml --candidate ./output` is a **target API, not a currently implemented command**. It should inspect a real report, identify exact visual-level defects, propose and apply safe style/chart fixes on a disposable copy, open and recapture in Desktop, and return the modified candidate plus actionable pass/fail/blocked evidence. Start with existing visuals, not unconstrained generation.

```text
Consumer: standalone CLI / PBIPDocumenter / CI / later UI
    │
    ▼
Run controller: artifact identity, profile, permissions, task budget, durable run log
    │
    ├─ Intent contract: supplied persona + task + design profile, otherwise conditional story discovery
    │    └─ question/decision graph: what, compared with what, when, where/who,
    │       how, why-hypotheses, so what, uncertainty, omissions, scenario, next action
    ├─ Artifact facts: PBIR/schema, TMDL/measure lineage, effective themes and visual overrides
    ├─ Authorized data evidence: scoped read-only model queries, refresh/RLS context, distributions
    ├─ Rule engines: native design + semantic/question tests; optional Fab Inspector / Draco adapter
    ├─ Windows render port: exact saved PBIP/Desktop PID → full canvas and visual crops
    ├─ Independent vision port: page + crop + structured facts → observed symptoms only
    │
    ▼
Evidence adjudicator: verified fact vs observed symptom vs hypothesis vs unknown
    │
    ▼
Finding registry: issue → question/visual/source/filter → repair option → verification test
    │
    ▼
Independent planner → typed allowlist validator → isolated PBIR/Word repair executor
    │
    ▼
Full regression: schema + data/query + style + page render + interaction/task + re-review
    │
    └─ pass / fail / blocked + durable JSON/SARIF/HTML and source-bound candidate/diff
```

## Ports and packages

| Package / port | Responsibility and boundary |
| --- | --- |
| `vqs.core` | Stable artifact/run identities, evidence schema, applicability (`pass/fail/unknown/blocked`), rule provenance, security policy, test assertions and final gate. No Power BI, GUI, network or model dependency. |
| `vqs.intent` (planned) | Question ontology, explicit persona/decision/expected-answer contracts, conditional default story generator, domain packs and mapping to page/visual/interaction IDs. No invented target, geography, denominator or causal interpretation. |
| `vqs.powerbi` | PBIR page/visual/query/interaction inventory, effective theme resolution, semantic metadata, field-role semantics, exact source fingerprint; read-only by default. Dedicated versioned authoring port for supported PBIR edits. |
| `vqs.data` (planned) | Authorized read-only model query provider and test fixtures. Record dataset and refresh identity, filter context, date/population scope, RLS, units, sample/uncertainty and query results. No query access means `unknown`, not a made-up result. |
| `vqs.design` | Measured style and chart rules: palette role/semantic reuse, text and mark contrast, typography, label budget, category/axis precision, chart/task suitability, encoding truth, spacing and alignment. Aesthetic/brand fit is a structured independent review with profile and explicit evidence. |
| `vqs.integrations` (planned) | Version/capability-probed, opt-in adapters for Fab Inspector, Microsoft authoring/schema tools, semantic-model query, Desktop Bridge and optional Draco 2. Normalize tool output; do not treat an upstream pass as global approval. |
| `vqs.render` (planned port) | Windows-only exact Desktop PID/path and saved-state validation, first-open data preflight, native capture and independently verified complete canvas/viewport at each scale; source-hashed crops. Document paginated renderer as separate plugin. |
| `vqs.review` (planned port) | Configurable image-capable multimodal reviewer for perceptual hierarchy, overall feeling, palettes as actually rendered, misleading presentation and journey affordances. It sees whole page and focused visuals with factual context. Separate reviewer ID/provider from fixer, explicit image-transfer consent. |
| `vqs.repair` (planned port) | Structured repair plan with expected semantic effect, narrowly typed PBIR/theme mutations or validated template instantiation; safe isolated execution, diff, rollback, iteration limit and promotion boundary. AI planners cannot issue arbitrary file operations or self-approve. |
| `vqs.journey` (planned) | Task benchmark against expected query results, visual and interaction routes (filters, drillthrough, back navigation), ambiguity and available AI-answer parity. Human study required before claiming measured end-user usability gains. |
| `vqs.document` (planned) | OOXML typography and figure/measure lineage; every page's render and page-break checks, tied to source report revision. |
| `vqs.cli` | Headless inspect/review/improve/verify commands and machine-readable outputs. Offline static passes are not equivalent to an end-to-end quality pass. |

## Canonical contracts and durable run bundle

`IntentContract`: `schema_version, persona, decision, question_id, question, answer_type, required_metrics, dimension_roles, comparison, population, period, supported_explanation_level, expected_evidence, allowed_interactions, next_action, provenance, applicability`. Supplied user stories override inferred defaults. A generated story is only a *candidate* until its required fields, measure meanings and model queries are checked; unsupported stories are skipped with a reason. Default families are conditional, **not mandatory chart counts**.

`VisualFact`: report/page/visual IDs, visual type, data roles, explicit and inherited effective formatting (with provenance), layout, query/filter/RLS context, populated-data status, report source digest, page/image/crop digests and any unsupported/unknown properties. Do not conflate an explicitly configured property with its actual rendered value.

`Finding`: versioned rule ID, story/question ID when applicable, visual/page IDs, evidence object IDs and methods, data scope, measurable violation or visibly located symptom, severity, confidence/uncertainty, alternative explanations, verified cause *only when verified*, safe repair candidates, test oracles and regression scope. Keep direct facts, hypotheses and subjective assessment separate. No overall unexplained aesthetic score.

`RunBundle`: input source digest and dataset/refresh identity, intent+design profile revision, tool/model versions, all invoked capabilities and access policy, findings, capture/crop hashes, candidate git diff, task-oracle results, independently sourced before/after evidence and `pass|fail|blocked`. Invalidated source, missing images/data, untested interaction or provider disagreement must not silently pass. JSON first; SARIF/HTML optional derived views.

## Design and data evaluation: two complementary lanes

**Measured lane:** detect bounds, alignment, palette role collisions, non-distinct labels, insufficient measured contrast, inappropriate zero baseline and insufficient category/label space using *real effective properties and scoped data*. Check `compared with what`, units, denominators, incomplete periods, materiality and uncertainty at question level; test against authoritative read-only DAX or domain-specific reference oracles. Without exact tick positions or effective formatting, report a risk/unknown, not a fabricated finding.

**Perceptual lane:** assess hierarchy, overall style/brand fit, reading order, clutter, meaningful use of color, visible clipping and cognitive effort from whole-page and chart renders. The reviewer also sees the intent graph and measured evidence, but may not infer specific DAX causes from pixels. Disagreements trigger independent adjudication. Color-blind or small-screen review can augment but not replace measurable contrast and semantic-color tests.

The two lanes meet in the finding registry; a pleasing screenshot cannot override a false answer, missing cohort, stale source or broken interaction. A formally valid chart cannot pass when it is unreadable at target viewport.

## Authoring and verification are different trust domains

Use existing Microsoft authoring tooling and optional configurable repair model to **propose** source-level designs; use allowlisted, version-pinned PBIR transformations and validated visual templates to **implement** them only in a disposable clean candidate. Verify references, filters, RLS, category visibility, measure correctness and adjacent visual layout before promoting. A scatter-to-bar change may switch the analytical task from correlation to ranking; require a matching intent contract rather than treating it as a universal cosmetic fix.

Use an **independent** verification actor, deterministic oracles and a fresh Desktop render to judge the candidate. A model that authored a chart cannot be the sole authority approving it. For a claim of improvement, compare the same questions and expected answers before and after, ensure no lost interaction or data segment, and resolve the original issue plus newly introduced defects. If human task speed or comprehension is asserted, test representative users rather than claiming AI simulation proves it.

## Integrations: build vs reuse

Consume Fab Inspector as an optional external rule engine and map its governance findings into VQS IDs. Use Microsoft PBIR/report-authoring/schema tools and Desktop Bridge for supported authoring, validity and real capture; do **not** assume the live Bridge exposes every per-visual property or actual numeric result. Use a separate authorized semantic query provider for data. Test a neutral chart-task adapter before invoking Draco 2; maintain explicit unsupported Power BI visual/interaction capabilities. Pin versions, discover supported operations and respect third-party licenses. External tools are **providers, not the product definition**.

The minimal runtime is **one portable Python process with optional child processes** and a Windows Desktop execution port; no Kubernetes, message broker, database or full agent mesh needed for the first release. Persist each run to a local artifact directory, deterministic JSON and optional SQLite registry for replay. Remote rendering and CI workers can be added behind the same typed ports later. Provider credentials and report images stay out of the public repository. Cloud image/data submission requires explicit permission and minimization.

## Practical staged delivery and acceptance

1. **P0 — real report repair:** stabilize portable evidence/rule schemas; integrate Fab Inspector optionally, effective color/theme rules, chart/context rules and Windows capture; port constrained repair. On two unrelated real PBIPs, fix a true chart/style defect in an isolated report, reopen Desktop and verify readable populated pages, exact answers, all categories and unaffected neighboring visuals. No claim of autonomy until all steps run unattended within bounded retries.
2. **P1 — question and decision contracts:** infer only supported default stories; map existing and missing question coverage; add baseline, materiality, uncertainty and provenance oracles with explicit ambiguous/unknown outcomes. Test with two domain fixtures and adversarially ambiguous measures.
3. **P2 — interactions and AI answers:** support scripted filter/drillthrough/return checks and compare available AI replies to the same question under identical context; report answer disagreement without auto-selecting a winner. Test human task performance separately when claiming end-user benefit.
4. **P3 — domain packs and continuous quality:** domain questions, validated predictive eligibility, drift/change-triggered invalidation of previously approved answers and snapshots; optionally support DOCX paginated acceptance as its own tested adapter milestone.
5. **Extraction/adoption:** only after equivalent standalone tests, release a pinned VQS package, make PBIPDocumenter a consumer, and retire duplicate prototype code without merging unverified design approval.

**Current executable boundary:** the standalone repository has inventory, policy, provenance and limited measured-rule primitives. `vqs improve`, full question mapping, independent journey verification and all-port integration are **not implemented**. See [README](../README.md), [default stories](DEFAULT_STORIES_AND_AUTOMATED_DESIGN.md), [integration strategy](INTEGRATION_STRATEGY.md), and [research](RESEARCH.md).
