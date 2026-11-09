"""Canonical schema cases; the CLI consumes the same cases for semantic checks.

Set CFSE_CONTRACT_BINARY to run a compatible semantic validator in both
serializations. The default suite checks schemas; it does not parse logic or
validate cross-artifact evidence consistency.
"""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/contract/cases.json'
PREFIXES = {'C': 'concept', 'EP': 'entry_point', 'PRJ': 'prj',
            'I': 'interaction', 'F': 'flow', 'S': 'scenario',
            'E': 'exploration', 'FD': 'finding', 'P': 'predicate',
            'INV': 'invariant', 'GEN': 'generator', 'PATCH': 'patch',
            'T': 'trace'}


def corpus_for(data, case):
    corpus = copy.deepcopy(data['base'])
    corpus.update(case.get('replace', {}))
    corpus.update(case.get('add', {}))
    for name in case.get('remove', []):
        corpus.pop(name)
    return corpus


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        files = list((ROOT / 'spec').rglob('*.schema.yaml'))
        cls.schemas = {f.parent.name: yaml.safe_load(f.read_text()) for f in files}
        cls.registry = Registry().with_resources(
            (d['$id'], Resource.from_contents(d)) for d in cls.schemas.values())
        cls.data = json.loads(FIXTURES.read_text())

    def validator(self, kind):
        return Draft202012Validator(self.schemas[kind], registry=self.registry,
                                    format_checker=FormatChecker())

    def test_schemas_are_valid_and_references_resolve(self):
        def refs(obj):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    yield obj['$ref']
                for value in obj.values():
                    yield from refs(value)
            elif isinstance(obj, list):
                for value in obj:
                    yield from refs(value)
        identifiers = [schema['$id'] for schema in self.schemas.values()]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for schema in self.schemas.values():
            with self.subTest(schema=schema['$id']):
                self.assertTrue(schema['$id'].startswith('https://cfse.ai/schemas/'))
                Draft202012Validator.check_schema(schema)
                for ref in refs(schema):
                    self.registry.resolver(schema['$id']).lookup(ref)

    def test_canonical_schema_cases(self):
        for case in self.data['cases']:
            with self.subTest(case=case['name']):
                errors = []
                for name, obj in corpus_for(self.data, case).items():
                    kind = ('invariant_library' if 'predicates' in obj and
                            'invariants' in obj and 'id' not in obj else
                            PREFIXES[obj['id'].split('-')[0]])
                    errors.extend(f'{name}: {e.json_path}: {e.message}'
                                  for e in self.validator(kind).iter_errors(obj))
                self.assertEqual(not errors, case['schema_valid'], '\n'.join(errors))

    def test_complete_artifact_examples(self):
        checked = 0
        for path in (ROOT / 'spec/artifacts').rglob('*.md'):
            kind = path.parent.name
            for match in re.finditer(r'^```yaml\n(.*?)^```', path.read_text(), re.M | re.S):
                obj = yaml.safe_load(match.group(1))
                if not isinstance(obj, dict):
                    continue
                required = set(self.schemas[kind].get('required', []))
                if not required.issubset(obj):
                    continue  # field snippets are intentionally incomplete
                checked += 1
                with self.subTest(path=str(path.relative_to(ROOT)), id=obj.get('id')):
                    self.validator(kind).validate(obj)
        self.assertGreaterEqual(checked, 16)

    def test_public_flow_trigger_and_interaction_ids(self):
        path = ROOT / 'spec/artifacts/primary/flow/flow.md'
        examples = [yaml.safe_load(m.group(1)) for m in re.finditer(
            r'^```yaml\n(.*?)^```', path.read_text(), re.M | re.S)]
        flow = next(obj for obj in examples if isinstance(obj, dict)
                    and obj.get('id') == 'F-SHOP-CHECKOUT-001')
        self.validator('flow').validate(flow)
        self.assertIn('initial_interaction', flow['trigger'])
        obsolete = copy.deepcopy(flow)
        obsolete['trigger']['entry_point'] = obsolete['trigger'].pop('initial_interaction')
        self.assertFalse(self.validator('flow').is_valid(obsolete))
        for value, valid in [('I-SHOP-COLLECT-GUESTINFO-001', True),
                             ('I-SHOP-COLLECT-GUEST-INFO-001', False)]:
            candidate = copy.deepcopy(flow)
            candidate['trigger']['initial_interaction'] = value
            with self.subTest(interaction=value):
                self.assertEqual(self.validator('flow').is_valid(candidate), valid)

    @unittest.skipUnless(os.environ.get('CFSE_CONTRACT_BINARY'),
                         'set CFSE_CONTRACT_BINARY for optional semantic validation')
    def test_cli_shared_cases_yaml_and_frontmatter(self):
        for case in self.data['cases']:
            results = []
            for frontmatter in (False, True):
                with self.subTest(case=case['name'], frontmatter=frontmatter):
                    with tempfile.TemporaryDirectory() as tmp:
                        for name, obj in corpus_for(self.data, case).items():
                            body = yaml.safe_dump(obj, sort_keys=False)
                            suffix = '.md' if frontmatter else '.yaml'
                            if frontmatter:
                                body = '---\n' + body + '---\nReview notes.\n'
                            Path(tmp, name + suffix).write_text(body)
                        run = subprocess.run([os.environ['CFSE_CONTRACT_BINARY'],
                                              'validate', '--spec', str(ROOT),
                                              '--format', 'json', tmp],
                                             capture_output=True, text=True, timeout=30)
                    self.assertIn(run.returncode, (0, 1), run.stderr + run.stdout)
                    result = json.loads(run.stdout)
                    self.assertEqual(run.returncode == 0, case['valid'], run.stdout)
                    results.append(sorted(d['code'] for d in result['diagnostics']))
            self.assertEqual(results[0], results[1], case['name'])


if __name__ == '__main__':
    unittest.main()
