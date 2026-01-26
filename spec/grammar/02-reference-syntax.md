# Reference Syntax Specification

## Overview

CFSE documents establish relationships between artifacts through references. This specification defines three distinct reference styles, each serving specific documentation needs:

1. **Inline Backtick Reference** - Casual mentions in prose
2. **Bracketed Link Reference** - Formal, navigable references
3. **Field Reference** - Structured metadata fields

## Reference Styles

### 1. Inline Backtick Reference

Used for casual mentions of artifacts within narrative text.

#### Syntax

```
`<ARTIFACT-ID>`
```

#### Characteristics

| Property | Value |
|----------|-------|
| Purpose | Casual mention in prose |
| Navigation | Not automatically linked |
| Validation | ID syntax validation only |
| Context | Running text, explanations |

#### Usage Guidelines

- Use when mentioning an artifact without implying dependency
- Appropriate for examples and explanatory text
- Does not create formal traceability
- May appear multiple times for the same artifact

#### Examples

**Prose usage:**

> The `C-AWS-IAM-ROLE` concept represents an AWS IAM role that can be
> assumed by principals. When combined with `C-AWS-TRUST-POLICY`, it
> enables cross-account access patterns.

**In lists:**

> Key concepts involved:
> - `C-AWS-IAM-ROLE` - The assumable role
> - `C-AWS-TRUST-POLICY` - Defines who can assume
> - `C-AWS-SESSION-TOKEN` - Temporary credentials

**In code comments:**

```yaml
# This interaction implements the assume role pattern
# See `I-AWS-ASSUME-ROLE-001` for details
```

---

### 2. Bracketed Link Reference

Used for formal references that establish navigable relationships.

#### Syntax

```
[[<ARTIFACT-ID>]]
```

#### Characteristics

| Property | Value |
|----------|-------|
| Purpose | Formal, navigable reference |
| Navigation | Automatically resolved to link |
| Validation | ID existence verification |
| Context | Traceability sections, formal links |

#### Usage Guidelines

- Use when establishing formal relationships
- Creates traceability in dependency graphs
- Should resolve to actual artifact documents
- Tooling may verify existence and generate links

#### Examples

**Formal dependency:**

```markdown
## Dependencies

This scenario depends on:
- [[C-AWS-IAM-ROLE]] - Core role concept
- [[C-AWS-TRUST-POLICY]] - Trust relationship definition
- [[I-AWS-ASSUME-ROLE-001]] - Assume role interaction
```

**Cross-references in YAML frontmatter:**

```yaml
related:
  concepts:
    - "[[C-AWS-IAM-ROLE]]"
    - "[[C-AWS-SESSION-TOKEN]]"
  interactions:
    - "[[I-AWS-ASSUME-ROLE-001]]"
```

**Inline formal reference:**

> This exploration validates [[INV-AWS-ROLE-TRUST-BOUNDARY]] through
> systematic testing of [[F-AWS-CROSS-ACCOUNT-ACCESS]].

#### Resolution Rules

| Context | Resolution Behavior |
|---------|---------------------|
| Markdown | Convert to relative file link |
| YAML | Validate existence, store as string |
| HTML export | Convert to hyperlink |
| Validation | Verify artifact exists |

---

### 3. Field Reference

Used in structured metadata fields within YAML frontmatter or configuration.

#### Syntax

```yaml
<FIELD>: <ID>
```

Or for multiple references:

```yaml
<FIELD>:
  - <ID-1>
  - <ID-2>
```

#### Characteristics

| Property | Value |
|----------|-------|
| Purpose | Structured metadata binding |
| Navigation | Field-specific interpretation |
| Validation | Type-checked against field schema |
| Context | YAML frontmatter, schemas |

#### Usage Guidelines

- Use in document frontmatter for machine-readable relationships
- Field name determines expected ID type
- Enables automated validation and tooling
- Supports both single and list values

#### Examples

**Single value fields:**

```yaml
---
id: E-AWS-PRIVILEGE-ESCALATION-001-01
scenario: S-AWS-PRIVILEGE-ESCALATION-001
flow: F-AWS-CROSS-ACCOUNT-ACCESS
---
```

**List value fields:**

```yaml
---
id: F-AWS-CROSS-ACCOUNT-ACCESS
concepts:
  - C-AWS-IAM-ROLE
  - C-AWS-TRUST-POLICY
  - C-AWS-SESSION-TOKEN
interactions:
  - I-AWS-ASSUME-ROLE-001
  - I-AWS-GET-CREDENTIALS-002
invariants:
  - INV-AWS-ROLE-TRUST-BOUNDARY
  - INV-AWS-SESSION-DURATION
---
```

