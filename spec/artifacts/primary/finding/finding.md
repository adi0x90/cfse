# Finding Artifact Specification

## Definition

A **Finding** is a confirmed vulnerability with evidence. Findings are the final artifact of the CFSE workflow, documenting vulnerabilities discovered through successful Explorations. They bridge security research and remediation, providing actionable information for developers and stakeholders.

Findings represent proven security issues - not hypotheses (scenarios) or experiments (explorations), but confirmed vulnerabilities ready for remediation.

**Key principle:** No finding without evidence. A finding must link to an exploration that demonstrated the invariant violation through Delta Analysis.

**Schema:** [`finding.schema.yaml`](./finding.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | FindingID | Unique identifier `FD-<SYSTEM>-<CATEGORY>-<NNN>` |
| `title` | string | Brief, descriptive vulnerability title |
| `severity` | Severity | CRITICAL, HIGH, MEDIUM, LOW, or INFO |
| `description` | string | Detailed vulnerability description |
| `evidence` | Evidence[] | Concrete proof the vulnerability exists |
| `violated_invariants` | ViolatedInvariant[] | Invariants proven to be violated |
| `remediation` | Remediation | How to fix the vulnerability |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `category` | FindingCategory | - | Classification: AUTHZ, AUTHN, IDOR, etc. |
| `summary` | string | - | One-paragraph executive summary |
| `impact` | ImpactAssessment | - | CIA triad, financial, compliance impact |
| `affected_components` | AffectedComponents | - | Concepts, flows, interactions, code |
| `root_cause` | RootCause | - | Why the vulnerability exists |
| `traceability` | Traceability | - | Links to scenario, exploration, patch |
| `metadata` | FindingMetadata | - | Status, dates, CVSS, references |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version |

---

## When to Create a Finding

Create a Finding when:

1. **Exploration verdict = VIOLATION_CONFIRMED**
   - Delta Analysis showed invariant was violated
   - Attack succeeded where it should have failed

2. **Impact is measurable**
   - Can quantify damage (data exposure, unauthorized access)

3. **Reproducible**
   - Can demonstrate vulnerability consistently
   - Have clear steps to reproduce

**Do NOT create Finding for:**
- Scenarios not yet tested
- Explorations with INCONCLUSIVE verdict
- Theoretical vulnerabilities without proof

---

## Field Details

### severity

| Level | CVSS Range | Description | Response Time |
|-------|------------|-------------|---------------|
| CRITICAL | 9.0-10.0 | System compromise, mass data breach | < 24 hours |
| HIGH | 7.0-8.9 | Significant unauthorized access, PII exposure | < 1 week |
| MEDIUM | 4.0-6.9 | Limited unauthorized access | < 1 month |
| LOW | 0.1-3.9 | Minimal impact, significant preconditions | When convenient |
| INFO | 0.0 | Informational only | No fix required |

### evidence

Evidence proves the vulnerability exists:

| Type | Description | Example |
|------|-------------|---------|
| `exploration` | Link to exploration results | `E-SHOP-IDOR-001-01` |
| `trace` | Link to trace evidence | `T-SHOP-IDOR-DELETE-001-01-02` |
| `log` | Relevant log entries | Server logs showing unauthorized access |
| `request` | HTTP request demonstrating attack | curl command output |
| `response` | HTTP response showing success | 200 OK when should be 403 |
| `database` | Database state showing impact | Query results |
| `code` | Vulnerable code snippet | Missing authorization check |

```yaml
evidence:
  - type: exploration
    description: "Delta Analysis confirmed IDOR vulnerability"
    reference: E-SHOP-IDOR-DELETE-001-01

  - type: trace
    description: "Attack trace showing ordering and unexpected success"
    reference: T-SHOP-IDOR-DELETE-001-01-02

  - type: request
    description: "Bob's DELETE request to Alice's item"
    data: |
      DELETE /api/items/item-xyz789 HTTP/1.1
      Host: localhost:3000
      Authorization: Bearer bob-token-here

  - type: response
    description: "Successful deletion (should be 403)"
    data: |
      HTTP/1.1 200 OK
      {"deleted": true, "itemId": "item-xyz789"}
```

### violated_invariants

Document which invariants were broken:

```yaml
violated_invariants:
  - invariant: INV-SHOP-OWNER-DELETE
    rule: "Only the owner of an item can delete it"
    violation_details: >
      Bob (non-owner) successfully deleted Alice's item.
      The API checked authentication but not ownership.
    evidence_ref: "exploration:E-SHOP-IDOR-DELETE-001-01"
```

### remediation

Provide both immediate and systemic fixes:

```yaml
remediation:
  summary: "Add ownership check before delete operation"

  immediate_fix:
    description: "Add owner validation in delete handler"
    code_before: |
      async function deleteItem(req, res) {
        const item = await Item.findById(req.params.id);
        await item.delete();
        return res.json({ deleted: true });
      }
    code_after: |
      async function deleteItem(req, res) {
        const item = await Item.findById(req.params.id);
        if (item.ownerId !== req.user.id) {
          return res.status(403).json({ error: "Forbidden" });
        }
        await item.delete();
        return res.json({ deleted: true });
      }
    files:
      - "controllers/items.js"

  systemic_fix:
    description: "Create authorization middleware for all resource operations"
    code_after: |
      function requireOwnership(Model) {
        return async (req, res, next) => {
          const resource = await Model.findById(req.params.id);
          if (resource.ownerId !== req.user.id) {
            return res.status(403).json({ error: "Forbidden" });
          }
          req.resource = resource;
          next();
        };
      }

  testing:
    - "Add unit test: non-owner cannot delete item"
    - "Add integration test: ownership enforced across all endpoints"

  deployment:
    - "Deploy to staging"
    - "Re-run exploration E-SHOP-IDOR-DELETE-001-01"
    - "Verify verdict changes to ENFORCEMENT_CONFIRMED"
    - "Deploy to production"
```

---

## Key Patterns

- **Evidence first.** Every claim must be backed by concrete evidence from explorations.

- **Invariants are central.** Findings exist because invariants are violated. Always link to specific INV-* IDs.

- **Actionable remediation.** Include code changes, not just descriptions. Developers should be able to copy-paste fixes.

- **Traceability chain.** Maintain links: Scenario -> Exploration -> Finding -> Patch.

- **Root cause analysis.** Don't just fix the symptom - understand why the vulnerability exists.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] No evidence | Claims without proof | Link to exploration with VIOLATION_CONFIRMED |
| [ ] Missing invariant reference | Unclear what security rule was broken | Always cite INV-* IDs |
| [ ] Vague remediation | "Fix the authorization" not actionable | Include specific code changes |
| [ ] No severity justification | Arbitrary severity assignment | Base on impact assessment |
| [ ] Missing traceability | Orphaned finding | Link to scenario and exploration |
| [ ] Creating finding before exploration | Hypothesis treated as fact | Only create after VIOLATION_CONFIRMED |

---

## Example: FD-SHOP-AUTHZ-001

```yaml
id: FD-SHOP-AUTHZ-001
title: "Unauthorized Item Deletion via IDOR"
severity: HIGH
category: IDOR

summary: >
  An authorization bypass vulnerability allows any authenticated user to
  delete items owned by other users. By manipulating the item_id parameter
  in DELETE /api/items/:id without proper ownership validation, an attacker
  can delete arbitrary items, causing data loss and service disruption.
  This violates INV-SHOP-OWNER-DELETE.

description: >
  The delete item endpoint at DELETE /api/items/:id accepts any valid item
  ID from an authenticated user without verifying that the authenticated
  user owns the item. The vulnerability occurs because the API only checks
  for a valid authentication token (identity verification) but does not
  perform authorization (ownership verification).

  An attacker can:
  1. Authenticate with any valid account
  2. Enumerate or guess item IDs (they are UUIDs but may be exposed)
  3. Delete any item by calling DELETE /api/items/{target_item_id}
  4. Cause permanent data loss for other users

  This is a classic Insecure Direct Object Reference (IDOR) pattern where
  the reference to the resource (item_id) is directly used without checking
  whether the requester has authorization to perform the action.

evidence:
  - type: exploration
    description: "Delta Analysis confirmed Bob deleted Alice's item"
    reference: E-SHOP-IDOR-DELETE-001-01
    timestamp: "2025-01-15T10:30:00Z"

  - type: request
    description: "Attacker's DELETE request using victim's item ID"
    data: |
      curl -X DELETE "http://localhost:3000/api/items/item-xyz789" \
        -H "Authorization: Bearer eyJhbGc...bob_token"

  - type: response
    description: "Server returned 200 OK (should be 403)"
    data: |
      HTTP/1.1 200 OK
      Content-Type: application/json
      {"deleted": true, "itemId": "item-xyz789"}

  - type: database
    description: "Item confirmed deleted from database"
    data: |
      SELECT * FROM items WHERE id = 'item-xyz789';
      -- Empty result (item deleted)

  - type: log
    description: "Server logs show no authorization failure"
    data: |
      [2025-01-15 10:30:45] INFO item.deleted user=bob item=item-xyz789

violated_invariants:
  - invariant: INV-SHOP-OWNER-DELETE
    rule: "Only the owner of an item can delete it"
    violation_details: >
      User bob (user-789) successfully deleted item-xyz789 which is
      owned by alice (user-123). The delete operation completed with
      200 OK and the item was removed from the database.
    evidence_ref: "E-SHOP-IDOR-DELETE-001-01"

impact:
  confidentiality:
    level: NONE
    details: "Deletion does not expose item data"
  integrity:
    level: HIGH
    details: "Attackers can delete any user's items, causing data loss"
  availability:
    level: HIGH
    details: "Mass deletion can disrupt service for all users"
  financial: "Potential customer loss, data recovery costs"
  compliance:
    - "GDPR: Data availability obligations (Art. 32)"
    - "SOC 2: Access control requirements"
  attack_scenario: >
    1. Attacker creates legitimate account
    2. Attacker enumerates item IDs via /api/items listing
    3. Attacker deletes competitor's items to disrupt their sales
    4. Victim discovers items missing, no backup available
  affected_users: "All users with items on the platform"

affected_components:
  concepts:
    - C-SHOP-USER
    - C-SHOP-ITEM
  flows:
    - F-SHOP-ITEM-MANAGEMENT
  interactions:
    - I-SHOP-DELETE-ITEM-001
  code:
    - file: "controllers/items.js"
      lines: "45-52"
      function: "deleteItem"
      description: "Missing ownership check before deletion"
    - file: "middleware/auth.js"
      lines: "23"
      function: "verifyToken"
      description: "Only validates identity, not authorization"

root_cause:
  summary: >
    Missing authorization check after authentication. The code assumes
    that being authenticated (having a valid token) implies being
    authorized (having permission to delete the specific item).
  vulnerable_code: |
    async function deleteItem(req, res) {
      const { itemId } = req.params;
      const { userId } = req.user; // From auth middleware

      // MISSING: Ownership check!
      const item = await Item.findById(itemId);

      if (!item) {
        return res.status(404).json({ error: "Item not found" });
      }

      await item.delete();
      return res.status(200).json({ deleted: true });
    }
  design_flaw: >
    Authentication middleware verified "who you are" but application
    logic assumed this also answers "what you can do". Identity is
    not authorization.
  pattern: "Authorization Bypass via IDOR"
  cwe: "CWE-639"

remediation:
  summary: "Add ownership verification before delete operation"

  immediate_fix:
    description: "Add ownership check in deleteItem function"
    code_before: |
      const item = await Item.findById(itemId);
      if (!item) {
        return res.status(404).json({ error: "Item not found" });
      }
      await item.delete();
    code_after: |
      const item = await Item.findById(itemId);
      if (!item) {
        return res.status(404).json({ error: "Item not found" });
      }
      // ADD: Ownership check
      if (item.ownerId !== req.user.id) {
        return res.status(403).json({ error: "Forbidden: Not item owner" });
      }
      await item.delete();
    files:
      - "controllers/items.js"

  systemic_fix:
    description: "Create reusable ownership middleware"
    code_after: |
      // middleware/authz.js
      function requireOwnership(Model) {
        return async (req, res, next) => {
          const resource = await Model.findById(req.params.id);
          if (!resource) {
            return res.status(404).json({ error: "Not found" });
          }
          if (resource.ownerId !== req.user.id) {
            return res.status(403).json({ error: "Forbidden" });
          }
          req.resource = resource;
          next();
        };
      }

      // Apply to routes
      router.delete('/items/:id', requireOwnership(Item), deleteItem);
      router.patch('/items/:id', requireOwnership(Item), updateItem);
    files:
      - "middleware/authz.js"
      - "routes/items.js"

  testing:
    - "it('should reject deletion by non-owner', ...) -> expect 403"
    - "it('should allow deletion by owner', ...) -> expect 200"
    - "it('should enforce INV-SHOP-OWNER-DELETE', ...)"

  deployment:
    - "Deploy patch to staging"
    - "Re-run E-SHOP-IDOR-DELETE-001-01"
    - "Verify verdict = ENFORCEMENT_CONFIRMED"
    - "Run regression tests for Item endpoints"
    - "Deploy to production"
    - "Monitor logs for 403 errors (attack attempts)"

traceability:
  scenario: S-SHOP-IDOR-DELETE-001
  exploration: E-SHOP-IDOR-DELETE-001-01
  trace_refs:
    - T-SHOP-IDOR-DELETE-001-01-01
    - T-SHOP-IDOR-DELETE-001-01-02
  related_findings:
    - FD-SHOP-AUTHZ-002  # Similar IDOR in update endpoint
    - FD-SHOP-AUTHZ-003  # Similar IDOR in share endpoint
  patch: PATCH-SHOP-001

metadata:
  finding_status: OPEN
  discovered: "2025-01-15"
  discoverer: "Security Team"
  cvss_score: 7.5
  cvss_vector: "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H"
  references:
    - "https://cwe.mitre.org/data/definitions/639.html"
    - "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References"

status: ACTIVE
version: "1.0.0"
```

---

## Finding Lifecycle

```
Exploration (VIOLATION_CONFIRMED)
  |
  v
Create Finding (status: OPEN)
  |
  v
Verify: Apply patch, re-test exploration
  |
  v
Validate: Confirm root cause and pattern
  |
  v
Vaccinate: Fix similar vulnerabilities
  |
  v
Valuate: Measure security improvement
  |
  v
Close Finding (status: VERIFIED)
```

---

## Validation Criteria

A valid finding artifact MUST:

1. **Have a unique ID** matching pattern `FD-<SYSTEM>-<CATEGORY>-<NNN>`
2. **Have a descriptive title** (max 100 chars)
3. **Have a severity level** from the Severity enum
4. **Have detailed description** (min 50 chars)
5. **Have at least one evidence item** with type and description
6. **Have at least one violated invariant** with INV-* reference
7. **Have remediation** with at least a summary
8. **Link to exploration** that confirmed the vulnerability

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Exploration Artifact](../exploration/exploration.md) - Experiments that produce findings
- [Trace Artifact](../../supporting/trace/trace.md) - Optional structured evidence for ordering/temporal claims
- [Scenario Artifact](../scenario/scenario.md) - Hypotheses that findings confirm
- [Invariant Artifact](../../supporting/invariant/invariant.md) - Rules that findings violate
- [Concept Artifact](../concept/concept.md) - Entities affected by findings

---

## Common Pitfalls

- Recording a finding without linking reproducible explorations (violates traceability expectations).
- Mixing “suspicions” and “confirmed” issues; unconfirmed hypotheses belong in Scenarios/Explorations.
- Omitting remediation guidance or verification expectations, leaving fixes untestable.
