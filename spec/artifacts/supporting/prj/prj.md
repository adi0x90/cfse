# Projection (PRJ) Artifact Specification

## Definition

A **PRJ** artifact describes **what a specific viewer context sees** across one or more entry points.

Entry Points (`EP-*`) can optionally include a viewer-agnostic exposure inventory (`exposes[]`, a superset). PRJ (`PRJ-*`) is viewer-specific (a slice): it binds an audience definition (role/relationship/tenancy context) to a set of surfaces and documents what is visible in that context.

## Purpose

PRJ enables:

- Auditable, reproducible “who can see what” documentation
- Systematic privacy/access-control analysis across multiple surfaces
- Traceability to the invariants that govern viewer-specific visibility

## Core Principles

- **Invariants are SSOT for logic.** PRJ MUST NOT encode executable visibility rules.
- **Viewer context is label + reference based.** Use tags and references (`INV-*`, `P-*`) for traceability.
- **Composes from EP.** PRJ references entry points (`EP-*`) and MAY optionally list visible exposures as a viewer-specific slice.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ProjectionID | Unique identifier following pattern `PRJ-*` |
| `title` | string | Human-readable name |
| `viewer_context` | object | Viewer definition (label + reference based; no executable logic) |
| `surfaces` | SurfaceRef[] | Entry point surfaces included in this projection |

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `assumptions` | object | - | Traceability references to `P-*` / `INV-*` used to define the projection’s context |
| `visible` | Exposure[] | - | Optional explicit “what is visible” listing |
| `notes` | string | - | Additional notes |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version |
| `extensions` | Extensions | - | Extension-specific fields |

---

## Schema

**Schema:** [`prj.schema.yaml`](./prj.schema.yaml)

---

## Common Pitfalls

- Encoding executable policy logic in PRJ; invariants are SSOT for logic.
- Treating PRJ as required for core conformance; it is optional unless a profile/extension requires it.
- Duplicating entry point surface metadata in PRJ instead of referencing `EP-*`.
