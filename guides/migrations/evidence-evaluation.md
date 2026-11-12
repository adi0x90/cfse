# Migrating to core evidence-evaluation requirements (unreleased)

The working specification now includes normative [Evidence Evaluation](../../spec/semantics/06-evidence-evaluation.md). This change promotes guarantees previously implemented by the optional finite-trace profile into core semantic obligations. The parser, adapter format, numeric reward scale and execution limits remain optional tooling choices.

## Compatibility and release boundary

No artifact schema, Predicate Boolean return type, or InvariantState enumeration changes. Existing correctly supported records need no mechanical rewrite. However, an evaluator that substitutes false for unknown, treats failure as success, or promotes formula truth to confirmed enforcement may no longer conform. This is a normative tightening, not merely editorial guidance.

`VERSION` remains 2.0.1 because no release is being made. These requirements are **unreleased**, not retroactive claims about the published 2.0.1 contract. Under [RELEASING.md](../../RELEASING.md), breaking conformance-requirement changes require a major release; do not publish this as a patch-only clarification. Release selection/publication remains a separate action.

## Review existing implementations and records

1. Preserve unobserved values separately from Boolean results. Audit implicit false defaults, truthiness, null comparisons, failed lookups and assumed complete domains.
2. Compare supported operators against the [portable vectors](../../tests/fixtures/uncertainty/cases.json). Distinguish operational failure from U, and retain independent counterexamples/witnesses.
3. Review `P-X-KNOWN AND P-X-VALUE`: it means known-and-true, not X with an unknown state. Do not copy the conjunction's false result into VALUE. A false KNOWN implication guard can be vacuously true without establishing VALUE.
4. Keep formula truth separate from execution-backed `InvariantResult` and Exploration verdicts. Existing matched BASE/ATT and direct-evidence requirements still apply.
5. Report uncertainty/failure reasons and identify affected checks. Keep diagnostics outside closed artifact objects unless an existing field or declared extension supports them. Do not count unperformed checks as passed.
6. Review previously emitted decisive results where insufficient evidence or operational failure may have caused a false pass. Re-evaluate with adequate evidence; preserve original provenance and follow existing state-transition/new-Exploration rules rather than silently rewriting history.
7. Review success/reward mappings: no full credit for demonstrated satisfaction or successful checking where the required evidence/check remains unresolved or failed. Scoring a correctly reported unknown is a different task and must be labeled accordingly.

## Optional finite-trace output compatibility

The profile adds `truth`, `result_scope: finite_formula`, `exploration_state: not_checked`, and a separate `exploration_verdict` capability. Its prior `state` shorthand is retained for existing local consumers but is explicitly **not** a core Exploration `InvariantResult`. Use the explicit scope and `truth` for formula evaluation. Results also include a digest of the normative evidence contract in their identity, invalidating stale identity matches when that contract changes.

Historical verification records remain attached to their original revisions. They are not rewritten to imply that earlier runs tested these new normative requirements.
