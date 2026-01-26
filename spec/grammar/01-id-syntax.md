# ID Syntax Specification

## Overview

Every CFSE artifact is assigned a unique identifier following strict syntactic rules. These identifiers enable:

- **Unambiguous reference** across documentation and tooling
- **Automated validation** via regex patterns
- **Hierarchical organization** through component structure
- **Traceability** from concepts through explorations to findings

CFSE core defines the identifier patterns in this document. CFSE extensions MAY introduce additional artifact types and identifier patterns; extension ID rules are defined by the extension and apply only when that extension is declared (see `foundations/extensions.md`).

## General Rules

### Character Set

| Category | Allowed Characters |
|----------|-------------------|
| System codes | `A-Z`, `0-9` |
| Names/Themes | `A-Z`, `0-9`, `-` (hyphen as separator) |
| Sequence numbers | `0-9` |

### Naming Conventions

1. **UPPERCASE only** - All alphabetic characters must be uppercase
2. **No leading/trailing hyphens** - Hyphens only between words
3. **No consecutive hyphens** - Use single hyphen as separator
4. **Meaningful abbreviations** - Use domain-standard abbreviations

---

## Artifact ID Patterns

### Entry Point ID (`EntryPointID`)

Entry Points represent concrete system operations (API endpoints, UI actions, CLI commands, events) and are first-class artifacts (`EP-*`).

#### Pattern Description

```
EP-<SYSTEM>-<CONCEPT>-<CHANNEL>-<ACTION>[-<NN>]
```

#### Notes

- The regex allows flexibility; the convention above is RECOMMENDED for traceability.
- The convention is compatible with multiple channels (API/WEB/GRAPHQL/CLI/EVENT) and multiple variants via the optional `-<NN>` suffix.

#### Regex

```regex
^EP-[A-Z0-9-]{1,128}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `EP-SHOP-USER-API-CREATE` | Yes | Standard concept entry point |
| `EP-SHOP-ITEM-API-DELETE` | Yes | Standard concept entry point |
| `EP-I-SHOP-ITEM-DELETE-API` | Yes | Interaction-scoped entry point ID |
| `EP-shop-user-api-create` | No | Lowercase not allowed |
| `EP--USER-API-CREATE` | No | Malformed hyphens |

### Projection ID (`ProjectionID`)

Projections describe what a viewer-context sees across one or more surfaces.

#### Pattern Description

```
PRJ-<SYSTEM>-<NAME>
```

#### Regex

```regex
^PRJ-[A-Z0-9-]{1,128}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `PRJ-SHOP-PUBLIC-VIEWER` | Yes | Standard PRJ ID |
| `PRJ-GL-ANON-RSS` | Yes | Standard PRJ ID |
| `PRJ_gl_anon` | No | Underscores not allowed |

### 1. Concept ID (`ConceptID`)

Concepts represent the foundational security-relevant entities in a system.

#### Pattern Description

```
C-<SYSTEM>-<NAME>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `C-` | 2 | Fixed concept identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| NAME | `[A-Z0-9-]+` | 1-32 | Descriptive name with optional hyphens |

#### Regex

```regex
^C-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `C-AWS-IAM-ROLE` | Yes | Standard concept identifier |
| `C-K8S-POD` | Yes | Short system code, short name |
| `C-OAUTH2-ACCESS-TOKEN` | Yes | Hyphenated name |
| `C-GCP-SERVICE-ACCOUNT-KEY` | Yes | Multiple hyphens in name |
| `c-aws-iam-role` | No | Lowercase not allowed |
| `C-A-ROLE` | No | System code too short (min 2) |
| `C-AWS-` | No | Trailing hyphen |
| `C--IAM-ROLE` | No | Missing system code |
| `CONCEPT-AWS-ROLE` | No | Wrong prefix |

---

### 2. Interaction ID (`InteractionID`)

Interactions capture security-relevant operations between concepts.

#### Pattern Description

```
I-<SYSTEM>-<VERB>-<NOUN>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `I-` | 2 | Fixed interaction identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| VERB | `[A-Z]+` | 1-16 | Action verb (e.g., CREATE, INVOKE, ATTACH) |
| NOUN | `[A-Z]+` | 1-16 | Target entity (e.g., ROLE, TOKEN, KEY) |
| SEQ | `[0-9]+` | 3 | Three-digit sequence number |

#### Regex

```regex
^I-[A-Z0-9]{2,8}-[A-Z]{1,16}-[A-Z]{1,16}-[0-9]{3}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `I-AWS-ASSUME-ROLE-001` | Yes | Standard interaction |
| `I-K8S-CREATE-POD-042` | Yes | Kubernetes pod creation |
| `I-OAUTH2-REFRESH-TOKEN-003` | Yes | OAuth token refresh |
| `I-GCP-INVOKE-FUNCTION-100` | Yes | GCP function invocation |
| `I-AWS-ASSUME-ROLE-1` | No | Sequence must be 3 digits |
| `I-AWS-assume-ROLE-001` | No | Lowercase not allowed |
| `I-AWS-ASSUME-ROLE` | No | Missing sequence number |
| `I-AWS-ASSUME_ROLE-001` | No | Underscore not allowed |
| `I-A-ASSUME-ROLE-001` | No | System code too short |

