# Architecture and delivery plan

**Status:** target architecture; individual prototype elements live in PBIPDocumenter PR #12. This document deliberately separates existing behavior from designed interfaces. No third-party engine integration or complete second-project test has been completed in this new repository.

## Core principle

VQS must not consist of `take screenshot → ask an LLM whether it looks good`. Its core is a versioned, evidence-backed *visual fact model* assembled from report definition, authorized real data, formal rules and verified rendering. The vision reviewer handles interpretive properties that cannot be measured reliably. A repair plan is valid only if source and data checks support its diagnosis, and only a fresh whole-page render can verify its perceptual result.

```text
consumer (PBIPDocumenter, CLI, CI, other report generator)
  → import artifact + pinned quality profile + security policy
  → artifact adapter: Power BI PBIR/TMDL | DOCX/OOXML | future plugin
  → normalized page/visual/measure/format/geometry FACT GRAPH
      ↳ static PBIR/schema validator; theme/effective-format resolver
      ↳ semantic model query adapter (opt-in, read-only, scoped)
      ↳ formal policy engine (native rules and optional Fab Inspector / Draco 2)
  → render adapter (exact Desktop PID/path + saved state | DOCX pager)
  → artifact-bound visual evidence and independent reviewer
  → evidence adjudicator (measured fact / observed symptom / inferred cause / unknown)
  → issue registry → safe repair planner → isolated repair executor
  → full structural+data+render regression → independent re-review
  → pass | fail | blocked + JSON/SARIF/HTML evidence + source digests
```

## Package boundaries

- `vqs.core`: artifact identities, content digests, policy profiles, rule evaluation, findings, severity and applicability, evidence provenance, fail-closed release gate. No Power BI, model vendor, network or GUI dependency.
- `vqs.powerbi`: PBIR reader and versioned schema adapter, page/visual inventory, semantic-model/field roles, filter context, effective themes, geometry, chart-intent contract, quantitative axis/label/cardinality/encoding rules and visual IDs. Read-only by default.
- `vqs.powerbi.integrations`: Microsoft metadata/validation CLI, Desktop Bridge (Windows, exact PID), a read-only semantic-model MCP interface, and optional Fab Inspector CLI JSON normalization. Each adapter declares capabilities, version, provenance and failure modes; no blind or mandatory downloads.
- `vqs.design`: neutral chart/task specification, measured-design rules, contrast/typography/spacing computations, optional Draco 2 mapping. A rule must include data requirements and say `unknown` when evidence is absent.
- `vqs.vision`: provider-agnostic opt-in independent reviewer receiving verified page, crops and structured facts. It reports observable symptoms, supported locations and repair suggestions separately from root-cause hypotheses. No default cloud upload.
- `vqs.repair`: allowlisted source changes in a clean temporary worktree, safety policy, plan validation, rollback, regression and review-round history. A model cannot execute arbitrary shell/JSONPath or approve its own changes.
- `vqs.document`: OOXML facts, style/table/figure/page constraints, rendered pagination and cross-document figure provenance. This remains a separate adapter, not Power BI-specific code buried in the engine.
- `vqs.cli` / `vqs.ci`: inspect, render, review, plan, repair/iterate, verify, report and machine-readable exit codes. CI can run offline static checks; Desktop-only checks require a permitted Windows executor. No false green when that runner is unavailable.

## Evidence and diagnostic contract

A `finding` contains `schema_version`, `rule_id`, `artifact_kind`, `source_digest`, `page_id`, `visual_id`, `category`, `severity`, `status`, `evidence[]`, `symptom`, `hypotheses[]`, `verified_cause`, `repair_options[]`, `verification[]` and `reviewer_id` where applicable. `evidence` elements include method (`PBIR`, `TMDL`, `DAX`, `Desktop rendering`, `OOXML`, `independent visual review`), object locator, captured value, data scope and hash/timestamp. `verified_cause` cannot be populated solely by a model's interpretation of a screenshot. Data-query provenance includes effective filters, units, date range and table/measure source; inaccessible or stale data blocks semantic approval.

`pass` = all mandatory applicable checks complete on current source and output; `fail` = validated outstanding violation; `blocked` = data unavailable, invalid capture, unknown schema, unconfigured provider, reviewer disagreement unresolved, unsaved Desktop state, timeout, unsafe repair or stale output. All three states must remain distinguishable in JSON and CLI exit code. User-defined advisory exceptions require explicit rationale and expiry; mandatory data readiness and source hashes cannot be waived by an LLM.

