"""Public finite execution acceptance tests; no generated code is executed."""
import copy
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'extensions/finite-trace'
spec = importlib.util.spec_from_file_location('finite_trace', PROFILE / 'evaluate.py')
ft = importlib.util.module_from_spec(spec) if spec and spec.loader and (PROFILE / 'evaluate.py').exists() else None
if ft:
    sys.modules[spec.name] = ft
    spec.loader.exec_module(ft)


class FiniteTraceTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ft, 'finite-trace evaluator must be implemented')
        self.corpus = json.loads((PROFILE / 'fixtures/artifacts.json').read_text())
        self.config = json.loads((PROFILE / 'fixtures/bindings.json').read_text())
        self.trace = json.loads((PROFILE / 'fixtures/trace.json').read_text())

    def run_profile(self):
        return ft.evaluate(self.corpus, self.config, self.trace)

    def fact(self, predicate, **changes):
        row = next(r for r in self.trace['steps'][0]['facts'] if r['predicate'] == predicate)
        row.update(changes)
        return row

    def test_false_pass_regression(self):
        expected_delivery, actual_delivery = None, False
        verdict = True
        if expected_delivery is None:
            if actual_delivery:
                verdict = None
        self.assertIs(verdict, True, 'reproduces generated comparator bug, not a CFSE core bug')
        for actual in (False, True):
            self.fact('P-DEMO-AVAILABLE', state='unknown', reason='availability not observed', value=None)
            self.fact('P-DEMO-DELIVERED', value=actual)
            result = self.run_profile()
            self.assertEqual((result['state'], result['reward'], result['passed']), ('UNKNOWN', 0, False))

    def test_truth_tables(self):
        vals = [True, False, None]
        for a, b in itertools.product(vals, repeat=2):
            ea, eb = ft.Evidence(a), ft.Evidence(b)
            expected_and = False if a is False or b is False else True if a is True and b is True else None
            expected_or = True if a is True or b is True else False if a is False and b is False else None
            expected_iff = None if a is None or b is None else a == b
            expected_implies = True if a is False or b is True else False if a is True and b is False else None
            for op, expected in [('AND', expected_and), ('OR', expected_or), ('IFF', expected_iff), ('IMPLIES', expected_implies)]:
                self.assertIs(ft.combine(op, ea, eb).value, expected, (op, a, b))
            self.assertIs(ft.negate(ea).value, None if a is None else not a)
        with self.assertRaises(TypeError):
            bool(ft.Evidence(None))
        with self.assertRaises(ValueError):
            ft.Evidence(1)

    def test_benign_reuse_and_capabilities(self):
        result = self.run_profile()
        self.assertEqual((result['state'], result['reward'], result['passed']), ('HOLDS', 1, True))
        self.assertEqual(set(result['invariants']), {'INV-DEMO-REQUEST', 'INV-DEMO-DELIVERY'})
        for r in result['invariants'].values():
            self.assertEqual(r['bindings']['P-DEMO-ROLE'], '1.0.0')
        self.assertEqual(result['capabilities']['authenticity'], 'not_checked')
        self.assertEqual(result['capabilities']['proof'], 'not_checked')

    def test_independent_violation_survives_missing(self):
        self.fact('P-DEMO-AVAILABLE', state='unknown', value=None, reason='not observed')
        self.fact('P-DEMO-REQUESTED', value=False)
        result = self.run_profile()
        self.assertEqual((result['state'], result['reward']), ('VIOLATED', 0))
        self.assertEqual(result['invariants']['INV-DEMO-DELIVERY']['state'], 'UNKNOWN')

    def test_static_diagnostics(self):
        original = self.corpus[-1]['logic']
        cases = [
            ('P-DEMO-ROLE(u)', 'ARITY'),
            ('P-DEMO-ROLE(p, u)', 'ARGUMENT_TYPE'),
            ('P-DEMO-ROLE(missing, p)', 'UNBOUND_VARIABLE'),
            ('P-DEMO-MISSING(u, p)', 'UNRESOLVED_REFERENCE'),
            ('ALWAYS P-DEMO-ROLE(u, p)', 'UNSUPPORTED_OPERATOR'),
            ('P-DEMO-ROLE(user=u, user=p)', 'ARGUMENT_NAMES'),
            ('P-DEMO-ROLE(user=u, p)', 'ARGUMENT_NAMES'),
            ('P-DEMO-ROLE(u.id, p)', 'UNSUPPORTED_VALUE'),
            ('(P-DEMO-ROLE(u,p)', 'PARSE_ERROR'),
        ]
        for expression, code in cases:
            self.corpus[-1]['logic'] = 'FORALL u: C-DEMO-USER. FORALL p: C-DEMO-PROJECT. ' + expression
            with self.subTest(code=code):
                r = self.run_profile()
                self.assertEqual(r['diagnostics'][0]['code'], code)
                self.assertFalse(r['passed'])
                self.assertIn('path', r['diagnostics'][0])
        self.corpus[-1]['logic'] = original

    def test_named_arguments_and_precedence(self):
        self.corpus[-1]['logic'] = self.corpus[-1]['logic'].replace('P-DEMO-ROLE(u, p)', 'P-DEMO-ROLE(project=p, user=u)')
        self.assertTrue(self.run_profile()['passed'])
        self.corpus[-1]['logic'] = 'false AND true OR true IMPLIES false IFF false'
        self.corpus[-1]['predicates'] = ['P-DEMO-ROLE']
        self.assertTrue(self.run_profile()['passed'])
        self.corpus[-1]['logic'] = '!false && true || false => false <=> false'
        self.assertTrue(self.run_profile()['passed'])

    def test_dependency_cycle_and_assumption(self):
        self.corpus[-1]['dependencies'] = ['INV-DEMO-REQUEST']
        self.fact('P-DEMO-REQUESTED', value=False)
        r = self.run_profile()
        self.assertEqual(r['invariants']['INV-DEMO-DELIVERY']['state'], 'UNKNOWN')
        self.assertEqual(r['state'], 'VIOLATED')
        self.corpus[-2]['dependencies'] = ['INV-DEMO-DELIVERY']
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'DEPENDENCY_CYCLE')

    def test_identity_changes_invalidate_reuse(self):
        old = self.run_profile()
        for target, key, value in [(self.config, 'policy_version', '2.0.0'),
                                   (self.config, 'scope', 'another-project')]:
            before = target[key]
            target[key] = value
            self.assertFalse(ft.reusable(old, self.corpus, self.config, self.trace))
            target[key] = before
        self.config['bindings']['P-DEMO-ROLE']['version'] = '2.0.0'
        self.assertFalse(ft.reusable(old, self.corpus, self.config, self.trace))
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'BINDING_VERSION')

    def test_domains_and_trace_completeness(self):
        self.trace['domains']['C-DEMO-USER']['complete'] = False
        self.assertEqual(self.run_profile()['state'], 'UNKNOWN')
        self.fact('P-DEMO-REQUESTED', value=False)
        self.assertEqual(self.run_profile()['state'], 'VIOLATED')
        self.trace['domains']['C-DEMO-USER'] = {'members': [], 'complete': True}
        self.trace['steps'][0]['facts'] = []
        self.assertEqual(self.run_profile()['state'], 'HOLDS')
        self.trace['complete'] = False
        self.assertEqual(self.run_profile()['state'], 'UNKNOWN')

    def test_absent_missing_invalid_and_operational_outcomes(self):
        self.fact('P-DEMO-AVAILABLE', state='absent', value=False, reason='artifact confirmed absent')
        self.fact('P-DEMO-DELIVERED', value=False)
        self.assertTrue(self.run_profile()['passed'])
        self.trace['steps'][0]['facts'] = [r for r in self.trace['steps'][0]['facts'] if r['predicate'] != 'P-DEMO-AVAILABLE']
        self.assertEqual(self.run_profile()['outcome'], 'UNKNOWN')
        self.fact('P-DEMO-DELIVERED', value='false')
        self.assertEqual(self.run_profile()['outcome'], 'INVALID_TRACE')

    def test_failures_are_not_rewards(self):
        for state, outcome in [('runtime_error', 'RUNTIME_ERROR'), ('timeout', 'TIMEOUT')]:
            self.fact('P-DEMO-AVAILABLE', state=state, value=None, reason='synthetic adapter failure')
            r = self.run_profile()
            self.assertEqual((r['outcome'], r['reward'], r['passed']), (outcome, 0, False))
        self.config['bindings'].pop('P-DEMO-AVAILABLE')
        self.assertEqual(self.run_profile()['outcome'], 'NO_GRADER')

    def test_budget(self):
        self.config['max_operations'] = 1
        r = self.run_profile()
        self.assertEqual((r['outcome'], r['reward'], r['passed']), ('TIMEOUT', 0, False))

    def test_degenerate_qualification_controls(self):
        expected = ['HOLDS', 'VIOLATED', 'UNKNOWN']
        good = [dict(state=s, outcome=s, reward=int(s == 'HOLDS'), passed=s == 'HOLDS') for s in expected]
        self.assertTrue(ft.qualify(good, expected)['qualified'])
        for outcome in ['HOLDS', 'VIOLATED', 'UNKNOWN', 'RUNTIME_ERROR']:
            rows = [dict(state=outcome if outcome != 'RUNTIME_ERROR' else 'UNKNOWN', outcome=outcome,
                         reward=int(outcome == 'HOLDS'), passed=outcome == 'HOLDS')] * 3
            self.assertFalse(ft.qualify(rows, expected)['qualified'], outcome)


