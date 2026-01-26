# Invariant Artifact Specification

## Definition

An **Invariant** is the heart of CFSE security logic. Invariants are rules that must always hold true for a system to be considered secure. They codify security requirements as formal expressions using predicates, enabling systematic testing and verification.

Every security property in CFSE is expressed as an invariant. Concepts, interactions, flows, scenarios, explorations, and findings all reference invariants - they never inline security logic. This single-source-of-truth approach ensures consistency and maintainability.

**Schema:** [`invariant.schema.yaml`](./invariant.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | InvariantID | Unique identifier following pattern `INV-<SYSTEM>-<NAME>` |
| `rule` | string | Plain English statement of the security rule |
| `logic` | string | Formal logical expression using CFSE predicate notation |
| `predicates` | PredicateID[] | List of predicate IDs (`P-*`) used in the logic |
| `criticality` | Criticality | Priority level: P0, P1, P2, or P3 |
| `tags` | InvariantTag[] | Category tags for filtering and organizing |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dependencies` | InvariantID[] | - | Other invariants this one depends on or assumes |
| `observability` | Observability | - | How to detect violations (logs, metrics, alerts) |
| `aliases` | string[] | - | Previous IDs for backward compatibility during migrations |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status: DRAFT, REVIEW, PLANNED, ACTIVE, DEPRECATED, ARCHIVED |

---

## Field Details

### rule

The rule is a plain English statement that communicates the security requirement to stakeholders. It should be:
- **Clear**: Understandable without reading formal logic
- **Unambiguous**: One interpretation only
- **Actionable**: Developers know what to implement

**Examples:**
- Good: "Only resource owners can delete their own resources"
- Good: "All API endpoints require authentication"
- Bad: "Access control should be enforced" (Too vague)
- Bad: "Users without proper authorization tokens cannot access protected endpoints unless they have admin privileges or the endpoint is marked as public" (Too complex for one rule - split it)

### logic

The logic field contains the formal expression that can be mechanically verified. It uses:
- **Quantifiers**: `FORALL`, `EXISTS`
- **Logical operators**: `AND`, `OR`, `NOT`, `IMPLIES`, `IFF`
- **Predicates**: `P-*` references
- **Actions**: `CREATE`, `READ`, `UPDATE`, `DELETE`, `ACCESS`, `EXECUTE`

The logic must semantically match the rule - they express the same requirement in different forms.

### criticality

Criticality indicates the severity of violating this invariant:

| Level | Name | Response Time | Description |
|-------|------|---------------|-------------|
| P0 | Critical | < 24 hours | System compromise, data breach, immediate exploitation risk |
| P1 | High | < 1 week | Significant security impact, urgent remediation needed |
| P2 | Medium | < 1 month | Moderate impact, planned remediation acceptable |
| P3 | Low | Convenient | Minor impact, address during normal development |

### tags

Tags categorize invariants for filtering and organization:

| Tag | Domain | Examples |
|-----|--------|----------|
| `authn` | Authentication | Login requirements, session validation, MFA |
| `authz` | Authorization | Permission checks, role-based access |
| `ownership` | Resource ownership | Owner-only operations, creator rights |
| `state` | State machine | Valid transitions, lifecycle constraints |
| `data` | Data validation | Format requirements, input validation |
| `integrity` | Data integrity | Consistency, non-repudiation, checksums |
| `confidentiality` | Information disclosure | Data leakage, exposure prevention |
| `availability` | Service availability | Rate limiting, resource exhaustion |

---

## Formal Logic Operators

| Operator | Symbol | Precedence | Associativity | Description |
|----------|--------|------------|---------------|-------------|
| NOT | `NOT`, `!` | 1 (highest) | Right | Logical negation |
| AND | `AND`, `&&` | 2 | Left | Logical conjunction |
| OR | `OR`, `\|\|` | 3 | Left | Logical disjunction |
| IMPLIES | `IMPLIES`, `=>` | 4 | Right | Material implication |
| IFF | `IFF`, `<=>` | 5 (lowest) | None | Biconditional |

### Quantifiers

| Quantifier | Syntax | Meaning |
|------------|--------|---------|
| FORALL | `FORALL x: Domain. expression` | For all x in Domain, expression holds |
| EXISTS | `EXISTS x: Domain. expression` | There exists x in Domain where expression holds |

### Actions

| Action | Description |
|--------|-------------|
| `CREATE(subject, object)` | Subject creates object |
| `READ(subject, object)` | Subject reads object |
| `UPDATE(subject, object)` | Subject modifies object |
| `DELETE(subject, object)` | Subject removes object |
| `ACCESS(subject, object)` | Subject accesses object (generic) |
| `EXECUTE(subject, object)` | Subject executes object |

---

## Key Patterns

- **One invariant = one rule.** If a security requirement has multiple independent conditions, split into multiple invariants. Compose them using dependencies.

- **Rule and logic must match.** The formal logic is the precise version of the English rule. If they say different things, fix the mismatch.

- **List all predicates.** Every `P-*` reference in the logic must appear in the predicates array. This enables dependency tracking and validation.

- **Use appropriate criticality.** Resist the urge to make everything P0. Reserve critical for actual critical issues - authentication bypass, authorization bypass, data breaches.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Vague rules | Developers cannot implement, testers cannot verify | Make rules specific and testable |
| [ ] Missing predicates | Incomplete traceability, validation fails | Ensure predicates array includes all P-* from logic |
| [ ] Logic/rule mismatch | Confusion about what is actually required | Review both forms, ensure semantic equivalence |
| [ ] Everything is P0 | Cry wolf effect, actual critical issues ignored | Reserve P0 for system compromise scenarios |
| [ ] Missing tags | Cannot filter or organize invariant library | Add at least one relevant tag |
| [ ] Overly complex logic | Hard to understand, verify, and maintain | Split into simpler invariants with dependencies |

---

## Example: INV-SHOP-OWNER-DELETE

```yaml
id: INV-SHOP-OWNER-DELETE
rule: >
  Only the owner of an item can delete it. Users cannot delete items
  that belong to other users, preventing unauthorized data destruction.

logic: |
  FORALL user: C-SHOP-USER.
    FORALL item: C-SHOP-ITEM.
      DELETE(user, item) IMPLIES P-SHOP-IS-OWNER(user, item)

predicates:
  - P-SHOP-IS-OWNER

criticality: P1

tags:
  - authz
  - ownership

dependencies:
  - INV-SHOP-AUTH-REQUIRED

observability:
  logs:
    - event: "item.deleted"
      fields:
        - user_id
        - item_id
        - item_owner_id
      indicates: holds
    - event: "item.delete.unauthorized"
      fields:
        - user_id
        - item_id
        - item_owner_id
      indicates: violated

  metrics:
    - name: shop_delete_attempts_total
      type: counter
      labels:
        - authorized
        - item_type
    - name: shop_unauthorized_deletes_total
      type: counter
      labels:
        - endpoint
      threshold: 0

  alerts:
    - name: UnauthorizedDeleteAttempt
      condition: "shop_unauthorized_deletes_total > 0"
      severity: warning
      runbook: "https://wiki.example.com/runbooks/unauthorized-delete"

status: ACTIVE
```

---

## Validation Criteria

A valid invariant artifact MUST:

1. **Have a unique ID** matching pattern `INV-<SYSTEM>-<NAME>`
2. **Have a non-empty rule** that describes the security requirement in plain English
3. **Have valid logic** using proper CFSE predicate notation
4. **List all predicates** used in the logic expression
5. **Have a criticality** level (P0, P1, P2, or P3)
6. **Have at least one tag** from the allowed enum
7. **Have semantic equivalence** between rule and logic (they express the same thing)
8. **Reference only existing predicates** (predicate IDs should be defined)

### Logic Validation

The logic expression must be syntactically valid:

| Requirement | Valid | Invalid |
|-------------|-------|---------|
| Balanced parentheses | `(A AND B) OR C` | `(A AND B OR C` |
| Quantifiers have domain | `FORALL x: C-TYPE. P(x)` | `FORALL x. P(x)` |
| Variables are bound | `FORALL x: C. P(x)` | `P(x)` where x is unbound |
| Actions have arguments | `DELETE(user, item)` | `DELETE(item)` |
| Predicates use P-* IDs | `P-SHOP-IS-OWNER(u, i)` | `is_owner(u, i)` |

---

## Predicate Relationship

Invariants are composed from predicates. Each predicate is an atomic boolean condition:

```
Predicate: P-SHOP-IS-OWNER
  Parameters: (user: C-SHOP-USER, item: C-SHOP-ITEM)
  Returns: boolean
  Definition: True if user.id equals item.owner_id

Invariant: INV-SHOP-OWNER-DELETE
  Uses: P-SHOP-IS-OWNER
  Logic: FORALL user, item. DELETE(user, item) IMPLIES P-SHOP-IS-OWNER(user, item)
```

Predicates answer simple yes/no questions. Invariants compose them into security rules.

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Formal Logic](../../../grammar/03-formal-logic.md) - Complete logic specification
- [Concept Artifact](../../primary/concept/concept.md) - Concepts that invariants govern
- [Predicate Specification](../predicate/predicate.md) - Atomic boolean conditions
- [Invariant Library Specification](../invariant_library/invariant_library.md) - Canonical packaging format for many invariants/predicates

---

## Common Pitfalls

- Writing invariants that aren’t decidable from evidence (no clear observable conditions).
- Referencing predicates in `logic` but not listing them in `predicates[]` (breaks traceability).
- Encoding policy logic in other artifacts (like PRJ); invariants are SSOT for logic.
