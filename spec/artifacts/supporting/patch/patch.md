# Patch Artifact Specification

## Definition

A **Patch** is a structured remediation document that transforms a confirmed vulnerability into durable security improvements. Patches follow the 4V methodology: Verify, Validate, Vaccinate, Valuate.

The 4V methodology ensures that fixes are not just quick patches but systematic improvements:
- **Verify**: Confirm the fix works by re-running explorations
- **Validate**: Ensure completeness and no regressions
- **Vaccinate**: Apply systemic changes to prevent similar issues
- **Valuate**: Assess the security improvement's value and capture lessons

**Schema:** [`patch.schema.yaml`](./patch.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | PatchID | Unique identifier following pattern `PATCH-<SYSTEM>-<NNN>` |
| `finding_ref` | FindingReference | Reference to the finding(s) being patched |
| `root_cause` | RootCause | Analysis of the underlying implementation issue |
| `fix_description` | string | Plain-language description of the changes made |
| `verification` | Verification | 4V Phase 1: How the fix was verified to work |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | string | - | Short description of the patch |
| `code_changes` | CodeChange[] | - | Specific code changes made |
| `validation` | Validation | - | 4V Phase 2: Broader validation and regression testing |
| `vaccination` | Vaccination | - | 4V Phase 3: Systemic changes to prevent recurrence |
| `valuation` | Valuation | - | 4V Phase 4: Value assessment and lessons learned |
| `related_invariants` | InvariantID[] | - | Invariants affected by this patch |
| `status` | PatchStatus | `DRAFT` | Current lifecycle status |
| `created_at` | datetime | - | When the patch was created |
| `completed_at` | datetime | - | When all 4V phases completed |

---

## The 4V Methodology

### Verify (Phase 1) - REQUIRED

Confirm the fix actually works.

| Element | Description |
|---------|-------------|
| Re-run explorations | Run the original failing exploration(s) against patched code |
| Before/after results | Document VIOLATED -> HOLDS transition |
| Additional variations | Test variations of the original exploit |
| Verified by/at | Record who verified and when |

A patch without verification is just a hope.

### Validate (Phase 2)

Ensure completeness and no regressions.

| Element | Description |
|---------|-------------|
| Regression tests | Tests to prevent reintroduction |
| Edge cases | Boundary conditions and special cases |
| Integration tests | Tests across component boundaries |
| Code review | Reviewers who validated the fix |

### Vaccinate (Phase 3)

Apply systemic changes that prevent similar vulnerabilities.

| Change Type | Example |
|-------------|---------|
| `middleware` | Centralized authorization middleware |
| `library` | Shared ownership check library |
| `framework` | Framework-level security defaults |
| `pattern` | Documented secure coding pattern |
| `configuration` | Security-hardened default config |
| `linting` | Static analysis rules |
| `training` | Developer security training |
| `none` | Single instance, no systemic fix needed |

Vaccination turns individual fixes into organizational learning.

### Valuate (Phase 4)

Assess the security improvement's value.

| Element | Description |
|---------|-------------|
| Metrics | Quantitative measures (coverage, blocked attempts) |
| Status overlay updates | Update invariant enforcement status |
| Lessons learned | What we learned from this vulnerability |
| Recommendations | Future prevention strategies |
| Business impact | Value delivered to the organization |

---

## Field Details

### finding_ref

Links the patch to the original finding:

```yaml
finding_ref:
  finding_id: FD-SHOP-AUTHZ-001
  invariant: INV-SHOP-OWNER-DELETE
  scenario: S-SHOP-IDOR-DELETE-001
  exploration: E-SHOP-IDOR-DELETE-001-01
  impact: "Any authenticated user could delete items belonging to other users"
```

### root_cause

Explains WHY the vulnerability exists:

```yaml
root_cause:
  issue: |
    The delete endpoint extracted item_id from the URL but did not verify
    that the authenticated user owned the item before deletion. The ownership
    check was accidentally removed during refactoring in commit abc123.
  code_locations:
    - file: "src/api/items.py"
      line: 42
      function: "delete_item"
      snippet: "item = Item.query.get(item_id)  # Missing: check user == item.owner"
  pattern: "Missing authorization check on resource operations"
  contributing_factors:
    - "No unit test for ownership verification"
    - "Code review did not catch missing check"
    - "Authorization logic not centralized"
```

### verification

The critical first phase of 4V:

```yaml
verification:
  explorations_rerun:
    - exploration_id: E-SHOP-IDOR-DELETE-001-01
      result_before: VIOLATED
      result_after: HOLDS
      notes: "UserB can no longer delete UserA's items"
    - exploration_id: E-SHOP-IDOR-DELETE-001-02
      result_before: VIOLATED
      result_after: HOLDS
      notes: "Verified with admin user as well"
  additional_tests:
    - "Tested with edge case: owner deleting own item (should succeed)"
    - "Tested with non-existent item_id (should 404, not leak info)"
  verified_by: "security-team"
  verified_at: "2024-01-15T14:30:00Z"
```

---

## Key Patterns

- **Root cause, not symptoms.** Describe why the vulnerability exists, not what the vulnerability is. "Missing ownership check" is better than "IDOR vulnerability."

- **Verification is mandatory.** Every patch must include re-run exploration results. Without verification, the patch is just a hypothesis.

- **Vaccination amplifies value.** Individual fixes have linear value; systemic fixes have multiplicative value. Always consider vaccination.

- **Update status overlay.** When a patch completes, update the invariant status overlay to reflect the new enforcement status.

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] No verification | Cannot confirm fix actually works | Always re-run explorations, document before/after |
| [ ] Symptom-level root cause | "There was a bug" - not actionable | Explain why the bug existed, what allowed it |
| [ ] Missing code locations | Others cannot find or verify the fix | Include specific file:line references |
| [ ] No vaccination | Same bug will recur elsewhere | Consider systemic fixes even if fix is local |
| [ ] Empty valuation | Miss learning opportunity | Capture lessons learned, update metrics |
| [ ] Status overlay not updated | Stale enforcement status misleads teams | Update overlay when fix is verified |

