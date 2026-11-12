# Exploration Verdicts Specification

Verdict assignment MUST preserve uncertainty and independently supported findings under [Evidence Evaluation](06-evidence-evaluation.md). A finite formula result or unavailable evaluator alone does not establish a confirmed verdict.

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

`VIOLATION_CONFIRMED` indicates that ATT succeeded in a way that demonstrates a security violation established by direct property-specific evidence relative to BASE, and at least one targeted invariant is observed as `VIOLATED`.

### Requirements

When `verdict.result` is `VIOLATION_CONFIRMED`:

1. A Finding MUST be created.
2. The Finding MUST reference the exploration (TR-1).
3. The exploration SHOULD set `verdict.finding_ref` to the created Finding ID. If supplied, it MUST resolve to a Finding referencing this exploration.
4. The Finding's violated invariants MUST be targeted by the Scenario and recorded as `VIOLATED` in this exploration.

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
2. The exploration MUST record every targeted invariant exactly once as `HOLDS`, with nonblank direct-evidence descriptions in `observations.delta.invariant_states[]`.

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
2. `observations.executed_at` and a nonblank `verdict.summary` MUST record the execution and uncertainty.
3. The exploration SHOULD include next steps in `verdict.recommendations[]`.

---

## BLOCKED

### Definition

`BLOCKED` indicates that the exploration could not be executed due to external constraints (missing credentials, unavailable environment, tooling limitations, test data cannot be provisioned, etc.).

### Requirements

When `verdict.result` is `BLOCKED`:

1. A Finding MUST NOT be created.
2. The blocking reason MUST be recorded in a nonblank `verdict.summary`.
3. `observations` MUST be empty; if execution occurred, use `INCONCLUSIVE` for an unresolved outcome.

---

## Shared record requirements

Both confirmed verdicts require a timestamp, environment, successful matched BASE, nonempty ATT results, a nonblank delta summary and verdict summary, and recorded targeted invariant states. Decisive states require nonblank evidence. Duplicate or unrelated invariant observations are invalid. See [Exploration record requirements](../artifacts/primary/exploration/exploration.md#record-requirements-by-outcome).

An unexecuted `DRAFT` or `PLANNED` exploration MAY omit `verdict` with `observations: {}`. Other lifecycle states require a verdict. A supplied verdict always carries its requirements, regardless of lifecycle status.

## Aggregation Guidance

When deciding a verdict from invariant observations:

- If a targeted invariant is supported as `VIOLATED` and all confirmed-violation requirements are met, use `VIOLATION_CONFIRMED`. An unrelated UNKNOWN target MUST NOT erase that supported violation.
- Else if EVERY targeted invariant is observed as `HOLDS` and the delta matches expectations, prefer `ENFORCEMENT_CONFIRMED`.
- Else prefer `INCONCLUSIVE`.

Use `BLOCKED` when execution itself was not possible.
