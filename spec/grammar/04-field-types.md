# Field Types Specification

## Overview

CFSE artifacts use consistent field types across all specifications. This document defines:

- Identifier types with regex patterns
- Enumeration types with allowed values
- Composite types for structured data
- Reference collections for lists of artifacts

These types are used in YAML frontmatter, JSON schemas, and validation tooling.

---

## Identifier Types

### ConceptID

Identifies a security concept artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^C-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Example | `C-AWS-IAM-ROLE` |

```yaml
# Schema definition
ConceptID:
  type: string
  pattern: "^C-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$"
```

### InteractionID

Identifies an interaction artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^I-[A-Z0-9]{2,8}-[A-Z]{1,16}-[A-Z]{1,16}-[0-9]{3}$` |
| Example | `I-AWS-ASSUME-ROLE-001` |

```yaml
# Schema definition
InteractionID:
  type: string
  pattern: "^I-[A-Z0-9]{2,8}-[A-Z]{1,16}-[A-Z]{1,16}-[0-9]{3}$"
```

### FlowID

Identifies a flow artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^F-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Example | `F-AWS-CROSS-ACCOUNT-ACCESS` |

```yaml
# Schema definition
FlowID:
  type: string
  pattern: "^F-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$"
```

### ScenarioID

Identifies a scenario artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^S-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}$` |
| Example | `S-AWS-PRIVILEGE-ESCALATION-001` |

```yaml
# Schema definition
ScenarioID:
  type: string
  pattern: "^S-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}$"
```

### ExplorationID

Identifies an exploration artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^E-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}$` |
| Example | `E-AWS-PRIVILEGE-ESCALATION-001-01` |

```yaml
# Schema definition
ExplorationID:
  type: string
  pattern: "^E-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}$"
```

### TraceID

Identifies a trace artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^T-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}-[0-9]{2}$` |
| Example | `T-AWS-PRIVILEGE-ESCALATION-001-01-02` |

```yaml
# Schema definition
TraceID:
  type: string
  pattern: "^T-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}-[0-9]{2}$"
```

### FindingID

Identifies a finding artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^FD-[A-Z0-9]{2,8}-[A-Z]{1,16}-[0-9]{3}$` |
| Example | `FD-AWS-AUTHZ-001` |

```yaml
# Schema definition
FindingID:
  type: string
  pattern: "^FD-[A-Z0-9]{2,8}-[A-Z]{1,16}-[0-9]{3}$"
```

### PredicateID

Identifies a predicate artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^P-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Example | `P-AWS-HAS-MFA` |

```yaml
# Schema definition
PredicateID:
  type: string
  pattern: "^P-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$"
```

### InvariantID

Identifies an invariant artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^INV-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` |
| Example | `INV-AWS-NO-PUBLIC-S3` |

```yaml
# Schema definition
InvariantID:
  type: string
  pattern: "^INV-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$"
```

### EntryPointID

Identifies an entry point (surface) artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^EP-[A-Z0-9-]{1,128}$` |
| Example | `EP-AWS-S3-BUCKET-API-READ` |

```yaml
# Schema definition
EntryPointID:
  type: string
  pattern: "^EP-[A-Z0-9-]{1,128}$"
```

### ProjectionID

Identifies a projection artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^PRJ-[A-Z0-9-]{1,128}$` |
| Example | `PRJ-AWS-ANON-S3-LIST` |

```yaml
# Schema definition
ProjectionID:
  type: string
  pattern: "^PRJ-[A-Z0-9-]{1,128}$"
```

### GeneratorID

Identifies a generator artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^GEN-[A-Z0-9-]{1,24}-[0-9]{3}$` |
| Example | `GEN-BOUNDARY-001` |

```yaml
# Schema definition
GeneratorID:
  type: string
  pattern: "^GEN-[A-Z0-9-]{1,24}-[0-9]{3}$"
```

### PatchID

Identifies a patch artifact.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | `^PATCH-[A-Z0-9]{2,8}-[0-9]{3}$` |
| Example | `PATCH-AWS-001` |

```yaml
# Schema definition
PatchID:
  type: string
  pattern: "^PATCH-[A-Z0-9]{2,8}-[0-9]{3}$"