class AdversarialTests(unittest.TestCase):
    setUp = FiniteTraceTests.setUp
    run_profile = FiniteTraceTests.run_profile
    fact = FiniteTraceTests.fact

    def test_exhaustive_synthetic_decisions(self):
        # Independent truth oracle across 36 role/availability/decision combinations.
        def land(a, b):
            if a is False or b is False:
                return False
            return None if a is None or b is None else True
        def iff(a, b):
            return None if a is None or b is None else a == b
        for role, available, requested, delivered in itertools.product([True, False, None], [True, False, None], [True, False], [True, False]):
            for pid, value in [('ROLE', role), ('AVAILABLE', available), ('REQUESTED', requested), ('DELIVERED', delivered)]:
                self.fact('P-DEMO-' + pid, state='unknown' if value is None else 'known', value=value)
            expected = land(iff(requested, role), iff(delivered, land(role, available)))
            r = self.run_profile()
            self.assertEqual((r['state'], r['reward'], r['passed']),
                             ({True:'HOLDS', False:'VIOLATED', None:'UNKNOWN'}[expected], int(expected is True), expected is True),
                             (role, available, requested, delivered))

    def test_exists_on_incomplete_domains(self):
        self.corpus[-1]['logic'] = 'EXISTS j: C-DEMO-JOB. P-DEMO-AVAILABLE(j)'
        self.trace['domains']['C-DEMO-JOB']['complete'] = False
        self.assertTrue(self.run_profile()['passed'])
        self.fact('P-DEMO-AVAILABLE', value=False)
        self.assertEqual(self.run_profile()['state'], 'UNKNOWN')
        self.trace['domains']['C-DEMO-JOB']['complete'] = True
        self.assertEqual(self.run_profile()['state'], 'VIOLATED')

    def test_invariant_order_cannot_mask_violation(self):
        self.fact('P-DEMO-AVAILABLE', state='unknown', value=None)
        self.fact('P-DEMO-REQUESTED', value=False)
        self.corpus[-2:] = self.corpus[-2:][::-1]
        self.assertEqual(self.run_profile()['state'], 'VIOLATED')

    def test_schema_and_binding_drift(self):
        pid = 'P-DEMO-ROLE'
        predicate = next(a for a in self.corpus if a['id'] == pid)
        predicate['returns'] = 'tristate'
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'SCHEMA_ERROR')
        predicate['returns'] = 'boolean'
        predicate['definition'] += ' Changed.'
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'BINDING_ARTIFACT')
        self.config['bindings'][pid]['predicate_digest'] = ft.digest(predicate)
        self.config['bindings'][pid]['parameters'] = self.config['bindings'][pid]['parameters'][::-1]
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'BINDING_SIGNATURE')

    def test_forged_scope_malformed_and_duplicate_observations(self):
        original = copy.deepcopy(self.trace)
        self.trace['scope'] = 'other'
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'SCOPE')
        self.trace = copy.deepcopy(original)
        self.trace['steps'][0]['facts'].append(copy.deepcopy(self.trace['steps'][0]['facts'][0]))
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'DUPLICATE_OBSERVATION')
        self.trace = copy.deepcopy(original)
        for invalid in [None, 0, 1, 'true', [], {}]:
            self.fact('P-DEMO-ROLE', value=invalid)
            r = self.run_profile()
            self.assertEqual((r['outcome'], r['reward'], r['passed']), ('INVALID_TRACE', 0, False))
        self.trace = copy.deepcopy(original)
        self.fact('P-DEMO-ROLE', state='absent', value=False)
        self.assertEqual(self.run_profile()['diagnostics'][0]['code'], 'ABSENCE_CONTRACT')

    def test_real_engine_qualification_controls(self):
        expected = ['HOLDS', 'VIOLATED', 'UNKNOWN']
        traces = [copy.deepcopy(self.trace) for _ in expected]
        next(f for f in traces[1]['steps'][0]['facts'] if f['predicate'] == 'P-DEMO-DELIVERED')['value'] = False
        next(f for f in traces[2]['steps'][0]['facts'] if f['predicate'] == 'P-DEMO-AVAILABLE').update(state='unknown', value=None)
        def run(corpus, controls):
            return [ft.evaluate(corpus, self.config, trace) for trace in controls]
        self.assertTrue(ft.qualify(run(self.corpus, traces), expected)['qualified'])
        for constant in ('true', 'false'):
            corpus = copy.deepcopy(self.corpus)
            for artifact in corpus[-2:]:
                artifact['logic'] = f'{constant} AND {constant}'
            self.assertFalse(ft.qualify(run(corpus, traces), expected)['qualified'])
        for state in ('unknown', 'runtime_error'):
            controls = copy.deepcopy(traces)
            for trace in controls:
                for fact in trace['steps'][0]['facts']:
                    fact.update(state=state, value=None)
            self.assertFalse(ft.qualify(run(self.corpus, controls), expected)['qualified'])

    def test_parser_rejection_and_scope_controls(self):
        for logic, code in [
            ('FORALL u: C-DEMO-USER. FORALL u: C-DEMO-USER. true', 'SHADOWED_VARIABLE'),
            ('true IFF false IFF true', 'PARSE_ERROR'),
            ('true LEADS_TO false', 'UNSUPPORTED_OPERATOR'),
            ('FORALL u: C-DEMO-NOPE. true', 'UNRESOLVED_REFERENCE'),
            ('__import__("os")', 'PARSE_ERROR'),
        ]:
            self.corpus[-1]['logic'] = logic
            self.assertEqual(self.run_profile()['diagnostics'][0]['code'], code)

    def test_multistep_failure_and_identity(self):
        old = self.run_profile()
        step = copy.deepcopy(self.trace['steps'][0])
        step['id'] = 'decision-2'
        next(f for f in step['facts'] if f['predicate'] == 'P-DEMO-DELIVERED')['value'] = False
        self.trace['steps'].append(step)
        self.assertEqual(self.run_profile()['state'], 'VIOLATED')
        self.assertFalse(ft.reusable(old, self.corpus, self.config, self.trace))

    def test_failure_cannot_be_hidden_by_known_true_disjunction(self):
        self.corpus[-1]['logic'] = 'FORALL j: C-DEMO-JOB. true OR P-DEMO-AVAILABLE(j)'
        self.fact('P-DEMO-AVAILABLE', state='runtime_error', value=None)
        r = self.run_profile()
        self.assertEqual((r['state'], r['outcome'], r['reward'], r['passed']), ('HOLDS', 'RUNTIME_ERROR', 0, False))


    def test_reject_trailing_comma_and_report_completed_schema_check(self):
        self.corpus[-1]['logic'] = 'FORALL u: C-DEMO-USER. FORALL p: C-DEMO-PROJECT. P-DEMO-ROLE(u, p,)'
        r = self.run_profile()
        self.assertEqual(r['outcome'], 'PARSE_ERROR')
        self.assertEqual(r['capabilities']['schema'], 'passed')
        self.assertEqual(r['capabilities']['static_logic'], 'failed')

    def test_implementation_hint_is_never_executed(self):
        pid = 'P-DEMO-ROLE'
        predicate = next(a for a in self.corpus if a['id'] == pid)
        predicate['implementation'] = {'language': 'python', 'code': 'raise RuntimeError("MUST NOT EXECUTE")'}
        self.config['bindings'][pid]['predicate_digest'] = ft.digest(predicate)
        self.assertTrue(self.run_profile()['passed'])


