# World Model

## Overview

A world model is a conceptual map of a system - a simplified representation that captures the essential building blocks, their relationships, and the rules that govern them.

## The Map Analogy

Just as a map is not the territory it represents, a world model is not the system itself. Maps serve specific purposes:

| Map Type | Purpose | Omits |
|----------|---------|-------|
| Road map | Navigation | Terrain elevation |
| Topographic map | Terrain analysis | Road conditions |
| Transit map | Route planning | Geographic accuracy |

Similarly, a CFSE world model focuses on **security-relevant structure**, omitting implementation details that don't affect security properties.

## Logic Layer vs Implementation Layer

CFSE operates at two abstraction levels:

### Logic Layer

The logic layer contains **abstract security rules** independent of implementation:

- Concepts (what entities exist)
- Invariants (what rules must hold)
- Flows (what sequences are legitimate)

Example: "Only the owner of a resource can delete it"

### Implementation Layer

The implementation layer contains **concrete realizations**:

- Code (functions, classes, modules)
- Configuration (ACLs, policies, settings)
- Infrastructure (services, databases, networks)

Example: `if resource.owner_id != current_user.id: raise PermissionDenied`

### Why Separate?

| Benefit | Explanation |
|---------|-------------|
| Stability | Logic layer changes less often than implementation |
| Portability | Same invariants apply across different implementations |
| Clarity | Security rules are explicit, not buried in code |
| Testability | Can verify logic layer compliance independently |

## Building a World Model

A world model is built through progressive refinement:

```
1. Identify Concepts    -> What are the "nouns"?
2. Map Interactions     -> How do concepts connect?
3. Document Flows       -> What are legitimate sequences?
4. Define Invariants    -> What rules must always hold?
```

## World Model Quality

A good world model is:

| Property | Meaning |
|----------|---------|
| Complete | Covers all security-relevant concepts |
| Minimal | No redundant or unnecessary concepts |
| Consistent | No contradictory invariants |
| Testable | Invariants can be verified through exploration |

## Relationship to Artifacts

| Artifact | World Model Role |
|----------|-----------------|
| Concept | Building block of the model |
| Interaction | Connection between building blocks |
| Flow | Path through the model |
| Invariant | Rule constraining the model |
| Scenario | Hypothesis about model weakness |
| Exploration | Test of model behavior |
