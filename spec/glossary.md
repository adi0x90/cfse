# Glossary

Terms in CFSE have precise meanings. When a term appears in the spec, it carries the definition below.

## Core Terms

| Term | Definition |
|------|------------|
| Artifact | A documented unit of CFSE output |
| World Model | The conceptual map of a system's building blocks and rules |
| Logic Layer | Abstract security rules independent of implementation |
| Implementation Layer | Concrete code/config that realizes the logic layer |

## Artifacts

| Term | Definition |
|------|------------|
| Concept | A fundamental building block representing a system entity |
| Interaction | A single-step operation between concepts |
| Flow | A multi-step legitimate sequence achieving a goal |
| Scenario | A testable vulnerability hypothesis |
| Exploration | A concrete test comparing BASE and ATT behavior |
| Finding | A confirmed vulnerability with evidence |
| Predicate | An atomic boolean condition |
| Invariant | A rule that MUST always hold true |
| Entry Point | A first-class surface artifact (`EP-*`) describing how a surface is accessed, what it can expose, and where it is tangible |
| PRJ | Projection artifact (`PRJ-*`) describing what a viewer-context sees across one or more surfaces |
| Generator | A reusable pattern for creating scenarios |
| Patch | A documented fix with verification |

## States and Verdicts

| Term | Definition |
|------|------------|
| HOLDS | Invariant state: the invariant is satisfied |
| VIOLATED | Invariant state: the invariant is not satisfied |
| UNKNOWN | Invariant state: could not determine |
| NOT_APPLICABLE | Invariant state: the invariant does not apply in context |
| VIOLATION_CONFIRMED | Exploration verdict: attack hypothesis succeeded (invariant violated) |
| ENFORCEMENT_CONFIRMED | Exploration verdict: attack blocked as expected (invariant enforced) |
| INCONCLUSIVE | Exploration verdict: results ambiguous |
| BLOCKED | Exploration verdict: could not execute due to environment/tooling constraints |

## Methodologies

| Term | Definition |
|------|------------|
| CIA | Concept Interaction Analysis - systematic interaction discovery |
| Delta Analysis | Comparison method isolating single-variable differences |
| 4V | Verify, Validate, Vaccinate, Valuate - patch methodology |
| BASE | Legitimate user behavior in exploration |
| ATT | Attack behavior in exploration |

## Modeling Helpers

| Term | Definition |
|------|------------|
| tangible_locations | Field listing concrete access locators for a surface (URLs, CLI invocations, etc.), intended for scoping and testing |

## Document Types

| Term | Definition |
|------|------------|
| Normative | Spec content defining requirements (uses SHALL/MUST) |
| Informative | Spec content providing guidance (non-binding) |
| Derivative | Content generated from normative definitions |
