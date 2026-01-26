# Scenario Artifact Specification

## Definition

A **Scenario** is a testable vulnerability hypothesis. Scenarios formulate precise "what-if" questions about invariant violations by manipulating interactions, flow steps, inputs, or states. They connect a hypothesis to concrete targets and define acceptance criteria for testing.

Scenarios are the bridge between the world model (concepts, interactions, flows, invariants) and actual security testing (explorations, findings). A scenario asks: "What happens if we violate this assumption?"

**Key principle:** Scenarios are hypotheses, not confirmed vulnerabilities. They become findings only after successful exploration validates the hypothesis.

**Schema:** [`scenario.schema.yaml`](./scenario.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ScenarioID | Unique identifier following pattern `S-<SYSTEM>-<NAME>-<NNN>` |
| `title` | string | Concise title describing the attack hypothesis |
| `hypothesis` | string | The suspected vulnerability, referencing specific invariants |
| `targeted_invariants` | InvariantID[] | Invariants this scenario attempts to violate |
| `attack_vector` | AttackVector | Method of attack: anchor point and manipulation |
| `expected_outcome` | ExpectedOutcome | What indicates success (vulnerable) or failure (secure) |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | - | Natural language question the scenario answers |
| `premise` | string | - | Setup assumptions and context |
| `targeted_concepts` | ConceptID[] | - | Concepts involved in the scenario |
| `targeted_interactions` | InteractionID[] | - | Interactions being manipulated |
| `targeted_flows` | FlowTarget[] | - | Flows being manipulated with step references |
| `acceptance_criteria` | AcceptanceCriteria | - | Precise validation/refutation criteria |
| `generator` | GeneratorRef | - | Generator that produced this scenario |
| `observability` | ScenarioObservability | - | Test evidence (add only after validation) |
| `notes` | string | - | Additional context |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version |

---

## Field Details

### hypothesis

The hypothesis is the core of the scenario. It must:
- State what vulnerability might exist
- Reference specific invariants that could be violated
- Be testable through concrete actions

**Good hypothesis:**
```
The owner check (INV-SHOP-OWNER-DELETE) can be bypassed by directly
calling DELETE /api/items/{id} with another user's item ID, because
the API only validates authentication, not authorization.
```

**Bad hypothesis:**
```
The delete endpoint might be insecure.
```

### targeted_invariants

The primary oracle for the scenario. These invariants are what we're trying to break:

```yaml
targeted_invariants:
  - INV-SHOP-OWNER-DELETE    # Main target
  - INV-SHOP-AUTH-REQUIRED   # Secondary guard
```

A scenario must target at least one invariant. Multiple invariants may be targeted if they form a related security boundary.

### attack_vector

The attack vector has two key components:

**Anchor** - What is being targeted:
| Type | Example | Description |
|------|---------|-------------|
| `interaction` | `I-SHOP-DELETE-ITEM-001` | Target a specific interaction |
| `flow_step` | `F-SHOP-CHECKOUT#step=3` | Target a step in a flow |
| `state` | `C-SHOP-ORDER.status` | Manipulate state directly |
| `parameter` | `item_id` | Manipulate a parameter value |
| `entry_point` | `EP-ITEM-DELETE` | Target an entry point |

**Manipulation** - How the anchor is perturbed:
| Type | Description | Example |
|------|-------------|---------|
| `skip_step` | Omit a required step | Skip payment in checkout |
| `reorder` | Execute steps out of order | Pay before selecting delivery |
| `mutate_param` | Change critical parameters | Use another user's item_id |
| `set_state` | Force unexpected state | Set order.status='paid' directly |
| `fault_injection` | Inject errors/timeouts | Timeout payment callback |
| `timing` | Race concurrent actions | Double-spend via parallel requests |
| `replay` | Replay captured requests | Reuse expired auth token |
| `inject` | Inject malicious data | SQL injection in search |

### expected_outcome

Documents what success and failure look like:

```yaml
expected_outcome:
  if_vulnerable: >
    Bob successfully deletes Alice's item. Response 200 OK.
    Item no longer exists in database.
  if_secure: >
    Bob receives 403 Forbidden. Alice's item remains intact.
    Log shows unauthorized delete attempt.
```

---

## Key Patterns

- **Invariants are the oracle.** The targeted invariants determine whether the hypothesis is validated. If they're violated, the system is vulnerable.

- **Be specific.** Vague scenarios can't be tested. Name exact interactions, parameters, and expected responses.

- **One hypothesis per scenario.** If you're testing multiple independent attack paths, create multiple scenarios.

- **Reference, don't define.** Scenarios reference flows, interactions, and invariants - they don't define them.

- **Scenarios are unproven.** A scenario is a hypothesis until an exploration validates it.

---

## Manipulation Types

### skip_step
Omit a required flow step and attempt subsequent steps.
- **Example:** Skip authentication step, try to access protected resource
- **Tests:** Authorization checks, state machine guards

### reorder
Execute steps out of sequence.
- **Example:** Process payment before adding items to cart
- **Tests:** Sequence dependencies, state prerequisites

### mutate_param
Alter critical parameters to break guards.
- **Example:** Change `user_id` from self to another user
- **Tests:** IDOR, authorization bypass, input validation

### set_state
Force preconditions or internal state to unexpected values.
- **Example:** Set `order.status` to 'shipped' before payment
- **Tests:** State machine integrity, business logic

### fault_injection
Induce errors, timeouts, or failure conditions.
- **Example:** Make payment gateway timeout after charging
- **Tests:** Error handling, compensation, idempotency

### timing
Race concurrent actions to test atomicity.
- **Example:** Two simultaneous requests to use same coupon
- **Tests:** TOCTOU, double-spend, race conditions

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Vague hypothesis | Cannot be tested, unclear success criteria | Reference specific invariants and outcomes |
| [ ] No targeted invariants | Missing oracle for success/failure | Every scenario must target at least one INV-* |
| [ ] Multiple unrelated attacks | Scenario becomes unfocused | Split into separate scenarios |
| [ ] Missing expected_outcome | Don't know what to observe | Define both if_vulnerable and if_secure |
| [ ] Confusing scenario with finding | Scenarios are hypotheses, not confirmed bugs | Mark as finding only after successful exploration |
| [ ] Implementation-specific | Tied to code details that may change | Focus on logical vulnerabilities |

---

## Example: S-SHOP-IDOR-DELETE-001

```yaml
id: S-SHOP-IDOR-DELETE-001
title: "IDOR: Delete Other User's Items"

question: "Can User A delete items owned by User B?"

premise: >
  Two users exist in the system: Alice (who owns items) and Bob (attacker).
  Both users are authenticated with valid sessions.

hypothesis: >
  The owner check (INV-SHOP-OWNER-DELETE) can be bypassed by directly
  calling DELETE /api/v1/items/{item_id} with another user's item ID.
  The API validates that the caller is authenticated but may not verify
  they own the specific item being deleted.

targeted_invariants:
  - INV-SHOP-OWNER-DELETE

targeted_concepts:
  - C-SHOP-USER
  - C-SHOP-ITEM

targeted_interactions:
  - I-SHOP-DELETE-ITEM-001

targeted_flows:
  - flow: F-SHOP-ITEM-MANAGEMENT
    steps: [4]
    anchor: "F-SHOP-ITEM-MANAGEMENT#step=4"

attack_vector:
  anchor:
    type: interaction
    ref: I-SHOP-DELETE-ITEM-001
    description: "The delete item endpoint"

  manipulation:
    type: mutate_param
    details: >
      Replace the item_id parameter with an item ID owned by
      a different user (Alice's item ID in Bob's request)

  parameter_bindings:
    - name: item_id
      value: "alice-item-uuid"
      description: "Item owned by Alice, not the attacker Bob"
    - name: auth_token
      value: "bob-session-token"
      description: "Valid auth token for Bob (the attacker)"

  negative_sequence:
    description: >
      Bob authenticates legitimately, then attempts to delete Alice's
      item by substituting the item_id in the delete request.
    expected_rejection:
      - invariant: INV-SHOP-OWNER-DELETE
        at: I-SHOP-DELETE-ITEM-001
        error_code: 403

expected_outcome:
  if_vulnerable: >
    Bob's DELETE request returns 200 OK. Alice's item is deleted from
    the database. Bob has successfully destroyed another user's data
    without authorization.
  if_secure: >
    Bob's DELETE request returns 403 Forbidden with error message
    "Not authorized to delete this item". Alice's item remains intact.
    Audit log shows unauthorized delete attempt by Bob.

acceptance_criteria:
  violation:
    - "DELETE returns 2xx status code"
    - "Item no longer exists in database after Bob's request"
    - "No authorization error logged"
  enforcement:
    - "DELETE returns 403 Forbidden"
    - "Item still exists in database"
    - "Unauthorized attempt logged with user IDs"

generator:
  id: GEN-IDOR-001
  name: "IDOR Parameter Mutator"
  strategy: "Param-Mutator"
  config:
    target_param: "resource_id"
    substitution: "other_user_resource"

notes: >
  This is a classic IDOR pattern. The authorization check must verify
  ownership, not just authentication. If the system only checks that
  a valid session token is present without verifying the relationship
  between the authenticated user and the target resource, this attack
  will succeed.

status: ACTIVE
version: "1.0.0"
```

---

## Scenario Generation

Scenarios can be generated systematically using generators:

| Generator Strategy | What It Does | Example Scenarios |
|-------------------|--------------|-------------------|
| **Skip-Step** | Omit flow steps | Skip auth, skip payment |
| **Reorder** | Permute step order | Pay before checkout |
| **Param-Mutator** | Vary parameters | IDOR, type confusion |
| **State-Corruptor** | Invalid state combos | Deleted + active |
| **Fault-Injector** | Error conditions | Timeout, disconnect |
| **Race-Detector** | Concurrent operations | Double-spend |

When a generator produces a scenario, reference it:

```yaml
generator:
  id: GEN-BOUNDARY-001
  name: "Ownership Boundary Tester"
  strategy: "Param-Mutator"
  config:
    boundary_type: "ownership"
    target_concept: "C-SHOP-ITEM"
```

---

## Validation Criteria

A valid scenario artifact MUST:

1. **Have a unique ID** matching pattern `S-<SYSTEM>-<NAME>-<NNN>`
2. **Have a testable hypothesis** referencing specific invariants
3. **Target at least one invariant** (INV-*)
4. **Have a complete attack_vector** with anchor and manipulation
5. **Define expected outcomes** for both vulnerable and secure cases
6. **Be specific enough** to derive concrete test steps
7. **Reference only valid artifact IDs** (INV-*, I-*, F-*, C-*)

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Flow Artifact](../flow/flow.md) - Legitimate sequences that scenarios target
- [Interaction Artifact](../interaction/interaction.md) - Operations that scenarios manipulate
- [Exploration Artifact](../exploration/exploration.md) - Experiments that test scenarios
- [Trace Artifact](../../supporting/trace/trace.md) - Optional structured evidence produced by explorations
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Rules that scenarios attempt to violate
- [Finding Artifact](../finding/finding.md) - Confirmed vulnerabilities from successful scenarios

---

## Common Pitfalls

- Writing a scenario without a clear oracle (`targeted_invariants`), making results non-decisive.
- Bundling multiple manipulations into one scenario (break into multiple scenarios for single-variable tests).
- Missing a concrete anchor (interaction, flow step, entry point, parameter) that an exploration can execute.
