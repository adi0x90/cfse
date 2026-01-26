# Invariant Library Specification

## Definition

An **Invariant Library** is a single YAML document that contains a set of CFSE **Predicates** (`P-*`) and **Invariants** (`INV-*`) for a system.

This format exists to support large-scale corpora where storing each invariant as a separate file would create thousands of files, while still keeping invariants and predicates **first-class** (schema-valid, ID-addressable, and independently referenceable by `INV-*` / `P-*`).

**Schema:** [`invariant_library.schema.yaml`](./invariant_library.schema.yaml)

---

## Canonicality and Source of Truth

- The **source of truth** for invariants and predicates is their **schema-defined object shape** (see `predicate.schema.yaml` and `invariant.schema.yaml`).
- The Invariant Library YAML format is a **canonical packaging** of those same objects into a single file.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `predicates` | Predicate[] | List of Predicate objects (each must conform to Predicate schema) |
| `invariants` | Invariant[] | List of Invariant objects (each must conform to Invariant schema) |

---

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `cfse` | object | Metadata block for version/system ownership |
| `metadata` | object | Implementation-defined metadata (not used for CFSE semantics) |

---

## Suggested Conventions

- One Invariant Library file per system, e.g.:
  - `invariants/SHOP.invariant-library.yaml`
  - `invariants/AWS.invariant-library.yaml`
- If a single file becomes contentious or too large, split by domain while keeping “few files”:
  - `invariants/SHOP.authn.invariant-library.yaml`
  - `invariants/SHOP.authz.invariant-library.yaml`

---

## Validation Requirements

A validator that supports Invariant Library YAML MUST enforce:

1. **Schema validity**
   - Every entry in `predicates[]` MUST validate against the Predicate schema.
   - Every entry in `invariants[]` MUST validate against the Invariant schema.
2. **Uniqueness**
   - Predicate IDs (`P-*`) MUST be unique within the file.
   - Invariant IDs (`INV-*`) MUST be unique within the file.
3. **Logic syntax**
   - Every invariant’s `logic` MUST be syntactically valid per `grammar/03-formal-logic.md`.
4. **Predicate composition**
   - For each invariant, every `P-*` referenced in `logic` MUST:
     - appear in that invariant’s `predicates[]` list (traceability), AND
     - resolve to a predicate defined in `predicates[]` in the same file OR in the enclosing corpus.
5. **No duplicate definitions across formats**
   - A corpus MUST NOT define the same `INV-*` or `P-*` ID in multiple places (e.g., both in an invariant library file and as standalone `INV-*.yaml` / `P-*.yaml` artifacts). Validators MUST treat duplicates as errors.

---

## Example

```yaml
cfse:
  version: "1.0.0"
  system: "SHOP"

predicates:
  - id: P-SHOP-IS-OWNER
    name: "Is Resource Owner"
    parameters:
      - name: user
        type: C-SHOP-USER
      - name: item
        type: C-SHOP-ITEM
    returns: boolean
    definition: "True if user.id equals item.owner_id"

invariants:
  - id: INV-SHOP-OWNER-DELETE
    rule: "Only the owner of an item can delete it."
    logic: |
      FORALL user: C-SHOP-USER.
        FORALL item: C-SHOP-ITEM.
          DELETE(user, item) IMPLIES P-SHOP-IS-OWNER(user, item)
    predicates:
      - P-SHOP-IS-OWNER
    criticality: P1
    tags: [authz, ownership]
```

---

## Common Pitfalls

- Defining duplicate `P-*` or `INV-*` IDs across multiple files (validators should treat as errors).
- Referencing predicates in invariant `logic` without listing them in `predicates[]`.
- Mixing core and extension fields without namespacing under `extensions.<extension_name>`.
