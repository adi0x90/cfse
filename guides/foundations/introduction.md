# Introduction

## What is CFSE?

Concept Flow Scenarios Explorations (CFSE) is a structured methodology for building an explicit world model of a system and then validating security hypotheses against it through evidence-backed experiments.

CFSE decomposes a target into Concepts, Interactions, and Flows, then expresses hypotheses as Scenarios and validates them with Explorations (baseline vs attack) so that conclusions are tied to traceable evidence.

CFSE is designed to work well for human teams and for tool-assisted workflows (including LLM-assisted analysis), without turning “tool output” into authority.

## Problem Statement

Security analysis of complex systems faces several challenges:

1. **Complexity** - Modern systems have many components with intricate relationships
2. **Implicit assumptions** - Security rules often exist only in developers' heads
3. **Ad-hoc testing** - Vulnerability discovery lacks systematic coverage
4. **Knowledge loss** - Findings don't feed back into reusable patterns
5. **Tool collaboration** - No common structure for human + tooling workflows (including AI-assisted workflows)

## Design Goals

CFSE addresses these challenges through:

| Goal | How CFSE Achieves It |
|------|---------------------|
| Manage complexity | Decompose systems into concepts with clear boundaries |
| Explicit rules | Codify security assumptions as formal invariants |
| Systematic testing | Generate scenarios from patterns, not intuition alone |
| Knowledge capture | Extract generators from findings for reuse |
| Tool-friendly | Structured artifacts with machine-parseable schemas |

## Non-Goals

CFSE does NOT aim to:

- Replace implementation-level security tools (SAST, DAST)
- Provide automated exploitation
- Guarantee complete vulnerability coverage
- Work without human judgment and expertise

## Audience

This specification is designed for:

| Audience | Use Case |
|----------|----------|
| Security engineers | Conduct structured analysis, document findings |
| Developers | Understand expected security properties and common failure modes |
| Architects / technical leads | Build shared system understanding; make security properties and assumptions explicit across teams |
| Platform / infrastructure engineers | Map real surfaces and trust boundaries across services and environments; validate invariants against deployments |
| Security leadership (CISO) / compliance / risk | Translate requirements into explicit properties (invariants) and evidence-linked validation; improve auditability and decision-making |
| Tool builders | Create validators, linters, editors, and automation |
| Educators and researchers | Teach, discuss, and evaluate evidence-linked security methods |

## Specification Structure

| Section | Content |
|---------|---------|
| Foundations | Core framework rules (artifact system, conformance, extensions) |
| Grammar | Syntax rules, ID patterns, formal logic |
| Artifacts | Schema and prose for each artifact type |
| Semantics | Interpretation rules, states, verdicts |
| Extensions | Optional opt-in add-ons (core remains stable) |

---

## Optional: Exposure Modeling (EP + PRJ)

Entry Points (`EP-*`) are a core CFSE artifact for inventorying tangible system surfaces. Some corpora additionally use optional exposure modeling to make “who can see what, where” more explicit:

- `tangible_locations[]` and `exposes[]` on `EP-*` (viewer-agnostic inventory)
- Projections (`PRJ-*`) to describe viewer-context-specific slices across one or more entry points

These are optional in CFSE core (unless a conformance profile or extension requires them).

See the canonical artifact specs:
- `spec/artifacts/supporting/entry_point/entry_point.md`
- `spec/artifacts/supporting/prj/prj.md`

## Potential Inspirations

CFSE has not been built in a void. It stands on the shoulder of giants - inspired by the work done by some amazing people - in the fields of **Formal Logic, Scientific Exploration, Proof Checking, and Software Architecture, Engineering and Design**.

- **Daniel Jackson — Alloy**: small-model thinking; making structure explicit and checkable.
- **Leslie Lamport — TLA+**: invariants, state transitions, and “spec first” reasoning about behavior.
- **Frederick P. Brooks — _The Mythical Man-Month_, _No Silver Bullet_**: respect for complexity; focus on communication and conceptual integrity rather than tooling optimism.
- **Edsger W. Dijkstra / C. A. R. Hoare**: correctness as a discipline; clarity of reasoning and contracts.
- **David Parnas**: modular decomposition and stable interfaces (helpful for world-model boundaries).
- **Model checking / formal methods (broadly)**: properties stated precisely; counterexamples treated as first-class learning artifacts.
- **Model-based & property-based testing (broadly)**: systematic hypothesis generation and oracle-driven validation.
- **The scientific method**: claims tied to experiments, deltas, and traceable evidence.

