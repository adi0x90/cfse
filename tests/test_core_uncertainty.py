"""Core evidence requirements; the optional finite runner is one tested adapter.

The portable vectors and normative tables are independent of that adapter.
These tests do not establish full CFSE conformance or evidence authenticity.
"""
import copy
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from test_finite_trace import ft, PROFILE
import test_contract as contract_tests

ROOT = Path(__file__).resolve().parents[1]
VECTORS = json.loads((ROOT / 'tests/fixtures/uncertainty/cases.json').read_text())
VALUES = {'T': True, 'F': False, 'U': None}
TRUTHS = {'T': 'TRUE', 'F': 'FALSE', 'U': 'UNKNOWN'}


def assert_tables(test):
    for row in VECTORS['binary']:
        for op in ('AND', 'OR', 'IMPLIES', 'IFF'):
            actual = ft.combine(op, ft.Evidence(VALUES[row['a']]), ft.Evidence(VALUES[row['b']]))
            test.assertIs(actual.value, VALUES[row[op]], (op, row))
    for row in VECTORS['unary']:
        test.assertIs(ft.negate(ft.Evidence(VALUES[row['a']])).value, VALUES[row['NOT']])


class CoreUncertaintyTests(unittest.TestCase):
    def test_normative_tables_match_portable_vectors(self):
        path = ROOT / 'spec/semantics/06-evidence-evaluation.md'
        self.assertTrue(path.exists(), 'core evidence guarantees need a normative specification')
        text = path.read_text()
        rows = re.findall(r'^\| ([TFU]) \| ([TFU]) \| ([TFU]) \| ([TFU]) \| ([TFU]) \| ([TFU]) \|$', text, re.M)
        expected = [tuple(row[k] for k in ('a', 'b', 'AND', 'OR', 'IMPLIES', 'IFF')) for row in VECTORS['binary']]
        self.assertEqual(rows, expected)
        unary = re.findall(r'^\| ([TFU]) \| ([TFU]) \|$', text, re.M)
        self.assertEqual(unary, [(r['a'], r['NOT']) for r in VECTORS['unary']])

    def test_core_tables_against_reference_adapter(self):
        assert_tables(self)

    def test_conformance_vectors_reject_broken_evaluators(self):
        original = ft.combine
        def default_false(op, a, b):
            return original(op, ft.Evidence(False if a.value is None else a.value),
                            ft.Evidence(False if b.value is None else b.value))
        def lose_violation(op, a, b):
            return ft.Evidence(None) if a.value is None or b.value is None else original(op, a, b)
        for broken in [default_false, lose_violation,
                       lambda op, a, b: ft.Evidence(True),
                       lambda op, a, b: ft.Evidence(False)]:
            with patch.object(ft, 'combine', broken):
                with self.assertRaises(AssertionError):
                    assert_tables(self)

    def test_core_formulas_and_failure_eligibility_through_typed_runner(self):
        for case in VECTORS['formulas']:
            with self.subTest(case=case['name']):
                corpus, config, trace = [json.loads((PROFILE / ('fixtures/' + n + '.json')).read_text()) for n in ('artifacts', 'bindings', 'trace')]
                # Keep one invariant so the whole-task outcome matches this formula.
                corpus = [a for a in corpus if a['id'] != 'INV-DEMO-REQUEST']
                invariant = corpus[-1]
                body = re.sub(r'\bA\b', 'P-DEMO-ROLE(u, p)', case['logic'])
                body = re.sub(r'\bB\b', 'P-DEMO-AVAILABLE(j)', body)
                invariant['logic'] = 'FORALL u: C-DEMO-USER. FORALL p: C-DEMO-PROJECT. FORALL j: C-DEMO-JOB. ' + body
                for fact in trace['steps'][0]['facts']:
                    key = {'P-DEMO-ROLE':'a', 'P-DEMO-AVAILABLE':'b'}.get(fact['predicate'])
                    if key:
                        fact.update(value=VALUES[case[key]], state='unknown' if case[key] == 'U' else 'known',
                                    reason='Synthetic vector ' + case['name'] + ': ' + ('value unobserved' if case[key] == 'U' else 'value observed'))
                        if key == 'b' and 'failure' in case:
                            fact['state'] = case['failure']
                if case.get('omit_b'):
                    trace['steps'][0]['facts'] = [f for f in trace['steps'][0]['facts'] if f['predicate'] != 'P-DEMO-AVAILABLE']
                result = ft.evaluate(corpus, config, trace)
                self.assertEqual(result.get('truth'), TRUTHS[case['expected']])
                self.assertEqual(result['passed'], case['eligible'])
                self.assertEqual(result['reward'], int(case['eligible']))
                self.assertEqual(result.get('result_scope'), 'finite_formula')
                self.assertEqual(result.get('exploration_state'), 'not_checked')
                self.assertEqual(result['capabilities'].get('exploration_verdict'), 'not_checked')
                if case.get('failure'):
                    self.assertEqual(result['outcome'], case['failure'].upper())
                # Even a vacuously true knowability guard is no core HOLDS evidence.
                for item in result['invariants'].values():
                    self.assertEqual(item.get('exploration_state'), 'not_checked')

    def test_core_guidance_is_linked_and_old_recipe_removed(self):
        paths = ['spec/artifacts/supporting/predicate/predicate.md',
                 'spec/grammar/03-formal-logic.md', 'spec/semantics/01-invariant-states.md',
                 'spec/semantics/02-exploration-verdicts.md', 'spec/foundations/conformance.md']
        for path in paths:
            self.assertIn('06-evidence-evaluation.md', (ROOT / path).read_text(), path)
        text = (ROOT / paths[0]).read_text()
        self.assertNotIn('model it as `P-X-KNOWN AND P-X-VALUE`', text)
        self.assertIn('different proposition', text)

    def test_uncertainty_does_not_weaken_exploration_record_gates(self):
        contract_tests.ContractTests.setUpClass()
        contract = contract_tests.ContractTests()
        data = contract.data
        for name in ('confirmed_empty_observations', 'failed_baseline', 'blank_evidence',
                     'enforcement_unknown', 'violation_without_violated', 'blocked_claims_execution'):
            case = next(c for c in data['cases'] if c['name'] == name)
            exploration = contract_tests.corpus_for(data, case)['exploration']
            self.assertFalse(contract.validator('exploration').is_valid(exploration), name)
        self.assertEqual(contract.schemas['predicate']['properties']['returns']['const'], 'boolean')
        for case in data['cases']:
            if case['name'] == 'confirmed_violation':
                exploration = copy.deepcopy(contract_tests.corpus_for(data, case)['exploration'])
                exploration['observations']['delta']['invariant_states'].append(
                    {'invariant':'INV-TEST-OTHER', 'state':'UNKNOWN', 'evidence':'Independent property not observed.'})
                # Structural only; cross-target validity is tested in the canonical corpus below.
                self.assertTrue(contract.validator('exploration').is_valid(exploration))


    def test_core_finite_domain_vectors(self):
        for case in VECTORS['domains']:
            with self.subTest(case=case['name']):
                corpus, config, trace = [json.loads((PROFILE / ('fixtures/' + n + '.json')).read_text()) for n in ('artifacts', 'bindings', 'trace')]
                corpus = [a for a in corpus if a['id'] != 'INV-DEMO-REQUEST']
                corpus[-1]['logic'] = case['operator'] + ' j: C-DEMO-JOB. P-DEMO-AVAILABLE(j)'
                trace['domains']['C-DEMO-JOB'] = dict(members=case['members'], complete=case['complete'])
                fact = next(f for f in trace['steps'][0]['facts'] if f['predicate'] == 'P-DEMO-AVAILABLE')
                fact.update(value=VALUES[case['value']], state='unknown' if case['value'] == 'U' else 'known')
                trace['steps'][0]['facts'] = [fact] if case['members'] else []
                result = ft.evaluate(corpus, config, trace)
                self.assertEqual(result['truth'], TRUTHS[case['expected']])
                self.assertEqual(result['exploration_state'], 'not_checked')

    def test_core_semantic_revision_is_bound_to_result(self):
        import hashlib
        corpus, config, trace = [json.loads((PROFILE / ('fixtures/' + n + '.json')).read_text()) for n in ('artifacts', 'bindings', 'trace')]
        result = ft.evaluate(corpus, config, trace)
        expected = hashlib.sha256((ROOT / 'spec/semantics/06-evidence-evaluation.md').read_bytes()).hexdigest()
        self.assertEqual(result['identity'].get('evidence_contract'), expected)
