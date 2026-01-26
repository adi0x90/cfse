# Governance

This document defines how the CFSE specification is maintained and how decisions are made.

## Scope

This repository publishes the CFSE specification:

- `spec/` (normative) is the source of truth for CFSE core requirements, schemas, and semantics.
- Optional extensions may be published separately (this repository may or may not include any).
- `guides/` and `rfcs/` are informative and non-binding.

## Roles

- **Maintainers**: steward the spec, review changes, cut releases, and manage governance documents.
- **Contributors**: propose changes via issues and pull requests.

The current maintainers are listed in `MAINTAINERS.md`.

## Decision Process

1. **Small changes** (typos, clarifications that do not change requirements)
   - Can be merged via normal PR review.
2. **Spec changes** (new fields, schema changes, conformance/traceability changes)
   - MUST include:
     - A written rationale
     - Updates to both schema and normative prose (where applicable)
     - An entry in `spec/changelog.md`
   - SHOULD include a migration note if it affects existing corpora.
3. **Major changes** (breaking changes, new conformance levels, major restructures)
   - SHOULD start with an RFC in `rfcs/` or a tracked design issue.
   - MUST have maintainer consensus.

If maintainers disagree, maintainers will attempt to reach consensus. If consensus cannot be reached, the default is to defer the change.

## Normative vs Informative

- Normative requirements use RFC 2119 keywords (MUST/SHOULD/MAY).
- Informative text provides guidance and examples and is non-binding.

When in doubt, `spec/` is normative unless a section is explicitly labeled “Non-Normative”.

## Releases

Releases follow Semantic Versioning and are documented in `spec/changelog.md`. The release process is defined in `RELEASING.md`.