## Related Traditions (Neighborhood)

CFSE lives in the intersection of **security engineering**, **formal modeling**, and **experimental validation**. Related traditions include:

### Formal specification & model checking

Formal methods focus on stating a system model plus invariants, then proving properties or finding counterexamples.

CFSE complements this by providing:
- a practical artifact pipeline for building the system model incrementally (Concept → Interaction → Flow),
- explicit security invariants as first-class artifacts, and
- an experimentation discipline (Exploration) for validating properties against real implementations.

CFSE can be used alongside formal methods: use design-time reasoning where it helps, and use CFSE to keep implementation-time hypotheses, experiments, and evidence traceable.

### Protocol and adversary-model verification

Security protocol verification typically introduces an explicit attacker model and attempts to prove secrecy/authentication properties.

CFSE is compatible with this style of work, but is broader in scope (beyond protocols) and emphasizes:
- a shared “world model” vocabulary across stakeholders,
- traceability from hypothesis to evidence to remediation.

### Model-based testing & property-based testing

These approaches generate many test sequences from a behavioral model and check a property (oracle).

CFSE’s Scenario Generators and Explorations are the security-oriented variant of this idea:
- Scenario generators propose hypothesis families systematically,
- Explorations record baseline vs attack runs and their deltas,
- Findings and Patches feed new generator patterns back into the library.

### Safety-style constraint analysis (security constraints)

In safety engineering, analysis often centers on system constraints and how violations can occur.

CFSE adopts the “constraint-first” mindset (invariants) and binds it to:
- concrete entry points,
- structured experiments,
- and evidence/traceability rules.

### Taxonomies, checklists, and attack catalogs

Taxonomies and catalogs (threat categories, attack patterns, weakness types) are useful for coverage and classification.

CFSE uses them as inputs and labeling systems, but is not itself a taxonomy; CFSE is an **artifact protocol + workflow** for:
- modeling system behavior,
- stating security contracts (invariants),
- generating hypotheses (scenarios),
- validating with experiments (explorations),
- and extracting reusable patterns (generators).

---

## Positioning Summary

CFSE is not a scanner, checklist, or testing framework. It is a **formal methodology for security epistemology**—a disciplined approach to *knowing* whether a system is secure, not guessing or hoping.

### Depth, Not Surface

| Surface-level approach | CFSE equivalent |
|------------------------|-----------------|
| "Scan for vulnerabilities" | Build a world model, derive attack hypotheses from structure |
| "Follow a checklist" | Express security properties as formal invariants |
| "Run some tests" | Execute systematic explorations with baseline/attack deltas |
| "Write up findings" | Produce evidence-backed findings with trace provenance |
| "Trust the expert" | Trace every claim to structured evidence |

### The Epistemological Stack

CFSE answers the question: **"How do we *know* this system is secure?"**

```
┌─────────────────────────────────────────────────────────────┐
│  CLAIM: "The system satisfies INV-AUTH-REQUIRED"            │
├─────────────────────────────────────────────────────────────┤
│  EVIDENCE: Trace artifacts T-* with steps, correlation,     │
│            sources, and integrity hashes                    │
├─────────────────────────────────────────────────────────────┤
│  METHOD: Exploration E-* with baseline vs attack paths,     │
│          evaluated against formal invariant                 │
├─────────────────────────────────────────────────────────────┤
│  FOUNDATION: World model (Concepts, Interactions, Flows)    │
│              defining what the system *is*                  │
└─────────────────────────────────────────────────────────────┘
```

This is the difference between "we tested it" and "here is the formal structure of our knowledge."

### Integration with Existing Practices

If you already use threat modeling, checklists, or red teaming, CFSE fits as the "deep structure" layer:

- **Threat modeling** helps enumerate concerns; CFSE turns concerns into **structured hypotheses** grounded in a world model.
- **Security testing** finds issues; CFSE turns results into **traceable findings** and **reusable generators**.
- **Formal methods** can prove properties; CFSE provides an on-ramp to formalization via explicit artifacts and invariants, and a bridge back to real-world validation via explorations.
- **Tool-assisted analysis** (including AI) benefits from structure; CFSE provides an ontology and artifact schemas that make reasoning and automation more systematic.