---

### 3. Flow ID (`FlowID`)

Flows represent ordered sequences of interactions forming complete operations.

#### Pattern Description

```
F-<SYSTEM>-<NAME>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `F-` | 2 | Fixed flow identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| NAME | `[A-Z0-9-]+` | 1-32 | Descriptive flow name |

#### Regex

```regex
^F-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `F-AWS-CROSS-ACCOUNT-ACCESS` | Yes | Multi-word flow name |
| `F-K8S-POD-SCHEDULING` | Yes | Kubernetes scheduling flow |
| `F-OAUTH2-AUTHORIZATION-CODE` | Yes | OAuth flow |
| `F-GCP-WORKLOAD-IDENTITY` | Yes | GCP identity flow |
| `f-aws-role-chain` | No | Lowercase not allowed |
| `F-A-ACCESS` | No | System code too short |
| `F-AWS--ACCESS` | No | Consecutive hyphens |
| `FLOW-AWS-ACCESS` | No | Wrong prefix |

---

### 4. Scenario ID (`ScenarioID`)

Scenarios define themed security test cases grouped by attack patterns or vulnerability classes.

#### Pattern Description

```
S-<SYSTEM>-<THEME>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `S-` | 2 | Fixed scenario identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| THEME | `[A-Z0-9-]+` | 1-24 | Attack theme or vulnerability class |
| SEQ | `[0-9]+` | 3 | Three-digit sequence number |

#### Regex

```regex
^S-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `S-AWS-PRIVILEGE-ESCALATION-001` | Yes | Privilege escalation scenario |
| `S-K8S-CONTAINER-ESCAPE-003` | Yes | Container security scenario |
| `S-OAUTH2-TOKEN-THEFT-010` | Yes | Token security scenario |
| `S-GCP-LATERAL-MOVEMENT-005` | Yes | Lateral movement scenario |
| `S-AWS-PRIVESC-1` | No | Sequence must be 3 digits |
| `S-AWS-PRIVILEGE-ESCALATION` | No | Missing sequence number |
| `s-aws-privesc-001` | No | Lowercase not allowed |
| `S-A-PRIVESC-001` | No | System code too short |

---

### 5. Exploration ID (`ExplorationID`)

Explorations document detailed security testing sessions derived from scenarios.

#### Pattern Description

```
E-<SYSTEM>-<THEME>-<SCENARIO-SEQ>-<VERSION>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `E-` | 2 | Fixed exploration identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| THEME | `[A-Z0-9-]+` | 1-24 | Theme from parent scenario |
| SCENARIO-SEQ | `[0-9]+` | 3 | Parent scenario sequence |
| VERSION | `[0-9]+` | 2 | Two-digit exploration version |

#### Regex

```regex
^E-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `E-AWS-PRIVILEGE-ESCALATION-001-01` | Yes | First exploration of scenario 001 |
| `E-K8S-CONTAINER-ESCAPE-003-05` | Yes | Fifth version |
| `E-OAUTH2-TOKEN-THEFT-010-12` | Yes | Twelfth exploration |
| `E-GCP-LATERAL-MOVEMENT-005-01` | Yes | Standard format |
| `E-AWS-PRIVESC-001-1` | No | Version must be 2 digits |
| `E-AWS-PRIVESC-01-01` | No | Scenario sequence must be 3 digits |
| `E-AWS-PRIVESC-001` | No | Missing version |
| `e-aws-privesc-001-01` | No | Lowercase not allowed |

#### Relationship to Scenario

The exploration ID embeds its parent scenario reference:

```
E-AWS-PRIVILEGE-ESCALATION-001-01
  |_______________________________|
         Derived from S-AWS-PRIVILEGE-ESCALATION-001
```

---

### 6. Trace ID (`TraceID`)

Traces capture ordered evidence (events and state facts) that support temporal and event-sequence claims. Traces are typically produced as part of an Exploration run (baseline and/or attack paths).

#### Pattern Description

