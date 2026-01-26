# Delta Interpretation Specification

## Overview

Delta Analysis is the scientific method at the heart of CFSE security testing. By comparing baseline (BASE) behavior against attack (ATT) behavior, explorations produce measurable differences (deltas) that determine whether invariants are enforced or violated.

---

## Core Principle

```
Delta = ATT - BASE
```

The delta represents the observable difference between legitimate behavior (baseline) and attack behavior. Security conclusions are drawn from whether this delta matches expected patterns.

---

## Baseline (BASE) Path Semantics

### Definition

The Baseline (BASE) path represents legitimate system behavior. It establishes the expected outcome when all preconditions are satisfied and the user operates within authorized boundaries.

### Validity Criteria

A BASE path is valid when ALL of the following conditions are met:

| Criterion | Requirement |
|-----------|-------------|
| Authentication | User MUST be properly authenticated |
| Authorization | User MUST have required permissions |
| Inputs | All inputs MUST be valid and well-formed |
| Preconditions | All flow preconditions MUST be satisfied |
| Sequence | Steps MUST follow the intended order |
| Outcome | Expected outcome MUST be success |

### BASE Path Characteristics

```yaml
baseline:
  authentication: required
  authorization: proper_permissions
  inputs: valid
  preconditions: satisfied
  sequence: correct_order
  expected_outcome: success
```

### Valid BASE Path Example

```bash
# Baseline: Authorized user deletes own file
# Preconditions: User A owns File 123, User A is authenticated

1. Login as User A
   POST /api/auth/login
   Response: 200 OK, token: "TOKEN_A"

2. Delete own file
   DELETE /api/files/123
   Headers: Authorization: Bearer TOKEN_A
   Response: 200 OK, {"deleted": true}

3. Verify deletion
   GET /api/files/123
   Response: 404 Not Found
```

### Invalid BASE Path Indicators

A BASE path is invalid when ANY of the following occur:

- [] BASE returns error response (4xx, 5xx)
- [] BASE fails to complete expected operation
- [] BASE requires steps not in the documented flow
- [] BASE state does not match expected outcome
- [] Environment issues prevent BASE execution

### Handling Invalid BASE

If the BASE path is invalid:

1. The exploration MUST NOT proceed to ATT execution
2. The environment or test data MUST be corrected
3. The verdict MUST be INCONCLUSIVE if forced to complete
4. The reason for BASE failure MUST be documented

---

## Attack (ATT) Path Semantics

### Definition

The Attack (ATT) path represents an attempt to violate the security property defined by the scenario. It manipulates one or more aspects of the legitimate path to test invariant enforcement.

### Validity Criteria

A ATT path is valid when ALL of the following conditions are met:

| Criterion | Requirement |
|-----------|-------------|
| Derivation | MUST be derived from a specific BASE path |
| Manipulation | MUST include at least one manipulation |
| Execution | MUST be fully executed (not partial) |
| Documentation | Manipulation type MUST be documented |
| Targeting | MUST target specific invariant(s) |

### Manipulation Types

| Type | Description | Example |
|------|-------------|---------|
| `skip_step` | Omit a required flow step | Skip payment in checkout |
| `reorder` | Execute steps out of sequence | Confirm before payment |
| `mutate_param` | Change parameter values | Use another user's ID |
| `set_state` | Force unexpected state | Set status to "paid" |
| `fault_injection` | Induce errors | Timeout during transaction |
| `timing` | Concurrent execution | TOCTOU race condition |

### ATT Path Characteristics

```yaml
attack:
  authentication: varies (may be wrong user or missing)
  authorization: attempting_to_bypass
  inputs: manipulated
  preconditions: intentionally_violated
  sequence: may_be_altered
  expected_outcome: rejection (if invariant holds)
```

### Valid ATT Path Example

```bash
# Attack: Unauthorized user attempts to delete another user's file
# Manipulation: mutate_param (wrong Authorization token)
# Target: INV-FILE-OWNER-DELETE

1. Login as User B (attacker)
   POST /api/auth/login
   Response: 200 OK, token: "TOKEN_B"

2. Attempt to delete User A's file
   DELETE /api/files/123
   Headers: Authorization: Bearer TOKEN_B  # Wrong owner!
   Response: ??? (expected 403 if invariant enforced)

3. Verify file state
   GET /api/files/123 (as admin)
   Response: ??? (expected 200 if invariant enforced)
```

### Invalid ATT Path Indicators

An ATT path is invalid when ANY of the following occur:

- [] ATT does not clearly target any invariant
- [] ATT manipulation is not documented
- [] ATT is not derived from corresponding BASE
- [] ATT execution is incomplete
- [] ATT encounters environment issues unrelated to security