class TraceabilityExamples(unittest.TestCase):
    def test_summary_and_validation_paths(self):
        import re
        import yaml
        text = (ROOT / 'spec/semantics/04-traceability.md').read_text()
        self.assertNotIn('exploration_refs', text)
        block = next(yaml.safe_load(s) for s in re.findall(r'```yaml\n(.*?)```', text, re.S) if 'TraceabilityValidation:' in s)
        rules = block['TraceabilityValidation']['rules']
        self.assertEqual(rules['TR-3']['field'], 'targeted_invariants')
        self.assertEqual(rules['TR-1']['fields'], ['traceability.exploration', 'evidence[type=exploration].reference'])
        self.assertEqual(rules['TR-5']['field'], 'finding_ref.finding_id')

    def test_tr5_valid_fragment_against_actual_schema(self):
        import re
        import yaml
        from jsonschema import Draft202012Validator
        text = (ROOT / 'spec/semantics/04-traceability.md').read_text()
        block = re.search(r'# Valid: Single finding reference\n(.*?)\n# INVALID:', text, re.S).group(1)
        ref = yaml.safe_load(block)['patch']['finding_ref']
        docs, registry = ft.schemas()
        validator = Draft202012Validator({'$ref': docs['patch']['$id'] + '#/$defs/FindingReference'}, registry=registry)
        self.assertTrue(validator.is_valid(ref), list(validator.iter_errors(ref)))
        self.assertFalse(validator.is_valid('FD-OJS-AUTHZ-001'))


