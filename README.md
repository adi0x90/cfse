# CFSE - Concept Flow Scenarios Explorations

**Version 1.0.0** | January 2026

> **CFSE is a formal methodology for security epistemology: a disciplined approach to replacing intuition with structure, and claims with evidence.**

CFSE is a formal methodology for security epistemology—a disciplined approach to *knowing* whether a system is secure, not guessing or hoping. It builds a world model of systems through concepts, interactions, and flows, expresses security properties as formal invariants with temporal logic, and validates claims through systematic exploration backed by structured evidence.

**Not a scanner. Not a checklist. A formal framework for security knowledge.**

---

## Quick Start

| Goal | Resource |
|------|----------|
| Start here (purpose + model) | `guides/foundations/introduction.md` |
| Understand the artifact pipeline | `spec/foundations/artifact-system.md` |
| Conformance levels | `spec/foundations/conformance.md` |
| ID syntax | `spec/grammar/01-id-syntax.md` |
| Normative spec | `spec/` |
| Architecture map | `ARCHITECTURE.yml` |

---

## Directory Structure

```
cfse-spec/
  spec/                 # Normative core specification (source of truth)
    foundations/        # Core concepts: artifact system, conformance, extensions
    grammar/            # ID syntax, references, formal logic, field types
    artifacts/          # Artifact definitions with YAML schemas
      primary/          # Concept, Interaction, Flow, Scenario, Exploration, Finding
      supporting/       # Predicate, Invariant, Generator, Patch
    semantics/          # Invariant states, verdicts, lifecycle, traceability
  extensions/           # Optional extensions (opt-in; may be empty)
  guides/               # Informative background and reading guides
  rfcs/                 # Informative RFC/proposal process (no archive required)
  ARCHITECTURE.yml      # Machine-readable structure manifest
```

---

## The CFSE Pipeline

```
Concept -> Interaction -> Flow -> Scenario -> Exploration -> Finding -> Patch
   C           I           F         S            E            FD       PATCH
```

1. **Concept** (C-): Define system building blocks
2. **Interaction** (I-): Document atomic operations
3. **Flow** (F-): Map legitimate user journeys
4. **Scenario** (S-): Hypothesize security violations
5. **Exploration** (E-): Test hypotheses with BASE vs ATT
6. **Finding** (FD-): Document confirmed vulnerabilities
7. **Patch** (PATCH-): Fix, verify, and learn

---

## Key Specifications

| Topic | Location |
|-------|----------|
| Framework Introduction | `guides/foundations/introduction.md` |
| World Model | `guides/foundations/world-model.md` |
| Artifact System | `spec/foundations/artifact-system.md` |
| ID Syntax | `spec/grammar/01-id-syntax.md` |
| Formal Logic | `spec/grammar/03-formal-logic.md` |

---

## Automation (Optional)

CFSE is designed to be both human-readable and tool-friendly.

- `ARCHITECTURE.yml` provides a machine-readable map of the spec (useful for editors, validators, and automation).
- Some supporting material (templates, examples, prompts) may be published separately.

---

## Classification

- **Normative** (`spec/`): Authoritative definitions - source of truth
- **Informative** (`guides/`, `rfcs/`): Explanations, templates, and design discussion scaffolding

---

## Positioning

CFSE is compatible with many existing practices (threat modeling, red teaming, property-based testing, and formal methods). It is not a replacement for any of them; it is the “evidence-linked structure layer” that makes security reasoning auditable and repeatable.

### Depth, Not Surface

| Surface approach | CFSE equivalent |
|------------------|-----------------|
| Scan for vulnerabilities | Build world model, derive hypotheses from structure |
| Follow a checklist | Express properties as formal invariants |
| Run some tests | Systematic explorations with baseline/attack deltas |
| Write up findings | Evidence-backed findings with trace provenance |

See `guides/foundations/introduction.md` for the full positioning.

---

## Getting Help

1. Start with `guides/foundations/introduction.md`
2. Read `spec/README.md` for the spec map
3. Consult `spec/glossary.md` for terminology
4. Reference `ARCHITECTURE.yml` for the complete structure map

---

## Contributing

See `CONTRIBUTING.md`.
