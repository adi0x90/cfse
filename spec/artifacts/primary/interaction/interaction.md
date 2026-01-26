# Interaction Artifact Specification

## Definition

An **Interaction** is an atomic operation between concepts. It represents a single-step action where one concept's entry point is exercised, with precise data flow, trust boundaries, and invariant-backed pre/post conditions.

Interactions are the "verbs" of the CFSE world model. While concepts are the nouns (entities), interactions describe what happens when those entities engage with each other. Each interaction is atomic - it either completes entirely or fails entirely.

**Key principle:** One interaction = one logical operation. If an operation requires multiple steps or can be decomposed into smaller meaningful units, create multiple interactions and compose them into flows.

**Schema:** [`interaction.schema.yaml`](./interaction.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | InteractionID | Unique identifier following pattern `I-<SYSTEM>-<ACTION>-<TARGET>-<NNN>` |
| `name` | string | Human-readable name describing the action |
| `from_concept` | ConceptID | The concept that initiates the interaction (actor/subject) |
| `to_concept` | ConceptID | The concept that receives the interaction (target/object) |
| `action` | ActionType | Type of operation: CREATE, READ, UPDATE, DELETE, ACCESS, EXECUTE, ASSUME, GRANT, REVOKE |
| `entry_points` | EntryPointID[] | Entry point surfaces (`EP-*`) that can trigger this interaction |
| `data_flow` | DataFlowItem[] | What data is read, written, created, or deleted |
| `pre_invariants` | InvariantID[] | Invariants that must hold before execution |
| `post_invariants` | InvariantID[] | Invariants that must hold after execution |
| `error_responses` | ErrorResponse[] | Expected error responses with conditions |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | - | Detailed description of the interaction's purpose |
| `intermediaries` | ConceptID[] | - | Concepts involved in the path but not initiator or target |
| `trust` | TrustBoundary | - | Trust boundary information (inputs, validation, encoding) |
| `key_transformations` | Transformation[] | - | Significant data or state changes |
| `state_transition` | StateTransition | - | State change in the target concept |
| `related_interactions` | RelatedInteractions | - | Prerequisites, subsequent, and alternatives |
| `security_insights` | SecurityInsights | - | Red flags, assumptions, gaps |
| `observability` | Observability | - | Live validation evidence (add only after testing) |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version (e.g., `1.0.0`) |

---

## Field Details

### from_concept and to_concept

These define the interaction's directionality:
- **from_concept**: The actor initiating the action (who does it)
- **to_concept**: The target receiving the action (what it's done to)

For self-referential operations (user updates their own profile), from and to may be the same concept.

**Examples:**
- `from: C-SHOP-USER, to: C-SHOP-ITEM` - User acts on Item
- `from: C-AWS-LAMBDA, to: C-AWS-S3-BUCKET` - Lambda accesses S3
- `from: C-SHOP-USER, to: C-SHOP-USER` - User modifies own profile

### entry_points

Entry points document which **surfaces** can trigger this interaction.

Interactions reference Entry Point artifacts (`EP-*`) by ID. The `EP-*` artifact is the single source
of truth for method/protocol, path/pattern, accepted inputs, and `tangible_locations`.

### data_flow

Documents every data operation using a structured format:

| Property | Required | Description |
|----------|----------|-------------|
| `mode` | Yes | READ, WRITE, CREATE, or DELETE |
| `concept` | Yes | Which concept's data is accessed |
| `attribute` | Yes | The specific attribute or relation |
| `reference` | No | Full reference notation (e.g., `C-SHOP-ITEM.owner_id`) |
| `notes` | No | Additional context |

**Modes:**
- **READ**: Data is retrieved but not modified
- **WRITE**: Existing data is updated
- **CREATE**: New data is inserted
- **DELETE**: Data is removed

### pre_invariants and post_invariants

These are the heart of interaction security:
- **Pre-invariants**: Guards that must hold for execution to proceed
- **Post-invariants**: Guarantees that hold after successful execution

Always reference invariants by ID (`INV-*`) - never inline invariant logic.

**Example:**
```yaml
pre_invariants:
  - INV-SHOP-AUTH-REQUIRED      # User must be authenticated
  - INV-SHOP-OWNER-ONLY         # Only owner can perform this action

post_invariants:
  - INV-SHOP-ITEM-DELETED       # Item no longer exists
  - INV-SHOP-COUNTS-CONSISTENT  # Aggregate counts are updated
```

### error_responses

Documents expected failure modes:

| Property | Required | Description |
|----------|----------|-------------|
| `code` | Yes | HTTP status code (400-599) |
| `condition` | Yes | What triggers this error |
| `response_body` | No | Expected response pattern |
| `related_invariant` | No | Invariant that enforces this condition |

**Common patterns:**
- 401: Authentication required (`INV-*-AUTH-REQUIRED`)
- 403: Not authorized (`INV-*-OWNER-ONLY`, `INV-*-ADMIN-ONLY`)
- 404: Resource not found
- 409: Conflict (state machine violation)
- 422: Validation failure

---

## Key Patterns

- **Atomic operations.** Each interaction is one logical step. Complex processes are flows composed of multiple interactions.

- **Clear directionality.** Always identify who initiates (from) and who/what receives (to). The actor may be explicit (user) or implicit (service).

- **Complete data flow.** Document every read and write. If the interaction checks ownership, document the ownership attribute being read.

- **Invariant-backed conditions.** Pre and post conditions reference the invariant library (see `artifacts/supporting/invariant_library/invariant_library.md`) - never inline security logic.

- **Error responses map to invariants.** Each error condition should connect to an invariant being enforced.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Combining multiple operations | Loses atomicity, harder to test, unclear failure modes | Split into separate interactions |
| [ ] Missing data flow entries | Incomplete security analysis, hidden data access | Document every read/write operation |
| [ ] Inlining invariant logic | Violates single source of truth | Reference `INV-*` IDs only |
| [ ] Forgetting error responses | Incomplete specification, missing security controls | Add all expected error conditions |
| [ ] Omitting intermediary concepts | Missing trust boundaries and attack surface | Include auth services, caches, queues |
| [ ] Adding observability without live testing | Speculative evidence, may be incorrect | Only add after validating on live system |

---

## Example: I-SHOP-DELETE-ITEM-001

```yaml
id: I-SHOP-DELETE-ITEM-001
name: "User Deletes Own Item"
description: >
  A logged-in user deletes an item they own from the marketplace.
  The item must exist and belong to the requesting user.

from_concept: C-SHOP-USER
to_concept: C-SHOP-ITEM
action: DELETE

entry_points:
  - EP-SHOP-ITEM-API-DELETE

data_flow:
  - mode: READ
    concept: C-SHOP-ITEM
    attribute: owner_id
    reference: "C-SHOP-ITEM.owner_id"
    notes: "Verify ownership before deletion"

  - mode: READ
    concept: C-SHOP-ITEM
    attribute: status
    reference: "C-SHOP-ITEM.status"
    notes: "Check item is not already deleted"

  - mode: WRITE
    concept: C-SHOP-ITEM
    attribute: status
    reference: "C-SHOP-ITEM.status"
    notes: "Set to DELETED"

  - mode: WRITE
    concept: C-SHOP-ITEM
    attribute: deleted_at
    reference: "C-SHOP-ITEM.deleted_at"
    notes: "Record deletion timestamp"

trust:
  user_input:
    - "item_id from path parameter"
  validation_points:
    - "UUID format validation"
    - "Ownership verification in service layer"
  boundary_crossings:
    - label: "auth"
      from: "public"
      to: "authenticated"
      notes: "Bearer token required"

key_transformations:
  - type: STATE_CHANGE
    description: "Item transitions to deleted state"
    from_state: "ACTIVE"
    to_state: "DELETED"

state_transition:
  concept: C-SHOP-ITEM
  from: "ACTIVE"
  to: "DELETED"
  guard: INV-SHOP-OWNER-ONLY
  effects:
    - "Item hidden from marketplace listings"
    - "User item count decremented"

related_interactions:
  prerequisite:
    - I-SHOP-LOGIN-USER-001
  subsequent:
    - I-SHOP-LIST-ITEMS-001
  alternative:
    - I-SHOP-ARCHIVE-ITEM-001

pre_invariants:
  - INV-SHOP-AUTH-REQUIRED
  - INV-SHOP-OWNER-ONLY
  - INV-SHOP-ITEM-EXISTS

post_invariants:
  - INV-SHOP-ITEM-DELETED
  - INV-SHOP-USER-COUNTS-CONSISTENT

error_responses:
  - code: 401
    condition: "No valid authentication token"
    response_body: '{"error": "Authentication required"}'
    related_invariant: INV-SHOP-AUTH-REQUIRED

  - code: 403
    condition: "User does not own the item"
    response_body: '{"error": "Forbidden: Not item owner"}'
    related_invariant: INV-SHOP-OWNER-ONLY

  - code: 404
    condition: "Item does not exist or already deleted"
    response_body: '{"error": "Item not found"}'
    related_invariant: INV-SHOP-ITEM-EXISTS

  - code: 409
    condition: "Item has pending transactions"
    response_body: '{"error": "Cannot delete item with pending transactions"}'

security_insights:
  red_flags:
    - "IDOR if item_id not validated against authenticated user"
    - "Race condition if checking ownership and deleting are not atomic"
  assumptions:
    - "Auth middleware correctly extracts user from token"
    - "Item ownership is immutable once set"
  gaps:
    - "No rate limiting on delete operations"
  external_dependencies:
    - "Authentication service for token validation"

status: ACTIVE
version: "1.0.0"
```

---

## Validation Criteria

A valid interaction artifact MUST:

1. **Have a unique ID** matching pattern `I-<SYSTEM>-<ACTION>-<TARGET>-<NNN>`
2. **Have valid from_concept and to_concept** that reference existing concepts
3. **Have a valid action type** from the ActionType enum
4. **Have at least one entry point** referencing an `EP-*` artifact
5. **Have at least one data flow item** documenting data access
6. **Have at least one pre_invariant** guarding the interaction
7. **Have at least one post_invariant** guaranteeing outcomes
8. **Have at least one error response** documenting failure modes
9. **Reference only valid invariant IDs** (no inline logic)
10. **Use appropriate HTTP status codes** in error responses (400-599)

---

## State-Aware Interactions

When an interaction performs a state transition:

1. **Declare the transition explicitly** in `state_transition`
2. **Reference guard invariants** in `pre_invariants`
3. **Reference effect invariants** in `post_invariants`
4. **Document side effects** in `key_transformations`

For access-only interactions (no state change), pre-invariants should assert the prerequisite state.

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Entry Point Artifact](../../supporting/entry_point/entry_point.md) - Surfaces that trigger interactions
- [Concept Artifact](../concept/concept.md) - Entities that participate in interactions
- [Flow Artifact](../flow/flow.md) - Multi-step sequences composed of interactions
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Security rules that govern interactions

---

## Common Pitfalls

- Encoding multi-step sequences as a single interaction (should be a Flow of multiple Interactions).
- Mixing policy logic into the interaction description instead of referencing `INV-*` for rules.
- Omitting the concrete surface(s) (`EP-*`) that can trigger the interaction in the real system.
