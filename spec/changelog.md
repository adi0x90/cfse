# Changelog

All notable changes to the CFSE specification.

Format: [Semantic Versioning](https://semver.org/)

This changelog starts at **1.0.0**, the first public release.

## [Unreleased]

### Added

- **Normative core:** Evidence Evaluation requirements distinguish Boolean propositions, insufficient evidence, operational failures and successful claims; define partial-evidence composition and finite-domain completeness; retain independent violations and existing BASE/ATT confirmation gates. Numeric reward scales and execution machinery remain implementation-specific.
- Portable core uncertainty conformance vectors and tests, plus a mixed definite-violation/unknown-target corpus case.

- Informative opt-in finite-trace reference tooling and synthetic tests for typed predicate reuse, evidence uncertainty and reward eligibility. This is not a core evaluator or a change to Boolean Predicate schemas.

### Changed

- Replace the misleading `KNOWN AND VALUE` uncertainty recipe with explicit knowability versus value-evidence semantics. This tightens evaluator conformance without changing artifact schemas or Predicate return types; see the [migration note](../guides/migrations/evidence-evaluation.md) and major-version conformance-change policy in [RELEASING.md](../RELEASING.md). Not released as 2.0.1.
- Optional finite-trace results now explicitly identify formula truth and unperformed Exploration evaluation, and bind the core evidence-contract digest.

- Correct residual TR-1/TR-3 summary/pseudocode paths and the TR-5 FindingReference example to match existing schemas. No schema or cardinality change.

### Removed

## [2.0.1] - 2026-11-10

### Added

- `CITATION.cff` with the author ORCID and repository.
- `.zenodo.json` for the Zenodo GitHub integration.

### Changed

- No normative changes; the specification text is unchanged.

## [2.0.0] - 2026-11-09

### Added

- Shared lifecycle metadata and conditional requirements across artifacts using `ArtifactStatus`.
- Synthetic schema and semantic conformance vectors, complete-example checks, and public schema CI.
- A [contract-repair proposal](../rfcs/PROPOSAL-CONTRACT-REPAIR.md) and [migration guide](../guides/migrations/contract-repair.md).

### Changed

- **Breaking:** Explorations reference exactly one Scenario. Unexecuted drafts/plans omit a verdict and have empty observations; blocked, inconclusive and confirmed results have distinct evidence-record requirements.
- `ACTIVE` artifacts require version and approval date; `DEPRECATED` artifacts require a deprecation date. Unknown fields remain rejected.
- Confirmed outcomes require direct property-specific evidence. HTTP status alone does not establish enforcement or violation; static record checks do not authenticate evidence.
- Formal-logic grammar, bindings and predicate-signature requirements are explicit. Schema validation does not establish semantic validity or proof.
- Shared verdict values, traceability fragments and delta documentation agree with the artifact schemas. Completed patches require every recorded rerun to report `HOLDS`.
- Complete artifact examples include required lifecycle metadata, and the flow example uses a valid Interaction ID. Public `cfse.ai` schema identifiers and `trigger.initial_interaction` are retained.

Existing 1.x corpora need explicit review and migration before claiming 2.0.0 conformance. This release does not supply missing approvals or execution evidence.

### Removed

## [1.0.0] - 2026-01-25

### Added
- First public release of the CFSE specification (core + schemas)
- Normative core spec (`spec/`) organized as foundations, grammar, artifacts, and semantics
- YAML schema definitions for CFSE artifacts
- Canonical Invariant Library YAML format (single-file packaging for `P-*` and `INV-*`)
- Conformance levels (minimal, standard, full)
- Normative language keywords per RFC 2119 + RFC 8174 (MUST/SHOULD/MAY in ALL CAPS)
- Entry Point (`EP-*`) and Projection (`PRJ-*`) supporting artifacts (optional exposure modeling)
- Optional extension mechanism (extensions may be published separately)
- Informative reading guides (`guides/`) and proposal process/templates (`rfcs/`)
