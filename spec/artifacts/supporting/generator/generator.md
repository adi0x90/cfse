# Generator Artifact Specification

## Definition

A **Generator** is a reusable pattern for creating scenarios. Generators encode testing strategies as templates with placeholders, enabling systematic scenario generation across different concepts, interactions, and invariants.

Instead of manually creating each scenario, security engineers define generators that capture common testing patterns. A generator for "unauthorized delete" can be instantiated for any concept with delete operations, automatically producing scenarios that test ownership enforcement.

**Schema:** [`generator.schema.yaml`](./generator.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | GeneratorID | Unique identifier following pattern `GEN-<STRATEGY>-<NNN>` |
| `name` | string | Human-readable name for the generator |
| `strategy` | GeneratorStrategy | Testing strategy being implemented |
| `template` | ScenarioTemplate | Template structure with placeholders |
| `variables` | TemplateVariable[] | Variables required for instantiation |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | - | Detailed description and usage guidance |
| `applicable_to` | ApplicabilityConstraints | - | Constraints on valid targets |
| `outputs` | string[] | `["scenario"]` | Artifact types produced |
| `examples` | GeneratorExample[] | - | Example instantiations |
| `related` | GeneratorID[] | - | Related generators |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |

---

## Field Details

### strategy

The strategy identifies the testing approach:

| Strategy | Purpose | Example |
|----------|---------|---------|
| `boundary` | Tests edge cases | Empty strings, max lengths, zero values |
| `mutation` | Mutates valid inputs | Type coercion, encoding bypass |
| `idor` | Tests object references | Accessing other users' resources |
| `privilege_escalation` | Tests privilege boundaries | User acting as admin |
| `state_transition` | Tests state machines | Invalid state jumps |
| `race_condition` | Tests concurrency | TOCTOU, double-submit |
| `injection` | Tests injection points | SQL, command, template injection |
| `bypass` | Tests control bypass | Authentication, authorization bypass |
| `denial` | Tests availability | Resource exhaustion, deadlocks |
| `confusion` | Tests type handling | Type confusion, mass assignment |
| `replay` | Tests replay attacks | Token reuse, request replay |
| `forgery` | Tests forgery attacks | CSRF, SSRF, request forgery |

### template

The template defines the scenario structure with `{{variable}}` placeholders:

```yaml
template:
  title_pattern: "Unauthorized {{action}} of {{concept}} by non-owner"
  hypothesis_pattern: |
    If a user attempts to {{action}} a {{concept}} they do not own,
    the system should reject the request.
  setup:
    - action: "Create {{concept}} owned by UserA"
      actor: admin
    - action: "Authenticate as UserB (non-owner)"
      actor: "{{attacker}}"
  steps:
    - action: "Attempt {{action}} on {{concept}}"
      actor: "{{attacker}}"
      expected: "403 Forbidden or equivalent denial"
  expected_result: "Request denied, {{invariant}} holds"
  invariants:
    - "{{invariant}}"
```

### variables

Variables define what must be provided during instantiation:

```yaml
variables:
  - name: concept
    type: concept_id
    description: "The concept being targeted"
    examples:
      - C-SHOP-ITEM
      - C-SHOP-ORDER
  - name: action
    type: action
    description: "The CRUD action to test"
    examples:
      - DELETE
      - UPDATE
  - name: attacker
    type: actor
    description: "The unauthorized actor"
    default: "authenticated_user_b"
  - name: invariant
    type: invariant_id
    description: "The invariant expected to hold"
```

---

## Key Patterns

- **One strategy per generator.** A generator implements one testing strategy. If you need both boundary testing and IDOR testing, create two generators.

- **Variables enable reuse.** Design templates with variables for all elements that change across instantiations: concepts, actions, actors, invariants.

- **Constraints focus applicability.** Use `applicable_to` to specify which concepts or interactions the generator targets. This helps tooling suggest relevant generators.

- **Examples demonstrate usage.** Include at least one example showing variable values and the resulting scenario. Examples are documentation and test cases.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Overly specific templates | Generator only works for one case | Abstract common patterns into variables |
| [ ] Missing variables | Template has hardcoded values that should vary | Identify all varying elements, make them variables |
| [ ] No applicability constraints | Generator suggested for irrelevant contexts | Define concept/interaction patterns in applicable_to |
| [ ] Vague step descriptions | Generated scenarios unclear to execute | Write precise action descriptions |
| [ ] No examples | Users cannot understand how to use generator | Add at least one complete example |
| [ ] Mixed strategies | Generator tries to test multiple things | Split into focused single-strategy generators |

---

## Example: GEN-IDOR-001

```yaml
id: GEN-IDOR-001
name: "Horizontal IDOR - Resource Access by Non-Owner"

strategy: idor

description: |
  Generates scenarios that test for horizontal privilege escalation via
  insecure direct object references. Tests whether UserB can access or
  modify resources belonging to UserA.

template:
  title_pattern: "IDOR: {{action}} {{concept}} owned by another user"
  hypothesis_pattern: |
    When UserB attempts to {{action}} a {{concept}} owned by UserA,
    the system should deny the request because ownership is not verified
    or the reference is predictable.
  preconditions:
    - "{{concept}} supports ownership"
    - "{{action}} endpoint accepts resource ID parameter"
  setup:
    - action: "Create {{concept}} instance owned by UserA"
      actor: user_a
      target: "{{concept}}"
    - action: "Note the resource ID"
      notes: "ID may be sequential, UUID, or predictable"
    - action: "Authenticate as UserB"
      actor: user_b
  steps:
    - action: "Request {{action}} on UserA's {{concept}} using known ID"
      actor: user_b
      target: "{{concept}}"
      parameters:
        resource_id: "{{resource_id_of_user_a}}"
      expected: "Access denied (403 or equivalent)"
  expected_result: "Request rejected, {{invariant}} holds"
  invariants:
    - "{{invariant}}"

variables:
  - name: concept
    type: concept_id
    description: "The concept with ownership semantics"
    examples:
      - C-SHOP-ITEM
      - C-SHOP-ORDER
      - C-APP-DOCUMENT
  - name: action
    type: action
    description: "The action to attempt"
    examples:
      - READ
      - UPDATE
      - DELETE
  - name: invariant
    type: invariant_id
    description: "The ownership invariant expected to hold"
    examples:
      - INV-SHOP-OWNER-DELETE
      - INV-SHOP-OWNER-UPDATE
  - name: resource_id_of_user_a
    type: string
    description: "The ID of UserA's resource (obtained in setup)"
    default: "obtained_during_execution"

applicable_to:
  invariant_tags:
    - ownership
    - authz
  requires_relationships: false

outputs:
  - scenario

examples:
  - name: "Shop Item Delete IDOR"
    variables:
      concept: C-SHOP-ITEM
      action: DELETE
      invariant: INV-SHOP-OWNER-DELETE
    produces: "S-SHOP-IDOR-DELETE-001"
    notes: "Tests item deletion ownership check"

  - name: "Document Update IDOR"
    variables:
      concept: C-APP-DOCUMENT
      action: UPDATE
      invariant: INV-APP-DOC-OWNER-UPDATE
    produces: "S-APP-IDOR-UPDATE-001"
    notes: "Tests document modification ownership check"

related:
  - GEN-IDOR-002  # Vertical IDOR
  - GEN-AUTHZ-001 # General authorization bypass

status: ACTIVE
```

---

## Example: GEN-BOUNDARY-001

```yaml
id: GEN-BOUNDARY-001
name: "Boundary Value Testing for Numeric Parameters"

strategy: boundary

description: |
  Generates scenarios testing boundary conditions for numeric input
  parameters. Tests zero, negative, maximum values, and overflow conditions.

template:
  title_pattern: "Boundary: {{parameter}} with {{boundary_type}} value"
  hypothesis_pattern: |
    When {{parameter}} is set to {{boundary_value}}, the system should
    {{expected_behavior}} rather than fail unexpectedly or bypass validation.
  setup:
    - action: "Authenticate as valid user"
      actor: "{{actor}}"
    - action: "Prepare valid request to {{interaction}}"
  steps:
    - action: "Submit request with {{parameter}} = {{boundary_value}}"
      actor: "{{actor}}"
      parameters:
        "{{parameter}}": "{{boundary_value}}"
      expected: "{{expected_behavior}}"
  expected_result: "System handles boundary gracefully, no bypass or crash"

variables:
  - name: interaction
    type: interaction_id
    description: "The interaction being tested"
  - name: parameter
    type: string
    description: "The numeric parameter to test"
    examples:
      - quantity
      - page_size
      - offset
  - name: boundary_type
    type: enum
    description: "Type of boundary being tested"
    examples:
      - zero
      - negative
      - max_int
      - overflow
  - name: boundary_value
    type: string
    description: "The actual boundary value"
    examples:
      - "0"
      - "-1"
      - "2147483647"
      - "9999999999999999999"
  - name: expected_behavior
    type: string
    description: "Expected system behavior"
    examples:
      - "reject with validation error"
      - "clamp to valid range"
      - "return empty result"
  - name: actor
    type: actor
    description: "Actor performing the request"
    default: "authenticated_user"

applicable_to:
  interactions:
    - "I-*"

outputs:
  - scenario

status: ACTIVE
```

---

## Validation Criteria

A valid generator artifact MUST:

1. **Have a unique ID** matching pattern `GEN-<STRATEGY>-<NNN>`
2. **Have a non-empty name** describing the testing pattern
3. **Have a valid strategy** from the enum
4. **Have a template** with at least title_pattern, hypothesis_pattern, setup, and steps
5. **Have at least one variable** with name, type, and description
6. **Use consistent placeholders** - all `{{variable}}` in template must have matching variable definitions

### Template Validation

| Requirement | Valid | Invalid |
|-------------|-------|---------|
| Placeholder format | `{{variable_name}}` | `{variable}`, `$variable` |
| Variable reference | `{{concept}}` with variable named `concept` | `{{concept}}` without definition |
| Step structure | Has `action` field | Missing action |

---

## Generator Lifecycle

```
Define Strategy -> Create Template -> Define Variables -> Add Examples -> Review -> ACTIVE

       ^                                                      |
       |                                                      v
       +---------------- Refine based on usage <--------------+
```

1. **Define Strategy**: Choose the testing approach
2. **Create Template**: Write the scenario structure with placeholders
3. **Define Variables**: Specify all varying elements
4. **Add Examples**: Show concrete instantiations
5. **Review**: Validate template produces valid scenarios
6. **ACTIVE**: Generator ready for use

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Scenario Artifact](../../primary/scenario/scenario.md) - What generators produce
- [Invariant Artifact](../invariant/invariant.md) - Invariants tested by generated scenarios

---

## Common Pitfalls

- Writing generators that are too vague to reliably instantiate into concrete scenarios.
- Generating scenarios that violate ID syntax or required schema fields.
- Treating generators as exhaustive; they improve coverage but don’t replace judgment.