```

### ArtifactID (Union Type)

Any valid artifact identifier.

| Property | Value |
|----------|-------|
| Base Type | `string` |
| Pattern | Union of all artifact patterns |
| Example | Any valid artifact ID |

```yaml
# Schema definition
ArtifactID:
  oneOf:
    - $ref: "#/$defs/ConceptID"
    - $ref: "#/$defs/InteractionID"
    - $ref: "#/$defs/FlowID"
    - $ref: "#/$defs/ScenarioID"
    - $ref: "#/$defs/ExplorationID"
    - $ref: "#/$defs/TraceID"
    - $ref: "#/$defs/FindingID"
    - $ref: "#/$defs/PredicateID"
    - $ref: "#/$defs/InvariantID"
    - $ref: "#/$defs/GeneratorID"
    - $ref: "#/$defs/PatchID"
```

---

## Enumeration Types

### Criticality

Priority level for security artifacts.

| Value | Description | Response Time |
|-------|-------------|---------------|
| `P0` | Critical - Immediate action required | < 24 hours |
| `P1` | High - Urgent attention needed | < 1 week |
| `P2` | Medium - Plan remediation | < 1 month |
| `P3` | Low - Address when convenient | Best effort |

```yaml
# Schema definition
Criticality:
  type: string
  enum: [P0, P1, P2, P3]
```

### Verdict

Outcome of exploration or test execution.

| Value | Description |
|-------|-------------|
| `PASS` | Test passed, no security issues found |
| `FAIL` | Test failed, security issue confirmed |
| `INCONCLUSIVE` | Unable to determine outcome |
| `BLOCKED` | Test could not be executed |
| `SKIPPED` | Test intentionally skipped |

```yaml
# Schema definition
Verdict:
  type: string
  enum: [PASS, FAIL, INCONCLUSIVE, BLOCKED, SKIPPED]
```

### InvariantState

Current state of an invariant.

| Value | Description |
|-------|-------------|
| `HOLDS` | Invariant is satisfied |
| `VIOLATED` | Invariant is not satisfied |
| `UNKNOWN` | State cannot be determined |
| `NOT_APPLICABLE` | Invariant does not apply in context |

```yaml
# Schema definition
InvariantState:
  type: string
  enum: [HOLDS, VIOLATED, UNKNOWN, NOT_APPLICABLE]
```

### ArtifactStatus

Lifecycle status of an artifact.

| Value | Description |
|-------|-------------|
| `DRAFT` | Initial creation, not reviewed |
| `REVIEW` | Under review |
| `PLANNED` | Approved future state (not yet current reality) |
| `ACTIVE` | Approved and in use |
| `DEPRECATED` | Being phased out |
| `ARCHIVED` | No longer in use |

```yaml
# Schema definition
ArtifactStatus:
  type: string
  enum: [DRAFT, REVIEW, PLANNED, ACTIVE, DEPRECATED, ARCHIVED]
```

### Extensions

Extension-specific fields, keyed by extension name.

This field exists to allow CFSE corpora to attach extension data to core artifacts without changing core semantics. Extension rules apply only when the extension is declared by the corpus (see `foundations/extensions.md`).

```yaml
Extensions:
  type: object
  additionalProperties: true

# Example usage in an artifact
extensions:
  example_ext:
    some_field: "value"
```

### Severity

Severity level for findings.

| Value | CVSS Range | Description |
|-------|------------|-------------|
| `CRITICAL` | 9.0 - 10.0 | Immediate exploitation risk |
| `HIGH` | 7.0 - 8.9 | Significant security impact |
| `MEDIUM` | 4.0 - 6.9 | Moderate security impact |
| `LOW` | 0.1 - 3.9 | Minor security impact |
| `INFO` | 0.0 | Informational only |

```yaml
# Schema definition
Severity:
  type: string
  enum: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
```

### FindingCategory

Category classification for findings.

| Value | Description |
|-------|-------------|
| `AUTHZ` | Authorization and access control |
| `AUTHN` | Authentication |
| `CRYPTO` | Cryptographic issues |
| `CONFIG` | Configuration vulnerabilities |
| `INJECT` | Injection vulnerabilities |
| `LEAK` | Information disclosure |
| `LOGIC` | Business logic flaws |
| `RACE` | Race conditions |
| `SSRF` | Server-side request forgery |
| `IDOR` | Insecure direct object reference |

```yaml
# Schema definition
FindingCategory:
  type: string
  enum: [AUTHZ, AUTHN, CRYPTO, CONFIG, INJECT, LEAK, LOGIC, RACE, SSRF, IDOR]
```

### ConceptType

Type classification for concepts.

| Value | Description |
|-------|-------------|
| `IDENTITY` | Principal or identity entity |
| `RESOURCE` | Protected resource |
| `POLICY` | Policy or permission document |
| `CREDENTIAL` | Authentication credential |
| `TOKEN` | Session or access token |
| `KEY` | Cryptographic key |
| `CONFIGURATION` | System configuration |

```yaml
# Schema definition
ConceptType:
  type: string
  enum: [IDENTITY, RESOURCE, POLICY, CREDENTIAL, TOKEN, KEY, CONFIGURATION]
