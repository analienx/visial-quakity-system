# Visual Quality System (VQS)

**Design, repair and independently verify analytical experiences that answer the right questions.** VQS is a source-aware quality system for Power BI reports **first**, Fabric Apps (Rayfin/React or other web frontends) **next**, and analytical documents **later**. It checks whether users can reach a useful and defensible conclusion—not just whether a chart renders or an AI likes a screenshot. For supported changes, it proposes a patch to an isolated *real artifact* and verifies the actual result and affected user tasks.

> **Status: pre-alpha / partial extraction.** This repository currently contains a portable PBIR inventory, observation policy, source/image integrity checks, a limited CLI and isolated quantitative design-rule primitives. It does **not** yet run the end-to-end Power BI repair loop, a Fabric Apps browser adapter, live data/refresh checks, comprehensive design rules or user-journey tests. A single-project prototype remains in [PBIPDocumenter draft PR #12](https://github.com/analienx/pbidocumenter/pull/12). All execution flows below are an implementation blueprint until verified by tests; do not market them as shipping features.

## What makes VQS different?

AI can generate reports and apps. VQS's durable responsibility is a **decision-quality contract**: `persona → decision → analytical question → scoped expected evidence → page/visual/route and interaction → actual data/answer → perceived communication → action`. User-provided stories and brand profile override defaults. Without them, VQS should propose only data-supported candidate questions: what, compared with what, when, where/who/which, how/decomposition, possible why, so what/materiality, uncertainty, missing populations, what-if, eligible prediction and next investigative action. Unknown business meaning, unsupported causality, absent dates or inadequate forecast history must not result in invented insight.

**P0 is pragmatic:** inspect an *existing* Power BI report, identify exact design or semantic defects, improve palettes/typography/spacing/labels and supported chart configurations in a disposable PBIP, reopen the actual Desktop report and independently prove the improvement without breaking adjacent content. Only then generate new visual templates and more complex journeys. Images are evidence of rendered reality; PBIR, data oracles and quantitative style/layout rules supply root-cause facts.

## How it will run in reality

**Do not host the whole system inside Fabric.** Start with a modular Python CLI coordinating typed contracts, native rules, evidence storage and bounded repairs. Launch external **Windows Power BI Desktop Bridge** and report-authoring/semantic-model tools for PBIP; launch a **pinned Node/TypeScript Playwright worker** for React/web apps. Use a run-local SQLite/event log and content-addressed evidence; keep source edits in disposable worktrees. No broker, Kubernetes, service mesh or compulsory cloud models for the first version.

The same intent, question, design-token, finding and acceptance schemas apply to both surfaces; **the editors and observers are different**. PBIR is edited/validated then rendered by Desktop, while a Fabric App is TypeScript/React/CSS/chart code built and exercised through a browser. Rayfin's backend model/runtime is TypeScript, not a native Python VQS host. Its Fabric-hosted preview has capacity, SSO and portal-specific semantic-query constraints; local Playwright passing does not prove deployed Fabric behavior. Use a separate staging workspace and authorized portal test later, never an automatic production deployment.

**Read the actionable [execution architecture](docs/EXECUTION_ARCHITECTURE.md)** for process topology, CLI target, typed evidence and component IDs, phase state machine, exact-PID Desktop locks, browser selectors/DOM/computed CSS/chart-data probes, model/privacy boundaries, typed PBIR and TypeScript repair operations, deployment gates, recovery, caching and acceptance slices. The [architecture overview](docs/ARCHITECTURE.md), [integration strategy](docs/INTEGRATION_STRATEGY.md), [default-story specification](docs/DEFAULT_STORIES_AND_AUTOMATED_DESIGN.md) and [research](docs/RESEARCH.md) explain the corresponding product requirements and upstream tool choices.

## Evaluation scope and honesty about status

| Dimension | Target evidence and outcome | Standalone status |
| --- | --- | --- |
| **Design and safe repair (P0)** | Effective palettes/semantic colors, actual typography, hierarchy, chart-task fit, label density, whitespace, alignment and accessible contrast; approved source patch and fresh full-page regression | PBIR inventory and isolated axis/contrast/category-space primitives; Desktop/repair loop remains in prototype |
| **Decision/story contracts (P1)** | Persona, candidate question families, comparable baselines, units, materiality, uncertainty, explanation limits, missing answers and evidence-backed expected outputs | Specified, not implemented |
| **Data integrity** | Authorized query oracles with exact filters, roles, model/source identity, freshness and units; no cache-only approval | No standalone live-model adapter yet |
| **User-journey/AI-answer assurance (P2)** | Overview → exception → investigation → evidence → action/return; actual interaction states and scope-equivalent answers | Specified, not implemented |
| **Power BI rendered review** | Complete exact-PID Desktop canvas/crops, visible categories, clipped labels, data-loaded check, independent source-aware image review | PNG/hash evidence extracted; renderer and reviewer in prototype |
| **Fabric Apps/web adapter** | Read tokens/routes/TSX/chart configs; test desktop/mobile with Playwright, DOM/computed CSS, SVG/chart data, accessibility, console/network and task oracles; patch vetted TS/CSS then rebuild/retest | **Planned. No browser runner or deployed Fabric acceptance in this repo** |
| **Word and monitoring (later)** | OOXML plus paginated review, figure lineage, domain packs and change-triggered question regression | Policy only; complete workflows pending |

A VQS finding must identify a rule and actual source/component, intended question, applicable state/role, measured or directly observed evidence, proposed bounded repair and regression requirement. The verifier records `pass`, `fail` or `blocked` separately. An independent vision model assesses subjective cohesion/overall feeling against an explicit design profile; it cannot override a failed data, accessibility or measurement check, or sign off its own patch. Cloud transfer of data or images is opt-in.

## Reuse instead of rebuilding platforms

VQS owns intent/question contracts, normalized evidence, rule evaluation, cross-tool adjudication and safe acceptance. Optional version-pinned capabilities may come from Fab Inspector (PBIR/Fabric governance), Microsoft report-authoring/schema and semantic-model tools, Desktop Bridge (rendering), Draco 2 (only supported neutral chart constraints), Playwright plus axe-core (web state and automated accessibility checks) and a configured vision model (interpretive review). Do not fork whole projects or pretend that passing an upstream validator means the dashboard is analytically or aesthetically sound. Fabric's official data-app template already includes centralized styling, chart/format primitives and Playwright validation: extend it instead of rebuilding Fabric SSO or a web server. See [integration boundaries](docs/INTEGRATION_STRATEGY.md).

## Available commands today

```bash
python -m pip install -e '.[test]'
vqs inventory /path/to/Example.Report
python -m pytest
```

`vqs inventory` returns PBIR visual IDs/types, geometry, bindings, explicit properties and source digest; it **does not** certify loaded data or visual design. `vqs request-review REPORT RENDERS --fixer-id EXECUTOR` verifies provided source-bound page PNGs and emits an **unapproved** checklist; it cannot independently capture or repair. The planned `vqs run --artifact ... --kind powerbi|fabric-app --mode review|propose|repair` is **not yet implemented**. No general autonomous designer or independent second-project acceptance is claimed.

## Delivery and ownership

**Slice A:** port and verify a real isolated PBIP Desktop review/repair including neighbor/data regression on two unrelated examples. **B:** effective visual-language and measured design engine. **C:** local synthetic React app and Playwright source/DOM/visual/interaction checks plus a real style repair. **D:** an official Rayfin data-app template in an authorized staging Fabric workspace, separately test deployed SSO and semantic queries. **E:** shared decision contracts and verified domain packs. Platform-unsupported or capacity-inaccessible cases are explicitly blocked, never simulated as green.

PBIPDocumenter becomes a pinned consumer when independent coverage is proven; its draft PR stays intact meanwhile. The public VQS repo excludes Contoso ABF caches/screenshots, personal profiles, real user data, secrets, third-party binaries and deployment credentials. License: [Apache-2.0 and attribution](NOTICE). Implementation work is tracked in [extraction issue #1](https://github.com/analienx/visual-quality-system/issues/1) and [design/auto-authoring issue #2](https://github.com/analienx/visual-quality-system/issues/2).