class CommandLineTests(unittest.TestCase):
    def test_public_fixtures_end_to_end(self):
        cases = json.loads((PROFILE / 'fixtures/cases.json').read_text())
        for case in cases:
            with self.subTest(case=case['name']), tempfile.TemporaryDirectory() as directory:
                corpus, config, trace = [json.loads((PROFILE / ('fixtures/' + name + '.json')).read_text()) for name in ('artifacts', 'bindings', 'trace')]
                for fact in trace['steps'][0]['facts']:
                    if fact['predicate'] in case.get('facts', {}):
                        fact.update(case['facts'][fact['predicate']])
                        fact['reason'] = 'synthetic case: ' + case['name']
                if 'max_operations' in case:
                    config['max_operations'] = case['max_operations']
                if 'remove_binding' in case:
                    config['bindings'].pop(case['remove_binding'])
                if 'logic' in case:
                    corpus[-1]['logic'] = case['logic']
                args = []
                for name, obj in [('artifacts', corpus), ('config', config), ('trace', trace)]:
                    path = Path(directory) / (name + '.json')
                    path.write_text(json.dumps(obj))
                    args.extend(['--' + name, str(path)])
                run = subprocess.run([sys.executable, '-B', str(PROFILE / 'evaluate.py'), *args], capture_output=True, text=True, timeout=10)
                result = json.loads(run.stdout)
                self.assertEqual(run.stderr, '')
                self.assertEqual(run.returncode, 0 if case['passed'] else 1)
                for key in ('outcome', 'reward', 'passed'):
                    self.assertEqual(result[key], case[key])

    def test_invalid_json_and_input_limit(self):
        for data in ['{"id":1,"id":2}', '{broken', '[' * 1500, ' ' * (ft.MAX_BYTES + 1)]:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'input.json'
                path.write_text(data)
                run = subprocess.run([sys.executable, '-B', str(PROFILE / 'evaluate.py'), '--artifacts', str(path), '--config', str(path), '--trace', str(path)], capture_output=True, text=True, timeout=10)
                result = json.loads(run.stdout)
                self.assertEqual((result['outcome'], result['reward'], result['passed']), ('INVALID_INPUT', 0, False))


if __name__ == '__main__':
    unittest.main()
