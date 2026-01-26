# Predicate Artifact Specification

## Definition

A **Predicate** is an atomic boolean condition that forms the smallest building block of CFSE security logic. Predicates answer simple yes/no questions about system state: "Is this user the owner?" "Is MFA enabled?" "Is the token expired?"

Predicates are composed into invariants. While invariants express complete security rules, predicates express the individual conditions that those rules depend on. This separation enables reuse, testing, and clear reasoning about security logic.

**Schema:** [`predicate.schema.yaml`](./predicate.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | PredicateID | Unique identifier following pattern `P-<SYSTEM>-<NAME>` |
| `name` | string | Human-readable name for the predicate |
| `parameters` | PredicateParameter[] | Typed input parameters for evaluation |
| `returns` | "boolean" | Always `boolean` - predicates evaluate to true or false |
| `definition` | string | Plain English description of when predicate is true |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `implementation` | Implementation | - | Code hints showing how predicate maps to implementation |
| `domain` | string | - | Security domain (authentication, authorization, etc.) |
| `used_in` | InvariantID[] | - | Invariants that use this predicate |
| `negation` | PredicateID | - | ID of the logical negation predicate |
| `related` | PredicateID[] | - | Related predicates often used together |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status: DRAFT, REVIEW, PLANNED, ACTIVE, DEPRECATED, ARCHIVED |

---

## Field Details

### parameters

Parameters define what inputs the predicate requires for evaluation. Each parameter has:
- **name**: snake_case identifier used in the definition
- **type**: Either a Concept ID (C-*) or primitive type (string, integer, boolean, uuid, timestamp, any)
- **description**: What the parameter represents

Using Concept IDs as types provides strong typing:

```yaml
parameters:
  - name: user
    type: C-SHOP-USER
    description: "The user attempting the action"
  - name: item
    type: C-SHOP-ITEM
    description: "The item being accessed"
```

### definition

The definition explains when the predicate evaluates to true. It should be:
- **Precise**: No ambiguity about conditions
- **Implementable**: Developers know exactly what to check
- **Testable**: QA can verify the behavior

Good definitions reference parameter names and describe the exact comparison:

| Quality | Example |
|---------|---------|
| Good | "True if user.id equals item.owner_id" |
| Good | "True if current_time is less than token.expiry" |
| Bad | "Checks if the user owns the item" (What does "own" mean?) |
| Bad | "Returns true for valid users" (What makes a user valid?) |

### returns

Always `"boolean"`. This field exists for:
- Documentation clarity
- Tooling support
- Type system integration

Predicates must evaluate to exactly true or false. If you need a predicate that could be "unknown," model it as `P-X-KNOWN AND P-X-VALUE` where the first predicate checks knowability.

---

## Key Patterns

- **Atomic conditions only.** A predicate tests one thing. If you find yourself writing "AND" or "OR" in the definition, split into multiple predicates.

- **Parameters are positional.** When predicates are used in invariant logic, parameters are matched by position: `P-SHOP-IS-OWNER(user, item)` maps first argument to first parameter.

- **Concept types over primitives.** Use `C-SHOP-USER` instead of `uuid` when the parameter represents a concept. This enables validation and tooling.

- **Implementation hints are optional.** Include them when the mapping to code is non-obvious. They help developers find and verify the implementation.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Complex conditions | Predicate does too much, hard to reuse | Split into atomic predicates, combine in invariants |
| [ ] Vague definitions | "Checks if valid" - what does valid mean? | Be specific: "True if X equals Y" |
| [ ] Missing parameters | Predicate references concepts not in parameters | Add all required inputs as parameters |
| [ ] Primitive types everywhere | Loses semantic meaning and validation | Use Concept IDs when parameter represents a concept |
| [ ] No parameter descriptions | Others cannot understand parameter purpose | Always describe what each parameter represents |
| [ ] Embedded logic | "True if user.role == 'admin' OR user.role == 'superadmin'" | Split: P-IS-ADMIN, P-IS-SUPERADMIN |

---

## Example: P-SHOP-IS-OWNER

```yaml
id: P-SHOP-IS-OWNER
name: "Is Resource Owner"

parameters:
  - name: user
    type: C-SHOP-USER
    description: "The user to check ownership for"
  - name: item
    type: C-SHOP-ITEM
    description: "The item to check ownership of"

returns: boolean

definition: |
  True if user.id equals item.owner_id. The ownership check
  compares the authenticated user's identifier against the
  owner_id field stored on the item record.

domain: ownership

implementation:
  language: python
  code: |
    def is_owner(user: User, item: Item) -> bool:
        return user.id == item.owner_id
  file: "src/auth/ownership.py"

used_in:
  - INV-SHOP-OWNER-DELETE
  - INV-SHOP-OWNER-UPDATE

related:
  - P-SHOP-IS-ADMIN
  - P-SHOP-HAS-PERMISSION

status: ACTIVE
```

---

## Example: P-AWS-HAS-MFA

```yaml
id: P-AWS-HAS-MFA
name: "Has MFA Enabled"

parameters:
  - name: user
    type: C-AWS-IAM-USER
    description: "The IAM user to check"

returns: boolean

definition: |
  True if the IAM user has at least one MFA device configured
  and that device is in an active state. Checks the MFADevices
  list returned by iam:ListMFADevices.

domain: authentication

implementation:
  language: python
  code: |
    def has_mfa(user_arn: str) -> bool:
        devices = iam.list_mfa_devices(UserName=user_arn)
        return len(devices['MFADevices']) > 0

used_in:
  - INV-AWS-MFA-REQUIRED
  - INV-AWS-CONSOLE-MFA

status: ACTIVE
```

---

## Validation Criteria

A valid predicate artifact MUST:

1. **Have a unique ID** matching pattern `P-<SYSTEM>-<NAME>`
2. **Have a non-empty name** that describes the condition
3. **Have at least one parameter** with name and type
4. **Have returns set to "boolean"**
5. **Have a clear definition** that explains when predicate is true
6. **Use valid Concept IDs** for typed parameters (if using concept types)
7. **Reference only existing invariants** in used_in (if populated)

### Parameter Validation

| Requirement | Valid | Invalid |
|-------------|-------|---------|
| Name format | `user`, `item_id` | `User`, `item-id` |
| Concept type | `C-SHOP-USER` | `User`, `shop-user` |
| Primitive type | `string`, `uuid` | `str`, `number` |

---

## Predicate vs Invariant

| Aspect | Predicate | Invariant |
|--------|-----------|-----------|
| Scope | Single atomic check | Complete security rule |
| Logic | No operators | Uses FORALL, IMPLIES, AND, etc. |
| Returns | Always boolean | N/A (rules, not functions) |
| Reusability | High - used in many invariants | Medium - often unique rules |
| Example | "Is user the owner?" | "Only owners can delete their items" |

Predicates are the atoms; invariants are the molecules.

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Invariant Artifact](../invariant/invariant.md) - Composes predicates into rules
- [Formal Logic](../../../grammar/03-formal-logic.md) - Logic operators and syntax
- [Invariant Library Specification](../invariant_library/invariant_library.md) - Canonical packaging format for many predicates/invariants

---

## Common Pitfalls

- Writing predicates that are too high-level (“is authorized”) instead of testable atomic facts.
- Using ambiguous parameter names/types that can’t be grounded in the world model.
- Treating predicates as implementation code; they are logical conditions that map to evidence.
