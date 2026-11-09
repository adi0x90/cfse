# Artifact Lifecycle Specification

## Overview

CFSE artifacts using `ArtifactStatus` follow the lifecycle below. Patches use their separate 4V `PatchStatus` workflow; Invariant Library containers carry the lifecycle on their individual entries. This specification defines the lifecycle states and transition rules that govern artifact authority and usage.

---

## Shared lifecycle fields

Every artifact with `ArtifactStatus` accepts the following top-level metadata. Omitted `status` means `DRAFT`; defaults are interpretations, not fields a validator silently inserts.

| Field | Requirement |
|-------|-------------|
| `status` | Optional; one of the states below |
| `version` | Required for `ACTIVE`; a `major.minor.patch` string with optional prerelease suffix |
| `approved` | Required for `ACTIVE`; a quoted calendar date (`YYYY-MM-DD`) |
| `deprecated_date` | Required for `DEPRECATED`; a quoted calendar date |
| `superseded_by` | Optional ArtifactID; must resolve when supplied |
| `deprecation_reason` | Optional nonblank explanation |

Presence of an approval date is a record requirement, not proof that a review occurred. Dates must be real calendar dates. Quote dates in YAML so that serializers preserve string values. Other metadata fields are governed by the individual artifact schema; these examples show lifecycle fragments, not complete artifacts.

## State Definitions

### ArtifactStatus Enumeration

| State | Description | Authoritative |
|-------|-------------|---------------|
| `DRAFT` | Initial creation, not reviewed | No |
| `REVIEW` | Under review | No |
| `PLANNED` | Approved future state (not yet current reality) | No |
| `ACTIVE` | Approved and in use | Yes |
| `DEPRECATED` | Being phased out | Partial |
| `ARCHIVED` | No longer in use | No |

---

## DRAFT

### Definition

The `DRAFT` state indicates that an artifact is work in progress and not yet authoritative.

### Semantic Interpretation

When an artifact is in `DRAFT` state:

1. Content is incomplete or unvalidated
2. The artifact MUST NOT be used as authoritative reference
3. Other artifacts SHOULD NOT reference draft artifacts in production
4. The artifact is subject to significant change without notice

### Usage Criteria

An artifact SHOULD be marked `DRAFT` when ANY of the following conditions apply:

- Initial creation, content not complete
- Significant revision underway
- Awaiting review or validation
- Experimental or prototype content

### Allowed References

| Referencing Artifact State | Can Reference DRAFT? |
|---------------------------|---------------------|
| DRAFT | YES |
| REVIEW | YES |
| PLANNED | SHOULD NOT |
| ACTIVE | NO (SHOULD NOT) |
| DEPRECATED | NO |
| ARCHIVED | NO |

### Example

```yaml
---
id: C-AWS-LAMBDA-FUNCTION
status: DRAFT
version: 0.1.0
---
```

### Transition Rules

From `DRAFT`, an artifact MAY transition to:

- `REVIEW` - When ready for review
- `ACTIVE` - After review and approval
- `DEPRECATED` - If abandoned before activation (rare)

---

## REVIEW

### Definition

The `REVIEW` state indicates that an artifact is complete enough to review, but is not yet authoritative.

### Transition Rules

From `REVIEW`, an artifact MAY transition to:

- `ACTIVE` - After approval
- `DRAFT` - If significant revision is needed

---

## PLANNED

### Definition

The `PLANNED` state indicates that an artifact represents an approved future state, but is not yet current reality.

This is useful for modeling changes ahead of implementation (e.g., feature branches, planned migrations).

### Semantic Interpretation

When an artifact is in `PLANNED` state:

1. Content SHOULD be complete and reviewable
2. The artifact MUST NOT be treated as the current authoritative source for “what exists today”
3. Other `PLANNED` artifacts MAY reference it
4. `ACTIVE` artifacts SHOULD NOT reference it (to avoid mixing planned state into current reality)

### Transition Rules

From `PLANNED`, an artifact MAY transition to:

- `ACTIVE` - When the planned state becomes current reality
- `DEPRECATED` - If the plan is superseded before becoming active