---

## Observation Comparison

### Measurement Points

When comparing BASE and ATT, measure at these points:

| Measurement | Description | Weight |
|-------------|-------------|--------|
| HTTP Status | Response status code | Medium |
| Response Body | Response content/structure | Medium |
| Primary State | Main resource affected | High |
| Co-States | Related resources | High |
| Side Effects | Emails, logs, notifications | Medium |
| Timestamps | Created/updated times | Low |

### Comparison Table Template

```
| Measurement      | BASE           | ATT            | Delta          | Expected? |
|------------------|----------------|----------------|----------------|-----------|
| HTTP Status      | 200            | ???            | ???            | ???       |
| Response Body    | {"ok": true}   | ???            | ???            | ???       |
| Resource State   | deleted        | ???            | ???            | ???       |
| Audit Log        | "user deleted" | ???            | ???            | ???       |
```

### State Comparison Rules

1. Primary state comparison has highest weight
2. HTTP status alone is insufficient evidence
3. Multiple co-states SHOULD be checked
4. Side effects provide supporting evidence

---

## Delta Significance

### Significant Delta (Invariant Holds)

A delta is significant when it demonstrates protection:

| Indicator | BASE | ATT | Interpretation |
|-----------|------|-----|----------------|
| Status Code | 200 | 403/401 | Access denied |
| Resource | Modified | Unchanged | Protected |
| Side Effects | Triggered | Not triggered | Blocked |
| Audit Log | Success entry | Failure entry | Logged attempt |

### Example: Significant Delta

```
| Measurement      | BASE           | ATT              | Delta        | Expected? |
|------------------|----------------|------------------|--------------|-----------|
| HTTP Status      | 200            | 403              | Different    | Yes       |
| Response Body    | {"deleted":1}  | {"error":"..."}  | Different    | Yes       |
| File Exists      | No             | Yes              | Different    | Yes       |
| Audit Log        | "deleted"      | "denied"         | Different    | Yes       |

CONCLUSION: Delta is significant. Invariant HOLDS.
```

### Insignificant Delta (Invariant Violated)

A delta is insignificant when BASE and ATT behave identically:

| Indicator | BASE | ATT | Interpretation |
|-----------|------|-----|----------------|
| Status Code | 200 | 200 | Both succeeded |
| Resource | Modified | Modified | No protection |
| Side Effects | Triggered | Triggered | Bypass occurred |
| Audit Log | Success | Success | Not distinguished |

### Example: Insignificant Delta

```
| Measurement      | BASE           | ATT              | Delta        | Expected? |
|------------------|----------------|------------------|--------------|-----------|
| HTTP Status      | 200            | 200              | Same         | NO!       |
| Response Body    | {"deleted":1}  | {"deleted":1}    | Same         | NO!       |
| File Exists      | No             | No               | Same         | NO!       |
| Audit Log        | "deleted"      | "deleted"        | Same         | NO!       |

CONCLUSION: Delta is insignificant. Invariant VIOLATED. VULNERABILITY FOUND.
```

---

## Delta Interpretation Matrix

### Decision Logic

```
+-----------------+------------------+------------------+
| BASE Outcome    | ATT Outcome      | Interpretation   |
+-----------------+------------------+------------------+
| Success         | Rejected         | HOLDS            |
| Success         | Success          | VIOLATED         |
| Success         | Unexpected Error | UNKNOWN          |
| Failed          | Any              | INCONCLUSIVE     |
+-----------------+------------------+------------------+
```

### Detailed Interpretation

| BASE | ATT | State Changed | Verdict |
|------|-----|---------------|---------|
| 200 | 403 | No | `ENFORCEMENT_CONFIRMED` (HOLDS) |
| 200 | 401 | No | `ENFORCEMENT_CONFIRMED` (HOLDS) |
| 200 | 200 | Yes (same as BASE) | `VIOLATION_CONFIRMED` (VIOLATED) |
| 200 | 200 | No | INCONCLUSIVE (investigate) |
| 200 | 500 | Unknown | INCONCLUSIVE |
| 500 | Any | N/A | INCONCLUSIVE (fix BASE) |

---

## Noise vs. Signal

### What Constitutes Noise

Noise is variation that does not indicate security state:

| Noise Type | Example | How to Handle |
|------------|---------|---------------|
| Timing variations | Response time differs | Ignore unless testing timing attacks |
| Log timestamps | Different timestamp values | Compare presence, not values |
| Session IDs | Different session tokens | Compare authorization, not tokens |
| Request IDs | Different request identifiers | Ignore |
| Formatting | Whitespace differences | Normalize before comparison |