**Typed reference fields:**

```yaml
---
findings:
  - id: FD-AWS-AUTHZ-001
    severity: HIGH
    related_invariant: INV-AWS-ROLE-TRUST-BOUNDARY
---
```

---

## Reference Contexts by Artifact Type

### Concept References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Interaction subject | Field | `subject: C-AWS-IAM-ROLE` |
| Interaction target | Field | `target: C-AWS-TRUST-POLICY` |
| Flow participant | Field | `concepts: [C-AWS-IAM-ROLE]` |
| Prose mention | Backtick | `` `C-AWS-IAM-ROLE` `` |
| Formal dependency | Bracketed | `[[C-AWS-IAM-ROLE]]` |

### Interaction References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Flow step | Field | `steps: [I-AWS-ASSUME-ROLE-001]` |
| Invariant scope | Field | `applies_to: [I-AWS-ASSUME-ROLE-001]` |
| Prose mention | Backtick | `` `I-AWS-ASSUME-ROLE-001` `` |
| Traceability | Bracketed | `[[I-AWS-ASSUME-ROLE-001]]` |

### Entry Point References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Concept surface inventory | Field | `entry_points: [EP-AWS-IAM-ROLE-API-ASSUME]` |
| Interaction trigger surface | Field | `entry_points: [EP-AWS-IAM-ROLE-API-ASSUME]` |
| Scenario anchor | Field | `attack_vector.anchor.ref: EP-AWS-IAM-ROLE-API-ASSUME` |
| Projection surfaces | Field | `surfaces: [{ ref: EP-AWS-IAM-ROLE-API-ASSUME }]` |
| Prose mention | Backtick | `` `EP-AWS-IAM-ROLE-API-ASSUME` `` |
| Formal dependency | Bracketed | `[[EP-AWS-IAM-ROLE-API-ASSUME]]` |

### Flow References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Scenario flow | Field | `flow: F-AWS-CROSS-ACCOUNT-ACCESS` |
| Exploration target | Field | `flow: F-AWS-CROSS-ACCOUNT-ACCESS` |
| Related flows | Bracketed | `[[F-AWS-CROSS-ACCOUNT-ACCESS]]` |
| Prose mention | Backtick | `` `F-AWS-CROSS-ACCOUNT-ACCESS` `` |

### Scenario References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Exploration parent | Field | `scenario: S-AWS-PRIVILEGE-ESCALATION-001` |
| Finding source | Field | `scenario: S-AWS-PRIVILEGE-ESCALATION-001` |
| Cross-reference | Bracketed | `[[S-AWS-PRIVILEGE-ESCALATION-001]]` |
| Prose mention | Backtick | `` `S-AWS-PRIVILEGE-ESCALATION-001` `` |

### Exploration References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Finding source | Field | `exploration: E-AWS-PRIVILEGE-ESCALATION-001-01` |
| Patch target | Field | `exploration: E-AWS-PRIVILEGE-ESCALATION-001-01` |
| Cross-reference | Bracketed | `[[E-AWS-PRIVILEGE-ESCALATION-001-01]]` |
| Prose mention | Backtick | `` `E-AWS-PRIVILEGE-ESCALATION-001-01` `` |

### Trace References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Exploration trace evidence | Field | `trace_refs.attack: T-AWS-PRIVILEGE-ESCALATION-001-01-02` |
| Finding trace evidence | Field | `traceability.trace_refs: [T-AWS-PRIVILEGE-ESCALATION-001-01-01]` |
| Cross-reference | Bracketed | `[[T-AWS-PRIVILEGE-ESCALATION-001-01-02]]` |
| Prose mention | Backtick | `` `T-AWS-PRIVILEGE-ESCALATION-001-01-02` `` |

### Projection References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Prose mention | Backtick | `` `PRJ-AWS-ANON-S3-LIST` `` |
| Formal dependency | Bracketed | `[[PRJ-AWS-ANON-S3-LIST]]` |

### Finding References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Patch addresses | Field | `addresses: [FD-AWS-AUTHZ-001]` |
| Related findings | Bracketed | `[[FD-AWS-AUTHZ-001]]` |
| Prose mention | Backtick | `` `FD-AWS-AUTHZ-001` `` |

