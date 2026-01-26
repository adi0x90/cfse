# Artifact System

## Overview

CFSE produces structured artifacts that build upon each other in a defined pipeline. Understanding this system is essential for effective CFSE practice.

## Artifact Categories

### Primary Artifacts

The six core deliverables of CFSE analysis:

| Artifact | Prefix | Purpose | Phase |
|----------|--------|---------|-------|
| Concept | `C-` | Define system building blocks | Foundation |
| Interaction | `I-` | Document single-step operations | Relationships |
| Flow | `F-` | Document multi-step sequences | Sequences |
| Scenario | `S-` | Hypothesize vulnerabilities | Hypothesis |
| Exploration | `E-` | Test hypotheses concretely | Validation |
| Finding | `FD-` | Document confirmed issues | Documentation |

### Supporting Artifacts

Enable and enhance primary artifacts:

| Artifact | Prefix | Purpose |
|----------|--------|---------|
| Predicate | `P-` | Atomic boolean conditions |
| Invariant | `INV-` | Composed security rules |
| Generator | `GEN-` | Reusable scenario patterns |
| Patch | `PATCH-` | Fix documentation |

### Invariant Library YAML (Packaging Format)

CFSE also defines a canonical **Invariant Library YAML** packaging format for large corpora that prefer “few files” over thousands of `INV-*` / `P-*` files. This format stores many Predicate and Invariant objects in a single YAML document, while keeping IDs and schemas first-class.

See `artifacts/supporting/invariant_library/invariant_library.md`.

## Artifact Pipeline

Artifacts flow through a defined pipeline:

```
Foundation     Relationships     Sequences      Hypothesis     Validation     Documentation
    |               |                |               |               |               |
    v               v                v               v               v               v
 Concepts --> Interactions --> Flows --> Scenarios --> Explorations --> Findings
    |               |                |               |               |               |
    +---------------+----------------+-------+-------+---------------+---------------+
                                             |
                              +--------------+--------------+
                              |    Supporting Artifacts     |
                              |  Predicates, Invariants,    |
                              |  Generators, Patches        |
                              +-----------------------------+
```

## Artifact Dependencies

Each artifact type has defined dependencies:

| Artifact | References | Referenced By |
|----------|------------|---------------|
| Concept | Invariants | Interactions, Flows |
| Interaction | Concepts, Invariants | Flows, Explorations |
| Flow | Interactions, Invariants | Scenarios |
| Scenario | Flows, Invariants, Generators | Explorations |
| Exploration | Scenarios, Interactions, Invariants | Findings |
| Finding | Explorations, Invariants | Patches |
| Predicate | (none) | Invariants |
| Invariant | Predicates | All primary artifacts |
| Generator | (none) | Scenarios |
| Patch | Findings, Invariants | (none) |

## Artifact Lifecycle

Each artifact instance progresses through states:

```
Draft --> Active --> Deprecated
  |          |           |
  |          |           +-- No longer applicable
  |          +-- In use, authoritative
  +-- Work in progress, not authoritative
```

## Traceability Requirements

CFSE requires explicit traceability between artifacts:

| Rule | Requirement |
|------|-------------|
| TR-1 | Every Finding MUST reference at least one Exploration |
| TR-2 | Every Exploration MUST reference exactly one Scenario |
| TR-3 | Every Scenario MUST reference at least one Invariant |
| TR-4 | Every Invariant MUST reference at least one Predicate |
| TR-5 | Every Patch MUST reference exactly one Finding |