### What Constitutes Signal

Signal is variation that indicates security state:

| Signal Type | Example | Interpretation |
|-------------|---------|----------------|
| Status code class | 2xx vs 4xx | Authorization decision |
| Resource state | Exists vs deleted | Protection effectiveness |
| Permission errors | "Forbidden" message | Access control working |
| Audit entries | "denied" vs "allowed" | Security logging |
| Side effect presence | Email sent vs not sent | Flow control |

### Filtering Rules

1. Ignore timestamps unless testing temporal properties
2. Ignore request-specific identifiers
3. Normalize response formatting before comparison
4. Focus on state changes and permission messages
5. Compare semantic meaning, not byte-for-byte content

---

## Advanced Delta Patterns

### Multi-Point Delta

For complex flows, measure at multiple points:

```yaml
delta_measurements:
  - point: http_response
    base: 200
    att: 403
    significant: true
  - point: order.status
    base: "paid"
    att: "pending"
    significant: true
  - point: inventory.reserved
    base: -1
    att: 0
    significant: true
  - point: wallet.balance
    base: -100
    att: 0
    significant: true
```

### Temporal Delta

For race condition testing:

```yaml
temporal_delta:
  - t0:
      base: "User A starts checkout"
      att: "User A starts checkout"
  - t1:
      base: "Payment authorized"
      att: "User B starts checkout (same item)"
  - t2:
      base: "Inventory reserved (stock: 0)"
      att: "Both payments authorized (TOCTOU!)"
  - t3:
      base: "Order confirmed"
      att: "Inventory: -1 (over-reserved!)"
  conclusion: VIOLATED (race condition)
```

### Idempotency Delta

For replay attack testing:

```yaml
idempotency_delta:
  request:
    method: POST
    path: /api/transfer
    body: {"from": "A", "to": "B", "amount": 100}
  first_execution:
    balance_a: 900
    balance_b: 100
    tx_id: "tx-123"
  replay_execution:
    expected_balance_a: 900  # Idempotent
    actual_balance_a: 800    # Double charge!
  conclusion: VIOLATED (not idempotent)
```

---

## Common Mistakes

### BASE Path Mistakes

- [] Executing ATT before establishing valid BASE
- [] Not resetting state between BASE and ATT
- [] Assuming BASE succeeds without verification
- [] Using BASE with incorrect preconditions

### ATT Path Mistakes

- [] Not documenting the manipulation type
- [] Combining multiple manipulation types (hard to interpret)
- [] Not targeting specific invariants
- [] Incomplete ATT execution

### Comparison Mistakes

- [] Comparing only HTTP status codes
- [] Ignoring database/resource state
- [] Not checking side effects
- [] Confusing noise for signal
- [] Not resetting state between executions

### Interpretation Mistakes

- [] Concluding HOLDS without checking state
- [] Concluding VIOLATED when BASE failed
- [] Not documenting unexpected behavior
- [] Ignoring partial enforcement

---

## Validation Rules

### Schema Compliance

```yaml
DeltaAnalysis:
  type: object
  required: [baseline, attack, measurements, conclusion]
  properties:
    baseline:
      type: object
      required: [steps, outcome]
      properties:
        steps:
          type: array
          items:
            $ref: "#/$defs/ExecutionStep"
        outcome:
          type: string
          enum: [success, failure]
        observations:
          type: object
    attack:
      type: object
      required: [manipulation, steps, outcome]
      properties:
        manipulation:
          type: string
          enum: [skip_step, reorder, mutate_param, set_state, fault_injection, timing]
        steps:
          type: array
          items:
            $ref: "#/$defs/ExecutionStep"
        outcome:
          type: string
          enum: [success, failure, error]
        observations:
          type: object
    measurements:
      type: array
      items:
        $ref: "#/$defs/DeltaMeasurement"
      minItems: 1
    conclusion:
      type: object
      required: [delta_significant, invariant_state]
      properties:
        delta_significant:
          type: boolean
        invariant_state:
          type: string
          enum: [HOLDS, VIOLATED, UNKNOWN]
```

### Consistency Checks

Validators MUST enforce:

1. BASE MUST have outcome: success for valid delta
2. ATT manipulation MUST be documented
3. At least one measurement point MUST be recorded
4. conclusion MUST align with measurements
5. VIOLATED conclusion MUST have evidence of state modification

---

## Related Specifications

- [[01-invariant-states]] - How delta determines invariant state
- [[02-exploration-verdicts]] - How invariant states produce verdicts
- [[../explorations/explorations-spec]] - Exploration structure
- [[../explorations/delta-analysis-spec]] - Detailed methodology
