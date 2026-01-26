# Traceability Rules Specification

## Overview

CFSE artifacts form a connected graph where each artifact type references others according to defined rules. Traceability ensures that security findings can be traced back to their origins and that all artifacts are properly connected.

---

## Traceability Rules Summary

CFSE core defines TR-1 through TR-5. Extensions MAY define additional traceability rules. Extension traceability rules apply only when the extension is declared by the corpus (see `foundations/extensions.md`).

| Rule | Statement |
|------|-----------|
| TR-1 | Every Finding MUST reference at least one Exploration |
| TR-2 | Every Exploration MUST reference exactly one Scenario |
| TR-3 | Every Scenario MUST reference at least one Invariant |
| TR-4 | Every Invariant MUST reference at least one Predicate |
| TR-5 | Every Patch MUST reference exactly one Finding |

---

## EP/PRJ Traceability

CFSE includes a supporting artifact for viewer-context modeling:

- `EP-*` (Entry Point): first-class surface artifact (how accessed + what it can expose, as a viewer-agnostic superset)
- `PRJ-*` (Projection): viewer-context-specific “what is seen” slice across one or more surfaces

Recommended traceability conventions:

- An `EP-*` SHOULD reference exactly one `owner_concept: C-*`.
- `EP.exposes[].governed_by_invariants` SHOULD reference the invariants that gate that exposure (traceability only; invariants carry the logic).
- A `PRJ-*` SHOULD reference one or more `EP-*` surfaces, and SHOULD reference the invariants/predicates assumed by its viewer context.

These conventions do not affect CFSE core conformance unless a conformance profile explicitly requires them.

---

## Trace Evidence (T-*)

CFSE also supports a supporting **Trace** artifact (`T-*`) for capturing ordered evidence (events and/or state facts). Traces are especially useful when:

- An invariant uses temporal operators (`ALWAYS`, `EVENTUALLY`, `LEADS_TO`)
- A finding depends on ordering ("A happened before B", "B never occurred after A")
- You need reproducible evidence beyond prose log snippets

Recommended conventions:

- A `T-*` SHOULD reference exactly one `exploration_ref: E-*` (the exploration that produced or motivated the trace).
- An Exploration SHOULD link baseline/attack traces via `trace_refs` when temporal or ordering claims are central.
- A Finding MAY link one or more trace artifacts via `traceability.trace_refs` to make the evidence auditable.

Example:

```yaml
exploration:
  id: E-SHOP-IDOR-DELETE-001-01
  scenario_ref: S-SHOP-IDOR-DELETE-001
  trace_refs:
    baseline: T-SHOP-IDOR-DELETE-001-01-01
    attack: T-SHOP-IDOR-DELETE-001-01-02

finding:
  id: FD-SHOP-AUTHZ-001
  traceability:
    exploration: E-SHOP-IDOR-DELETE-001-01
    trace_refs:
      - T-SHOP-IDOR-DELETE-001-01-01
      - T-SHOP-IDOR-DELETE-001-01-02
```

These conventions do not affect CFSE core conformance unless a conformance profile explicitly requires them.

---

## TR-1: Finding to Exploration

### Rule Statement

**Every Finding MUST reference at least one Exploration.**

### Rationale

Findings represent confirmed vulnerabilities. They MUST be supported by reproducible evidence captured in explorations. A Finding without exploration reference is an unsubstantiated claim.

### Cardinality

| From | To | Cardinality |
|------|----|-------------|
| Finding | Exploration | 1..* |

### Validation

```yaml
# Valid: Single exploration reference
finding:
  id: FD-OJS-AUTHZ-001
  exploration_refs:
    - E-OJS-PAYMENT-BYPASS-001-01

# Valid: Multiple exploration references
finding:
  id: FD-OJS-AUTHZ-002
  exploration_refs:
    - E-OJS-IDOR-001-01
    - E-OJS-IDOR-001-02
    - E-OJS-IDOR-002-01

# INVALID: No exploration reference
finding:
  id: FD-OJS-AUTHZ-003
  # Missing exploration_refs - VIOLATION OF TR-1
```

### When Traceability Breaks

If TR-1 is violated:

