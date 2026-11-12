# Finite-trace execution profile, version 1

An **opt-in, informative reference implementation** for [proposal #6](https://github.com/adi0x90/cfse/issues/6) and [uncertainty contract #7](https://github.com/adi0x90/cfse/issues/7). Only adopted `spec/` requirements are normative. The core [Evidence Evaluation](../../spec/semantics/06-evidence-evaluation.md) guarantees are now normative in the unreleased working specification; this profile is one implementation. Its execution machinery remains optional. No core schema, Predicate return type, or released version changes. Invoke it explicitly; it is not the full core semantic validator.

## Run the public example

From the repository root, with Python 3.12 or later:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -B extensions/finite-trace/evaluate.py \
  --artifacts extensions/finite-trace/fixtures/artifacts.json \
  --config extensions/finite-trace/fixtures/bindings.json \
  --trace extensions/finite-trace/fixtures/trace.json
.venv/bin/python -B -m unittest discover -s tests -v
```

The benign example returns `HOLDS`, reward `1`, `passed=true`, exit `0`. Other outcomes exit `1`. `fixtures/cases.json` defines twelve independent synthetic variants of these inputs. `CommandLineTests.test_public_fixtures_end_to_end` materializes each variant and invokes this exact CLI. No private corpus, credentials, network service, model, or generated Python is needed.

## Implementation choice and authority

A bounded inventory preceded implementation. The available corpus tooling supplied reference scanning and schema/static validation approaches; the inspected propositional engine supported three-valued connectives but treated predicate applications as opaque atoms rather than typed finite-domain calls. An evaluation runner orchestrated checks without supplying this binding model. None was directly compatible with all of this profile's typed calls, finite quantifiers, and public standalone packaging. This is a statement about the inspected implementations, not the ecosystem.

The implementation reuses the public repository's local `jsonschema`/`referencing` loading approach and existing test dependencies. A small checked parser implements the documented subset of the existing CFSE EBNF. No private engine is copied or imported. The schema baseline is CFSE 2.0.1, revision `34575b9191c6a457faf669e505abac9af2e6dd2a`; results also record the digest of the actual local schema files, interpreter source and unreleased core evidence contract.

`capabilities.json` declares the supported surface. Results independently report schema validation, static logic validation, finite execution, authenticity, proof, policy correspondence, and full core conformance. Authenticity, proof, English/binding correspondence and full core conformance remain `not_checked`. Schema validation covers supplied C/P/INV/EP artifacts; static validation is limited to the profile's logic, signatures, listed predicates, Concept entry-point/invariant references, entry-point owners and invariant dependencies. Other metadata relationships, attribute constraints, lifecycle cross-reference consistency, and whole-corpus TR-1..TR-5 semantics are not evaluated.

## Supported language

- `NOT`, `AND`, `OR`, `IMPLIES`, `IFF`, their core ASCII aliases, grouping, and lowercase Boolean constants. Precedence and associativity follow the pinned grammar; chained unparenthesized IFF is rejected.
- Nested `FORALL variable: C-... . expression` and `EXISTS variable: C-... . expression`. Quantifier bodies extend through the following expression, as in the core EBNF. Shadowing is rejected.
- Calls to schema-valid P artifacts with Concept-typed parameters. Positional order follows the signature. Named arguments must match every parameter exactly once, in any order; mixed calls, duplicate names and trailing commas are rejected.
- Unresolved IDs, arity, names, Concept types, unbound variables, unsupported values/operators and syntax have separate diagnostic codes and artifact/offset or JSON-path locations.

Primitive domains/parameters, property access, literal arguments, temporal operators and action terms are unsupported. Actions are **not inferred**: request and delivery decisions are explicit observed Boolean predicates in this fixture. Unsupported action/temporal terms are diagnosed rather than approximated. This profile does not implement the held general-purpose authoring or receipt proposals.

`implementation` hints are documentation only and are never executed. Artifact extensions are rejected by this profile; the external configuration is not a new core artifact field or extension namespace. Opt-in is by choosing this command and its `profile` setting.

## Observation binding and correspondence review

Configuration is operator-owned and passed separately from submitted artifacts/observations. Do not let a candidate choose its bindings, policy version, scope, operation budget, or qualification labels. `boolean-table/1` is the only adapter. It consumes a table of observed propositions, keyed by predicate ID and ordered entity identifiers, at each evaluation point. It does not collect or authenticate those observations.

Each binding has a version, exact parameter signature, predicate-content digest, nonblank correspondence review and explicit absence interpretation. A changed predicate or signature requires renewed binding review. A review string/digest is a declaration of operator review, **not proof that the review or semantic correspondence is correct**.

The self-contained User, Project and ExportJob model uses these bindings:

| Predicate | Meaning of the table value | Review boundary |
|---|---|---|
| `P-DEMO-ROLE(user, project)` | User holds the export role for this project at this point | Reused by request and delivery; not inferred from HTTP status |
| `P-DEMO-AVAILABLE(job)` | This job's export artifact is available at this point | Confirmed absence means false; missing evidence means unknown |
| `P-DEMO-REQUESTED(user, project)` | Observed request decision allows the request | Must equal the role-policy decision |
| `P-DEMO-DELIVERED(user, project, job)` | Observed delivery decision allows delivery | Must equal role AND availability |

The example's declared scope contains one project and its job. Larger scopes must supply the relevant product-domain observations or author a relation predicate; job/project membership is not silently inferred. The fixtures assert synthetic facts and illustrate correspondence only. A real collector needs separate review and authentication.

## Finite domains, time and completeness

Trace inputs are a **profile JSON envelope**, not claimed to be core `T-*` Trace artifacts. Each trace has an ID, exact operator scope, completeness flag, typed domains and ordered steps. Step IDs identify observation points; observations in one step describe the same logical point. Every invariant is evaluated at every supplied step, then conjoined. There is no future-time or wall-clock interpretation.

Domain members are opaque string identifiers tagged by their Concept domain. Each domain explicitly declares whether its enumeration is complete for the stated scope/window. Missing domains are incomplete, not empty. Missing predicate rows are unknown, not denial. Duplicate domain members, steps or rows are invalid.

FORALL is conjunction over the enumerated members; EXISTS is disjunction. Incomplete domains contribute unknown: a counterexample still makes FORALL false, and a witness still makes EXISTS true. Empty **complete** domains have ordinary vacuous semantics (FORALL true, EXISTS false). Empty trace step lists are invalid. An incomplete trace contributes unknown to the overall conjunction, while observed violations survive. Completeness flags are supplied assertions, not authenticated facts. An operator must review scope/completeness; vacuous satisfaction alone does not qualify a grader as useful.

Supported dependencies form a DAG. All invariant bodies are evaluated, in dependency order. A dependency that is not definitely established contributes unknown to the dependent result; a dependent's own definite violation survives. Dependency failure reasons are retained. Cycles and unresolved dependencies are rejected. The engine recomputes results, with no persistent result cache. Whole-input identity comparison invalidates a proposed reuse after **any** artifact, dependency, binding, policy version, scope, schema, engine, or trace change. `reusable` checks input identity only; it must never authenticate a caller-supplied result.

## Boolean proposition, evidence, and reward

`Predicate.returns` remains `boolean`. `Evidence.value` represents whether that Boolean proposition is known true, known false or unobserved (`None`). This is an adapter evidence state, not a third Predicate return value. Python truthiness of Evidence raises an error. Known values must be exact Booleans; `0`, `1`, strings, null, lists and objects are rejected. There is no `bool(None)`, equality-to-null policy fallback, or implicit denial.

| Observation state | Required value | Interpretation |
|---|---|---|
| `known` | Boolean | Observed proposition |
| `unknown` | null | Evidence insufficient |
| `absent` | false | Known absence, allowed only by reviewed `absent_is_false` binding |
| `runtime_error` | null | Adapter-reported operational error |
| `timeout` | null | Adapter-reported timeout |

Every supplied row requires a reason, observation reference and matching binding version. Omitted rows carry a generated missing-observation reason and trace/step reference. Imported failure rows report adapter failures; they are not claims that this interpreter executed an external adapter. Interpreter operation-budget exhaustion independently yields `TIMEOUT`.

An explicit `P-X-KNOWN` can be bound to a Boolean observation of knowability; `P-X-VALUE` remains Boolean. The profile never invents either predicate or converts unobserved VALUE evidence into false. A KNOWABILITY proposition requires its own defined/reviewed binding.

The connective algebra is strong Kleene evidence evaluation: false dominates AND, true dominates OR, NOT preserves unknown, and IFF (decision equality) is unknown if either side is unobserved. IMPLIES is `NOT A OR B`. Both sides and all invariant bodies are considered, so an unrelated missing fact cannot mask a definite violation. Reasons and operational failures are retained even when another operand determines the Boolean value.

`truth` records `TRUE`, `FALSE` or `UNKNOWN` as formula evidence. Every result explicitly carries `result_scope: finite_formula` and `exploration_state: not_checked`; `capabilities.exploration_verdict` is also `not_checked`. The profile's legacy `state` labels (`HOLDS`, `VIOLATED`, `UNKNOWN`) are shorthand for formula truth only, **not core Exploration InvariantResults**. No BASE/ATT record or confirmed security verdict is emitted. Consumers MUST use the explicit result scope and MUST NOT promote these labels into execution-backed core states. `outcome` separately distinguishes these from `NO_GRADER`, `PARSE_ERROR`, `STATIC_ERROR`, `INVALID_TRACE`, `INVALID_INPUT`, `RUNTIME_ERROR`, and `TIMEOUT`. Full reward `1` and `passed=true` require HOLDS **and no operational failure**. Every other case earns zero and fails full-reward admission. A known-true disjunction can therefore have state HOLDS and outcome RUNTIME_ERROR, with reward zero. All encountered failure classes remain in `failures` even if TIMEOUT takes precedence in the summary.

The denied-with-unknown regression reproduces the reduced **generated comparator grader** mechanism from issue #7. It does not attribute that historical bug to a normative CFSE core evaluator. In this profile, deny IFF unknown and allow IFF unknown both remain unknown, unless an independent logical result resolves the combined formula.

## Qualification and execution limits

`qualify(results, expected)` requires operator-owned conforming, violating and indeterminate controls, exact expected states/outcomes, and consistent reward/pass pairs. Constant true fails violating/unknown controls; constant false fails conforming controls; always-unknown and always-error fail usefulness/correctness. Tests execute these controls through the actual engine. This is a small correctness/usefulness gate, not a comparative reliability benchmark or proof of generalization.

The interpreter accepts data only: no eval/exec, imports, callbacks, shell commands, filesystem operations or network requests from candidate artifacts. The CLI reads only operator-selected inputs and local schemas. Bounds: 1 MB combined JSON input, 128 artifacts, 512 tokens and 48 nesting levels per formula, 128 members/domain, 256 steps, and an operator-controlled budget of 1..100,000 evaluation-node visits. A budget is a deterministic work limit, not a wall-clock measurement. CLI fixture subprocesses additionally have a ten-second test deadline. Any future executable adapter needs a separate external sandbox; this parser is not a sandbox for arbitrary code.

See [verification and acceptance matrix](VERIFICATION.md). No historical study was rerun or altered, and no representation advantage, policy truth, source/binary correspondence, unbounded security property or theorem proof follows from these checks.
