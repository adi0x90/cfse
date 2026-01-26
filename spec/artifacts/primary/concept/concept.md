# Concept Artifact Specification

## Definition

A **Concept** is a foundational building block of the CFSE world model. Concepts represent the "nouns" of your system: entities, resources, principals, credentials, and other logical units that participate in security-relevant operations.

Concepts are NOT implementation artifacts (classes, tables, services). A single concept may span multiple implementation components. Concepts capture how users and security analysts think about the system - one concept equals one distinct "thing" that matters for security analysis.

**Schema:** [`concept.schema.yaml`](./concept.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ConceptID | Unique identifier following pattern `C-<SYSTEM>-<NAME>` |
| `name` | string | Human-readable name using domain terminology |
| `promise` | string | Single sentence describing what the concept represents and its security significance |
| `attributes` | Attribute[] | Data properties with types, constraints, and security metadata |
| `entry_points` | EntryPointID[] | References to `EP-*` Entry Point artifacts owned by this concept |
| `invariants` | InvariantID[] | List of invariant IDs (`INV-*`) that govern this concept |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `states` | StateMachine | - | Lifecycle states and transitions if concept has discrete states |
| `how_it_works` | string | - | High-level description of internal mechanisms and potential implementation patterns |
| `security_investigation_candidates` | string[] | - | Potential weaknesses, fragility points, or security areas worth exploring |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status: DRAFT, REVIEW, PLANNED, ACTIVE, DEPRECATED, ARCHIVED |
| `version` | string | - | Semantic version (e.g., `1.0.0`) |

---

## Field Details

### promise

The promise is a single sentence that captures the essence of the concept. It should answer:
- What is this thing?
- What role does it play in security?
- Why does it matter?

A good promise is specific enough to differentiate this concept from others, yet general enough to cover all instances.

**Examples:**
- Good: "A user account that can authenticate, own resources, and perform actions within the shop system."
- Bad: "A user." (Too vague)
- Bad: "A database record in the users table with columns id, email, password_hash, created_at, and associated orders." (Implementation detail)

### attributes

Attributes define the data properties of the concept. Each attribute includes:

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Attribute name in snake_case |
| `type` | Yes | Data type: string, integer, boolean, array, object, uuid, timestamp, enum |
| `required` | No | Whether attribute must be present (default: true) |
| `default` | No | Default value when not set |
| `sensitive` | No | Contains PII, secrets, or other sensitive data (default: false) |
| `immutable` | No | Cannot be changed after creation (default: false) |
| `description` | No | Human-readable description |
| `constraints` | No | Validation constraints |
| `enum_values` | No | Allowed values when type is enum |

**Security-relevant attributes** should be marked with `sensitive: true`. This enables:
- Proper handling in logs and error messages
- Data classification for compliance
- Encryption requirements identification

### entry_points

Concepts list the entry points (surfaces) they own as references to Entry Point artifacts (`EP-*`).

The `EP-*` artifact is the single source of truth for surface metadata:
method/protocol, path/pattern, `tangible_locations`, accepted inputs, and optional exposure inventory (`exposes[]`).

Concepts SHOULD:
- Include every `EP-*` whose `owner_concept` is this concept.
- Avoid duplicating method/path/locations here; keep them on the `EP-*` artifact.

#### Entry Point ID Convention (Recommended)

Entry Point IDs SHOULD follow this convention to keep ownership and traceability obvious:

`EP-<SYSTEM>-<CONCEPT>-<CHANNEL>-<ACTION>[-<NN>]`

- Other artifacts SHOULD reference Entry Points by ID (never restate them as prose-only paths).

### invariants

Invariants are referenced by ID only - never inline invariant logic in concept documents. This ensures:
- Single source of truth for security rules
- Consistent application across artifacts
- Easier maintenance and updates

**Correct:**
```yaml
invariants:
  - INV-SHOP-OWNER-ONLY
  - INV-SHOP-AUTH-REQUIRED
```

**Incorrect:**
```yaml
invariants:
  - rule: "Only owners can delete their items"
    logic: "FORALL item: C-SHOP-ITEM. DELETE(user, item) IMPLIES user.id == item.owner_id"
```

### how_it_works

A high-level description of how the concept operates internally. This is NOT implementation code, but rather a logical summary of:
- The underlying mechanism or algorithm
- Key implementation patterns or approaches
- How the concept achieves its security properties

This field helps analysts understand the concept deeply enough to identify potential security weaknesses.

**Examples:**
- Good: "Authentication tokens are generated using HMAC-SHA256 with a server-side secret. Tokens include the user ID, expiration timestamp, and a nonce. Validation checks signature integrity, expiration, and revocation status against a Redis blacklist."
- Bad: "Uses JWT." (Too vague)
- Bad: The actual source code (Implementation detail)

### security_investigation_candidates

A bullet-point list of potential security areas worth exploring for this concept. These are hypotheses about what could go wrong - they feed directly into invariant definition and scenario creation.

Each candidate should identify:
- A potential weakness or fragility point
- Why it might be exploitable
- What type of attack it might enable

**Examples:**
```yaml
security_investigation_candidates:
  - "Token expiration bypass - what if system clock is manipulated?"
  - "Race condition in balance updates - concurrent purchases might overdraw"
  - "Email verification bypass - can unverified accounts access protected resources?"
  - "Role escalation through parameter tampering - is role validated server-side?"
```

---

## Key Patterns

- **One concept = one logical entity.** If users think of "User" and "Admin" as the same kind of thing with different permissions, they are one concept with a role attribute, not two concepts.

- **Attributes reflect security-relevant state.** Include attributes that affect authorization decisions, audit requirements, or data sensitivity - not every database column.

- **Entry points map to attack surface.** Each entry point is a potential target for security testing. Document all ways to interact with the concept.

- **Invariants govern, concepts don't.** Concepts reference invariants; they don't define security rules. Keep concepts as "data models" and invariants as "security policies."

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Creating concepts for user roles | Roles are attributes of a User concept, not separate concepts | Use a `role` enum attribute on the User concept |
| [ ] Inlining invariant logic | Violates single source of truth, makes maintenance hard | Extract to invariant library (see `artifacts/supporting/invariant_library/invariant_library.md`), reference by INV-* ID |
| [ ] Omitting sensitive markers | Security-relevant data not properly classified | Mark PII, secrets, and credentials with `sensitive: true` |
| [ ] Implementation-focused attributes | Concept becomes tied to specific implementation | Focus on logical properties, not database columns |
| [ ] Missing entry points | Incomplete attack surface documentation | Audit all APIs that touch this concept |

---

## Example: C-SHOP-USER

```yaml
id: C-SHOP-USER
name: "Shop User"
promise: >
  A user account that can authenticate, own items for sale, and purchase
  items from other users within the shop marketplace.

attributes:
  - name: id
    type: uuid
    immutable: true
    description: "Unique identifier for the user"

  - name: email
    type: string
    sensitive: true
    description: "User's email address, used for authentication and notifications"
    constraints:
      - type: pattern
        value: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  - name: password_hash
    type: string
    sensitive: true
    description: "Bcrypt hash of user's password"

  - name: role
    type: enum
    enum_values:
      - buyer
      - seller
      - admin
    default: buyer
    description: "User's role determining available actions"

  - name: verified
    type: boolean
    default: false
    description: "Whether email has been verified"

  - name: created_at
    type: timestamp
    immutable: true
    description: "Account creation timestamp"

  - name: balance
    type: integer
    default: 0
    description: "Account balance in cents"
    constraints:
      - type: range
        min: 0
        message: "Balance cannot be negative"

entry_points:
  - EP-USER-CREATE
  - EP-USER-READ
  - EP-USER-UPDATE
  - EP-USER-DELETE

invariants:
  - INV-SHOP-AUTH-REQUIRED
  - INV-SHOP-OWNER-ONLY
  - INV-SHOP-ADMIN-OVERRIDE
  - INV-SHOP-EMAIL-UNIQUE
  - INV-SHOP-BALANCE-NON-NEGATIVE

states:
  states:
    - name: PENDING
      description: "Account created but email not verified"
    - name: ACTIVE
      description: "Email verified, account fully functional"
    - name: SUSPENDED
      description: "Account suspended by admin"
    - name: DELETED
      description: "Account soft-deleted"
      terminal: true
  initial: PENDING
  transitions:
    - from: PENDING
      to: ACTIVE
      trigger: I-SHOP-VERIFY-EMAIL-001
    - from: ACTIVE
      to: SUSPENDED
      trigger: I-SHOP-SUSPEND-USER-001
      guard: INV-SHOP-ADMIN-ONLY
    - from: SUSPENDED
      to: ACTIVE
      trigger: I-SHOP-UNSUSPEND-USER-001
      guard: INV-SHOP-ADMIN-ONLY
    - from: ACTIVE
      to: DELETED
      trigger: I-SHOP-DELETE-USER-001
      guard: INV-SHOP-OWNER-ONLY
    - from: SUSPENDED
      to: DELETED
      trigger: I-SHOP-DELETE-USER-001
      guard: INV-SHOP-ADMIN-ONLY

how_it_works: |
  User accounts are stored in PostgreSQL with bcrypt-hashed passwords. Authentication
  uses session tokens stored in Redis with 24-hour expiration. Email verification
  generates a signed token (HMAC-SHA256) with 48-hour validity. Balance updates use
  database transactions with row-level locking to prevent race conditions.

security_investigation_candidates:
  - "Session fixation - can an attacker force a known session ID?"
  - "Password reset token reuse - are tokens invalidated after use?"
  - "Balance race condition - do concurrent purchases properly lock?"
  - "Email verification bypass - can unverified accounts access protected resources?"
  - "Role parameter injection - is role validated server-side on registration?"
  - "Account enumeration via timing - do login/reset responses leak existence?"

status: ACTIVE
version: "1.2.0"
```

---

## Validation Criteria

A valid concept artifact MUST:

1. **Have a unique ID** matching pattern `C-<SYSTEM>-<NAME>`
2. **Have a non-empty promise** that describes security significance
3. **Have at least one attribute** with valid type
4. **Have at least one entry point** referencing an `EP-*` artifact
5. **Reference only valid invariant IDs** (no inline logic)
6. **Use snake_case** for attribute names
7. **Use UPPER_SNAKE_CASE** for state names (if states are defined)
8. **Have valid state transitions** where from/to reference defined states

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Entry Point Artifact](../../supporting/entry_point/entry_point.md) - Surfaces owned by concepts
- [Interaction Artifact](../interaction/interaction.md) - Operations between concepts
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Security rules that govern concepts

---

## Common Pitfalls

- Modeling implementation objects (tables/services/classes) instead of security-relevant “nouns”.
- Duplicating surface metadata (method/path/URLs) in Concepts instead of referencing `EP-*`.
- Inlining invariant logic inside Concepts instead of referencing `INV-*` IDs.
