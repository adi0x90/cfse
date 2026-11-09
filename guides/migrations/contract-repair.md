# Migrating from CFSE 1.x to 2.0.0

This informative guide describes the breaking contract changes in CFSE 2.0.0. The normative requirements are in `spec/` at tag `v2.0.0`. Upgrading a validator or schema set does not automatically migrate existing corpora.

Pin the specification revision used by your tools, inventory existing records, and review validation failures before adopting the new contract. Preserve the original records and their provenance.

| Existing record | Required review or change |
|---|---|
| `scenario_ref: [S-EXAMPLE-TEST-001]` | Convert a singleton array to its scalar Scenario ID. |
| Multiple Scenario references | Determine which Scenario the experiment actually tested. Split records only when separate experiments and evidence support that split; do not silently choose the first reference. |
| `ACTIVE` without lifecycle metadata | Supply the actual version and approval date if known. Otherwise retain an unapproved lifecycle state; do not invent an approval to satisfy validation. |
| `DEPRECATED` without a date | Recover the actual deprecation date or leave the migration unresolved. Do not substitute today's date for unknown history. |
| Unexecuted draft or plan with a placeholder verdict | Use `observations: {}` and omit `verdict`. Omitted status means `DRAFT`. |
| `BLOCKED` | Use empty observations and a nonblank verdict summary describing why execution could not occur. |
| Executed but unresolved experiment | Use `INCONCLUSIVE`, record `observations.executed_at`, and explain uncertainty in `verdict.summary`. |
| Confirmed verdict with sparse observations | Recover the actual execution record or repeat the experiment. A timestamp, environment, successful matched BASE, nonempty ATT result, delta summary, invariant states and verdict summary are required. |
| `HOLDS` or `VIOLATED` supported only by HTTP status | Review the property-specific effect. A response code alone cannot support a decisive invariant state. Preserve uncertainty when direct evidence is missing. |
| Duplicate or unrelated invariant observations | Keep each targeted invariant at most once and reconcile it with the referenced Scenario. Enforcement requires every target as `HOLDS`; violation requires a targeted `VIOLATED` state and a referencing Finding. |
| Arbitrary text or invalid bindings in `logic` | Parse and type check the expression against its actual Concepts and Predicate signatures. Rewrite the intended property; adding characters to meet a length threshold does not repair logic. |
| `COMPLETE` patch with a non-`HOLDS` rerun | Resolve the verification result before claiming completion. Do not relabel a failed or unknown result as successful. |

Quote dates in YAML, for example `approved: "2026-01-25"`, to preserve their string type. Lifecycle metadata is available on each artifact using `ArtifactStatus`; Patches retain their separate 4V workflow and Invariant Library containers carry lifecycle metadata on their individual entries.

The shared Verdict type now uses `VIOLATION_CONFIRMED`, `ENFORCEMENT_CONFIRMED`, `INCONCLUSIVE` and `BLOCKED`, matching Exploration verdicts. A legacy `PASS` or `FAIL` label is not enough to select a replacement; inspect the recorded evidence.

The Flow example's invalid `I-SHOP-COLLECT-GUEST-INFO-001` identifier is corrected. When fixing an identifier in a corpus, update its references together. The public `trigger.initial_interaction` field and `https://cfse.ai/schemas/` namespace are unchanged.

Run the [contract tests](../../tests/README.md) against the exact schema revision you intend to adopt. Schema checks validate representation and local record requirements; a semantic validator is needed for logic, cross-references and cross-artifact consistency. Direct evidence and approval still require researcher review. Passing the provided tests does not establish full CFSE conformance.

After reviewing and migrating a corpus, update its `cfse.version` declaration to `"2.0.0"` only when it satisfies the applicable requirements. Per-artifact `version` fields describe the artifacts themselves and do not need to become `2.0.0` merely because the specification changed. Keep older corpora pinned to their original specification revision until migration is complete.