```

### ActionType

Type classification for actions.

| Value | Description |
|-------|-------------|
| `CREATE` | Create new resource |
| `READ` | Read resource data |
| `UPDATE` | Modify existing resource |
| `DELETE` | Remove resource |
| `ACCESS` | Generic access |
| `EXECUTE` | Execute code or command |
| `ASSUME` | Assume identity |
| `GRANT` | Grant permission |
| `REVOKE` | Revoke permission |

```yaml
# Schema definition
ActionType:
  type: string
  enum: [CREATE, READ, UPDATE, DELETE, ACCESS, EXECUTE, ASSUME, GRANT, REVOKE]
```

---

## Composite Types

### InvariantRef

Reference to an invariant with state tracking.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | InvariantID | Yes | Invariant identifier |
| `state` | InvariantState | No | Current state |
| `notes` | string | No | Additional context |

```yaml
# Schema definition
InvariantRef:
  type: object
  required: [id]
  properties:
    id:
      $ref: "#/$defs/InvariantID"
    state:
      $ref: "#/$defs/InvariantState"
    notes:
      type: string
```

**Example:**

```yaml
invariant:
  id: INV-AWS-NO-PUBLIC-S3
  state: VIOLATED
  notes: "Public bucket found in staging environment"
```

### EntryPoint

Defines an entry point for scenario or exploration.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `interaction` | InteractionID | Yes | Starting interaction |
| `parameters` | Parameter[] | No | Input parameters |
| `preconditions` | string[] | No | Required preconditions |

```yaml
# Schema definition
EntryPoint:
  type: object
  required: [interaction]
  properties:
    interaction:
      $ref: "#/$defs/InteractionID"
    parameters:
      type: array
      items:
        $ref: "#/$defs/Parameter"
    preconditions:
      type: array
      items:
        type: string
```

**Example:**

```yaml
entry_point:
  interaction: I-AWS-ASSUME-ROLE-001
  parameters:
    - name: role_arn
      type: string
      required: true
    - name: session_name
      type: string
      required: false
  preconditions:
    - "Caller has sts:AssumeRole permission"
    - "Target role trust policy allows assumption"

### TangibleLocation

Records **where a surface is concretely accessible/observable** for testers and auditors (e.g., a full web URL).

This field type is intentionally declarative and MUST NOT encode security logic. Use invariants (`INV-*`) for logic.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | Locator kind (`web_url`, `api_url`, `graphql`, `cli`, `email`, `file`, `event`) |
| `web_url_template` | string | No | Templated fully-qualified URL (use placeholders like `{host}`) |
| `example_urls` | string[] | No | Concrete URLs a tester can paste into a browser/curl |
| `notes` | string | No | Scoping notes (auth preconditions, flags, instance settings) |

```yaml
# Schema definition
TangibleLocation:
  type: object
  required: [kind]
  properties:
    kind:
      type: string
      enum: [web_url, api_url, graphql, cli, email, file, event]
    web_url_template:
      type: string
    example_urls:
      type: array
      items:
        type: string
    notes:
      type: string
```

**Example:**

```yaml
tangible_locations:
  - kind: web_url
    web_url_template: "https://{host}/{namespace}/{project}/-/tags.rss"
    example_urls:
      - "https://gitlab.example.com/gitlab-org/gitlab/-/tags.rss"
    notes: "RSS feed for tags; unauthenticated for public projects"
```
```

### Parameter

Defines a typed parameter for interactions or generators.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Parameter name |
| `type` | string | Yes | Data type |
| `required` | boolean | No | Is required (default: true) |
| `default` | any | No | Default value |
| `description` | string | No | Parameter description |
| `constraints` | Constraint[] | No | Validation constraints |

```yaml
# Schema definition
Parameter:
  type: object
  required: [name, type]
  properties:
    name:
      type: string
      pattern: "^[a-z][a-z0-9_]*$"
    type:
      type: string
      enum: [string, integer, boolean, array, object]
    required:
      type: boolean
      default: true
    default:
      # Any type allowed
    description:
      type: string
    constraints:
      type: array
      items:
        $ref: "#/$defs/Constraint"
