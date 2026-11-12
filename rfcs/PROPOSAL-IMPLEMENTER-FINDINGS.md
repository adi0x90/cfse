# PROPOSAL-IMPLEMENTER-FINDINGS

**Status:** DRAFT evidence annex to PROPOSAL-FINITE-TRACE-EXECUTION; informative, not normative.
**Created:** 2026-11-12.
**Historical basis:** Eleven observations from an implementation against the older 1.1.0-era specification and a historical model-answer dialect.
**Current comparison:** Public CFSE revision `34575b9191c6a457faf669e505abac9af2e6dd2a`, whose README identifies version 2.0.1.

The original implementer note and tracker are **[REDACTED: private repository and issue]**. This annex includes the substantive observations and public current-spec references so readers need no access to that source. It does not publish private case data, infrastructure or receipts.

## Authority and interpretation

Only adopted requirements and schemas under `spec/` are normative. Neither the historical implementer note, this annex nor an execution-profile RFC supersedes them. A prototype workaround is not a specification amendment. The historical dialect remains historical; this reconciliation does not reinterpret its frozen results.

These are **eleven historical observations with current dispositions**, not eleven established open defects in CFSE 2.0.1. Some were repaired, some expose remaining documentation contradictions, and others are extension/tooling decisions. The execution-profile RFC addresses only the relevant execution and binding questions.

## Reconciliation

| # | Historical observation and workaround | Current finding | Proposed disposition |
|---|---|---|---|
| 1 | `invariant.logic` was accepted as a string; the prototype extracted predicate IDs and used its ledger for verdicts. | Current formal-logic rules require parsing, reference resolution, binding/signature and attribute checks. The public schema suite explicitly distinguishes these from schema validation and does not distribute a semantic-validator executable. | The old claim that no grammar is required is stale. Preserve the static/execution distinction; inventory implementations and specify a supported execution profile. Do not credit lexical extraction as semantic conformance. |
| 2 | Predicate definitions were English prose; the prototype mapped known predicates to ledger counters and did not score new authored definitions. | The Predicate contract intentionally has a Boolean result, typed inputs and a prose definition; optional implementation hints do not establish an executable interpretation. | Execution bindings are a tooling/profile requirement, not evidence that prose definitions are invalid core artifacts. Bind named predicates explicitly and review correspondence. |
| 3 | A Scenario list was schema-valid although TR-2 required one Scenario; the prototype rejected lists. | Current `scenario_ref` is a scalar ScenarioID and its description explicitly says exactly one. | Resolved in the inspected core revision. Retain as historical motivation, not a new open defect. |
| 4 | Empty observations could accompany a confirmed verdict; the prototype added observation requirements. | Current outcome-dependent constraints require timestamp, environment, matched results and invariant states for confirmed outcomes. Empty observations remain intentional for certain unexecuted/blocked records. | The confirmed-outcome defect is resolved at the schema-record layer. This does not authenticate evidence or prove an experiment occurred. |
| 5 | No family/archetype field existed and an anchor could not name an entry point; the prototype used a namespaced surface mapping. | Current `AttackAnchor.type` includes `entry_point`. The core still does not establish the implementer's full family/sibling closure model. | Entry-point anchor restriction is resolved. Treat family/surface mapping as a separate extension design, not a reason to weaken the core or assume family closure. |
| 6 | Verdicts lacked the implementer's complete release/runtime configuration identity; the prototype added its own configuration mapping. | Artifacts now have lifecycle/version metadata, and some environment/configuration descriptions exist. An artifact's semantic version is not the tested binary/runtime/build identity. | Replace the overbroad “nothing carries a version” claim with the precise need for evaluation-to-configuration binding. Address it in execution/receipt profiles without equating the two kinds of version. |
| 7 | Finding schema and TR-1 disagreed about `exploration_refs`; the prototype required its own list. | The main TR-1 section now documents `traceability.exploration` and exploration evidence entries. However, the later relationship table and `TraceabilityValidation` block still name `exploration_refs`, which is not the Finding schema field. Cross-artifact validation remains a separate semantic obligation. | Partially repaired; a residual documentation contradiction remains. Align the summary table and validation pseudocode with the supported schema-backed reference paths, and test examples. Do not add a second field just to preserve a stale summary. |
| 8 | TR-3 prose/schema used `targeted_invariants` while a validation example used `invariants`; the prototype chose the schema field. | Main TR-3 examples and the relationship table use `targeted_invariants`, but the `TraceabilityValidation` block still says `field: invariants`. | Residual documentation contradiction. Correct that example to `targeted_invariants` and include it in consistency checks. |
| 9 | Patch schema expected an object but the TR-5 example used a string; the prototype accepted both. | The current schema requires a `FindingReference` object with `finding_id` and `invariant`; the TR-5 “Valid” fragment still uses a scalar. A schema probe rejects that string and accepts a correctly shaped object. | Residual schema/example contradiction. Align the example with the existing object contract; accepting both would be a separate compatibility decision, not an automatic repair. |
| 10 | A static assessment could not honestly populate BASE/ATT execution fields; the prototype relaxed them and used some outcomes as predictions. | Current Exploration schema still requires BASE/ATT setup/action/expectation fields and tightly scopes confirmed outcomes. The core artifact is designed for exploration, not arbitrary static assessment. | A scope mismatch, not permission to fabricate execution. Use a separately reviewed assessment profile/artifact if needed; predictions never become confirmed execution outcomes. |
| 11 | External finding/patch IDs did not fit the core identifier grammar; the prototype kept ledger IDs internally and used compliant IDs in model documents. | Current Finding/Patch ID grammars still require their documented forms. Arbitrary external ledger IDs are not automatically CFSE IDs. | Integration/mapping concern rather than a demonstrated grammar contradiction. Preserve external IDs in an explicit mapping/extension and issue conforming artifact IDs; do not silently rewrite identifiers or widen the grammar. |

