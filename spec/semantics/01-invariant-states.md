# Invariant States Specification

## Overview

During explorations, invariants are evaluated against system behavior to determine whether security properties hold. This specification defines the four possible invariant states and their interpretation rules.

---

## State Definitions

### InvariantState Enumeration

| State | Description | Implies |
|-------|-------------|---------|
| `HOLDS` | System prevented the violation | Security control is working |
| `VIOLATED` | System allowed the violation | Security vulnerability exists |
| `UNKNOWN` | Could not determine state | Requires further investigation |
| `NOT_APPLICABLE` | Not evaluated in this exploration | Neutral - no conclusion drawn |

---

## HOLDS

### Definition

The invariant state HOLDS indicates that the system actively prevented an attempted violation of the security property.

### Semantic Interpretation

When an invariant is marked HOLDS:

1. The attack path (ATT) was executed
2. The attack was blocked or rejected by the system
3. The protected resource or state remained intact
4. Observable behavior differed from the baseline as expected

### Usage Criteria

An invariant MUST be marked HOLDS when ALL of the following conditions are met:

- The ATT path attempted to violate the invariant
- The system returned an error response (e.g., 403, 401, 422)
- The protected state was NOT modified
- Side effects were NOT triggered

### Example

```yaml
invariant:
  id: INV-FILE-OWNER-DELETE
  state: HOLDS
  evidence:
    att_status: 403
    att_body: '{"error": "Forbidden"}'
    resource_state: "unchanged"
    notes: "User B could not delete User A's file"
```

### Related Verdict

When an invariant is HOLDS, the exploration verdict SHOULD be `ENFORCEMENT_CONFIRMED`.

---

## VIOLATED

### Definition

The invariant state VIOLATED indicates that the system failed to prevent an attempted violation of the security property.

### Semantic Interpretation

When an invariant is marked VIOLATED:

1. The attack path (ATT) was executed
2. The attack succeeded in circumventing security controls
3. The protected resource or state was improperly modified
4. Observable behavior matched the baseline when it should have differed

### Usage Criteria

An invariant MUST be marked VIOLATED when ANY of the following conditions are met:

- The ATT path succeeded in modifying protected state
- The ATT path received success response when rejection was expected
- The ATT path triggered side effects that should have been blocked
- The delta between BASE and ATT is insufficient (both paths behave identically)

### Example

```yaml
invariant:
  id: INV-ORDER-PAYMENT-REQUIRED
  state: VIOLATED
  evidence:
    att_status: 200
    att_body: '{"status": "paid"}'
    resource_state: "modified"
    notes: "Order status changed to 'paid' without payment"
```

### Related Verdict

When an invariant is VIOLATED, the exploration verdict SHOULD be `VIOLATION_CONFIRMED`.

---

## UNKNOWN

### Definition

The invariant state UNKNOWN indicates that the exploration could not determine whether the invariant was enforced or violated.

### Semantic Interpretation

When an invariant is marked UNKNOWN:

1. The exploration was executed but results are ambiguous
2. System behavior did not match expected patterns for either enforcement or violation
3. Additional investigation or different test approach is required

### Usage Criteria

An invariant SHOULD be marked UNKNOWN when ANY of the following conditions are met:

- System returned unexpected error unrelated to authorization (e.g., 500, timeout)
- Baseline path itself failed, preventing delta comparison
- Multiple invariants could explain observed behavior
- Environment issues affected test execution
- Response format was unparseable or unexpected

### Example

```yaml
invariant:
  id: INV-PAYMENT-IDEMPOTENT
  state: UNKNOWN
  evidence:
    att_status: 500
    att_body: '{"error": "Internal server error"}'
    resource_state: "unknown"
    notes: "Server crashed during replay attempt; cannot determine if idempotency holds"
```

### Related Verdict

When an invariant is UNKNOWN, the exploration verdict SHOULD be `INCONCLUSIVE`.

---

## NOT_APPLICABLE

### Definition

The invariant state NOT_APPLICABLE indicates that the invariant was not evaluated during this exploration.

### Semantic Interpretation

When an invariant is marked NOT_APPLICABLE:

1. The invariant is relevant to the system under test
2. This specific exploration did not attempt to test it
3. No conclusion about enforcement or violation can be drawn
4. A separate exploration MAY test this invariant

### Usage Criteria

An invariant SHOULD be marked NOT_APPLICABLE when ANY of the following conditions are met:

- The exploration scope did not include this invariant
- Prerequisites for testing the invariant were not met
- The invariant is listed for awareness but not under evaluation
- Resource constraints prevented testing

### Example

```yaml
invariant:
  id: INV-ADMIN-REQUIRES-MFA
  state: NOT_APPLICABLE
  notes: "Out of scope for this exploration; covered by E-AUTH-MFA-001-01"
```

### Related Verdict

NOT_APPLICABLE invariants MUST NOT influence the exploration verdict.

---

## State Transition Rules

### Valid Transitions

The following state transitions are valid during exploration execution:

```
NOT_APPLICABLE --> HOLDS    (invariant tested, protection worked)
NOT_APPLICABLE --> VIOLATED    (invariant tested, protection failed)
NOT_APPLICABLE --> UNKNOWN     (invariant tested, results ambiguous)
UNKNOWN  --> HOLDS    (re-tested with clearer results)
UNKNOWN  --> VIOLATED    (re-tested with clearer results)
```

### Invalid Transitions

The following transitions MUST NOT occur:

```
HOLDS --> VIOLATED    (contradictory without new evidence)
VIOLATED --> HOLDS    (contradictory without new evidence)
HOLDS --> NOT_APPLICABLE    (cannot "untest" an evaluated invariant)
VIOLATED --> NOT_APPLICABLE    (cannot "untest" an evaluated invariant)
```

### Re-evaluation Rules

1. An invariant MAY transition from UNKNOWN to HOLDS or VIOLATED after re-testing
2. An invariant MUST NOT change from HOLDS to VIOLATED (or vice versa) within the same exploration without documented justification
3. If new evidence contradicts a previous state, a NEW exploration SHOULD be created

---

## Common Mistakes

Review this checklist when assigning invariant states:

### HOLDS Mistakes

- [] Marking HOLDS when only the HTTP status differs but state was modified
- [] Marking HOLDS without verifying database/resource state
- [] Marking HOLDS when rejection was due to unrelated error (use UNKNOWN)

### VIOLATED Mistakes

- [] Marking VIOLATED when baseline itself failed (use UNKNOWN)
- [] Marking VIOLATED without proper ATT execution
- [] Marking VIOLATED for expected behavior differences (false positive)

### UNKNOWN Mistakes

- [] Using UNKNOWN as default without investigation
- [] Marking UNKNOWN when clear evidence exists for HOLDS/VIOLATED
- [] Not documenting why the state could not be determined

### NOT_APPLICABLE Mistakes

- [] Marking NOT_APPLICABLE for invariants that were actually evaluated
- [] Leaving invariants as NOT_APPLICABLE without justification
- [] Confusing NOT_APPLICABLE with UNKNOWN (NOT_APPLICABLE = not attempted; UNKNOWN = attempted but ambiguous)

---

## Validation Rules

### Schema Compliance

```yaml
InvariantObservation:
  type: object
  required: [id, state]
  properties:
    id:
      $ref: "#/$defs/InvariantID"
    state:
      type: string
      enum: [HOLDS, VIOLATED, UNKNOWN, NOT_APPLICABLE]
    evidence:
      type: object
    notes:
      type: string
```

### Consistency Checks

Validators MUST enforce:

1. Every invariant referenced in an exploration MUST have a state
2. At least one targeted invariant MUST have state other than NOT_APPLICABLE for a valid exploration
3. VIOLATED state MUST be accompanied by evidence
4. HOLDS state SHOULD be accompanied by evidence

---

## Related Specifications

- [[02-exploration-verdicts]] - How invariant states determine verdicts
- [[../grammar/04-field-types]] - InvariantState enum definition
- `artifacts/primary/exploration/exploration.md` - Exploration artifact structure
- [[05-delta-interpretation]] - Delta analysis semantics