1. The Finding MUST NOT be considered valid
2. The Finding MUST be marked as `draft` status
3. An exploration MUST be created to substantiate the claim
4. Automated validators MUST reject the Finding

### Common Mistakes

- [] Creating Findings from theoretical analysis without exploration
- [] Referencing explorations with INCONCLUSIVE verdict
- [] Referencing explorations that test different vulnerabilities
- [] Failing to update Finding when exploration is deprecated

---

## TR-2: Exploration to Scenario

### Rule Statement

**Every Exploration MUST reference exactly one Scenario.**

### Rationale

Explorations are concrete executions of scenario hypotheses. Each exploration tests one specific scenario. Multiple explorations may test the same scenario with different parameters or approaches.

### Cardinality

| From | To | Cardinality |
|------|----|-------------|
| Exploration | Scenario | 1 |

### Validation

```yaml
# Valid: Single scenario reference
exploration:
  id: E-OJS-PAYMENT-BYPASS-001-01
  scenario_ref: S-OJS-PAYMENT-BYPASS-001

# Valid: Different exploration, same scenario
exploration:
  id: E-OJS-PAYMENT-BYPASS-001-02
  scenario_ref: S-OJS-PAYMENT-BYPASS-001

# INVALID: No scenario reference
exploration:
  id: E-OJS-UNKNOWN-001-01
  # Missing scenario_ref - VIOLATION OF TR-2

# INVALID: Multiple scenario references
exploration:
  id: E-OJS-MULTI-001-01
  scenario_ref:
    - S-OJS-PAYMENT-BYPASS-001
    - S-OJS-IDOR-001
  # Multiple scenarios - VIOLATION OF TR-2
```

### When Traceability Breaks

If TR-2 is violated:

1. The Exploration MUST NOT be considered valid
2. The appropriate Scenario MUST be identified or created
3. If testing multiple scenarios, MUST split into separate explorations
4. Automated validators MUST reject the Exploration

### Common Mistakes

- [] Executing explorations without defined scenarios
- [] Combining multiple attack hypotheses in one exploration
- [] Referencing deprecated scenarios without migration
- [] Using scenario_ref as array when only one is allowed

---

## TR-3: Scenario to Invariant

### Rule Statement

**Every Scenario MUST reference at least one Invariant.**

### Rationale

Scenarios describe attack hypotheses. These hypotheses are formalized as potential violations of invariants. Without invariant references, a scenario lacks testable security properties.

### Cardinality

| From | To | Cardinality |
|------|----|-------------|
| Scenario | Invariant | 1..* |

### Validation

```yaml
# Valid: Single invariant reference
scenario:
  id: S-OJS-PAYMENT-BYPASS-001
  targeted_invariants:
    - INV-ORDER-PAYMENT-REQUIRED

# Valid: Multiple invariant references
scenario:
  id: S-OJS-AUTHZ-COMPOSITE-001
  targeted_invariants:
    - INV-FILE-OWNER-DELETE
    - INV-FILE-OWNER-READ
    - INV-FILE-SHARE-EXPLICIT

# INVALID: No invariant reference
scenario:
  id: S-OJS-VAGUE-001
  # Missing targeted_invariants - VIOLATION OF TR-3
```

### When Traceability Breaks

If TR-3 is violated:

1. The Scenario MUST NOT be considered executable
2. Relevant invariants MUST be identified from the scenario hypothesis
3. New invariants MAY need to be created if none exist
4. Automated validators MUST reject the Scenario

### Common Mistakes

- [] Defining scenarios without identifying security properties
- [] Referencing invariants unrelated to the scenario hypothesis
- [] Using informal invariant descriptions instead of IDs
- [] Not updating scenario when invariants are deprecated

---

## TR-4: Invariant to Predicate

### Rule Statement

**Every Invariant MUST reference at least one Predicate.**

### Rationale

Invariants are composed of predicates that describe testable conditions. Predicates provide the atomic building blocks for invariant evaluation.

### Cardinality

| From | To | Cardinality |
|------|----|-------------|
| Invariant | Predicate | 1..* |

### Validation