```

**Example:**

```yaml
parameters:
  - name: role_arn
    type: string
    required: true
    description: "ARN of the role to assume"
    constraints:
      - type: pattern
        value: "^arn:aws:iam::[0-9]{12}:role/.+$"
  - name: duration_seconds
    type: integer
    required: false
    default: 3600
    constraints:
      - type: range
        min: 900
        max: 43200
```

### Constraint

Validation constraint for parameters.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Constraint type |
| `value` | any | Conditional | Constraint value |
| `min` | number | Conditional | Minimum value |
| `max` | number | Conditional | Maximum value |
| `message` | string | No | Custom error message |

```yaml
# Schema definition
Constraint:
  type: object
  required: [type]
  properties:
    type:
      type: string
      enum: [pattern, range, enum, length, custom]
    value:
      # Any type - depends on constraint type
    min:
      type: number
    max:
      type: number
    message:
      type: string
```

### FlowStep

Defines a step within a flow.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order` | integer | Yes | Step sequence number |
| `interaction` | InteractionID | Yes | Interaction executed |
| `description` | string | No | Step description |
| `conditional` | string | No | Condition for execution |
| `on_success` | integer | No | Next step on success |
| `on_failure` | integer | No | Next step on failure |

```yaml
# Schema definition
FlowStep:
  type: object
  required: [order, interaction]
  properties:
    order:
      type: integer
      minimum: 1
    interaction:
      $ref: "#/$defs/InteractionID"
    description:
      type: string
    conditional:
      type: string
    on_success:
      type: integer
    on_failure:
      type: integer
```

**Example:**

```yaml
steps:
  - order: 1
    interaction: I-AWS-GET-CALLER-IDENTITY-001
    description: "Verify current identity"
  - order: 2
    interaction: I-AWS-ASSUME-ROLE-001
    description: "Assume target role"
    on_success: 3
    on_failure: 4
  - order: 3
    interaction: I-AWS-GET-CREDENTIALS-001
    description: "Retrieve session credentials"
  - order: 4
    interaction: I-AWS-LOG-FAILURE-001
    description: "Log assumption failure"
```

### Finding

Complete finding document structure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | FindingID | Yes | Finding identifier |
| `title` | string | Yes | Brief title |
| `severity` | Severity | Yes | Severity level |
| `category` | FindingCategory | Yes | Finding category |
| `exploration` | ExplorationID | Yes | Source exploration |
| `invariant` | InvariantID | No | Violated invariant |
| `description` | string | Yes | Detailed description |
| `impact` | string | Yes | Security impact |
| `remediation` | string | Yes | Recommended fix |
| `evidence` | Evidence[] | No | Supporting evidence |

```yaml
# Schema definition
Finding:
  type: object
  required: [id, title, severity, category, exploration, description, impact, remediation]
  properties:
    id:
      $ref: "#/$defs/FindingID"
    title:
      type: string
      maxLength: 100
    severity:
      $ref: "#/$defs/Severity"
    category:
      $ref: "#/$defs/FindingCategory"
    exploration:
      $ref: "#/$defs/ExplorationID"
    invariant:
      $ref: "#/$defs/InvariantID"
    description:
      type: string
    impact:
      type: string
    remediation:
      type: string
    evidence:
      type: array
      items:
        $ref: "#/$defs/Evidence"
```

### Evidence

Supporting evidence for a finding.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Evidence type |
| `description` | string | Yes | Evidence description |
| `data` | string | No | Evidence content |
| `url` | string | No | Reference URL |

```yaml
# Schema definition
Evidence:
  type: object
  required: [type, description]
  properties:
    type:
      type: string
      enum: [log, screenshot, request, response, code, configuration]
    description:
      type: string
    data:
      type: string
    url:
      type: string
      format: uri
```

---

## Reference Collections

### ConceptList

List of concept references.

```yaml
# Schema definition
ConceptList:
  type: array
  items:
    $ref: "#/$defs/ConceptID"
  uniqueItems: true
```

**Example:**

```yaml
concepts:
  - C-AWS-IAM-ROLE
  - C-AWS-TRUST-POLICY
  - C-AWS-SESSION-TOKEN
```

### InteractionList

List of interaction references.

```yaml
# Schema definition
InteractionList:
  type: array
  items:
    $ref: "#/$defs/InteractionID"
  uniqueItems: true
```

**Example:**

```yaml
interactions:
  - I-AWS-ASSUME-ROLE-001
  - I-AWS-GET-CREDENTIALS-002
  - I-AWS-VALIDATE-TOKEN-003
```

### InvariantList

List of invariant references (simple or with state).

