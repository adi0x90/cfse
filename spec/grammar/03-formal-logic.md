# Formal Logic Specification

## Overview

CFSE uses a formal logic notation to express security invariants - properties that must always hold for a system to be considered secure. This specification defines:

- Logical operators and their precedence
- Optional temporal operators for liveness/response properties
- Quantifiers for universal and existential statements
- Predicate application syntax
- Action notation for security operations
- Complete invariant expression examples

## Logical Operators

### Operator Table

| Operator | Symbol | Precedence | Associativity | Description |
|----------|--------|------------|---------------|-------------|
| NOT | `NOT`, `!` | 1 (highest) | Right | Logical negation |
| AND | `AND`, `&&` | 2 | Left | Logical conjunction |
| OR | `OR`, `\|\|` | 3 | Left | Logical disjunction |
| IMPLIES | `IMPLIES`, `=>` | 4 | Right | Material implication |
| IFF | `IFF`, `<=>` | 5 (lowest) | None | Biconditional (if and only if) |

### Precedence Rules

Higher precedence operators bind more tightly. Without parentheses:

```
NOT A AND B OR C IMPLIES D
```

Parses as:

```
(((NOT A) AND B) OR C) IMPLIES D
```

### Operator Details

#### NOT (Negation)

| Property | Value |
|----------|-------|
| Arity | Unary (prefix) |
| Precedence | 1 |
| ASCII | `NOT`, `!` |
| Unicode | `NOT` |

**Truth table:**

| A | NOT A |
|---|-------|
| T | F |
| F | T |

**Examples:**

```
NOT P-AWS-HAS-MFA(principal)
NOT (A AND B)
!P-AWS-IS-PUBLIC(bucket)
```

#### AND (Conjunction)

| Property | Value |
|----------|-------|
| Arity | Binary (infix) |
| Precedence | 2 |
| ASCII | `AND`, `&&` |
| Unicode | `AND` |

**Truth table:**

| A | B | A AND B |
|---|---|---------|
| T | T | T |
| T | F | F |
| F | T | F |
| F | F | F |

**Examples:**

```
P-AWS-HAS-MFA(principal) AND P-AWS-IN-VPC(resource)
A && B && C
P-K8S-IS-PRIVILEGED(pod) AND P-K8S-HOST-NETWORK(pod)
```

#### OR (Disjunction)

| Property | Value |
|----------|-------|
| Arity | Binary (infix) |
| Precedence | 3 |
| ASCII | `OR`, `\|\|` |
| Unicode | `OR` |

**Truth table:**

| A | B | A OR B |
|---|---|--------|
| T | T | T |
| T | F | T |
| F | T | T |
| F | F | F |

**Examples:**

```
P-AWS-IS-ADMIN(role) OR P-AWS-HAS-POLICY(role, "AdministratorAccess")
A || B || C
P-K8S-IN-NAMESPACE(pod, "kube-system") OR P-K8S-IN-NAMESPACE(pod, "default")
```

#### IMPLIES (Material Implication)

| Property | Value |
|----------|-------|
| Arity | Binary (infix) |
| Precedence | 4 |
| ASCII | `IMPLIES`, `=>` |
| Unicode | `IMPLIES` |

**Truth table:**

| A | B | A IMPLIES B |
|---|---|-------------|
| T | T | T |
| T | F | F |
| F | T | T |
| F | F | T |

**Semantic meaning:** "If A is true, then B must be true."

**Examples:**

```
P-AWS-IS-PUBLIC(bucket) IMPLIES P-AWS-HAS-ENCRYPTION(bucket)
P-K8S-IS-PRIVILEGED(pod) => P-K8S-IN-TRUSTED-NS(pod)
ACCESS(resource) IMPLIES P-AUTH-AUTHENTICATED(principal)
```

#### IFF (Biconditional)

| Property | Value |
|----------|-------|
| Arity | Binary (infix) |
| Precedence | 5 |
| ASCII | `IFF`, `<=>` |
| Unicode | `IFF` |

**Truth table:**

| A | B | A IFF B |
|---|---|---------|
| T | T | T |
| T | F | F |
| F | T | F |
| F | F | T |

**Semantic meaning:** "A is true if and only if B is true."

**Examples:**

```
P-AWS-IS-ADMIN(role) IFF P-AWS-HAS-POLICY(role, "AdministratorAccess")
P-K8S-IS-MASTER(node) <=> P-K8S-HAS-TAINT(node, "master")
```

---

## Temporal Operators (Optional)

CFSE's core expression language is first-order logic over **state predicates** (and action/event terms). For most security invariants (safety properties), this is sufficient.

When you need to express **liveness/response** requirements ("good thing eventually happens") or "always ... eventually ..." constraints, CFSE additionally supports a small set of *temporal operators* inspired by temporal logic (e.g., TLA+).

