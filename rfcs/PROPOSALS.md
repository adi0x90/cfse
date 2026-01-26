# RFCs / Proposals

This directory defines the process and format for CFSE **RFCs / proposals**: non-normative documents used to discuss, review, and preserve context for changes that may later be incorporated into the **normative** specification under `spec/`.

Important: RFCs are **not requirements**. Only text and schemas under `spec/` are normative.

## When to Write an RFC

Use an RFC when a change is large enough that reviewing a PR alone would be expensive or contentious, for example:

- new artifact types or major schema shape changes
- changes to conformance, traceability, or interpretation rules
- re-structuring normative sections
- anything with meaningful backward-compatibility / migration implications

For small fixes (typos, clarifications that do not change requirements), open a PR directly.

## Where RFCs Live

- RFC process and guidance: `rfcs/PROPOSALS.md` (this file)
- RFC discussions start as GitHub issues using the “Spec proposal (RFC-style)” template: `.github/ISSUE_TEMPLATE/proposal.yml`
- This repository may include **zero or more** RFC documents. If an RFC archive is not present, issues still serve as the canonical discussion record.

## Status Keywords

Use a clear status marker near the top of an RFC:

- **DRAFT**: Under active discussion; may change substantially.
- **ACCEPTED**: Accepted in principle; implementation work may be in progress.
- **REJECTED**: Closed without acceptance (keep for historical context).
- **SUPERSEDED**: Replaced by a newer RFC or by normative text elsewhere.
- **IMPLEMENTED**: Landed in `spec/` (link to the PR(s) and/or release tag).

## RFC File Naming

If you add an RFC document, use:

- `PROPOSAL-<SHORT-NAME>.md` (all caps, hyphen-separated)

Examples:

- `PROPOSAL-ENTRY-POINT-ARTIFACT.md`
- `PROPOSAL-PARSABLE-CONDITIONS.md`

## Suggested RFC Template

Copy/paste this outline:

```markdown
# PROPOSAL-<SHORT-NAME>

> **Authors:** <name or handle>
> **Created:** YYYY-MM-DD
> **Target:** (optional) vX.Y.Z or "TBD"

## Summary

## Motivation / Problem Statement

## Non-Goals

## Proposed Changes (Normative)

### Schemas
- Files:
  - `spec/artifacts/.../<artifact>.schema.yaml`
- Changes:
  - (list exact fields/constraints)

### Normative Prose
- Files:
  - `spec/...`
- Changes:
  - (describe exact requirement/semantic changes)

## Backward Compatibility
- Impact on existing corpora/tools
- Migration guidance

## Security Considerations

## Alternatives Considered

## Open Questions

## References
- Links to issues/PRs
```

## Review Checklist (for RFC authors)

- Clearly states what is normative vs informative.
- Identifies every file in `spec/` that would change if adopted.
- Includes compatibility impact and migration guidance where relevant.
- Avoids making requirements outside `spec/`.
- If adopted, plan to add an entry to `spec/changelog.md` under `[Unreleased]`.