```
T-<SYSTEM>-<THEME>-<SCENARIO-SEQ>-<VERSION>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `T-` | 2 | Fixed trace identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| THEME | `[A-Z0-9-]+` | 1-24 | Theme from parent scenario/exploration |
| SCENARIO-SEQ | `[0-9]+` | 3 | Parent scenario sequence |
| VERSION | `[0-9]+` | 2 | Parent exploration version |
| SEQ | `[0-9]+` | 2 | Trace sequence for that exploration version (e.g., baseline vs attack) |

#### Regex

```regex
^T-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}-[0-9]{2}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `T-AWS-PRIVILEGE-ESCALATION-001-01-01` | Yes | First trace for exploration 001-01 |
| `T-AWS-PRIVILEGE-ESCALATION-001-01-02` | Yes | Second trace (e.g., attack path) |
| `T-K8S-CONTAINER-ESCAPE-003-05-01` | Yes | Trace for exploration 003-05 |
| `T-AWS-PRIVESC-001-1-01` | No | Version must be 2 digits |
| `T-AWS-PRIVESC-01-01-01` | No | Scenario sequence must be 3 digits |
| `T-AWS-PRIVESC-001-01-1` | No | Trace sequence must be 2 digits |

#### Relationship to Exploration

Trace IDs embed their parent exploration reference:

```
T-AWS-PRIVILEGE-ESCALATION-001-01-01
  |_________________________________|
         Derived from E-AWS-PRIVILEGE-ESCALATION-001-01
```

---

### 7. Finding ID (`FindingID`)

Findings document security issues discovered during explorations.

#### Pattern Description

```
FD-<SYSTEM>-<CATEGORY>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `FD-` | 3 | Fixed finding identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| CATEGORY | `[A-Z]+` | 1-16 | Finding category (e.g., AUTHZ, CRYPTO) |
| SEQ | `[0-9]+` | 3 | Three-digit sequence number |

#### Category Values

| Category | Description |
|----------|-------------|
| `AUTHZ` | Authorization/access control issues |
| `AUTHN` | Authentication issues |
| `CRYPTO` | Cryptographic weaknesses |
| `CONFIG` | Configuration vulnerabilities |
| `INJECT` | Injection vulnerabilities |
| `LEAK` | Information disclosure |
| `LOGIC` | Business logic flaws |
| `RACE` | Race conditions |

#### Regex

```regex
^FD-[A-Z0-9]{2,8}-[A-Z]{1,16}-[0-9]{3}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `FD-AWS-AUTHZ-001` | Yes | Authorization finding |
| `FD-K8S-CONFIG-023` | Yes | Configuration issue |
| `FD-OAUTH2-CRYPTO-005` | Yes | Cryptographic weakness |
| `FD-GCP-LEAK-012` | Yes | Information disclosure |
| `FD-AWS-AUTHZ-1` | No | Sequence must be 3 digits |
| `FD-AWS-auth-001` | No | Lowercase not allowed |
| `FD-A-AUTHZ-001` | No | System code too short |
| `FINDING-AWS-AUTHZ-001` | No | Wrong prefix |

---

### 8. Predicate ID (`PredicateID`)

Predicates are reusable boolean conditions for invariant composition.

#### Pattern Description

```
P-<SYSTEM>-<NAME>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `P-` | 2 | Fixed predicate identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| NAME | `[A-Z0-9-]+` | 1-32 | Descriptive predicate name |

#### Regex

```regex
^P-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `P-AWS-HAS-MFA` | Yes | MFA verification predicate |
| `P-K8S-IS-PRIVILEGED` | Yes | Privilege check |
| `P-OAUTH2-TOKEN-VALID` | Yes | Token validation |
| `P-GCP-IN-VPC` | Yes | Network location check |
| `p-aws-has-mfa` | No | Lowercase not allowed |
| `P-A-MFA` | No | System code too short |
| `PRED-AWS-MFA` | No | Wrong prefix |
| `P-AWS-` | No | Trailing hyphen |

---

### 9. Invariant ID (`InvariantID`)

Invariants express security properties that must always hold.

#### Pattern Description

```
INV-<SYSTEM>-<NAME>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `INV-` | 4 | Fixed invariant identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| NAME | `[A-Z0-9-]+` | 1-32 | Descriptive invariant name |

#### Regex

```regex
^INV-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `INV-AWS-NO-PUBLIC-S3` | Yes | S3 bucket visibility |
| `INV-K8S-POD-SECURITY` | Yes | Pod security policy |
| `INV-OAUTH2-TOKEN-EXPIRY` | Yes | Token lifecycle |
| `INV-GCP-IAM-LEAST-PRIVILEGE` | Yes | IAM principle |
| `inv-aws-no-public-s3` | No | Lowercase not allowed |
| `INV-A-S3` | No | System code too short |
| `INVARIANT-AWS-S3` | No | Wrong prefix |
| `INV-AWS--S3` | No | Consecutive hyphens |

