# Contract validation

The suite checks local JSON Schema definitions and references, the schema expectations of 42 synthetic corpus cases, and complete YAML examples in the artifact documentation. It also checks the public `cfse.ai` schema namespace and the Flow's `trigger.initial_interaction` field.

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

A compatible external validator can run all 42 cases in both YAML and Markdown frontmatter form. This repository does not distribute a semantic-validator executable or download one during CI.

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