```yaml
# Schema definition
InvariantList:
  type: array
  items:
    oneOf:
      - $ref: "#/$defs/InvariantID"
      - $ref: "#/$defs/InvariantRef"
  uniqueItems: true
```

**Example (simple):**

```yaml
invariants:
  - INV-AWS-NO-PUBLIC-S3
  - INV-AWS-ADMIN-MFA
```

**Example (with state):**

```yaml
invariants:
  - id: INV-AWS-NO-PUBLIC-S3
    state: HOLDS
  - id: INV-AWS-ADMIN-MFA
    state: VIOLATED
    notes: "Service account lacks MFA"
```

### FindingList

List of finding references.

```yaml
# Schema definition
FindingList:
  type: array
  items:
    $ref: "#/$defs/FindingID"
  uniqueItems: true
```

**Example:**

```yaml
findings:
  - FD-AWS-AUTHZ-001
  - FD-AWS-CONFIG-002
```

### FlowStepList

Ordered list of flow steps.

```yaml
# Schema definition
FlowStepList:
  type: array
  items:
    $ref: "#/$defs/FlowStep"
  minItems: 1
```

---

## Type Summary Table

### Identifier Types

| Type | Pattern | Example |
|------|---------|---------|
| ConceptID | `^C-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` | `C-AWS-IAM-ROLE` |
| InteractionID | `^I-[A-Z0-9]{2,8}-[A-Z]{1,16}-[A-Z]{1,16}-[0-9]{3}$` | `I-AWS-ASSUME-ROLE-001` |
| FlowID | `^F-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` | `F-AWS-CROSS-ACCOUNT-ACCESS` |
| ScenarioID | `^S-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}$` | `S-AWS-PRIVILEGE-ESCALATION-001` |
| ExplorationID | `^E-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}$` | `E-AWS-PRIVILEGE-ESCALATION-001-01` |
| TraceID | `^T-[A-Z0-9]{2,8}-[A-Z0-9-]{1,24}-[0-9]{3}-[0-9]{2}-[0-9]{2}$` | `T-AWS-PRIVILEGE-ESCALATION-001-01-02` |
| FindingID | `^FD-[A-Z0-9]{2,8}-[A-Z]{1,16}-[0-9]{3}$` | `FD-AWS-AUTHZ-001` |
| PredicateID | `^P-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` | `P-AWS-HAS-MFA` |
| InvariantID | `^INV-[A-Z0-9]{2,8}-[A-Z0-9-]{1,32}$` | `INV-AWS-NO-PUBLIC-S3` |
| GeneratorID | `^GEN-[A-Z0-9-]{1,24}-[0-9]{3}$` | `GEN-BOUNDARY-001` |
| PatchID | `^PATCH-[A-Z0-9]{2,8}-[0-9]{3}$` | `PATCH-AWS-001` |

### Enumeration Types

| Type | Values |
|------|--------|
| Criticality | `P0`, `P1`, `P2`, `P3` |
| Verdict | `PASS`, `FAIL`, `INCONCLUSIVE`, `BLOCKED`, `SKIPPED` |
| InvariantState | `HOLDS`, `VIOLATED`, `UNKNOWN`, `NOT_APPLICABLE` |
| ArtifactStatus | `DRAFT`, `REVIEW`, `ACTIVE`, `DEPRECATED`, `ARCHIVED` |
| Severity | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| FindingCategory | `AUTHZ`, `AUTHN`, `CRYPTO`, `CONFIG`, `INJECT`, `LEAK`, `LOGIC`, `RACE`, `SSRF`, `IDOR` |
| ConceptType | `IDENTITY`, `RESOURCE`, `POLICY`, `CREDENTIAL`, `TOKEN`, `KEY`, `CONFIGURATION` |
| ActionType | `CREATE`, `READ`, `UPDATE`, `DELETE`, `ACCESS`, `EXECUTE`, `ASSUME`, `GRANT`, `REVOKE` |

### Composite Types

| Type | Required Fields |
|------|-----------------|
| InvariantRef | `id` |
| EntryPoint | `interaction` |
| Parameter | `name`, `type` |
| Constraint | `type` |
| FlowStep | `order`, `interaction` |
| Finding | `id`, `title`, `severity`, `category`, `exploration`, `description`, `impact`, `remediation` |
| Evidence | `type`, `description` |

---

## Related Specifications

- [[01-id-syntax]] - Detailed ID pattern documentation
- [[02-reference-syntax]] - How to reference artifacts
- [[03-formal-logic]] - Logical expression types
- [[schemas/grammar.schema.yaml]] - JSON Schema implementation
