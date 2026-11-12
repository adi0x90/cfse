# Core uncertainty verification — 2026-11-12

Verified the normative [Evidence Evaluation](../../../spec/semantics/06-evidence-evaluation.md) guarantees, corrected knowability guidance, core conformance vectors and optional runner's explicit formula/Exploration reporting boundary. This is an **unreleased core change**, committed locally without a public push. Schemas, Boolean Predicate return types, and `VERSION` remain unchanged.

[`run.json`](run.json) records the parent revision, exact source hashes tested, command templates and output hashes. The changes and this evidence are committed together; source hashes identify the verified content without a self-referential commit hash.

## Results

- Python 3.12.13: **41 tests run, 40 passed, 1 skipped, 0 failed**.
- Python 3.15.2: **41 tests run, 40 passed, 1 skipped, 0 failed**.
- The skip is the existing optional full-core external semantic-validator integration (`CFSE_CONTRACT_BINARY` was not supplied). It is not claimed as covered by the finite subset runner.
- **59 portable evidence vectors:** 36 binary operator results, three negations, twelve composition/failure/knowability cases and eight finite-domain cases.
- **43 canonical corpus cases**, including the new schema-valid confirmed violation with an independent UNKNOWN target. Schema validation does not establish cross-artifact evidence truth; optional external semantic validation remains skipped.
- **Four deliberately broken evaluator controls rejected:** unknown defaulted to false, unknown erasing an independent definite result, constant true, constant false. Existing actual-runner qualification tests additionally reject always-unknown and always-error behavior.
- Existing twelve CLI cases and 36 request/delivery decision combinations remain green.
- Benign CLI smoke reports `truth=TRUE`, `result_scope=finite_formula`, `exploration_state=not_checked`, and `capabilities.exploration_verdict=not_checked`. A formula result is not a confirmed security conclusion.
- Schema/version diff and whitespace checks are empty. The modified/new documentation's 37 local Markdown targets resolve.

## Requirement-to-test mapping

| Core requirement | Evidence |
|---|---|
| UE-1: proposition/evidence/decision separation; no automatic Exploration promotion | `test_core_formulas_and_failure_eligibility_through_typed_runner`; CLI smoke; existing Exploration record-gate negatives |
| UE-2: missing is not false/absent; reasons and diagnostics | Core missing/absence vectors; existing exact-Boolean, absent/missing/invalid, duplicate-observation and failure tests |
| UE-3: normative evidence tables and preservation of definite results | `test_normative_tables_match_portable_vectors`, `test_core_tables_against_reference_adapter`, mutation controls, independent-violation/order tests |
| UE-4: finite scope and completeness | `test_core_finite_domain_vectors`; existing incomplete-trace, multi-step and identity tests |
| UE-5: operational failure distinctions | Runtime/timeout core vectors; existing no-grader, parser/static, invalid-input/trace and actual operation-budget tests; no execution-backed result inferred |
| UE-6: supported violation survives unknown; no unsupported success | New `violation_with_independent_unknown` canonical corpus; independent-violation runner tests; existing enforcement-unknown and failed-BASE schema negatives; qualification controls |
| UE-7: correct knowability interpretation | KNOWN-AND-VALUE is false while VALUE is unknown; KNOWN-IMPLIES-VALUE is vacuously true without an Exploration claim; old recipe removed and core links checked |
| Reuse binds the actual semantic contract | `test_core_semantic_revision_is_bound_to_result`; report identity hashes the new normative document |

## Review and test-first evidence

The first core test run failed because the normative section/linkage and explicit formula-result fields were absent. A later regression failed on the absent semantic-contract identity digest. Both passed after the corresponding changes. Existing truth computation already passed the new evidence tables; it was promoted into an explicit core contract, not presented as a newly discovered arithmetic bug.

A distinct self-review checked for weakening of BASE/ATT gates, conflation of UNKNOWN with failure, known-absent versus unobserved objects, failure hidden behind a true disjunction, vacuous knowability guards promoted to enforcement, stale semantic identities, and false claims that unchanged schemas imply unchanged conformance. The review retained the schema gates and explicit `not_checked` reporting, and added a major-release compatibility note. This was not an independent external audit.

## Reproduce

From the repository root, create a Python 3.12 environment and install the pinned test requirements, then run:

```sh
"$CFSE_VERIFY_ENV/bin/python" -B -m unittest discover -s tests -v
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B extensions/finite-trace/evaluate.py \
  --artifacts extensions/finite-trace/fixtures/artifacts.json \
  --config extensions/finite-trace/fixtures/bindings.json \
  --trace extensions/finite-trace/fixtures/trace.json
git diff --check
git diff e00bb89 -- 'spec/**/*.schema.yaml' VERSION
```

No evidence authentication, source/binary correspondence, theorem proof, ecosystem-wide evaluator compliance, or comparative reliability advantage is claimed. No model calls, historical study edits, release, or public push occurred.
