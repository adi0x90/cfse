# PROPOSAL-FINITE-TRACE-EXECUTION

**Status:** DRAFT, informative and non-binding.
**Created:** 2026-11-12. **Target:** Optional profile; version and implementation home TBD.
**Authority:** Only adopted text and schemas under `spec/` define CFSE core requirements. This RFC and its implementer annex do not.

Proposed archive path: `rfcs/PROPOSAL-FINITE-TRACE-EXECUTION.md`. Discussion follows the repository's documented GitHub issue process. The eleven historical implementer observations are reconciled in the accompanying `PROPOSAL-IMPLEMENTER-FINDINGS.md` annex; they are not eleven newly established defects in the current release.

## Summary

Define an opt-in execution profile that evaluates a documented subset of CFSE's existing Concept, Predicate and Invariant artifacts over finite observations. Publish a capability manifest and small, independent conformance examples. Keep this distinct from core schema validation, evidence authentication and theorem proving.

**Status:** Proposal, not an implemented feature or change to the released core.

## Motivation and evidence

An internal synthetic grader-construction pilot used an experimental envelope containing one `C-TRACE` concept and Python expressions named as invariants. It did not execute authored `P-*` artifacts, typed predicate signatures or the normative CFSE logic grammar. Only 4 of 12 maintenance blocks selected an executable grader; the profile accepted 29 of 96 conforming traces. This identifies a prototype qualification failure, not a failure of CFSE's complete architecture.

The existing specification already defines typed predicates, invariant predicate references, logical operators and dependency metadata. The missing capability in that prototype was an explicit executable mapping. A renamed expression envelope cannot test whether those existing CFSE facilities improve reuse or reliability.

Private prototype source and run provenance: **[REDACTED: private repository and raw research artifacts]**. The numerical observations are a reported internal pilot result; this issue does not provide a public reproduction of that study.

## Proposed work

1. Inventory existing implementations before writing another parser or executor. Reuse a compatible implementation where available; document the exact supported spec revision.
2. Describe a finite-trace subset, including supported operators, quantifier domains, action interpretation, observation time and completeness assumptions. Explicitly reject or report unsupported temporal features.
3. Load schema-valid `C-*`, `P-*` and `INV-*` artifacts. Validate identities, references, variable bindings, argument names/order, arity and concept types before execution.
4. Bind predicates to explicit, versioned observation adapters. Treat `implementation` hints as documentation, not automatically executable trusted code. Document review of correspondence between the English definition and binding; a matching ID or digest alone does not establish semantic equivalence.
5. Record artifact, binding, policy and trace identities with evaluation results. Keep operator-controlled checker configuration separate from submitted artifacts.
6. Publish a capability declaration separating schema checks, static logic checks, finite-trace evaluation, authenticity checks and proof. Unsupported checks remain `not_checked`.

## Minimal example and acceptance criteria

Use a synthetic User, ExportJob and Project model. A typed role predicate is reused by separate request and delivery invariants.

- [ ] A self-contained public fixture validates against the pinned core schemas and executes through the documented profile without private dependencies.
- [ ] The same predicate binding is referenced by at least two invariants; results identify which binding version was used.
- [ ] Wrong arity, wrong concept type, unbound variables, unresolved references and unsupported operators produce distinct diagnostics.
- [ ] Supported dependency relationships have defined evaluation/invalidation semantics; unsupported cycles are rejected rather than guessed.
- [ ] A binding or policy version change prevents reuse of a result whose declared inputs no longer match.
- [ ] Missing evidence and operational failures follow an explicit evaluation contract; neither becomes an authenticated or proved result.
- [ ] No core-conformance or universal-security claim is inferred merely from successful finite execution.

## Scope, compatibility and alternatives

Target an optional extension/profile and its conformance fixtures first. Reuse existing core artifacts rather than adding parallel predicate fields. Any normative core change requires a separate compatibility decision, coordinated schema/prose updates and changelog entry.

Continuing with anonymous expression blobs is smaller but leaves reuse untested. Implementing the entire logic language and a proof assistant would be much larger. A supported finite subset is the recommended first step.

This issue does not authorize another model experiment, a training run or deployment. It does not claim that no other CFSE implementation can execute artifacts.

## Specification references

- [Predicate contract](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/supporting/predicate/predicate.md)
- [Invariant contract](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/artifacts/supporting/invariant/invariant.md)
- [Formal logic](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/grammar/03-formal-logic.md)
- [Conformance boundaries](https://github.com/adi0x90/cfse/blob/34575b9191c6a457faf669e505abac9af2e6dd2a/spec/foundations/conformance.md)

## Files and adoption boundary

Initial deliverables are this informative RFC, its version-pinned evidence annex and synthetic profile fixtures. No core schema or meaning changes are proposed in this first stage. If adoption requires core changes, identify the exact affected paths under `spec/`, obtain maintainer agreement, and update both schemas/prose plus `spec/changelog.md`; do not make an RFC itself normative. The execution implementation may live separately from this specification repository.

## Open decisions

- Select an existing compatible interpreter or a bounded supported subset after inventory; do not infer ecosystem-wide absence from this one prototype.
- Define finite-domain completeness, action/observation binding, missing-evidence handling and limits of temporal evaluation.
- Review the uncertainty contract alongside this RFC before qualification. Receipt authenticity is a separate optional profile proposal; it does not follow from successful formula evaluation.
- Resolve surviving core prose/schema discrepancies in the annex through narrow corrections; they are not all prerequisites for an execution profile.

## Evidence annex

The annex preserves the old implementation observations, compares them with public revision `34575b9191c6a457faf669e505abac9af2e6dd2a`, and separates resolved defects, residual contradictions, implementation limitations and scope choices. Private original provenance is **[REDACTED: private implementer repository and tracker]**. No private link is necessary to inspect the public spec examples cited in the annex.

## Implementation follow-up (2026-11-12, unreleased)

The above preserves the published draft's scope and historical observations.
A bounded [reference profile](../extensions/finite-trace/README.md) now implements
typed predicate reuse and the companion uncertainty contract. Its
[acceptance matrix](../extensions/finite-trace/VERIFICATION.md) records tests and
limits. This informative implementation does not adopt the RFC as core requirements.
