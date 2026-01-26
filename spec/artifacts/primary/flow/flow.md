# Flow Artifact Specification

## Definition

A **Flow** is a multi-step legitimate sequence of Interactions that achieves a user or system goal. Flows represent intended behavior - the "happy path" through your system - with clear preconditions, step sequencing, invariant guards/effects, variants, and success criteria.

Flows compose Interactions into meaningful user journeys. While an Interaction is atomic (a single operation), a Flow chains multiple Interactions together to accomplish a larger goal like "checkout and pay" or "deploy a service."

**Key principle:** Flows describe intended behavior only. Negative paths, attacks, and deviations belong in Scenarios and Explorations, which reference Flows where they deviate.

**Schema:** [`flow.schema.yaml`](./flow.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | FlowID | Unique identifier following pattern `F-<SYSTEM>-<NAME>` |
| `name` | string | Human-readable name describing the user goal |
| `actor` | string | Primary actor executing the flow (concept ID or role) |
| `goal` | string | The outcome this flow achieves, expressed as a result |
| `trigger` | FlowTrigger | What initiates the flow (user action, event, schedule) |
| `preconditions` | FlowCondition[] | Conditions that must hold before flow begins |
| `steps` | FlowStep[] | Ordered sequence of interactions |
| `postconditions` | FlowCondition[] | Conditions that must hold after completion |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | - | Detailed description of the flow's purpose |
| `scope` | string | - | Boundary clarification (what's included/excluded) |
| `variants` | FlowVariant[] | - | Alternative paths based on conditions |
| `state_map` | StateMap | - | Visual state transitions driven by flow |
| `related` | RelatedArtifacts | - | Links to concepts, interactions, scenarios |
| `security_insights` | FlowSecurityInsights | - | Security considerations |
| `observability` | FlowObservability | - | Live validation evidence (add only after testing) |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version (e.g., `1.0.0`) |

---

## Field Details

### actor

The primary actor executing the flow. Can be:
- A concept ID: `C-SHOP-USER`
- A role description: `Authenticated User`
- A system actor: `Scheduled Job`, `Event Handler`

The actor should be the entity whose perspective defines the flow's purpose.

### goal

The goal is expressed as an outcome, not a list of actions:
- Good: "Convert a shopping basket into a paid order"
- Bad: "Login, add items, checkout, pay, confirm"

The goal should answer: "What does the actor want to accomplish?"

### preconditions and postconditions

Conditions use a structured format supporting multiple types:

| Type | Usage | Example |
|------|-------|---------|
| `invariant` | Reference to INV-* | `INV-SHOP-AUTH-REQUIRED` |
| `state` | Concept state requirement | `C-SHOP-ORDER.status = 'draft'` |
| `attribute` | Attribute value requirement | `C-SHOP-USER.verified = true` |
| `exists` | Existence check | `EXISTS(C-SHOP-BASKET.items)` |
| `custom` | Custom expression | `basket.total > 0` |

**Example:**
```yaml
preconditions:
  - type: invariant
    invariant: INV-SHOP-AUTH-REQUIRED
    description: "User must be authenticated"
  - type: state
    concept: C-SHOP-BASKET
    state: ACTIVE
    description: "Basket must be active"

postconditions:
  - type: state
    concept: C-SHOP-ORDER
    state: PAID
    description: "Order is paid"
  - type: invariant
    invariant: INV-SHOP-ORDER-PAYMENT-CONSISTENT
    description: "Payment amount matches order total"
```

### steps

Each step references an Interaction and provides context:

| Property | Required | Description |
|----------|----------|-------------|
| `order` | Yes | Sequence number (1-based) |
| `actor` | Yes | Who performs this step |
| `interaction` | Yes | Reference to I-* |
| `purpose` | Yes | Why this step exists in the flow |
| `pre` | No | Step-specific pre-invariants |
| `post` | No | Step-specific post-invariants |
| `conditional` | No | When step is optional |
| `on_failure` | No | Failure handling: abort, retry, skip, compensate |
| `compensation` | No | Rollback interaction if needed |

**Step satisfiability:** Every step's pre-conditions should be implied by the flow's preconditions plus prior steps' post-conditions.

### variants

Variants represent alternative paths through the flow:
- Payment method variants (credit card, wallet, crypto)
- User type variants (guest, member, admin)
- Feature flag variants

Each variant can replace steps, insert additional steps, or modify postconditions.

---

## Key Patterns

- **Legitimate behavior only.** Flows document the happy path. Attacks and deviations go in Scenarios.

- **Steps are existing Interactions.** Never define new operations inline - reference `I-*` IDs. If an interaction doesn't exist, create it first.

- **Preconditions enable first step.** The flow's preconditions must satisfy the first step's pre-invariants.

- **Each step enables the next.** Step N's post-conditions must satisfy step N+1's pre-conditions.

- **Postconditions span all steps.** Flow-level postconditions capture guarantees that result from the entire sequence.

---

## Flow Health Checks

Before considering a flow complete, verify:

| Check | Description |
|-------|-------------|
| Step satisfiability | Every step's pre is implied by flow pre + prior posts |
| No dead branches | All variant conditions can actually be true |
| Guards documented | State-changing steps cite relevant INV-* |
| Cycles have exits | Any loops have termination conditions |
| Idempotency noted | Retry/parallel steps have integrity invariants |
| Boundaries marked | Trust boundary crossings are identified |

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Including attack paths | Flows should be legitimate only | Move negative paths to Scenarios |
| [ ] Inlining interaction logic | Steps should reference, not define | Create Interaction first, then reference |
| [ ] Missing step connections | Gap between step N post and step N+1 pre | Ensure post-conditions enable next step |
| [ ] Vague goals | "Do checkout things" doesn't clarify intent | Express goal as concrete outcome |
| [ ] Monolithic steps | One step does too much | Split into smaller Interactions |
| [ ] No variants for alternatives | Real flows have branches | Add variants for different paths |

---

## Example: F-SHOP-CHECKOUT-001

```yaml
id: F-SHOP-CHECKOUT-001
name: "User Checkout and Payment"
description: >
  A logged-in user converts their shopping basket into a paid order.
  Includes delivery selection, optional coupon application, and payment capture.

actor: C-SHOP-USER
goal: "Convert a shopping basket into a paid order for a logged-in user"

trigger:
  type: user_action
  description: "User clicks 'Proceed to Checkout' button"
  entry_point: I-SHOP-CREATE-ORDER-001

scope: "From basket to paid order, excludes order fulfillment and shipping"

preconditions:
  - type: invariant
    invariant: INV-SHOP-AUTH-REQUIRED
    description: "User must be authenticated"

  - type: state
    concept: C-SHOP-BASKET
    state: ACTIVE
    description: "User has an active basket"

  - type: custom
    expression: "basket.items.length > 0"
    description: "Basket is not empty"

steps:
  - order: 1
    actor: User
    interaction: I-SHOP-CREATE-ORDER-001
    purpose: "Create order from basket contents"
    pre:
      - INV-SHOP-BASKET-NOT-EMPTY
    post:
      - INV-SHOP-ORDER-CREATED
    notes: "Associates basket items with new order"

  - order: 2
    actor: User
    interaction: I-SHOP-SELECT-DELIVERY-001
    purpose: "Choose delivery method and address"
    pre:
      - INV-SHOP-ORDER-EDITABLE
    post:
      - INV-SHOP-DELIVERY-SET
    notes: "Order total recalculated with shipping"

  - order: 3
    actor: User
    interaction: I-SHOP-APPLY-COUPON-001
    purpose: "Apply discount coupon if available"
    conditional: "user.has_coupon"
    pre:
      - INV-SHOP-COUPON-VALID
    post:
      - INV-SHOP-ORDER-TOTAL-CONSISTENT
    on_failure: skip
    notes: "Optional step - flow continues if coupon invalid"

  - order: 4
    actor: User
    interaction: I-SHOP-CAPTURE-PAYMENT-001
    purpose: "Process payment and complete order"
    pre:
      - INV-SHOP-PAYMENT-AUTHORIZED
      - INV-SHOP-ORDER-TOTAL-CONSISTENT
    post:
      - INV-SHOP-ORDER-PAID
      - INV-SHOP-PAYMENT-CAPTURED
    compensation: I-SHOP-REFUND-PAYMENT-001
    notes: "Payment failure triggers order cancellation"

postconditions:
  - type: state
    concept: C-SHOP-ORDER
    state: PAID
    description: "Order is in paid state"

  - type: invariant
    invariant: INV-SHOP-ORDER-PAYMENT-CONSISTENT
    description: "Payment amount equals order total"

  - type: state
    concept: C-SHOP-BASKET
    state: CONVERTED
    description: "Basket has been converted to order"

variants:
  - name: wallet_payment
    condition: "user.preferred_payment == 'wallet'"
    replaces: [4]
    steps:
      - order: 4
        actor: User
        interaction: I-SHOP-DEBIT-WALLET-001
        purpose: "Pay using account wallet balance"
        pre:
          - INV-SHOP-WALLET-SUFFICIENT
        post:
          - INV-SHOP-ORDER-PAID
          - INV-SHOP-WALLET-DEBITED
    postconditions:
      - type: invariant
        invariant: INV-SHOP-ORDER-PAYMENT-CONSISTENT
        description: "Wallet debit equals order total"

  - name: guest_checkout
    condition: "user.type == 'guest'"
    inserts_after: 1
    steps:
      - order: 2
        actor: User
        interaction: I-SHOP-COLLECT-GUEST-INFO-001
        purpose: "Gather email and contact for guest"
        post:
          - INV-SHOP-GUEST-INFO-VALID

state_map:
  concept: C-SHOP-ORDER
  states:
    - CREATED
    - PENDING_DELIVERY
    - PENDING_PAYMENT
    - PAID
  transitions:
    - from: CREATED
      to: PENDING_DELIVERY
      step: 1
      interaction: I-SHOP-CREATE-ORDER-001
    - from: PENDING_DELIVERY
      to: PENDING_PAYMENT
      step: 2
      interaction: I-SHOP-SELECT-DELIVERY-001
    - from: PENDING_PAYMENT
      to: PAID
      step: 4
      interaction: I-SHOP-CAPTURE-PAYMENT-001
      guard: INV-SHOP-PAYMENT-AUTHORIZED

related:
  concepts:
    - C-SHOP-USER
    - C-SHOP-BASKET
    - C-SHOP-ORDER
    - C-SHOP-PAYMENT
    - C-SHOP-COUPON
  interactions:
    - I-SHOP-CREATE-ORDER-001
    - I-SHOP-SELECT-DELIVERY-001
    - I-SHOP-APPLY-COUPON-001
    - I-SHOP-CAPTURE-PAYMENT-001
  scenarios:
    - S-SHOP-PAYMENT-BYPASS-001
    - S-SHOP-COUPON-ABUSE-001
  explorations:
    - E-SHOP-PAYMENT-BYPASS-001-01

security_insights:
  identity_continuity: >
    User identity from initial auth must be maintained throughout.
    All steps validate against same user_id.
  cross_tenant: >
    Order, basket, and payment must belong to same user.
    No cross-user data access.
  idempotency: >
    Payment capture must be idempotent. Retry with same order_id
    should not double-charge.
  compensation: >
    If payment fails after order creation, order transitions to CANCELLED.
    If payment captured but confirmation fails, refund is triggered.
  race_conditions:
    - "Concurrent checkout from same basket"
    - "Coupon used simultaneously by multiple users"
    - "Price change during checkout"
  trust_boundaries:
    - "Auth service validates token"
    - "Payment gateway processes charge"
    - "Inventory service checks stock"

status: ACTIVE
version: "1.2.0"
```

---

## Validation Criteria

A valid flow artifact MUST:

1. **Have a unique ID** matching pattern `F-<SYSTEM>-<NAME>`
2. **Have a meaningful goal** expressed as an outcome
3. **Have at least one precondition** enabling the flow
4. **Have at least one step** referencing a valid Interaction ID
5. **Have at least one postcondition** guaranteeing the outcome
6. **Have step ordering** with consecutive numbers starting at 1
7. **Reference only valid artifact IDs** (I-*, INV-*, C-*)
8. **Have satisfiable step sequence** (each step's pre enabled by prior context)

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Interaction Artifact](../interaction/interaction.md) - Atomic operations that compose flows
- [Concept Artifact](../concept/concept.md) - Entities that participate in flows
- [Scenario Artifact](../scenario/scenario.md) - Hypotheses that target flows
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Security rules for preconditions/postconditions

---

## Common Pitfalls

- Writing a flow as prose only (without stable references to `I-*` interactions and `EP-*` surfaces).
- Skipping preconditions/postconditions, making later scenarios and explorations ambiguous.
- Treating a “happy path” as exhaustive; flows should enumerate security-relevant variants.