---

## Example: PATCH-SHOP-001

```yaml
id: PATCH-SHOP-001
title: "Fix ownership checks on item delete()"

finding_ref:
  finding_id: FD-SHOP-AUTHZ-001
  invariant: INV-SHOP-OWNER-DELETE
  scenario: S-SHOP-IDOR-DELETE-001
  exploration: E-SHOP-IDOR-DELETE-001-01
  impact: "Any authenticated user could delete items belonging to other users"

root_cause:
  issue: |
    The delete_item endpoint extracted item_id from the URL path but did not
    verify that the authenticated user owned the item before deletion. The
    ownership check was present in the update endpoint but missing from delete.
  code_locations:
    - file: "src/api/items.py"
      line: 42
      function: "delete_item"
      snippet: |
        @app.route('/items/<item_id>', methods=['DELETE'])
        def delete_item(item_id):
            item = Item.query.get(item_id)
            # BUG: Missing ownership check here
            db.session.delete(item)
  pattern: "Missing authorization check on destructive operations"
  contributing_factors:
    - "Copy-paste from read endpoint without auth check"
    - "No integration test for ownership on delete"

fix_description: |
  Added ownership verification to the delete_item endpoint. Before deleting,
  the endpoint now checks that the authenticated user's ID matches the item's
  owner_id. Returns 403 Forbidden if the user is not the owner.

code_changes:
  - file: "src/api/items.py"
    description: "Added ownership check before delete"
    change_type: modified
    commit: "abc123def456"
    pull_request: "https://github.com/example/shop/pull/42"
  - file: "tests/test_items.py"
    description: "Added integration test for ownership on delete"
    change_type: modified

verification:
  explorations_rerun:
    - exploration_id: E-SHOP-IDOR-DELETE-001-01
      result_before: VIOLATED
      result_after: HOLDS
      notes: "UserB receives 403 when trying to delete UserA's items"
    - exploration_id: E-SHOP-IDOR-DELETE-001-02
      result_before: VIOLATED
      result_after: HOLDS
      notes: "Admin user also cannot delete non-owned items"
  additional_tests:
    - "Owner successfully deletes own item"
    - "Non-existent item returns 404"
    - "Unauthenticated request returns 401"
  verified_by: "security-team"
  verified_at: "2024-01-15T14:30:00Z"

validation:
  regression_tests:
    - "test_delete_own_item_succeeds"
    - "test_delete_other_user_item_forbidden"
    - "test_delete_nonexistent_item_not_found"
  edge_cases:
    - "Item with no owner field (legacy data)"
    - "Concurrent delete requests"
  reviewed_by:
    - "alice@example.com"
    - "bob@example.com"

vaccination:
  change_type: middleware
  description: |
    Created centralized @require_ownership decorator that can be applied to
    any endpoint that operates on owned resources. This decorator extracts
    the resource ID, loads the resource, and verifies ownership before
    allowing the request to proceed.
  new_invariants: []
  strengthened_invariants:
    - INV-SHOP-OWNER-DELETE
  automation:
    - "Added linting rule to flag endpoints without @require_auth or @require_ownership"
  scope: "All shop resource endpoints"

valuation:
  metrics:
    blocked_exploit_attempts: 0
    test_coverage_increase: "15%"
    endpoints_protected: 12
  status_overlay_updates:
    - invariant: INV-SHOP-OWNER-DELETE
      scope: "/api/items/*"
      previous_status: KNOWN_MISSING
      new_status: KNOWN_PRESENT
      evidence: "E-SHOP-IDOR-DELETE-001-01 now passes"
  lessons_learned:
    - "Destructive operations need explicit ownership checks"
    - "Copy-paste of endpoints should trigger auth review"
    - "Centralized auth middleware prevents omission"
  recommendations:
    - "Require ownership decorator for all CRUD operations"
    - "Add pre-commit hook for auth decorator linting"

related_invariants:
  - INV-SHOP-OWNER-DELETE
  - INV-SHOP-AUTH-REQUIRED

status: COMPLETE
created_at: "2024-01-14T10:00:00Z"
completed_at: "2024-01-16T09:00:00Z"
```

