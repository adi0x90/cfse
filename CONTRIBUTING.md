# Contributing to CFSE Spec

Thanks for helping improve the CFSE specification.

This repository is primarily the source of truth for the **normative** CFSE spec and schemas. Contributions should aim to improve clarity, correctness, and long-term interoperability.

## Before You Contribute

- Code of conduct: `CODE_OF_CONDUCT.md`
- Security issues: `SECURITY.md` (please do not file security issues publicly)
- Governance and roles: `GOVERNANCE.md`, `MAINTAINERS.md`

## Repository Structure (High Level)

- `spec/`: **normative** core specification (source of truth)
- `extensions/`: opt-in extensions (may be empty in this repository)
- `guides/`: **informative** background, explanations, and reading guides
- `rfcs/`: **informative** RFC/proposal process and templates (not requirements)
- Some additional **informative/derivative** materials (templates, examples) may be published separately and are not included in this repository.

## What To Open (Issue vs PR)

- **Typos / clarifications / small edits**: feel free to open a PR directly.
- **Normative changes** (schemas, conformance requirements, semantics): open an issue first so we can align on scope and compatibility.
  - Use the “Spec proposal (RFC-style)” issue template (`.github/ISSUE_TEMPLATE/proposal.yml`) for structured review.
- **Unsure**: open an issue; it’s cheaper than reworking a PR.

## Change Principles (Normative Spec)

- The published **schemas and normative prose must agree** (field names, types, constraints, semantics).
- Prefer **backward-compatible** changes unless there’s a clear, justified break.
- When behavior/requirements change, update `spec/changelog.md` under `[Unreleased]`.
- If a change needs extended discussion, consider adding an RFC under `rfcs/` (see `rfcs/PROPOSALS.md`).

## Proposals (RFC-Style, Informative)

Proposals help review and preserve context for changes that may later land in the normative spec.

- Proposals are **informative** and do not change requirements unless incorporated into `spec/`.
- If you add a proposal, place it in `rfcs/` and use the naming pattern `PROPOSAL-<SHORT-NAME>.md`.
- Include a clear status marker (e.g., **DRAFT**, **SUPERSEDED**) consistent with `rfcs/PROPOSALS.md`.

## Adding Fields to CFSE Artifacts

**Principle:** the YAML schema is the **source of truth** for each artifact type.

### Files to Update

**Required**
- `spec/artifacts/{category}/{artifact}/{artifact}.schema.yaml`: add the field to the schema
- `spec/artifacts/{category}/{artifact}/{artifact}.md`: document the field (tables + guidance)
- `spec/changelog.md`: record the change under `[Unreleased]`

**Recommended**
- Update any relevant templates (if applicable)
- `VERSION`: bump on release (SemVer)

### Step-by-Step

1. Update the schema (`*.schema.yaml`)
   - Add the property under `properties:`
   - If required, add it to `required:`

2. Update the spec documentation (`*.md`)
   - Add the field to the required/optional table
   - Add a short “Field Details” section with usage guidance and pitfalls

3. Update templates (if applicable)
   - Add a placeholder section so users discover the field naturally

4. Update the changelog
   - Add an entry under `[Unreleased]` describing the change

5. Versioning (on release)
   - New optional field: bump **minor** (e.g. `1.0.0` → `1.1.0`)
   - New required field or breaking change: bump **major**
   - Docs-only changes: bump **patch** (optional, depending on release policy)

### Validation Checklist

- Schema is valid YAML (example): `ruby -ryaml -e 'YAML.load_file(ARGV[0])' path/to/schema.yaml`
- Schema `description` is clear and unambiguous
- Spec markdown updated with the same field name/type semantics
- Any relevant templates updated
- Changelog updated

## Governance and Releases

- Governance: `GOVERNANCE.md`
- Maintainers: `MAINTAINERS.md`
- Release process: `RELEASING.md` (primarily maintainer-facing)
