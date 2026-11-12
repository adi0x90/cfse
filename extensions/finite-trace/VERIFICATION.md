# Finite-trace profile verification — 2026-11-12

Scope: [issue #6](https://github.com/adi0x90/cfse/issues/6) and [issue #7](https://github.com/adi0x90/cfse/issues/7), implemented as the [bounded opt-in profile](README.md). The core baseline is `34575b9191c6a457faf669e505abac9af2e6dd2a` (2.0.1). No core schema or Boolean Predicate contract changes. **Implemented and locally verified; not a release or publication claim.**

The final revision/command record is in `verification/run.json`; unit output and the benign CLI result are beside it. Commands below run from the repository root. Tests use only public synthetic inputs. No frozen study, provider call, training run, receipt verifier, or external candidate code is involved.

## Issue #6 criterion mapping

All test names are in [`tests/test_finite_trace.py`](../../tests/test_finite_trace.py), unless otherwise noted.

| Acceptance criterion | Implementation and evidence | Result/scope |
|---|---|---|
| Inventory before new interpreter | README implementation choice; public schema loader reused; inspected alternatives did not supply compatible typed finite-domain calls | Bounded local inventory, not ecosystem-wide absence |
| Public schema-valid C/P/INV fixture | `fixtures/artifacts.json`, includes resolvable EP artifacts; `test_benign_reuse_and_capabilities`, `test_public_fixtures_end_to_end` | Schema/static/execution checked |
| One typed predicate reused in two invariants | P-DEMO-ROLE in request and delivery; `test_benign_reuse_and_capabilities` checks both reported binding versions | Passed |
| Distinct arity, concept type, unbound, unresolved, unsupported diagnostics | `test_static_diagnostics`, `test_named_arguments_and_precedence`, `test_parser_rejection_and_scope_controls` | Named/positional signatures and locations checked; unsupported constructs rejected |
| Defined dependency evaluation/invalidation; reject cycles | `test_dependency_cycle_and_assumption`, whole-input identity | DAG assumptions; unestablished dependency yields unknown without erasing own violation; cycles rejected |
| Policy/binding changes invalidate reuse | `test_identity_changes_invalidate_reuse`, `test_schema_and_binding_drift`, `test_multistep_failure_and_identity` | Policy/scope/binding/trace identity changes; stale binding versions/digests rejected; no persistent cache |
| Explicit finite domains and completeness | `test_domains_and_trace_completeness`, `test_exists_on_incomplete_domains` | Vacuity documented; incomplete enumeration preserves witnesses/counterexamples |
| Operational failures and missing evidence separated | `test_failures_are_not_rewards`, `test_budget`, all twelve CLI cases | Unknown, no grader, parse/static, invalid trace/input, runtime, timeout distinguishable |
| No core/security/proof claim from finite execution | `test_benign_reuse_and_capabilities`, manifest, result capabilities | Authenticity, proof, full core conformance and policy correspondence remain not checked |
| Treat hints as documentation; review binding correspondence | `test_implementation_hint_is_never_executed`, artifact/signature digest tests; README correspondence table | No candidate-code execution; review declaration is not authenticated |

## Issue #7 criterion mapping

| Acceptance criterion | Test/evidence | Result |
|---|---|---|
| Unknown with observed allow and deny | `test_false_pass_regression`, CLI `allowed_unknown` / `denied_unknown` | UNKNOWN, reward 0, passed false for both |
| Public truth tables and comparison | `test_truth_tables`, `test_exhaustive_synthetic_decisions` | All 9 Boolean/unknown pairs for AND/OR/IFF; NOT; 36 independent end-to-end combinations |
| No truthiness/default-denial/null-comparison full reward | `Evidence.__bool__` rejection; `test_truth_tables`, `test_forged_scope_malformed_and_duplicate_observations`, original false-pass regression | Exact Booleans only; missing row is unknown |
| False conjunction, true disjunction, definite violations survive unknown | Truth tables; `test_independent_violation_survives_missing`, `test_invariant_order_cannot_mask_violation`, exhaustive decisions | Passed in either invariant order |
| Missing vs known absent vs malformed | `test_absent_missing_invalid_and_operational_outcomes`; CLI `known_absent`, unknown, invalid cases | Distinct semantics; absence requires reviewed binding |
| Reward and pass jointly deny unknown/failure | Failure/budget tests, CLI outcome matrix; `test_failure_cannot_be_hidden_by_known_true_disjunction` | Zero reward and passed false, including HOLDS with operational error |
| Degenerate graders fail usefulness/correctness | `test_real_engine_qualification_controls`, `test_degenerate_qualification_controls` | Constant true/false, all unknown and always error fail; real correct fixture controls pass |
| Boolean Predicate schema unchanged | `test_schema_and_binding_drift` rejects tristate; git schema diff against baseline empty | Existing return contract preserved |

## Annex criteria and surviving contradictions

The archived annex retains all eleven original historical observations, workarounds and version-pinned dispositions. Its follow-up distinguishes the new changes from the historical claims. Resolved 2.0.1-era findings are not reopened. Public archived text retains redactions; private notes and source paths are absent.

| Item | Authoritative correction | Regression |
|---|---|---|
| TR-1 summary/pseudocode | Union of `traceability.exploration` and `evidence[type=exploration].reference` | `test_summary_and_validation_paths` |
| TR-3 pseudocode | `targeted_invariants` | `test_summary_and_validation_paths` |
| TR-5 valid example and path | Existing FindingReference object with `finding_id` and `invariant`; summary traverses `finding_ref.finding_id` | `test_tr5_valid_fragment_against_actual_schema` accepts corrected object, rejects old scalar |

These are narrow prose/example corrections under `spec/`; no schema widening or new normative execution semantics. Annex items about static assessment and arbitrary external IDs remain separate concerns.

## Commands and observed checks

```sh
python3.12 -m venv "$CFSE_VERIFY_ENV"
"$CFSE_VERIFY_ENV/bin/python" -m pip install -r tests/requirements.txt
"$CFSE_VERIFY_ENV/bin/python" -B -m unittest discover -s tests -v
.venv/bin/python -B -m unittest discover -s tests -v
"$CFSE_VERIFY_ENV/bin/python" -B extensions/finite-trace/evaluate.py \
  --artifacts extensions/finite-trace/fixtures/artifacts.json \
  --config extensions/finite-trace/fixtures/bindings.json \
  --trace extensions/finite-trace/fixtures/trace.json
git diff --check
git diff 34575b9191c6a457faf669e505abac9af2e6dd2a -- 'spec/**/*.schema.yaml'
```

`CFSE_VERIFY_ENV` was a fresh temporary virtual environment created for Python 3.12; `.venv` used Python 3.15.2. Exact Python/dependency versions and final revision are in the run record. Both suites passed with one explicit skip: the pre-existing optional full-core external semantic validator integration. That skip is not claimed as covered by this subset evaluator. The twelve CLI variants are separate subprocess invocations with ten-second deadlines.

## Distinct adversarial pass

After the initial implementation passed its thirteen new tests, a separate self-review tried to invalidate the result through exhaustive decision combinations, changed signatures/digests, forged scopes, malformed values, reversed invariant order, dependency cycles, incomplete existential domains, multi-step counterexamples, degenerate graders, and operational errors hidden behind known-true disjunctions. This was not an independent external audit.

The review found a real parser defect: trailing commas were accepted. A regression first failed with `HOLDS` instead of `PARSE_ERROR`; the parser now rejects the input. It also improved capability reporting so completed schema validation remains visible after a static/parse failure. The TR regressions first failed on the stale exploration field and scalar Patch reference, then passed after the spec corrections. The original thirteen execution tests failed before the evaluator existed, and then passed after implementation.

Fresh final runs include the original repository suite, profile semantics, adversarial checks, twelve CLI cases, and malformed/duplicate-key/oversized/deep JSON cases. The false-pass test explicitly reproduces the **generated comparator grader** bug before checking the repaired declarative behavior. No normative CFSE core bug is inferred from that historical mechanism.

## Residual limits and completion boundary

The two issues' acceptance criteria are met for this explicitly bounded profile. General CFSE execution, primitive/property/action/temporal evaluation, full-core semantic integration, evidence authentication, policy-correspondence proof, source/binary correspondence and arbitrary executable adapters remain outside it and are reported/documented accordingly. A result can establish only what follows from the supplied observations and declared finite scope. Completeness and binding review are operator assertions. Vacuous HOLDS alone is not usefulness qualification. No new comparative advantage or historical study result is claimed.

Implementation and tests can be complete locally while GitHub issues remain open. This record does not claim a public push, release, or issue closure.