### Trace Semantics (Informal)

Temporal operators are interpreted over a **trace**: a discrete sequence of evaluation points (states and/or events) `t0, t1, t2, ...`.

- A non-temporal expression is evaluated at a single trace position `ti` ("at time i").
- An `ACTION(...)` term is treated as true at `ti` if that event occurs at `ti` (based on the trace's event data).
- If the available evidence is a single snapshot, tools MAY treat it as a 1-step trace.
- Traces MAY be represented explicitly as `T-*` Trace artifacts and referenced from Explorations/Findings.

### Operator Table

| Operator | Symbol | Description |
|----------|--------|-------------|
| ALWAYS | `ALWAYS`, `[]` | Holds at all future positions in the trace |
| EVENTUALLY | `EVENTUALLY`, `<>` | Holds at some future position in the trace |
| LEADS_TO | `LEADS_TO`, `~>` | Response property: `A LEADS_TO B` means `ALWAYS(A IMPLIES EVENTUALLY B)` |

### Examples

**Response property (leads-to):**

```
FORALL bucket: C-AWS-S3-BUCKET.
  P-AWS-IS-PUBLIC(bucket) LEADS_TO P-AWS-HAS-AUDIT-LOG(bucket)
```

**Explicit ALWAYS/EVENTUALLY form:**

```
ALWAYS(
  FORALL bucket: C-AWS-S3-BUCKET.
    P-AWS-IS-PUBLIC(bucket) IMPLIES EVENTUALLY P-AWS-HAS-AUDIT-LOG(bucket)
)
```

---

## Quantifiers

### FORALL (Universal Quantification)

Asserts that a property holds for all elements of a domain.

#### Syntax

```
FORALL <variable>: <domain>.
  <expression>
```

Or inline:

```
FORALL <variable>: <domain>. <expression>
```

#### Components

| Component | Description |
|-----------|-------------|
| `variable` | Bound variable name (lowercase) |
| `domain` | Type or set constraint (typically a ConceptID) |
| `expression` | Logical expression using the variable |

#### Examples

**Basic universal:**

```
FORALL bucket: C-AWS-S3-BUCKET.
  NOT P-AWS-IS-PUBLIC(bucket)
```

> "For all S3 buckets, the bucket is not public."

**With implication:**

```
FORALL role: C-AWS-IAM-ROLE.
  P-AWS-IS-ADMIN(role) IMPLIES P-AWS-HAS-MFA(role.principal)
```

> "For all IAM roles, if the role is an admin role, the principal must have MFA."

**Nested quantifiers:**

```
FORALL principal: C-AWS-IAM-PRINCIPAL.
  FORALL resource: C-AWS-S3-BUCKET.
    ACCESS(principal, resource) IMPLIES P-AWS-AUTHORIZED(principal, resource)
```

> "For all principals and resources, access implies authorization."

### EXISTS (Existential Quantification)

Asserts that a property holds for at least one element of a domain.

#### Syntax

```
EXISTS <variable>: <domain>.
  <expression>
```

#### Components

| Component | Description |
|-----------|-------------|
| `variable` | Bound variable name (lowercase) |
| `domain` | Type or set constraint (typically a ConceptID) |
| `expression` | Logical expression using the variable |

#### Examples

**Basic existential:**

```
EXISTS admin: C-AWS-IAM-ROLE.
  P-AWS-IS-ADMIN(admin)
```

> "There exists at least one admin IAM role."

**Negative existential (no such element):**

```
NOT EXISTS bucket: C-AWS-S3-BUCKET.
  P-AWS-IS-PUBLIC(bucket) AND P-AWS-HAS-SENSITIVE-DATA(bucket)
```

> "There does not exist a public bucket containing sensitive data."

**Combined quantifiers:**

```
FORALL sensitive: C-DATA-SENSITIVE.
  EXISTS key: C-CRYPTO-KEY.
    P-ENCRYPTED-WITH(sensitive, key)
```

> "For all sensitive data, there exists a key that encrypts it."

---

## Predicate Application

### Syntax

```
<PredicateID>(<argument1>, <argument2>, ...)
```

Or with named arguments:

```
<PredicateID>(<param1>=<value1>, <param2>=<value2>)
```

### Argument Types

| Type | Description | Example |
|------|-------------|---------|
| Variable | Bound variable from quantifier | `bucket`, `role` |
| Literal | String constant | `"AdministratorAccess"` |
| Property access | Object property | `role.principal` |
| Artifact ID | Reference to artifact | `C-AWS-S3-BUCKET` |

### Examples

**Single argument:**

```
P-AWS-HAS-MFA(principal)
P-K8S-IS-PRIVILEGED(pod)
P-OAUTH2-TOKEN-VALID(token)
```

**Multiple arguments:**

```
P-AWS-HAS-POLICY(role, "AdministratorAccess")
P-K8S-IN-NAMESPACE(pod, "kube-system")
P-AWS-CAN-ASSUME(source_role, target_role)
```

**Property access:**

```
P-AWS-HAS-MFA(role.principal)
P-K8S-MATCHES-SELECTOR(pod.labels, deployment.selector)
```

**Named arguments:**

```
P-AWS-HAS-PERMISSION(principal=role, action="s3:GetObject", resource=bucket)
```

---

## Grouping with Parentheses

Parentheses override default precedence.

### Examples

**Default precedence:**

```
A OR B AND C
```

Evaluates as: `A OR (B AND C)`

**Explicit grouping:**

```
(A OR B) AND C
```

Evaluates as: `(A OR B) AND C`

**Complex expressions:**

```
(P-AWS-HAS-MFA(principal) OR P-AWS-IN-VPC(resource))
  AND P-AWS-AUTHENTICATED(principal)
  IMPLIES P-AWS-AUTHORIZED(principal, resource)
```

---

## Action Notation

Actions represent security-relevant operations on resources.

### Standard Actions

| Action | Description | Example Domains |
|--------|-------------|-----------------|
| `CREATE` | Create new resource | IAM roles, S3 buckets, K8s pods |
| `READ` | Read resource data | S3 objects, secrets, configs |
| `UPDATE` | Modify existing resource | Policies, configurations |
| `DELETE` | Remove resource | IAM users, EC2 instances |
| `ACCESS` | Generic access (read or write) | Any resource |
| `EXECUTE` | Execute code or command | Lambda, container exec |

### Action Syntax

```
<ACTION>(<subject>, <object>)
```

Or with single argument (implicit subject):

```
<ACTION>(<object>)
```

### Examples

**Basic actions:**

```
CREATE(principal, role)
READ(principal, secret)
UPDATE(principal, policy)
DELETE(principal, resource)
```

**Access action (generic):**

```
ACCESS(principal, resource)
ACCESS(user, C-AWS-S3-BUCKET)
```

**Execute action:**

```
EXECUTE(principal, function)
EXECUTE(pod, command)
```

### Actions in Invariants

```
FORALL principal: C-AWS-IAM-PRINCIPAL.
  FORALL secret: C-AWS-SECRETS-MANAGER.
    READ(principal, secret) IMPLIES P-AWS-HAS-PERMISSION(principal, "secretsmanager:GetSecretValue", secret)
```

```
FORALL user: C-K8S-USER.
  FORALL pod: C-K8S-POD.
    EXECUTE(user, pod) IMPLIES P-K8S-HAS-EXEC-PERMISSION(user, pod.namespace)
```

---

## Complete Invariant Examples

### Example 1: No Public S3 Buckets

```yaml
id: INV-AWS-NO-PUBLIC-S3
name: No Public S3 Buckets
criticality: P0
expression: |
  FORALL bucket: C-AWS-S3-BUCKET.
    NOT P-AWS-IS-PUBLIC(bucket)
rationale: |
  Public S3 buckets are a leading cause of data breaches.
  All buckets must have explicit access controls.
```

### Example 2: MFA Required for Admin Access

```yaml
id: INV-AWS-ADMIN-MFA
name: MFA Required for Admin Access
criticality: P0
expression: |
  FORALL role: C-AWS-IAM-ROLE.
    P-AWS-IS-ADMIN(role) IMPLIES
    FORALL principal: C-AWS-IAM-PRINCIPAL.
      P-AWS-CAN-ASSUME(principal, role) IMPLIES
        P-AWS-HAS-MFA(principal)
rationale: |
  Administrative access must be protected by MFA to prevent
  credential theft attacks.
```

### Example 3: Pod Security Standards

```yaml
id: INV-K8S-POD-SECURITY
name: Pod Security Standards
criticality: P1
expression: |
  FORALL pod: C-K8S-POD.
    (P-K8S-IS-PRIVILEGED(pod) OR P-K8S-HOST-NETWORK(pod))
    IMPLIES P-K8S-IN-NAMESPACE(pod, "kube-system")
rationale: |
  Privileged pods and host network access are only permitted
  in the kube-system namespace for core components.
```

### Example 4: Encryption at Rest

```yaml
id: INV-AWS-ENCRYPTION-REST
name: Encryption at Rest Required
criticality: P0
expression: |
  FORALL resource: C-AWS-DATA-STORE.
    P-AWS-STORES-DATA(resource) IMPLIES
      EXISTS key: C-AWS-KMS-KEY.
        P-AWS-ENCRYPTED-WITH(resource, key)
rationale: |
  All data stores must use encryption at rest with
  customer-managed KMS keys.
```

### Example 5: Least Privilege Access

```yaml
id: INV-AWS-LEAST-PRIVILEGE
name: Least Privilege Access
criticality: P1
expression: |
  FORALL principal: C-AWS-IAM-PRINCIPAL.
    FORALL action: Action.
      FORALL resource: C-AWS-RESOURCE.
        EXECUTE(principal, action, resource) IMPLIES
          (P-AWS-EXPLICITLY-ALLOWED(principal, action, resource)
           AND NOT P-AWS-EXPLICITLY-DENIED(principal, action, resource))
rationale: |
  Access must be explicitly granted and not denied.
  Implicit permissions violate least privilege.
```

### Example 6: Token Expiration

```yaml
id: INV-OAUTH2-TOKEN-EXPIRY
name: Token Expiration Required
criticality: P1
expression: |
  FORALL token: C-OAUTH2-ACCESS-TOKEN.
    P-OAUTH2-HAS-EXPIRY(token) AND
    P-OAUTH2-EXPIRY-WITHIN(token, "1h")
rationale: |
  Access tokens must expire within one hour to limit
  the window of compromise.
```

### Example 7: Cross-Account Trust Boundaries

```yaml
id: INV-AWS-TRUST-BOUNDARY
name: Cross-Account Trust Boundaries
criticality: P0
expression: |
  FORALL role: C-AWS-IAM-ROLE.
    FORALL external: C-AWS-ACCOUNT.
      P-AWS-TRUSTS-ACCOUNT(role, external) IMPLIES
        (P-AWS-APPROVED-ACCOUNT(external)
         AND P-AWS-HAS-EXTERNAL-ID(role))
rationale: |
  Cross-account trust relationships must be restricted to
  approved accounts and use external IDs to prevent
  confused deputy attacks.
```

---

## Expression Grammar (EBNF)

```ebnf
expression     ::= iff_expr

iff_expr       ::= leads_to_expr (IFF leads_to_expr)?
leads_to_expr  ::= implies_expr (LEADS_TO implies_expr)?
implies_expr   ::= or_expr (IMPLIES or_expr)?
or_expr        ::= and_expr (OR and_expr)*
and_expr       ::= not_expr (AND not_expr)*
not_expr       ::= (NOT | temporal_unary) not_expr | quantified | primary

temporal_unary ::= ALWAYS | EVENTUALLY

quantified     ::= quantifier variable ':' domain '.' expression
quantifier     ::= FORALL | EXISTS

primary        ::= predicate_app | action | '(' expression ')' | variable
predicate_app  ::= PredicateID '(' arg_list ')'
action         ::= ACTION '(' arg_list ')'

arg_list       ::= argument (',' argument)*
argument       ::= variable | literal | property_access | artifact_id
property_access ::= variable '.' identifier

variable       ::= lowercase_identifier
domain         ::= ConceptID | type_name
literal        ::= '"' string '"' | number

IFF            ::= 'IFF' | '<=>'
LEADS_TO       ::= 'LEADS_TO' | '~>'
IMPLIES        ::= 'IMPLIES' | '=>'
OR             ::= 'OR' | '||'
AND            ::= 'AND' | '&&'
NOT            ::= 'NOT' | '!'
ALWAYS         ::= 'ALWAYS' | '[]'
EVENTUALLY     ::= 'EVENTUALLY' | '<>'
FORALL         ::= 'FORALL'
EXISTS         ::= 'EXISTS'
ACTION         ::= 'CREATE' | 'READ' | 'UPDATE' | 'DELETE' | 'ACCESS' | 'EXECUTE'
```

---

## Validation Rules

### Syntactic Validation

1. All parentheses must be balanced
2. Quantifiers must have variable, domain, and body
3. Predicates must have valid PredicateID format
4. Actions must use standard action keywords
5. Temporal operators must have required operand(s) (`ALWAYS X`, `EVENTUALLY X`, `A LEADS_TO B`)

### Semantic Validation

1. Variables must be bound by enclosing quantifier
2. Domain must reference valid ConceptID or type
3. Predicate arguments must match signature
4. Property access must reference valid concept attributes
5. Temporal operators require an evaluation trace (at minimum, a 1-step snapshot trace)

### Example Validation Errors

| Expression | Error |
|------------|-------|
| `FORALL x. P(x)` | Missing domain for variable x |
| `P-AWS-HAS-MFA(y)` | Variable y not bound |
| `A IMPLIES` | Missing right operand |
| `((A AND B)` | Unbalanced parentheses |
| `EXECUTE(principal)` | Missing required action target |

---

## Related Specifications

- [[01-id-syntax]] - Predicate and Invariant ID patterns
- [[02-reference-syntax]] - Referencing predicates in documents
- [[04-field-types]] - Invariant field type definitions