```yaml
# Valid: Single predicate reference
invariant:
  id: INV-USER-HAS-MFA
  predicates:
    - P-MFA-ENABLED

# Valid: Multiple predicate references (compound invariant)
invariant:
  id: INV-ADMIN-SECURE-ACCESS
  predicates:
    - P-USER-IS-ADMIN
    - P-MFA-ENABLED
    - P-SESSION-NOT-EXPIRED

# Valid: Predicate with logical operators
invariant:
  id: INV-FILE-ACCESS
  expression: "P-FILE-EXISTS AND (P-USER-IS-OWNER OR P-USER-HAS-SHARE)"
  predicates:
    - P-FILE-EXISTS
    - P-USER-IS-OWNER
    - P-USER-HAS-SHARE

# INVALID: No predicate reference
invariant:
  id: INV-VAGUE-SECURITY
  # Missing predicates - VIOLATION OF TR-4
```

### When Traceability Breaks

If TR-4 is violated:

1. The Invariant MUST NOT be considered testable
2. The invariant MUST be decomposed into predicate conditions
3. New predicates MAY need to be created
4. Automated validators MUST reject the Invariant

### Common Mistakes

- [] Defining invariants as prose without predicate decomposition
- [] Using predicates without formal definitions
- [] Not keeping predicate references updated when invariant logic changes
- [] Referencing deprecated predicates

---

## TR-5: Patch to Finding

### Rule Statement

**Every Patch MUST reference exactly one Finding.**

### Rationale

Patches are remediation artifacts that address specific findings. Each patch is the response to one finding. If a patch addresses multiple findings, each finding should have its own patch reference or the findings should be consolidated.

### Cardinality

| From | To | Cardinality |
|------|----|-------------|
| Patch | Finding | 1 |

### Validation

```yaml
# Valid: Single finding reference
patch:
  id: PATCH-OJS-001
  finding_ref: FD-OJS-AUTHZ-001

# INVALID: No finding reference
patch:
  id: PATCH-OJS-002
  # Missing finding_ref - VIOLATION OF TR-5

# INVALID: Multiple finding references
patch:
  id: PATCH-OJS-003
  finding_ref:
    - FD-OJS-AUTHZ-001
    - FD-OJS-AUTHZ-002
  # Multiple findings - VIOLATION OF TR-5 (split into multiple patches)
```

### When Traceability Breaks

If TR-5 is violated:

1. The Patch MUST NOT be considered valid
2. The associated Finding MUST be identified
3. If addressing multiple findings, MUST split into separate patches or consolidate findings
4. Automated validators MUST reject the Patch

### Common Mistakes

- [] Creating patches without associated findings
- [] Bundling fixes for multiple findings into one patch
- [] Referencing findings that have not been confirmed
- [] Not updating patch reference when finding ID changes

---

## Complete Traceability Chain

The full traceability chain flows as follows:

```
  Patch
    |
    | TR-5 (1)
    v
  Finding
    |
    | TR-1 (1..*)
    v
  Exploration
    |
    | TR-2 (1)
    v
  Scenario
    |
    | TR-3 (1..*)
    v
  Invariant
    |
    | TR-4 (1..*)
    v
  Predicate
```

Traces (`T-*`) are optional evidence artifacts that attach to Explorations and/or Findings. They do not change the core TR-1..TR-5 chain; they make evidence for ordering/temporal claims explicit and reproducible.

```
  Exploration  <-----  Trace (T-*)
      |
      v
   Finding
```

### Forward Traceability (Origin to Outcome)

From a Predicate, trace forward to understand impact:

```
Predicate -> Invariant -> Scenario -> Exploration -> Finding -> Patch
```

**Use Case**: "If this predicate changes, what findings might be affected?"

### Backward Traceability (Outcome to Origin)

From a Patch, trace backward to understand root cause:

```
Patch -> Finding -> Exploration -> Scenario -> Invariant -> Predicate
```

**Use Case**: "What security property was violated that led to this patch?"

---

## Validation Matrix

### Required Reference Fields by Artifact Type

