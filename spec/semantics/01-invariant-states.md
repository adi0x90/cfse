# Invariant States Specification

## Overview

During explorations, invariants are evaluated against system behavior to determine whether security properties hold. This specification defines the four possible invariant states and their interpretation rules.

---

## State Definitions

### InvariantState Enumeration

| State | Description | Implies |
|-------|-------------|---------|
| `HOLDS` | Evidence shows the targeted property held in this run | Scoped enforcement evidence |
| `VIOLATED` | Evidence shows a targeted property violation in this run | Scoped counterexample |
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
3. Property-specific evidence shows the protected state, data, or effect remained protected
4. Observable behavior differed from the baseline as expected

### Usage Criteria

An invariant MUST be marked HOLDS only when the ATT path was executed against a working matched BASE and direct, property-specific evidence shows the attempted violation was prevented. For a deletion invariant this includes verifying that the protected item remains present; for confidentiality it includes inspecting the returned data.

An error status alone is insufficient, and an error status is not mandatory: a safe no-op may return success while preserving the property. `HOLDS` describes this execution, not all possible executions of the system.

### Example

```yaml
invariant: INV-FILE-OWNER-DELETE
state: HOLDS
evidence: "ATT returned 403; an owner-side read confirmed the file remained present and unchanged after the attempted deletion."
```

### Related Verdict

Only when every targeted invariant is supported as `HOLDS` and the confirmed-outcome requirements are met may the exploration use `ENFORCEMENT_CONFIRMED`.

---

## VIOLATED

### Definition

The invariant state VIOLATED indicates that the system failed to prevent an attempted violation of the security property.

### Semantic Interpretation

When an invariant is marked VIOLATED:

1. The attack path (ATT) was executed
2. The attack succeeded in circumventing security controls
3. Direct evidence establishes an unauthorized effect, disclosure, or other breach of the targeted property
4. Observable behavior matched the baseline when it should have differed

### Usage Criteria

An invariant MUST be marked VIOLATED only when the ATT path executed against a working matched BASE and direct, property-specific evidence establishes a breach. This may be unauthorized modification, disclosure, an unintended side effect, or another concrete counterexample to the invariant.

A success response, an identical BASE/ATT status, or an otherwise small delta alone MUST NOT establish `VIOLATED`. If the protected effect is not observed or the result is ambiguous, use `UNKNOWN` and an `INCONCLUSIVE` exploration verdict.

### Example

```yaml
invariant: INV-ORDER-PAYMENT-REQUIRED
state: VIOLATED
evidence: "After ATT skipped payment, an independent order read showed status paid without a payment record."
```

### Related Verdict

A supported targeted `VIOLATED` state can justify `VIOLATION_CONFIRMED` when all confirmed-outcome requirements and Finding linkage are satisfied.

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
invariant: INV-PAYMENT-IDEMPOTENT
state: UNKNOWN
evidence: "ATT returned 500; post-request account state could not be read, so replay effects remain unknown."
```

### Related Verdict

If no targeted violation is established and any targeted invariant is `UNKNOWN`, the exploration verdict is `INCONCLUSIVE`. A supported violation of another target can still justify `VIOLATION_CONFIRMED`.

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
invariant: INV-ADMIN-REQUIRES-MFA
state: NOT_APPLICABLE
evidence: "Not tested; requires a separate exploration before claiming enforcement."
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

The authoritative record is `InvariantResult` in [the Exploration schema](../artifacts/primary/exploration/exploration.schema.yaml). It uses `invariant` (an InvariantID), `state` (an InvariantState), and optional `evidence` text. `HOLDS` and `VIOLATED` require nonblank evidence.

### Consistency Checks

Validators MUST reject duplicate or unrelated invariant observations. Confirmed violation requires at least one targeted `VIOLATED` state; confirmed enforcement requires every targeted invariant as `HOLDS`. Drafts, blocked runs and inconclusive runs do not require decisive observations.

Researchers MUST ensure the direct evidence comes from this execution or its linked Trace and supports the declared property. Static record validation does not establish that semantic relationship. See [Exploration Key Patterns](../artifacts/primary/exploration/exploration.md#key-patterns).

---

## Related Specifications

- [[02-exploration-verdicts]] - How invariant states determine verdicts
- [[../grammar/04-field-types]] - InvariantState enum definition
- `artifacts/primary/exploration/exploration.md` - Exploration artifact structure
- [[05-delta-interpretation]] - Delta analysis semantics
