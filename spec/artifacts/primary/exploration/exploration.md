# Exploration Artifact Specification

## Definition

An **Exploration** is a concrete, reproducible security experiment that tests a Scenario hypothesis. Every exploration includes both a **Baseline** (legitimate path) and an **Attack** path to enable Delta Analysis - comparing what happens when invariants are enforced versus when an attacker attempts to violate them.

Explorations transform theoretical scenarios into empirical evidence. They answer: "What actually happens when we try this attack?"

**Key principle:** Delta Analysis is the heart of exploration. By comparing baseline and attack paths side-by-side, we definitively determine whether security controls work as expected.

**Schema:** [`exploration.schema.yaml`](./exploration.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | ExplorationID | Unique identifier `E-<SYSTEM>-<NAME>-<NNN>-<VV>` |
| `title` | string | Descriptive name of the experiment |
| `scenario_ref` | ScenarioID | Reference to the Scenario being tested |
| `objective` | string | What the experiment aims to confirm/refute |
| `base_setup` | PathSetup | Setup for baseline (legitimate) path |
| `base_action` | PathAction | Steps executed in baseline path |
| `base_expected` | PathExpected | Expected observations for baseline |
| `att_setup` | PathSetup | Setup for attack path |
| `att_action` | PathAction | Steps executed in attack path |
| `att_expected` | PathExpected | Expected observations for attack |
| `observations` | Observations | Actual results from execution |
| `verdict` | ExplorationVerdict | Final determination (`VIOLATION_CONFIRMED`, `ENFORCEMENT_CONFIRMED`, `INCONCLUSIVE`, or `BLOCKED`) |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `setup` | ExplorationSetup | - | Shared setup (env, fixtures, bindings) |
| `trace_refs` | TraceRefs | - | Optional links to baseline/attack Trace artifacts (recommended for temporal claims) |
| `acceptance_criteria` | AcceptanceCriteria | - | Pass/fail definitions |
| `cleanup` | Cleanup | - | Teardown instructions |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version |

---

## Delta Analysis: BASE vs ATT

The core of exploration is **Delta Analysis** - comparing two parallel paths:

### Baseline (BASE)
The legitimate path where invariants should **hold**:
- Actor is authorized
- Parameters are valid
- Sequence is correct
- Expected: Success with proper authorization

### Attack (ATT)
The manipulated path where invariants should **block** (or be violated):
- Actor may be unauthorized
- Parameters may be manipulated
- Sequence may be disrupted
- Expected (if secure): Rejection with appropriate error
- Observed (if vulnerable): Unauthorized success

### Delta Comparison

| Aspect | Baseline | Attack | Indicates |
|--------|----------|--------|-----------|
| Status Code | 200 OK | 403 Forbidden | **Enforced** - attack blocked |
| Status Code | 200 OK | 200 OK | **Violated** - attack succeeded |
| Resource State | Modified by owner | Unchanged | **Enforced** |
| Resource State | Modified by owner | Modified by attacker | **Violated** |
| Logs | "user.deleted_own_item" | "unauthorized_delete_attempt" | **Enforced** |
| Logs | "user.deleted_own_item" | "user.deleted_own_item" | **Violated** (if attacker) |

---

## Field Details

### base_setup and att_setup

Each path has its own setup establishing context:

```yaml
base_setup:
  description: "Alice (owner) prepares to delete her own item"
  actor: "Alice"
  context: "Authenticated as alice@example.com with valid session"

att_setup:
  description: "Bob (attacker) prepares to delete Alice's item"
  actor: "Bob"
  context: "Authenticated as bob@example.com, using Alice's item_id"
  prerequisites:
    - "Obtained Alice's item_id through enumeration"
```

### base_action and att_action

Actions are ordered steps with concrete commands:

```yaml
base_action:
  goal: "Owner successfully deletes their own item"
  steps:
    - order: 1
      description: "Alice deletes her item"
      command: |
        curl -X DELETE "${BASE}/api/items/${alice_item_id}" \
          -H "Authorization: Bearer ${alice_token}"
      request:
        method: DELETE
        path: "/api/items/${alice_item_id}"
        headers:
          Authorization: "Bearer ${alice_token}"

att_action:
  goal: "Attacker attempts to delete another user's item"
  steps:
    - order: 1
      description: "Bob attempts to delete Alice's item"
      command: |
        curl -X DELETE "${BASE}/api/items/${alice_item_id}" \
          -H "Authorization: Bearer ${bob_token}"
      request:
        method: DELETE
        path: "/api/items/${alice_item_id}"
        headers:
          Authorization: "Bearer ${bob_token}"
```

### base_expected and att_expected

Document what should happen in each path:

```yaml
base_expected:
  outcome: "Alice successfully deletes her item"
  status_code: 200
  response_contains:
    - '"deleted": true'
  invariants:
    - invariant: INV-SHOP-OWNER-DELETE
      expected_state: HOLDS
      notes: "Owner deleting own resource - should succeed"
  state_changes:
    - "Item no longer exists in database"

att_expected:
  outcome: "Bob's attempt is rejected"
  status_code: 403
  response_contains:
    - '"error"'
    - "Forbidden"
  invariants:
    - invariant: INV-SHOP-OWNER-DELETE
      expected_state: HOLDS
      notes: "Non-owner blocked from deleting - invariant enforced"
  state_changes:
    - "Item remains intact in database"
```

### observations

Filled after execution:

```yaml
observations:
  executed_at: "2025-01-15T10:30:00Z"
  environment: "local-docker"
  base_results:
    success: true
    status_code: 200
    response_body: '{"deleted": true, "itemId": "item-123"}'
    state_after:
      item_exists: false
  att_results:
    success: true  # This is bad!
    status_code: 200
    response_body: '{"deleted": true, "itemId": "item-123"}'
    state_after:
      item_exists: false
  delta:
    summary: "Attack succeeded - no difference from baseline"
    differences:
      - aspect: "Authorization check"
        baseline: "Owner identity validated"
        attack: "No owner check performed"
        significance: "CRITICAL - anyone can delete any item"
    invariant_states:
      - invariant: INV-SHOP-OWNER-DELETE
        state: VIOLATED
        evidence: "Bob deleted Alice's item with 200 OK"
```

### trace_refs (optional)

When temporal operators are used (or ordering is central to the claim), link to structured Trace artifacts that capture the baseline and/or attack event sequence.

```yaml
trace_refs:
  baseline: T-SHOP-IDOR-DELETE-001-01-01
  attack: T-SHOP-IDOR-DELETE-001-01-02
```

### verdict

The final determination:

| Result | Meaning |
|--------|---------|
| `VIOLATION_CONFIRMED` | Attack succeeded, invariant was violated |
| `ENFORCEMENT_CONFIRMED` | Attack was blocked, invariant held |
| `INCONCLUSIVE` | Could not determine (errors, ambiguous results) |
| `BLOCKED` | Exploration could not be executed |

```yaml
verdict:
  result: VIOLATION_CONFIRMED
  summary: >
    The INV-SHOP-OWNER-DELETE invariant is violated. Bob successfully
    deleted Alice's item without authorization. The API only checks
    authentication, not authorization.
  confidence: HIGH
  finding_ref: FD-SHOP-AUTHZ-001
  recommendations:
    - "Add ownership check in delete endpoint"
    - "Review all resource operations for similar IDOR"
```

---

## Key Patterns

- **Always run both paths.** Without baseline, you can't confirm the attack path is actually different behavior.

- **Same environment.** Both paths must execute in identical conditions to make delta meaningful.

- **Concrete commands.** Use actual curl/httpie commands that can be copy-pasted and reproduced.

- **Extract and reuse values.** Capture tokens, IDs, and responses for use in subsequent steps.

- **Document everything.** Actual responses, timestamps, and state changes are evidence.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] No baseline path | Cannot prove attack behavior is abnormal | Always include baseline for comparison |
| [ ] Vague commands | Not reproducible | Use exact curl commands with all headers |
| [ ] Missing observations | No evidence for verdict | Fill observations after execution |
| [ ] Premature verdict | Claiming result before testing | Only set verdict after actual execution |
| [ ] Different environments | Delta not meaningful | Run both paths in same environment |
| [ ] No cleanup | State pollution affects other tests | Document teardown steps |

