# Entry Point (EP) Artifact Specification

## Definition

An **Entry Point** is a first-class description of a **surface**: a concrete way the system can be exercised (API endpoint, web route, GraphQL operation, CLI command, event trigger).

Entry Points are the single source of truth for:

- How a surface is accessed (method/protocol + path/pattern)
- What inputs it accepts (`parameters`, optional attacker-controlled classification)
- Where it is visible/exercisable in the real world (`tangible_locations`)
- What it can expose in some context (`exposes`, viewer-agnostic superset; no policy logic)
- Which invariants govern the surface (traceability only; invariants carry the logic)

**Schema:** [`entry_point.schema.yaml`](./entry_point.schema.yaml)

---

## Why EP is a Standalone Artifact

CFSE previously defined entry points inline inside Concepts/Interactions and introduced a separate “exposure inventory” artifact.

Making `EP-*` standalone:

- eliminates duplication/drift of `tangible_locations` and surface metadata
- enables “file-per-surface” authoring (critical for large systems)
- allows PRJ projections to reference surfaces directly without a second “exposure inventory” layer

---

## Relationship to Other Artifacts

- **Concept (`C-*`)** references one or more `EP-*` surfaces that belong to the concept.
- **Interaction (`I-*`)** references one or more `EP-*` surfaces as triggers for the interaction.
- **Projection (`PRJ-*`) (optional)** references one or more `EP-*` surfaces and documents viewer-context-specific visibility.
- **Invariant (`INV-*`)** remains the single source of truth for policy logic; EP uses invariants only for traceability.
- **Trace (`T-*`)** can use `EP-*` as a stable anchor when capturing ordered evidence for temporal/ordering claims.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | EntryPointID | Unique identifier `EP-*` |
| `title` | string | Human-readable name |
| `owner_concept` | ConceptID | Concept that owns the surface |
| `method` | string | Method/protocol/trigger type |
| `path` | string | Path/pattern / operation / event name |
| `action` | ActionType | CREATE/READ/UPDATE/DELETE/etc. |

---

## Optional Fields (Selected)

- `tangible_locations[]`: concrete locators (URLs, CLI invocations)
- `parameters[]`: inputs accepted
- `attacker_controlled_inputs[]`: descriptive threat-modeling metadata
- `exposes[]`: viewer-agnostic exposure inventory (superset)
- `governed_by_invariants[]`: traceability-only invariant references

---

## Example

```yaml
id: EP-SHOP-ORDERS-WEB-LIST
title: "Orders list page"
owner_concept: C-SHOP-ORDER
method: GET
path: "/orders"
action: READ
auth_required: true

tangible_locations:
  - kind: web_url
    web_url_template: "https://{host}/orders"
    example_urls:
      - "https://shop.example.com/orders"

attacker_controlled_inputs:
  - "page"
  - "sort"

exposes:
  - ref: C-SHOP-ORDER.id
    exposure_mode: DISCLOSE
  - ref: C-SHOP-ORDER.total_amount
    exposure_mode: DISCLOSE
    governed_by_invariants:
      - INV-SHOP-ORDER-READ-AUTHZ

governed_by_invariants:
  - INV-SHOP-ORDER-READ-AUTHZ

status: DRAFT
version: "1.0.0"
```

---

## Common Pitfalls

- Treating entry points as prose-only paths; use stable `EP-*` artifacts to reduce drift.
- Encoding policy logic directly in entry points; use invariants (`INV-*`) as SSOT for enforcement logic.
- Omitting `tangible_locations` when reproducibility and scoping depend on concrete locators.
