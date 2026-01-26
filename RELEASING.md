# Releasing CFSE

This document defines the release process for the CFSE specification.

## Versioning

CFSE follows Semantic Versioning:

- **MAJOR**: breaking changes to schemas, conformance requirements, or meaning of normative terms/fields
- **MINOR**: backward-compatible additions (e.g., new optional fields, new artifact types that do not break existing corpora)
- **PATCH**: clarifications, examples, typos, non-normative additions, or other changes that do not change requirements

The current version is stored in `VERSION` and mirrored in key docs.

## Pre-release tags (optional)

If you want to publish release candidates:

- `v1.0.0-rc.1`, `v1.0.0-rc.2`, etc.

## Release Checklist

1. **Update changelog**
   - Move relevant entries from `spec/changelog.md` `[Unreleased]` into a new version section.
   - Use an ISO date (`YYYY-MM-DD`) for the release.

2. **Bump version**
   - Update `VERSION`.
   - Update any version strings that are intended to be user-facing (at minimum: `README.md`, `spec/README.md`, `ARCHITECTURE.yml`).

3. **Sanity checks**
   - Ensure schemas are valid and self-consistent.
   - Ensure the spec navigation and links are not broken.

4. **Tag and release**
   - Create a git tag `vX.Y.Z`.
   - Publish GitHub Release notes from `spec/changelog.md`.

5. **Post-release**
   - Ensure `[Unreleased]` exists for future work.

