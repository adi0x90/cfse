# Contract validation

The suite checks local JSON Schema definitions and references, the schema expectations of 43 synthetic corpus cases, and complete YAML examples in the artifact documentation. It also checks the public `cfse.ai` schema namespace and the Flow's `trigger.initial_interaction` field.

Run from the repository root with Python 3.12:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -B -m unittest discover -s tests -v
```

The GitHub Actions workflow runs this same suite. It requires no research corpus, credentials, sibling checkout or private repository.

## What the fixtures mean

`fixtures/contract/cases.json` contains a base corpus and named mutations. `replace` replaces entire artifacts, `add` introduces artifacts, and `remove` removes named artifacts. Every ID, approval date and evidence statement is synthetic test data, not a research result.

Each case distinguishes:

- `schema_valid`: every artifact satisfies its JSON Schema, including format checks.
- `valid`: the corpus also satisfies the static reference, lifecycle, logic and evidence-consistency contract covered by these cases.

For example, `nonsense_logic` is schema-valid because its `logic` field is a string of the required length. It is semantically invalid. Other schema-valid negative cases include unbound variables, wrong predicate signatures, missing Findings, duplicate invariant identities with differing evidence, and incomplete enforcement coverage.

The default suite tests `schema_valid`. It deliberately skips semantic integration when no validator is supplied. A green schema CI run is **not** evidence that logic was parsed, references resolved, evidence authenticated or a security property proved.

## Optional semantic integration

A compatible external validator can run all 43 cases in both YAML and Markdown frontmatter form. This repository does not distribute a semantic-validator executable or download one during CI.

Supply an absolute path to a validator supporting this command interface:

```text
VALIDATOR validate --spec REPOSITORY_ROOT --format json CORPUS_DIRECTORY
```

The validator must load this checkout's schemas, return exit code 0 for valid cases and 1 for invalid cases, and emit a JSON object with `diagnostics` entries containing `code`. The integration test also checks that both serializations produce the same diagnostic codes.

```sh
CFSE_CONTRACT_BINARY=/absolute/path/to/validator \
  .venv/bin/python -B -m unittest discover -s tests -v
```

This integration tests the static contract only. Neither its success nor these synthetic fixtures establishes real approval, execution, evidence authenticity, temporal evaluation, exhaustive coverage or theorem proof. Extension payload semantics are outside this suite.

## Optional finite-trace profile tests

The same default suite also runs the [finite-trace profile](../extensions/finite-trace/README.md)
unit, adversarial and subprocess fixture tests. These execute the documented
subset with typed bindings; they do not replace the optional full-core validator
integration above. See the [criterion matrix](../extensions/finite-trace/VERIFICATION.md).

## Core uncertainty conformance

`fixtures/uncertainty/cases.json` is a portable, implementation-independent vector
set for `spec/semantics/06-evidence-evaluation.md`: 36 binary results, three unary
results, twelve composed formula/failure cases, and eight finite-domain cases.
T/F/U mean evidence of true/false/unresolved; they are not Predicate return types.
In the formula cases, `eligible` means eligibility for demonstrated formula
satisfaction and completed evaluation, not correctness at reporting uncertainty
and not confirmed enforcement. No extra logical relationships are supplied.

`test_core_uncertainty.py` checks the normative tables against the vectors and
runs them against the finite-trace adapter. It rejects deliberate broken controls
(default unknown to false, erase definite results with unknown, constant true,
constant false), distinguishes VALUE from KNOWN-AND-VALUE and a vacuous guard,
and checks that formula truth cannot masquerade as a core Exploration result.
The existing record-schema gates remain tested; the new canonical mixed-target
case retains a confirmed violation alongside an independently unknown target.
Cross-corpus semantic integration still requires `CFSE_CONTRACT_BINARY` and is
not claimed from schema acceptance.

Other evaluators can consume these vectors through their own adapters; the test
adapter's serialization and optional profile are not required by core. Implement
only supported operators, and report unsupported checks as `not_checked` rather
than passing or silently dropping vectors. These checks do not establish full
core conformance, evidence authenticity, or universal reliability.