## Example rule pipeline: repeated X-axis ticks

Read visual query role + measure numeric type and format; obtain the **actual** data distribution and authorized filter context; extract/estimate candidate domain and Power BI axis configuration. An offline heuristic can report a `potential_duplicate_ticks` risk but must **not** fabricate actual rendered tick coordinates/values. Analyze the fresh chart crop for displayed ticks, relate to the visual ID and compare distinct numeric positions with text. A confirmed mismatch yields `axis.display_values_not_distinct`; candidate repairs include changing precision, axis interval/size or visual type, subject to semantic and chart-intent checks. After change, verify the new data-bound chart still displays every required category and the adjacent table remains complete. Do not infer the underlying exact tick values solely from pixels.

## Example rule pipeline: unsuitable chart

Take an explicit analytical task (ranking, trend, part-to-whole, distribution, correlation or detailed lookup), roles and aggregation, cardinality, ranges and variation. Validate baseline semantics and generate feasible chart candidates. Use Draco 2 only for supported neutral representations; preserve Power BI-only semantics as explicit extensions or `unsupported`. Have an independent reviewer evaluate hierarchy and communication, but require the planner to justify any transformation using source/data. A scatter→bar replacement changes the *question* from correlation to ranking, so obtain an explicit business-intent declaration or record that trade-off rather than treating the conversion as an automatic cosmetic improvement.

## Rendering and security

Open a disposable PBIP copy and select the exact Desktop instance by PID and canonical path. Require saved state and page inventory agreement. Check actual native image dimensions and independently calibrated entire-canvas boundaries at every capture scale, with visual anchors or a measured viewport—not aspect ratio alone. Bind page PNGs and all derived crops to the exact source digest and instance state. An ABF cache is not proof of refresh reproducibility; first-open data and bulk refresh are separately verified. Do not commit report business data, cached credentials, user-local settings, screenshots or calibration by default. Cloud-model image/data transfer requires opt-in and redaction policy.

DOCX adapter reads styles and runs, table structure, section geometry, figure references, and independent rendered page count; it validates each page against document hash and relevant report screenshot hash. Page count and OOXML validity are not aesthetic approval.

## Build vs integrate

Use optional Fab Inspector for existing declarative PBIR governance and map its findings to native IDs. Use Microsoft's report-authoring CLI for current schema and visual-format capability discovery; do not hardcode undocumented formatting properties. Use Microsoft's Bridge for capture and Modeling MCP / a supported semantic query client for authorized values. Add Draco 2 only behind a neutral, tested spec adapter. In every case pin versions and fail explicitly on unsupported capabilities. See [research](RESEARCH.md) for alternatives, upstream limitations, licenses and links.

## Extraction plan and acceptance

1. **Bootstrap (current):** independent README, architecture, research and provenance. Do not move Contoso caches or generated screenshots. Keep PBIPDocumenter PR #12 unchanged.
2. **Portable core:** port versioned policy, SHA-bound image/review evidence, structured findings and pure PBIR visual inventories. Remove `pbip_documenter` imports, add a Python package, CLI, tests and a `PBIPDocumenter` adapter without hidden source paths.
3. **Quantitative design engine:** implement genuine data-aware rules for axis formatting, density and chart/role compatibility. Test with fixtures that distinguish potential risks, measured violations, unknowns and reviewer hallucinations.
4. **Native rendering:** adopt exact-instance Desktop Bridge, full-canvas verification, data-loaded preflight and independent high-resolution review. Test against a disposable copy and an unsaved/incorrect-instance matrix.
5. **Repair:** port conservative recipes and add transactional chart/axis/title/layout transformations, then prove defect resolution and absence of page-level regressions using fresh captures.
6. **Independent acceptance:** run on at least two unrelated PBIR projects (including a non-Contoso fixture), compare with Fab Inspector, verify user-specified design-policy behavior, then test real Word pagination and downstream PBIPDocumenter Word output.
7. **Adoption:** publish a pinned VQS release, update PBIPDocumenter to call the package/CLI, keep original provenance and migration notes, and retire duplicated prototype code only after equivalent or higher independent test coverage.

### Non-goals at extraction time

No autonomous approval by a single LLM; no arbitrary source edits proposed in free text; no project-specific chart aesthetic score; no assumed Power BI per-visual live API; no mandatory third-party account or remote image upload; no claims of general accessibility certification; no automatic upload of real model data to a public repo.
