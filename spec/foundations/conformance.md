# Conformance

## Overview

This section defines what it means for an implementation to conform to the CFSE specification.

## Conformance Levels

CFSE defines three conformance levels to accommodate different use cases:

### Minimal Conformance

**Required artifacts:** Concepts, Entry Points, Scenarios, Explorations

**Use case:** Quick security assessments, time-constrained engagements

**Requirements:**
- Concepts MUST have: ID, Name, Promise, Entry Points (with `EP-*` IDs), Invariants (may be empty)
- Entry Points MUST have: ID, Title, Owner Concept, Method, Path, Action
- Scenarios MUST have: ID, Hypothesis, Attack Vector
- Explorations MUST have: ID, Scenario Reference, Observations, Verdict

### Standard Conformance

**Required artifacts:** All Minimal + Interactions, Flows, Invariants, Findings

**Use case:** Typical security assessments, penetration testing

**Requirements:**
- All Minimal requirements
- Interactions MUST have: ID, From/To Concepts, Entry Points (`EP-*`), Pre/Post Invariants
- Flows MUST have: ID, Steps with Interaction references
- Invariants MUST have: ID, Rule, Logic expression
- Findings MUST have: ID, Evidence (Exploration references), Remediation

**Optional supporting artifacts (not required for conformance):**
- Projections (`PRJ-*`)
- Traces (`T-*`)

### Full Conformance

**Required artifacts:** All Standard + Predicates, Generators, Patches

**Use case:** Comprehensive security programs, methodology development

**Requirements:**
- All Standard requirements
- Predicates MUST have: ID, Parameters, Definition
- Invariants MUST decompose into Predicates
- Generators MUST have: ID, Template, Variables
- Patches MUST have: ID, Finding reference, Verification evidence
- Complete traceability (TR-1 through TR-5)

## Validation Criteria

### ID Syntax Validation

All artifact IDs MUST match their defined regex patterns (see grammar/01-id-syntax.md).

### Reference Validation

All cross-references MUST resolve to existing artifacts.

### Schema Validation

All artifacts MUST validate against their YAML schemas.

If a corpus uses an Invariant Library YAML file, every Predicate and Invariant entry in that library MUST validate against the Predicate and Invariant schemas (see `artifacts/supporting/invariant_library/invariant_library.md`).

### Traceability Validation

At Full conformance, all traceability rules (TR-1 through TR-5) MUST be satisfied.

## Conformance Declaration

A CFSE implementation SHOULD declare its conformance level:

```yaml
cfse:
  version: "1.0.0"
  conformance: "standard"  # minimal | standard | full
```

## Extensions

CFSE supports optional extensions. A corpus MAY declare extensions alongside core conformance.

See `foundations/extensions.md` for the normative extension mechanism.

Example:

```yaml
cfse:
  version: "1.0.0"
  conformance: "standard"
  extensions:
    example_ext:
      version: "0.1.0"
      conformance: "standard"
```

## Partial Conformance

An implementation that meets some but not all requirements of a level is considered non-conformant to that level but MAY declare partial conformance:

```yaml
cfse:
  version: "1.0.0"
  conformance: "partial"
  level: "standard"
  missing:
    - "Flows do not reference Interaction IDs"
```