---

### 10. Generator ID (`GeneratorID`)

Generators create scenario variations through systematic exploration strategies.

#### Pattern Description

```
GEN-<STRATEGY>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `GEN-` | 4 | Fixed generator identifier prefix |
| STRATEGY | `[A-Z0-9-]+` | 1-24 | Generation strategy name |
| SEQ | `[0-9]+` | 3 | Three-digit sequence number |

#### Strategy Values

| Strategy | Description |
|----------|-------------|
| `BOUNDARY` | Boundary value analysis |
| `MUTATION` | Input mutation testing |
| `COMBINATORIAL` | Pairwise/combinatorial testing |
| `FUZZ` | Fuzzing-based generation |
| `TEMPORAL` | Time-based variations |
| `PRIVILEGE` | Privilege level variations |

#### Regex

```regex
^GEN-[A-Z0-9-]{1,24}-[0-9]{3}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `GEN-BOUNDARY-001` | Yes | Boundary testing generator |
| `GEN-MUTATION-FUZZ-042` | Yes | Mutation fuzzing |
| `GEN-PRIVILEGE-ESCALATION-003` | Yes | Privilege testing |
| `GEN-TEMPORAL-RACE-010` | Yes | Race condition testing |
| `GEN-BOUNDARY-1` | No | Sequence must be 3 digits |
| `gen-boundary-001` | No | Lowercase not allowed |
| `GEN-BOUNDARY` | No | Missing sequence number |
| `GENERATOR-BOUNDARY-001` | No | Wrong prefix |

---

### 11. Patch ID (`PatchID`)

Patches document remediation changes applied to address findings.

#### Pattern Description

```
PATCH-<SYSTEM>-<SEQ>
```

#### Component Rules

| Component | Rule | Length | Description |
|-----------|------|--------|-------------|
| Prefix | `PATCH-` | 6 | Fixed patch identifier prefix |
| SYSTEM | `[A-Z0-9]+` | 2-8 | System or domain abbreviation |
| SEQ | `[0-9]+` | 3 | Three-digit sequence number |

#### Regex

```regex
^PATCH-[A-Z0-9]{2,8}-[0-9]{3}$
```

#### Examples

| ID | Valid | Reason |
|----|-------|--------|
| `PATCH-AWS-001` | Yes | AWS system patch |
| `PATCH-K8S-042` | Yes | Kubernetes patch |
| `PATCH-OAUTH2-003` | Yes | OAuth implementation patch |
| `PATCH-GCP-100` | Yes | GCP configuration patch |
| `PATCH-AWS-1` | No | Sequence must be 3 digits |
| `patch-aws-001` | No | Lowercase not allowed |
| `PATCH-A-001` | No | System code too short |
| `FIX-AWS-001` | No | Wrong prefix |

---

## Quick Reference Table

| Artifact | Pattern | Regex |
|----------|---------|-------|
| Concept | `C-<SYS>-<NAME>` | `^C-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Interaction | `I-<SYS>-<VERB>-<NOUN>-<SEQ>` | `^I-[A-Z0-9]{2,8}-[A-Z]{1,16}-[A-Z]{1,16}-[0-9]{3}$` |
| Flow | `F-<SYS>-<NAME>` | `^F-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Scenario | `S-<SYS>-<THEME>-<SEQ>` | `^S-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}$` |
| Exploration | `E-<SYS>-<THEME>-<SEQ>-<VER>` | `^E-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}$` |
| Trace | `T-<SYS>-<THEME>-<SEQ>-<VER>-<NN>` | `^T-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}-[0-9]{2}$` |
| Finding | `FD-<SYS>-<CAT>-<SEQ>` | `^FD-[A-Z0-9]{2,8}-[A-Z]{1,16}-[0-9]{3}$` |
| Predicate | `P-<SYS>-<NAME>` | `^P-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Invariant | `INV-<SYS>-<NAME>` | `^INV-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Entry Point | `EP-<SYS>-<NAME>` | `^EP-[A-Z0-9-]{1,128}$` |
| Projection | `PRJ-<SYS>-<NAME>` | `^PRJ-[A-Z0-9-]{1,128}$` |
| Generator | `GEN-<STRATEGY>-<SEQ>` | `^GEN-[A-Z0-9-]{1,24}-[0-9]{3}$` |
| Patch | `PATCH-<SYS>-<SEQ>` | `^PATCH-[A-Z0-9]{2,8}-[0-9]{3}$` |

---

## Related Specifications

- [[02-reference-syntax]] - How to reference artifacts in documentation
- [[03-formal-logic]] - Logical operators for invariant expressions
- [[04-field-types]] - Reusable field type definitions