---

## Example: E-SHOP-IDOR-DELETE-001-01

```yaml
id: E-SHOP-IDOR-DELETE-001-01
title: "IDOR Delete Attack: Bob Deletes Alice's Item"

scenario_ref: S-SHOP-IDOR-DELETE-001

objective: >
  Confirm whether INV-SHOP-OWNER-DELETE is enforced when Bob attempts
  to delete Alice's item using the DELETE /api/items/{id} endpoint.

setup:
  env:
    BASE: "http://localhost:3000"
  preconditions:
    - "Application running on localhost:3000"
    - "Database seeded with test data"
  fixtures:
    - name: alice
      type: user
      data:
        email: "alice@example.com"
        password: "password123"
    - name: bob
      type: user
      data:
        email: "bob@example.com"
        password: "password456"
    - name: alice_item
      type: item
      data:
        name: "Alice's Laptop"
        price: 999
        owner: "${alice.id}"
  bindings:
    - role: owner
      user: alice
      token: alice_token
    - role: attacker
      user: bob
      token: bob_token

base_setup:
  description: "Alice (owner) prepares to delete her own item"
  actor: "Alice"
  context: "Authenticated as alice@example.com"
  prerequisites:
    - "Login as Alice to obtain token"

base_action:
  goal: "Owner successfully deletes their own item"
  steps:
    - order: 1
      description: "Alice logs in"
      command: |
        curl -X POST "${BASE}/api/auth/login" \
          -H "Content-Type: application/json" \
          -d '{"email":"alice@example.com","password":"password123"}'
      extract:
        - name: alice_token
          path: ".token"
          description: "Alice's authentication token"
        - name: alice_id
          path: ".userId"
          description: "Alice's user ID"

    - order: 2
      description: "Get Alice's item ID"
      command: |
        curl -X GET "${BASE}/api/items?owner=${alice_id}" \
          -H "Authorization: Bearer ${alice_token}"
      extract:
        - name: alice_item_id
          path: ".items[0].id"
          description: "Alice's item ID"

    - order: 3
      description: "Alice deletes her item"
      interaction: I-SHOP-DELETE-ITEM-001
      command: |
        curl -X DELETE "${BASE}/api/items/${alice_item_id}" \
          -H "Authorization: Bearer ${alice_token}"
      request:
        method: DELETE
        path: "/api/items/${alice_item_id}"
        headers:
          Authorization: "Bearer ${alice_token}"

base_expected:
  outcome: "Alice successfully deletes her own item"
  status_code: 200
  response_contains:
    - '"deleted": true'
  invariants:
    - invariant: INV-SHOP-OWNER-DELETE
      expected_state: HOLDS
      notes: "Owner deleting own resource - should succeed"
  state_changes:
    - "Alice's item no longer exists in database"

att_setup:
  description: "Bob (attacker) prepares to delete Alice's item"
  actor: "Bob"
  context: "Authenticated as bob@example.com, targeting Alice's item"
  prerequisites:
    - "Bob has Alice's item_id (obtained through enumeration)"
    - "Fresh item created for Alice (to avoid test pollution)"

att_action:
  goal: "Attacker attempts to delete another user's item"
  steps:
    - order: 1
      description: "Bob logs in"
      command: |
        curl -X POST "${BASE}/api/auth/login" \
          -H "Content-Type: application/json" \
          -d '{"email":"bob@example.com","password":"password456"}'
      extract:
        - name: bob_token
          path: ".token"
          description: "Bob's authentication token"

    - order: 2
      description: "Create fresh item for Alice"
      command: |
        curl -X POST "${BASE}/api/items" \
          -H "Authorization: Bearer ${alice_token}" \
          -H "Content-Type: application/json" \
          -d '{"name":"Target Item","price":100}'
      extract:
        - name: target_item_id
          path: ".id"
          description: "Alice's item that Bob will target"

    - order: 3
      description: "Bob attempts to delete Alice's item"
      interaction: I-SHOP-DELETE-ITEM-001
      command: |
        curl -X DELETE "${BASE}/api/items/${target_item_id}" \
          -H "Authorization: Bearer ${bob_token}"
      request:
        method: DELETE
        path: "/api/items/${target_item_id}"
        headers:
          Authorization: "Bearer ${bob_token}"
      notes: "This should fail with 403 if INV-SHOP-OWNER-DELETE is enforced"

att_expected:
  outcome: "Bob's attempt is rejected with 403 Forbidden"
  status_code: 403
  response_contains:
    - '"error"'
    - "Forbidden"
    - "not authorized"
  invariants:
    - invariant: INV-SHOP-OWNER-DELETE
      expected_state: HOLDS
      notes: "Non-owner should be blocked from deleting"
  state_changes:
    - "Alice's item remains intact in database"

observations:
  executed_at: "2025-01-15T10:30:00Z"
  environment: "local-docker (shop-app:latest)"
  base_results:
    success: true
    status_code: 200
    response_body: '{"deleted":true,"itemId":"item-abc123"}'
    state_after:
      item_exists: false
    logs:
      - "[INFO] item.deleted user=alice item=item-abc123"
  att_results:
    success: true
    status_code: 200
    response_body: '{"deleted":true,"itemId":"item-xyz789"}'
    state_after:
      item_exists: false
    logs:
      - "[INFO] item.deleted user=bob item=item-xyz789"
    errors: []
  delta:
    summary: >
      CRITICAL: Attack path succeeded identically to baseline.
      Bob deleted Alice's item with 200 OK. No ownership check performed.
    differences:
      - aspect: "HTTP Response"
        baseline: "200 OK"
        attack: "200 OK"
        significance: "Attack should have returned 403"
      - aspect: "Resource State"
        baseline: "Item deleted (expected - owner)"
        attack: "Item deleted (VULNERABILITY - non-owner)"
        significance: "Unauthorized deletion succeeded"
      - aspect: "Audit Log"
        baseline: "item.deleted user=alice"
        attack: "item.deleted user=bob"
        significance: "No authorization failure logged"
    invariant_states:
      - invariant: INV-SHOP-OWNER-DELETE
        state: VIOLATED
        evidence: "Bob (non-owner) successfully deleted Alice's item"

verdict:
  result: VIOLATION_CONFIRMED
  summary: >
    INV-SHOP-OWNER-DELETE is VIOLATED. The delete endpoint only checks
    authentication (valid token) but not authorization (ownership).
    Any authenticated user can delete any item by knowing its ID.
  confidence: HIGH
  finding_ref: FD-SHOP-AUTHZ-001
  recommendations:
    - "Add ownership check: if (item.ownerId !== user.id) return 403"
    - "Audit all resource endpoints for similar IDOR patterns"
    - "Add integration tests for authorization boundaries"

acceptance_criteria:
  pass:
    - "Attack returns 200 OK (same as baseline)"
    - "Item deleted by non-owner"
    - "No authorization error in logs"
  fail:
    - "Attack returns 403 Forbidden"
    - "Item remains intact"
    - "Unauthorized attempt logged"

cleanup:
  description: "Remove test users and items"
  steps:
    - "DELETE FROM items WHERE name LIKE 'Target Item%'"
    - "DELETE FROM users WHERE email IN ('alice@example.com', 'bob@example.com')"
  automated: true

status: ACTIVE
version: "1.0.0"
```

---

## Validation Criteria

A valid exploration artifact MUST:

1. **Have a unique ID** matching pattern `E-<SYSTEM>-<NAME>-<NNN>-<VV>`
2. **Reference a valid scenario** (S-*)
3. **Have complete base_setup, base_action, base_expected** for baseline path
4. **Have complete att_setup, att_action, att_expected** for attack path
5. **Have observations** section (even if empty before execution)
6. **Have verdict** section with result and summary
7. **Use concrete, reproducible commands** in action steps
8. **Include invariant expectations** tied to scenario's targeted invariants

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Scenario Artifact](../scenario/scenario.md) - Hypotheses that explorations test
- [Finding Artifact](../finding/finding.md) - Confirmed vulnerabilities from successful explorations
- [Interaction Artifact](../interaction/interaction.md) - Operations referenced in action steps
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Rules being tested
- [Trace Artifact](../../supporting/trace/trace.md) - Optional structured evidence for ordering/temporal claims

---

## Common Pitfalls

- Omitting a baseline run (BASE) so you can’t interpret the attack delta (ATT).
- Changing multiple variables between BASE and ATT (violates Delta Analysis discipline).
- Recording outcomes without reproducible evidence (response codes, payload diffs, logs, traces).
