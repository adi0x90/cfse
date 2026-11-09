# Changelog

All notable changes to the CFSE specification.

Format: [Semantic Versioning](https://semver.org/)

This changelog starts at **1.0.0**, the first public release.

## [Unreleased]

### Added

- Shared lifecycle metadata and conditional requirements across artifacts using `ArtifactStatus`.
- Synthetic schema and semantic conformance vectors, complete-example checks, and public schema CI.
- A [contract-repair proposal](../rfcs/PROPOSAL-CONTRACT-REPAIR.md) and [migration guide](../guides/migrations/contract-repair.md).

### Changed

- **Breaking; intended for the next major release:** Explorations reference exactly one Scenario. Unexecuted drafts/plans omit a verdict and have empty observations; blocked, inconclusive and confirmed results have distinct evidence-record requirements.
- `ACTIVE` artifacts require version and approval date; `DEPRECATED` artifacts require a deprecation date. Unknown fields remain rejected.
- Confirmed outcomes require direct property-specific evidence. HTTP status alone does not establish enforcement or violation; static record checks do not authenticate evidence.
- Formal-logic grammar, bindings and predicate-signature requirements are explicit. Schema validation does not establish semantic validity or proof.
- Shared verdict values, traceability fragments and delta documentation agree with the artifact schemas. Completed patches require every recorded rerun to report `HOLDS`.
- Complete artifact examples include required lifecycle metadata, and the flow example uses a valid Interaction ID. Public `cfse.ai` schema identifiers and `trigger.initial_interaction` are retained.

`VERSION` remains the last released version until the release process is completed. Existing corpora need explicit review and migration; this change does not supply missing approvals or execution evidence.

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
