# Extensions

## Overview

CFSE is intentionally **security-focused**. It defines a security analysis artifact pipeline (Concepts → Flows → Scenarios → Explorations → Findings → Patches), along with schemas, semantics, traceability rules, and conformance levels.

At the same time, teams often want to reuse CFSE’s artifact graph, traceability discipline, and validation tooling for adjacent workflows (e.g., product development planning, incident response).

To preserve CFSE’s identity and avoid turning the core spec into a “god spec”, CFSE supports **optional extensions**.

---

## Core vs Extension

### CFSE Core

CFSE Core owns:
- Core artifact types and their schemas
- Core semantics (states/verdicts/lifecycle)
- Core traceability rules (TR-1 through TR-5)
- Core conformance levels (minimal/standard/full)

### CFSE Extensions

An extension MAY add:
- New artifact types (with new ID prefixes + schemas)
- Extension-specific fields on existing artifacts (namespaced)
- Additional traceability rules
- Additional conformance profiles
- Additional validation rules

An extension MUST NOT:
- Change the meaning of CFSE core artifact types
- Weaken CFSE core validation requirements
- Override CFSE core traceability rules

---

## Extension Declaration (Corpus Opt-In)

A CFSE corpus SHOULD declare which extensions it uses:

```yaml
cfse:
  version: "1.0.0"
  conformance: "standard" # minimal | standard | full | partial
  extensions:
    example_ext:
      version: "0.1.0"
      conformance: "standard" # extension-defined profiles
```

If an extension is declared, all extension rules for that extension apply to the corpus.

If an extension is NOT declared, extension artifact types and extension validation rules MUST NOT be required for core conformance.

---

## Namespacing Rules (Extension Fields)

Any extension-specific fields added to existing CFSE artifacts MUST be placed under the top-level `extensions` field, nested under a key matching the extension name.

Example:

```yaml
extensions:
  example_ext:
    some_field: "value"
```

---

## Validation Model

Validators SHOULD validate a corpus in two phases:

1. **Core validation** (always):
   - Core schemas validate
   - Core reference validation applies
   - Core traceability rules validate (TR-1..TR-5 at full conformance)
2. **Extension validation** (only for declared extensions):
   - Extension schemas validate
   - Extension traceability rules validate
   - Extension conformance profile validates

If an extension is declared but unknown to the validator, the validator MUST error.