---

## Validation Criteria

A valid patch artifact MUST:

1. **Have a unique ID** matching pattern `PATCH-<SYSTEM>-<NNN>`
2. **Reference a finding** with at minimum finding_id and invariant
3. **Have a root cause** with a non-empty issue description
4. **Have a fix description** explaining what was changed
5. **Have verification** with at least one exploration result showing before/after

### Verification Requirements

| Requirement | Valid | Invalid |
|-------------|-------|---------|
| Has explorations_rerun | Array with 1+ items | Empty array or missing |
| Before state | VIOLATED or UNKNOWN | HOLDS (wasn't broken?) |
| After state | HOLDS | VIOLATED (fix didn't work) |

---

## Patch Lifecycle

```
DRAFT -> IN_PROGRESS -> VERIFICATION -> VALIDATION -> VACCINATION -> VALUATION -> COMPLETE
                              |               |             |             |
                              v               v             v             v
                           Verify          Validate     Vaccinate      Valuate
                        (Required)        (Optional)   (Recommended)  (Recommended)
```

1. **DRAFT**: Patch document created, not yet started
2. **IN_PROGRESS**: Fix being implemented
3. **VERIFICATION**: Re-running explorations (4V Phase 1)
4. **VALIDATION**: Regression testing and code review (4V Phase 2)
5. **VACCINATION**: Applying systemic fixes (4V Phase 3)
6. **VALUATION**: Assessing value and lessons (4V Phase 4)
7. **COMPLETE**: All applicable phases finished
8. **REJECTED**: Patch superseded or rejected

---

## Related Specifications

- [Grammar Schema](../../../grammar/schemas/grammar.schema.yaml) - Shared type definitions
- [Finding Artifact](../../primary/finding/finding.md) - What patches address
- [Exploration Artifact](../../primary/exploration/exploration.md) - Used in verification
- [Invariant Artifact](../invariant/invariant.md) - What patches restore

---

## Common Pitfalls

- Claiming a patch fixed a finding without re-running the exploration and recording verification evidence.
- Narrow fixes that don’t generalize (“vaccinate”); update invariants/generators when appropriate.
- Leaving regression risk unaddressed (no tests, no invariant reasoning, no guardrails).