---

## ACTIVE

### Definition

The `ACTIVE` state indicates that an artifact is approved, in use, and authoritative.

### Semantic Interpretation

When an artifact is in `ACTIVE` state:

1. Content is complete and validated
2. The artifact is the authoritative reference for its subject
3. Other artifacts SHOULD reference active artifacts
4. Changes MUST follow versioning and review processes

### Usage Criteria

An artifact MUST be marked `ACTIVE` when ALL of the following conditions are met:

- Content is complete and accurate
- Artifact has been reviewed and approved
- Artifact is the current authoritative source
- Artifact is actively used in explorations or referenced by other artifacts

### Allowed References

| Referencing Artifact State | Can Reference ACTIVE? |
|---------------------------|----------------------|
| DRAFT | YES |
| REVIEW | YES |
| PLANNED | YES |
| ACTIVE | YES |
| DEPRECATED | YES |
| ARCHIVED | NO |

### Example

```yaml
---
id: INV-FILE-OWNER-DELETE
status: ACTIVE
version: 1.0.0
approved: "2025-01-12"
---
```

### Transition Rules

From `ACTIVE`, an artifact MAY transition to:

- `DEPRECATED` - When superseded or no longer applicable
- `DRAFT` - Only for major revision (creates new version branch)

---

## DEPRECATED

### Definition

The `DEPRECATED` state indicates that an artifact is being phased out and should not be used for new work.

### Semantic Interpretation

When an artifact is in `DEPRECATED` state:

1. Content remains valid but is being superseded
2. Existing references MAY continue but SHOULD be updated
3. New artifacts MUST NOT reference deprecated artifacts
4. A successor artifact SHOULD be identified

### Usage Criteria

An artifact SHOULD be marked `DEPRECATED` when ANY of the following conditions apply:

- A newer version or replacement exists
- The subject matter is no longer applicable
- The artifact contains outdated information
- Security policy has changed, invalidating the artifact

### Deprecation Requirements

When deprecating an artifact:

1. A `deprecated_date` MUST be recorded
2. A `superseded_by` reference SHOULD be provided when applicable
3. A deprecation notice SHOULD explain the reason
4. Dependent artifacts SHOULD be notified/updated

### Allowed References

| Referencing Artifact State | Can Reference DEPRECATED? |
|---------------------------|--------------------------|
| DRAFT | SHOULD NOT |
| REVIEW | SHOULD NOT |
| PLANNED | SHOULD NOT |
| ACTIVE | SHOULD NOT (migrate) |
| DEPRECATED | MAY (legacy chains) |
| ARCHIVED | NO |

### Example

```yaml
---
id: INV-LEGACY-AUTH-CHECK
status: DEPRECATED
version: 1.0.0
deprecated_date: "2025-01-20"
superseded_by: INV-MODERN-AUTH-CHECK
deprecation_reason: "Legacy authentication flow replaced with OAuth 2.0"
---
```

### Transition Rules

From `DEPRECATED`, an artifact MAY transition to:

- `ARCHIVED` - When all references have been migrated
- `ACTIVE` - If deprecation is reversed (rare, requires justification)

---

## State Transition Diagram

```
+----------+     review      +---------+
|  DRAFT   | --------------> | REVIEW  |
+----+-----+                 +----+----+
     |                            |
     |                            | approve
     |                            v
     |    +----------+       +----+----+
     +--->|  ACTIVE  |<------| ACTIVE  |
          +----+-----+       +---------+
               |
               | supersede
               v
          +----+-----+      archive     +----------+
          |DEPRECATED| --------------> | ARCHIVED |
          +----------+                 +----------+
```

### Simplified Transition Matrix

| From State | To State | Trigger | Requirements |
|------------|----------|---------|--------------|
| DRAFT | REVIEW | Review started | Artifact is ready for review |
| REVIEW | ACTIVE | Approval | Review complete, content valid |
| REVIEW | DRAFT | Rework | Significant revision needed |
| DRAFT | DEPRECATED | Abandonment | Documented reason |
| ACTIVE | DEPRECATED | Supersession | Successor identified |
| ACTIVE | DRAFT | Major revision | Creates version branch |
| DEPRECATED | ARCHIVED | Migration complete | No active references |
| DEPRECATED | ACTIVE | Reversal | Justification documented |

