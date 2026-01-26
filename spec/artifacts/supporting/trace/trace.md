# Trace Artifact Specification

## Definition

A **Trace** is a structured, ordered sequence of observations (events and/or state facts) used as evidence for temporal and event-sequence claims.

Traces are most useful when:

- An invariant uses temporal operators (`ALWAYS`, `EVENTUALLY`, `LEADS_TO`)
- A finding depends on ordering ("A happened before B", "B never happened after A")
- You need reproducible evidence instead of narrative log excerpts

**Schema:** [`trace.schema.yaml`](./trace.schema.yaml)

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | TraceID | Unique identifier for the trace (`T-*`) |
| `title` | string | Descriptive name for the trace |
| `exploration_ref` | ExplorationID | Exploration that produced or motivated the trace |
| `path` | enum | `BASELINE`, `ATTACK`, or `OTHER` |
| `steps` | TraceStep[] | Ordered steps of the trace (`t0, t1, ...`) |

---

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `scenario_ref` | ScenarioID | - | Convenience link back to the scenario |
| `time_window` | TimeWindow | - | Time bounds of the evidence slice |
| `sources` | TraceSource[] | - | Where evidence came from (logs, CloudTrail, etc.) |
| `correlation` | Correlation | - | How events were grouped into this trace |
| `description` | string | - | Narrative context |
| `status` | ArtifactStatus | `DRAFT` | Lifecycle status |
| `version` | string | - | Semantic version |

---

## Field Details

### steps

Each step represents a trace position `ti`. A step MAY contain:

- `events`: actions/events that occurred at `ti`
- `states`: facts assumed/observed true at `ti`

When using CFSE temporal operators, tools (including AI assistants) interpret temporal expressions over the sequence of steps.

---

## Example: Baseline vs Attack Traces

```yaml
id: T-SHOP-IDOR-DELETE-001-01-01
title: "Baseline trace: owner deletes own item"
exploration_ref: E-SHOP-IDOR-DELETE-001-01
scenario_ref: S-SHOP-IDOR-DELETE-001
path: BASELINE
sources:
  - type: app_log
    ref: "logs/shop-api-2026-01-24.log"
correlation:
  keys: ["request_id"]
  values:
    request_id: "req_123"
steps:
  - i: 0
    events:
      - "DELETE(\"alice\", \"item-xyz789\")"
  - i: 1
    states:
      - "P-SHOP-ITEM-EXISTS(\"item-xyz789\")" # Example predicate fact (optional)
    notes: "Item deleted successfully by owner"
status: ACTIVE
version: "1.0.0"
```

```yaml
id: T-SHOP-IDOR-DELETE-001-01-02
title: "Attack trace: non-owner deletes victim item"
exploration_ref: E-SHOP-IDOR-DELETE-001-01
scenario_ref: S-SHOP-IDOR-DELETE-001
path: ATTACK
sources:
  - type: app_log
    ref: "logs/shop-api-2026-01-24.log"
correlation:
  keys: ["request_id"]
  values:
    request_id: "req_456"
steps:
  - i: 0
    events:
      - "DELETE(\"bob\", \"item-xyz789\")"
  - i: 1
    notes: "Unexpected success: item deleted by non-owner"
status: ACTIVE
version: "1.0.0"
```

---

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| [ ] Missing correlation | Trace is ambiguous | Record correlation keys and values (request_id, trace_id, principal_id) |
| [ ] Mixing unrelated sessions | False ordering claims | Split into separate traces per correlation |
| [ ] Only prose | Not reproducible | Put ordering into `steps[]` |
| [ ] No source pointers | Not auditable | Add `sources[]` with refs/hashes when possible |

---

## Common Pitfalls

- Using traces as a prose dump without structured steps (`steps[]`) and stable references.
- Capturing ordering claims without linking to the producing exploration (`exploration_ref`) when applicable.
- Missing provenance (sources, hashes, correlation IDs) for evidence that needs auditability.