### Invariant References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Scenario invariants | Field | `invariants: [INV-AWS-ROLE-TRUST-BOUNDARY]` |
| Finding violation | Field | `violated_invariant: INV-AWS-ROLE-TRUST-BOUNDARY` |
| Formal reference | Bracketed | `[[INV-AWS-ROLE-TRUST-BOUNDARY]]` |
| Prose mention | Backtick | `` `INV-AWS-ROLE-TRUST-BOUNDARY` `` |

### Predicate References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Invariant composition | Field | `predicates: [P-AWS-HAS-MFA]` |
| Logic expression | Inline | `P-AWS-HAS-MFA(principal)` |
| Formal reference | Bracketed | `[[P-AWS-HAS-MFA]]` |

### Generator References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Scenario generator | Field | `generator: GEN-BOUNDARY-001` |
| Cross-reference | Bracketed | `[[GEN-BOUNDARY-001]]` |
| Prose mention | Backtick | `` `GEN-BOUNDARY-001` `` |

### Patch References

| Context | Reference Style | Example |
|---------|-----------------|---------|
| Finding resolution | Field | `resolved_by: PATCH-AWS-001` |
| Cross-reference | Bracketed | `[[PATCH-AWS-001]]` |
| Prose mention | Backtick | `` `PATCH-AWS-001` `` |

---

## Resolution Rules

### Backtick Resolution

```
Input:  `C-AWS-IAM-ROLE`
Output: <code>C-AWS-IAM-ROLE</code>
```

- No link resolution
- Syntax validation only
- Rendered as inline code

### Bracketed Resolution

```
Input:  [[C-AWS-IAM-ROLE]]
Output: `C-AWS-IAM-ROLE` → `<corpus_root>/concepts/C-AWS-IAM-ROLE.md`
```

Resolution algorithm:

1. Parse artifact ID from brackets
2. Detect artifact type from prefix
3. Look up artifact in appropriate directory
4. Generate relative or absolute path
5. Validate artifact exists (optional, configurable)
6. Produce markdown/HTML link

### Field Resolution

```yaml
Input:  scenario: S-AWS-PRIVILEGE-ESCALATION-001
Output: { "scenario": "S-AWS-PRIVILEGE-ESCALATION-001", "_resolved": true }
```

Resolution algorithm:

1. Parse field name and value
2. Determine expected ID type from schema
3. Validate ID matches expected pattern
4. Optionally verify artifact exists
5. Store for tooling consumption

---

## Mixed Reference Example

Complete document showing all reference styles:

```markdown
---
id: E-AWS-PRIVILEGE-ESCALATION-001-01
title: IAM Role Chain Privilege Escalation
scenario: S-AWS-PRIVILEGE-ESCALATION-001
flow: F-AWS-CROSS-ACCOUNT-ACCESS
concepts:
  - C-AWS-IAM-ROLE
  - C-AWS-TRUST-POLICY
invariants:
  - INV-AWS-ROLE-TRUST-BOUNDARY
---

# IAM Role Chain Privilege Escalation

## Overview

This exploration tests the `C-AWS-IAM-ROLE` concept for privilege
escalation vulnerabilities through role chaining.

## Dependencies

Formal dependencies for this exploration:
- [[C-AWS-IAM-ROLE]] - Primary target concept
- [[C-AWS-TRUST-POLICY]] - Trust boundary definition
- [[I-AWS-ASSUME-ROLE-001]] - Core interaction tested

## Invariants Tested

This exploration validates [[INV-AWS-ROLE-TRUST-BOUNDARY]]:

> FORALL role: C-AWS-IAM-ROLE.
>   `P-AWS-TRUST-VALIDATED`(role) IMPLIES
>   `P-AWS-WITHIN-BOUNDARY`(role)

## Methodology

Testing follows the [[F-AWS-CROSS-ACCOUNT-ACCESS]] flow pattern,
executing `I-AWS-ASSUME-ROLE-001` with various trust policy
configurations.

## Findings

| ID | Severity | Invariant Violated |
|----|----------|-------------------|
| [[FD-AWS-AUTHZ-001]] | HIGH | [[INV-AWS-ROLE-TRUST-BOUNDARY]] |
```

---

## Related Specifications

- [[01-id-syntax]] - Artifact ID patterns and validation
- [[03-formal-logic]] - Logical operators in expressions
- [[04-field-types]] - Field type definitions for schemas