## Public checks and links

- [Static logic requirements](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/grammar/03-formal-logic.md) and [test-suite boundaries](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/tests/README.md).
- [Predicate contract](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/supporting/predicate/predicate.md).
- [Exploration schema](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/primary/exploration/exploration.schema.yaml) and [Scenario schema](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/primary/scenario/scenario.schema.yaml).
- [Traceability prose and summary blocks](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/semantics/04-traceability.md), [Finding schema](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/primary/finding/finding.schema.yaml), and [Patch schema](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/supporting/patch/patch.schema.yaml).
- [Identifier grammar](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/grammar/schemas/grammar.schema.yaml), [extension mechanism](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/foundations/extensions.md), and [conformance boundaries](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/foundations/conformance.md).

For item 9, validate `FD-OJS-AUTHZ-001` against the Patch schema's `FindingReference` definition: it fails the object type requirement. The object `{finding_id: FD-OJS-AUTHZ-001, invariant: INV-OJS-PAYMENT-COMPLETE}` passes that definition. This is a schema-fragment check, not validation of an entire Patch or its evidence.

## Acceptance criteria for maintaining this annex

- [ ] Every historical item retains its original scope, workaround and version-pinned current disposition.
- [ ] Resolved issues are not presented as current failures; unimplemented profile features are not presented as core regressions.
- [ ] Residual contradictions have small public reproductions and proposed corrections separate from the execution architecture.
- [ ] Any adopted correction updates the authoritative spec, not just this annex; this annex then links the implementation/release.
- [ ] Private provenance stays redacted in public text; the internal source note links back to this one reconciled account after publication.

## Implementation follow-up (2026-11-12, unreleased)

The table above retains the historical and version-pinned dispositions. The
remaining examples in items 7, 8 and 9 are corrected in
[`spec/semantics/04-traceability.md`](../spec/semantics/04-traceability.md): TR-1
uses the union of schema-backed exploration paths, TR-3 uses
`targeted_invariants`, and TR-5 uses the existing FindingReference object.
`TraceabilityExamples` regressions check the summary/pseudocode and validate the
TR-5 fragment against its schema. No compatibility field or schema widening was
introduced. The [execution profile](../extensions/finite-trace/README.md) and
[verification matrix](../extensions/finite-trace/VERIFICATION.md) address the
bounded tooling questions in items 1, 2 and 6; all other dispositions remain.