| Artifact Type | Required Reference | Field Name | Cardinality |
|--------------|-------------------|------------|-------------|
| Concept | Invariant | `invariants` | 0..* |
| Concept | Entry Point | `entry_points` | 1..* |
| Entry Point | Concept | `owner_concept` | 1 |
| Interaction | Concept | `from_concept` | 1 |
| Interaction | Concept | `to_concept` | 1 |
| Interaction | Invariant | `pre_invariants` | 1..* |
| Interaction | Invariant | `post_invariants` | 1..* |
| Interaction | Entry Point | `entry_points` | 1..* |
| Projection | Entry Point | `surfaces[].ref` | 1..* |
| Finding | Exploration | `exploration_refs` | 1..* |
| Exploration | Scenario | `scenario_ref` | 1 |
| Scenario | Invariant | `targeted_invariants` | 1..* |
| Invariant | Predicate | `predicates` | 1..* |
| Patch | Finding | `finding_ref` | 1 |

### Optional Evidence Reference Fields

| Artifact Type | Optional Reference | Field Name | Cardinality |
|--------------|-------------------|------------|-------------|
| Trace | Exploration | `exploration_ref` | 1 |
| Exploration | Trace | `trace_refs` | 0..* |
| Finding | Trace | `traceability.trace_refs` | 0..* |

### Cross-Reference Validation Rules

1. All referenced IDs MUST exist
2. Referenced artifacts MUST be in `DRAFT`, `REVIEW`, or `ACTIVE` status (not `ARCHIVED`)
3. References to `DEPRECATED` artifacts MUST generate warnings
4. Circular references MUST NOT exist within the same artifact type
5. Reference chains MUST be finite (no infinite loops)

---

## Orphan Detection

### Definition

An orphan artifact has no incoming references when references are expected.

### Orphan Detection Rules

| Artifact Type | Expected Incoming | Orphan Condition |
|--------------|-------------------|------------------|
| Exploration | Finding (if `VIOLATION_CONFIRMED`) | `VIOLATION_CONFIRMED` verdict but no Finding references it |
| Scenario | Exploration | No Exploration tests this Scenario |
| Invariant | Scenario | No Scenario references this Invariant |
| Predicate | Invariant | No Invariant uses this Predicate |
| Finding | Patch | No Patch addresses this Finding (may be acceptable) |

### Orphan Handling

1. Orphan Explorations (`VIOLATION_CONFIRMED`): MUST create associated Finding
2. Orphan Scenarios: SHOULD be executed or marked deprecated
3. Orphan Invariants: SHOULD be incorporated into scenarios or deprecated
4. Orphan Predicates: SHOULD be used or deprecated
5. Orphan Findings: Acceptable (not all findings need patches immediately)

---

## Common Mistakes Summary

### General Traceability Mistakes

- [] Creating artifacts without required references
- [] Referencing non-existent artifact IDs
- [] Referencing archived or invalid artifacts
- [] Not updating references when target artifacts change IDs
- [] Creating circular reference chains
- [] Using informal references instead of formal IDs

### Reference Staleness

- [] Not validating references when importing artifacts
- [] Not propagating deprecation notices through reference chains
- [] Not auditing orphan artifacts periodically

---

## Validation Rules

### Schema Compliance

```yaml
TraceabilityValidation:
  rules:
    TR-1:
      source: Finding
      target: Exploration
      field: exploration_refs
      cardinality: "1..*"
      required: true
    TR-2:
      source: Exploration
      target: Scenario
      field: scenario_ref
      cardinality: "1"
      required: true
    TR-3:
      source: Scenario
      target: Invariant
      field: invariants
      cardinality: "1..*"
      required: true
    TR-4:
      source: Invariant
      target: Predicate
      field: predicates
      cardinality: "1..*"
      required: true
    TR-5:
      source: Patch
      target: Finding
      field: finding_ref
      cardinality: "1"
      required: true
```

### Automated Checks

Validators MUST enforce:

1. All TR-* rules on artifact creation
2. Reference existence checks
3. Reference state checks (not archived)
4. Orphan detection and reporting
5. Circular reference detection

---

## Related Specifications

- [[../grammar/04-field-types]] - Artifact ID patterns
- [[../grammar/02-reference-syntax]] - Reference syntax rules
- [[03-artifact-lifecycle]] - Artifact state rules
- [[01-invariant-states]] - Invariant-specific states