---

## Governance Considerations

### Authority Levels

| State | Write Access | Reference Authority | Usage in Production |
|-------|--------------|--------------------|--------------------|
| DRAFT | Author | None | Prohibited |
| REVIEW | Maintainer + Review | None | Prohibited |
| PLANNED | Maintainer + Review | Planned only | Prohibited as current reality |
| ACTIVE | Maintainer + Review | Full | Permitted |
| DEPRECATED | Maintainer | Historical only | Migrate away |
| ARCHIVED | Maintainer | None | Prohibited |

### Version Management

1. `DRAFT` artifacts MAY use pre-release versions (e.g., `0.1.0`, `1.0.0-alpha`)
2. `ACTIVE` artifacts MUST use semantic versioning (e.g., `1.0.0`, `1.1.0`)
3. `DEPRECATED` artifacts retain their final version number
4. Version changes within `ACTIVE` state follow semver rules

### Audit Requirements

| State Transition | Audit Required | Approval Required |
|------------------|----------------|-------------------|
| REVIEW -> ACTIVE | Yes | Yes |
| ACTIVE -> DEPRECATED | Yes | Yes |
| DEPRECATED -> ARCHIVED | No | No |
| any -> DRAFT (revision) | Yes | Depends on scope |

---

## Artifact-Specific Lifecycle Rules

### Concepts

- SHOULD remain `ACTIVE` as long as the concept exists in the system
- Deprecation implies concept removal from system model

### Invariants

- MUST be `ACTIVE` to be used in explorations
- Deprecation requires review of all dependent scenarios

### Findings

- SHOULD transition: DRAFT -> ACTIVE -> (resolved) -> ARCHIVED
- `DEPRECATED` is typically not used for Findings

### Patches

- MUST reference exactly one Finding
- Lifecycle tracks with the Finding it addresses

---

## Common Mistakes

Review this checklist when managing lifecycle states:

### DRAFT Mistakes

- [] Using DRAFT artifacts as authoritative references in production
- [] Leaving artifacts in DRAFT state indefinitely without review
- [] Not documenting the reason for DRAFT status

### ACTIVE Mistakes

- [] Marking artifacts ACTIVE without proper review
- [] Making breaking changes to ACTIVE artifacts without versioning
- [] Not updating dependent artifacts when ACTIVE content changes

### DEPRECATED Mistakes

- [] Deprecating without providing a successor reference
- [] Not communicating deprecation to artifact consumers
- [] Creating new references to deprecated artifacts
- [] Leaving deprecated artifacts without migration plan

### General Mistakes

- [] Not recording state transition timestamps
- [] Skipping required approvals for state transitions
- [] Not maintaining version history across transitions

---

## Validation Rules

### Schema Compliance

Each artifact schema declares the shared metadata properties and applies the `ArtifactLifecycle` constraints from [the grammar schema](../grammar/schemas/grammar.schema.yaml). `status` is optional with interpreted default `DRAFT`; `ACTIVE` requires `version` and `approved`, and `DEPRECATED` requires `deprecated_date`. The artifact schema remains authoritative for all other fields.

### Consistency Checks

Validators MUST enforce:

1. `ACTIVE` artifacts MUST have `version` and an `approved` date
2. `DEPRECATED` artifacts MUST have a `deprecated_date`
3. `DEPRECATED` artifacts SHOULD have `superseded_by` when applicable
4. References to `DEPRECATED` artifacts MUST generate warnings
5. References from `ACTIVE` to `DRAFT` MUST generate errors

---

## Related Specifications

- [[../grammar/04-field-types]] - ArtifactStatus enum definition
- [[04-traceability]] - Reference rules between artifacts
- [[01-invariant-states]] - Invariant-specific states
- [[02-exploration-verdicts]] - Exploration-specific outcomes
