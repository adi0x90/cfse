# Exploration Verdicts Specification

## Overview

An exploration is a concrete security experiment that executes a Baseline (BASE) path and an Attack (ATT) path, then interprets the observed delta.

Explorations record their final outcome in `verdict`, using `verdict.result` to indicate whether a vulnerability was demonstrated, the defense was demonstrated, or results were not usable.

---

## Verdict Enumeration

`verdict.result` MUST be one of:

| Result | Meaning | Finding Required |
|--------|---------|------------------|
| `VIOLATION_CONFIRMED` | Attack achieved the objective (invariant violated) | MUST create Finding |
| `ENFORCEMENT_CONFIRMED` | Attack was blocked as expected (invariant holds) | No Finding required |
| `INCONCLUSIVE` | Execution occurred but evidence is ambiguous | MUST NOT create Finding |
| `BLOCKED` | Could not execute due to environment/tooling constraints | MUST NOT create Finding |

---

## VIOLATION_CONFIRMED

### Definition

`VIOLATION_CONFIRMED` indicates that ATT succeeded in a way that demonstrates a security violation (insufficient delta relative to BASE), and at least one targeted invariant is observed as `VIOLATED`.

### Requirements

When `verdict.result` is `VIOLATION_CONFIRMED`:

1. A Finding MUST be created.
2. The Finding MUST reference the exploration (TR-1).
3. The exploration SHOULD set `verdict.finding_ref` to the created Finding ID.

### Example

```yaml
verdict:
  result: VIOLATION_CONFIRMED
  summary: "ATT behaved like BASE; authorization bypass confirmed"
  confidence: HIGH
  finding_ref: FD-SHOP-AUTHZ-001
```

---

## ENFORCEMENT_CONFIRMED

### Definition

`ENFORCEMENT_CONFIRMED` indicates that ATT was rejected/blocked as expected and the protected state remained intact, producing a meaningful delta from BASE. Targeted invariants are observed as `HOLDS` (and none as `VIOLATED`).

### Requirements

When `verdict.result` is `ENFORCEMENT_CONFIRMED`:

1. A Finding MUST NOT be created.
2. The exploration SHOULD include evidence in `observations.delta.invariant_states[]` and/or other observation fields.

### Example

```yaml
verdict:
  result: ENFORCEMENT_CONFIRMED
  summary: "ATT rejected; protected resource unchanged"
  confidence: HIGH
```

---

## INCONCLUSIVE

### Definition

`INCONCLUSIVE` indicates that execution happened, but the evidence does not support a confident conclusion (e.g., invariant states are `UNKNOWN`, the delta is noisy/contradictory, or results can be interpreted multiple ways).

### Requirements

When `verdict.result` is `INCONCLUSIVE`:

1. A Finding MUST NOT be created from this exploration alone.
2. The exploration SHOULD include next steps in `verdict.recommendations[]`.

---

## BLOCKED

### Definition

`BLOCKED` indicates that the exploration could not be executed due to external constraints (missing credentials, unavailable environment, tooling limitations, test data cannot be provisioned, etc.).

### Requirements

When `verdict.result` is `BLOCKED`:

1. A Finding MUST NOT be created.
2. The blocking reason SHOULD be recorded (commonly in `verdict.summary` and/or `observations.environment`).

---

## Aggregation Guidance

When deciding a verdict from invariant observations:

- If ANY targeted invariant is observed as `VIOLATED`, prefer `VIOLATION_CONFIRMED`.
- Else if targeted invariants are observed as `HOLDS` and the delta matches expectations, prefer `ENFORCEMENT_CONFIRMED`.
- Else prefer `INCONCLUSIVE`.

Use `BLOCKED` when execution itself was not possible.
