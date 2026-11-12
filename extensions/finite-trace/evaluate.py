"""Opt-in finite-trace reference profile. Data only: never eval/exec candidate code."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
PROFILE = 'cfse-finite-trace/1'
CORE_REVISION = '34575b9191c6a457faf669e505abac9af2e6dd2a'
MAX_BYTES = 1_000_000


class Diagnostic(Exception):
    def __init__(self, code, message, path='$', outcome='STATIC_ERROR'):
        self.code, self.message, self.path, self.outcome = code, message, path, outcome
        super().__init__(message)

    def as_dict(self):
        return dict(code=self.code, message=self.message, path=self.path)


@dataclass(frozen=True)
class Evidence:
    value: bool | None
    reasons: tuple[str, ...] = ()
    observations: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()

    def __post_init__(self):
        if self.value is not None and type(self.value) is not bool:
            raise ValueError('evidence is an exact Boolean or unobserved, never truthiness')

    def __bool__(self):
        raise TypeError('Evidence has no Python truthiness; inspect value explicitly')


def unique(items):
    return tuple(dict.fromkeys(items))


def negate(a):
    return Evidence(None if a.value is None else not a.value, a.reasons, a.observations, a.failures)


def combine(op, a, b):
    x, y = a.value, b.value
    if op == 'AND':
        v = False if x is False or y is False else True if x is True and y is True else None
    elif op == 'OR':
        v = True if x is True or y is True else False if x is False and y is False else None
    elif op == 'IFF':
        v = None if x is None or y is None else x == y
    elif op == 'IMPLIES':
        return combine('OR', negate(a), b)
    else:
        raise ValueError(f'unsupported operation {op}')
    return Evidence(v, unique(a.reasons + b.reasons), unique(a.observations + b.observations),
                    unique(a.failures + b.failures))


ALIASES = {'!': 'NOT', '&&': 'AND', '||': 'OR', '=>': 'IMPLIES', '<=>': 'IFF'}
PRECEDENCE = {'IFF': 1, 'IMPLIES': 2, 'OR': 3, 'AND': 4}
UNSUPPORTED = {'ALWAYS', 'EVENTUALLY', 'LEADS_TO', '[]', '<>', '~>',
               'CREATE', 'READ', 'UPDATE', 'DELETE', 'ACCESS', 'EXECUTE', 'ASSUME', 'GRANT', 'REVOKE'}
TOKEN = re.compile(r'\s+|<=>|=>|&&|\|\||\[\]|<>|~>|[A-Za-z][A-Za-z0-9_-]*|[():.,=!]|\S')


class Parser:
    """Checked subset of the pinned EBNF, with its precedence and quantifier scope."""
    def __init__(self, text, artifacts, path):
        self.tokens = [(ALIASES.get(m.group(), m.group()), m.start()) for m in TOKEN.finditer(text)
                       if not m.group().isspace()]
        self.i, self.artifacts, self.path, self.used = 0, artifacts, path, set()
        if len(self.tokens) > 512:
            self.fail('LIMIT', 'at most 512 tokens per expression')

    def fail(self, code, message):
        pos = self.tokens[self.i][1] if self.i < len(self.tokens) else 'end'
        raise Diagnostic(code, message, f'{self.path}@{pos}', 'PARSE_ERROR' if code == 'PARSE_ERROR' else 'STATIC_ERROR')

    def peek(self):
        return self.tokens[self.i][0] if self.i < len(self.tokens) else ''

    def take(self, expected=None):
        t = self.peek()
        if not t or expected is not None and t != expected:
            self.fail('PARSE_ERROR', f'expected {expected or "token"}; got {t or "end"}')
        self.i += 1
        return t

    def parse(self):
        node = self.expression({}, 1, 0)
        if self.peek():
            self.fail('UNSUPPORTED_OPERATOR' if self.peek() in UNSUPPORTED else 'PARSE_ERROR',
                      f'unexpected {self.peek()}; use supported Boolean operators')
        return node

    def expression(self, env, minimum, depth):
        if depth > 48:
            self.fail('LIMIT', 'at most 48 nested expressions')
        token = self.peek()
        if token in UNSUPPORTED:
            self.fail('UNSUPPORTED_OPERATOR', f'{token} is not supported; bind observed decisions as typed predicates')
        if token == 'NOT':
            self.take()
            left = ('NOT', self.expression(env, 5, depth + 1))
        elif token in ('FORALL', 'EXISTS'):
            op = self.take()
            name = self.take()
            if not re.fullmatch('[a-z][a-z0-9_]*', name):
                self.fail('PARSE_ERROR', 'quantifier requires lowercase variable')
            if name in env:
                self.fail('SHADOWED_VARIABLE', f'{name} already bound; use another variable')
            self.take(':')
            domain = self.take()
            if domain not in self.artifacts or not domain.startswith('C-'):
                self.fail('UNRESOLVED_REFERENCE', f'{domain} must resolve to a Concept; primitive domains unsupported')
            self.take('.')
            left = (op, name, domain, self.expression({**env, name: domain}, 1, depth + 1))
        elif token == '(':
            self.take()
            left = self.expression(env, 1, depth + 1)
            self.take(')')
        elif token in ('true', 'false'):
            left = ('CONST', self.take() == 'true')
        elif token.startswith('P-'):
            pid = self.take()
            if pid not in self.artifacts:
                self.fail('UNRESOLVED_REFERENCE', f'predicate {pid} not found')
            params = self.artifacts[pid]['parameters']
            self.take('(')
            args, names = [], []
            while self.peek() != ')':
                name = self.take()
                if self.peek() == '=':
                    self.take()
                    names.append(name)
                    name = self.take()
                else:
                    names.append(None)
                if self.peek() == '.' or not re.fullmatch('[a-z][a-z0-9_]*', name):
                    self.fail('UNSUPPORTED_VALUE', 'only bound Concept variables are supported as arguments')
                if name not in env:
                    self.fail('UNBOUND_VARIABLE', f'{name} has no enclosing quantifier')
                args.append(name)
                if self.peek() != ',':
                    break
                self.take()
                if self.peek() == ')':
                    self.fail('PARSE_ERROR', 'trailing comma is not an argument')
            self.take(')')
            if any(n is not None for n in names):
                expected = [p['name'] for p in params]
                if None in names or len(set(names)) != len(names) or set(names) != set(expected):
                    self.fail('ARGUMENT_NAMES', f'use exactly these names: {expected}, or positional arguments')
                args = [args[names.index(n)] for n in expected]
            if len(args) != len(params):
                self.fail('ARITY', f'{pid} requires {len(params)} arguments')
            for arg, param in zip(args, params):
                if env[arg] != param['type']:
                    self.fail('ARGUMENT_TYPE', f'{param["name"]} expects {param["type"]}, got {env[arg]}')
            self.used.add(pid)
            left = ('CALL', pid, args)
        else:
            self.fail('PARSE_ERROR', f'expected predicate, quantifier or Boolean; got {token or "end"}')
        seen_iff = False
        while self.peek() in PRECEDENCE and PRECEDENCE[self.peek()] >= minimum:
            op = self.take()
            if op == 'IFF' and seen_iff:
                self.fail('PARSE_ERROR', 'IFF is non-associative; parenthesize')
            seen_iff |= op == 'IFF'
            right = self.expression(env, PRECEDENCE[op] + (op != 'IMPLIES'), depth + 1)
            left = (op, left, right)
        return left


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=1)
def schemas():
    docs = [yaml.safe_load(p.read_text()) for p in sorted((ROOT / 'spec').rglob('*.schema.yaml'))]
    registry = Registry().with_resources((d['$id'], Resource.from_contents(d)) for d in docs)
    return {d['$id'].rsplit('/', 1)[-1].split('.')[0]: d for d in docs}, registry


def schema_digest():
    return digest({str(p.relative_to(ROOT)): p.read_text() for p in sorted((ROOT / 'spec').rglob('*.schema.yaml'))})


def identity(corpus, config, trace):
    return {'profile': PROFILE, 'core_revision': CORE_REVISION, 'schemas': schema_digest(),
            'engine': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'evidence_contract': hashlib.sha256((ROOT / 'spec/semantics/06-evidence-evaluation.md').read_bytes()).hexdigest(),
            'artifacts': digest(corpus), 'configuration': digest(config), 'trace': digest(trace)}


def reusable(result, corpus, config, trace):
    """Equality of declared inputs only; NOT authentication of a supplied result."""
    return result.get('identity') == identity(corpus, config, trace)


def require(condition, code, message, path='$', outcome='STATIC_ERROR'):
    if not condition:
        raise Diagnostic(code, message, path, outcome)


def object_keys(obj, required, optional=(), path='$', outcome='STATIC_ERROR'):
    require(isinstance(obj, dict) and set(required) <= set(obj) <= set(required) | set(optional),
            'INPUT_SHAPE', f'expected fields {required}; optional {optional}', path, outcome)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def compile_corpus(corpus, config, capabilities):
    require(isinstance(corpus, list) and 0 < len(corpus) <= 128, 'CORPUS', 'expected 1..128 artifacts')
    docs, registry = schemas()
    artifacts = {}
    for i, artifact in enumerate(corpus):
        path = f'$.artifacts[{i}]'
        require(isinstance(artifact, dict) and isinstance(artifact.get('id'), str), 'SCHEMA_ERROR', 'artifact needs ID', path)
        aid = artifact['id']
        kind = {'C': 'concept', 'P': 'predicate', 'INV': 'invariant', 'EP': 'entry_point'}.get(aid.split('-')[0])
        require(kind is not None, 'UNSUPPORTED_ARTIFACT', aid, path)
        errors = list(Draft202012Validator(docs[kind], registry=registry, format_checker=FormatChecker()).iter_errors(artifact))
        require(not errors, 'SCHEMA_ERROR', str(errors[0].message) if errors else '', path)
        require(aid not in artifacts, 'DUPLICATE_ID', aid, path)
        require(not artifact.get('extensions'), 'UNSUPPORTED_EXTENSION', 'extension payloads not checked by this profile', path)
        artifacts[aid] = artifact
    capabilities['schema'] = 'passed'
    for aid, a in artifacts.items():
        refs = []
        if aid.startswith('C-'):
            refs = a['entry_points'] + a['invariants']
        elif aid.startswith('EP-'):
            refs = [a['owner_concept']] if 'owner_concept' in a else []
        elif aid.startswith('P-'):
            names = [p['name'] for p in a['parameters']]
            require(len(names) == len(set(names)), 'SIGNATURE', 'duplicate parameter name', aid)
            refs = [p['type'] for p in a['parameters']]
            require(all(t.startswith('C-') for t in refs), 'UNSUPPORTED_TYPE', 'profile supports Concept parameters only', aid)
        elif aid.startswith('INV-'):
            refs = a['predicates'] + a.get('dependencies', [])
        for ref in refs:
            require(ref in artifacts, 'UNRESOLVED_REFERENCE', ref, aid)
    object_keys(config, ['profile', 'scope', 'policy_version', 'bindings', 'max_operations'])
    require(config['profile'] == PROFILE, 'PROFILE', 'unsupported profile')
    require(nonblank(config['scope']) and nonblank(config['policy_version']), 'CONFIG', 'scope and policy version required')
    require(type(config['max_operations']) is int and 1 <= config['max_operations'] <= 100000, 'CONFIG', 'operation budget must be 1..100000')
    require(isinstance(config['bindings'], dict), 'CONFIG', 'bindings must be an object')
    for pid, binding in config['bindings'].items():
        require(pid in artifacts and pid.startswith('P-'), 'UNRESOLVED_REFERENCE', pid)
        object_keys(binding, ['version', 'adapter', 'parameters', 'predicate_digest', 'review', 'absent_is_false'], path=pid)
        require(binding['adapter'] == 'boolean-table/1', 'UNSUPPORTED_BINDING', 'only boolean-table/1 is implemented', pid)
        require(nonblank(binding['version']) and nonblank(binding['review']), 'BINDING_REVIEW', 'version and correspondence review required', pid)
        require(type(binding['absent_is_false']) is bool, 'CONFIG', 'absent_is_false must be Boolean', pid)
        require(binding['parameters'] == artifacts[pid]['parameters'], 'BINDING_SIGNATURE', 'binding signature differs from predicate', pid)
        require(binding['predicate_digest'] == digest(artifacts[pid]), 'BINDING_ARTIFACT', 'predicate changed; review and rebind', pid)
    trees, uses = {}, {}
    for aid, a in artifacts.items():
        if not aid.startswith('INV-'):
            continue
        parser = Parser(a['logic'], artifacts, aid + '.logic')
        trees[aid] = parser.parse()
        uses[aid] = parser.used
        require(parser.used <= set(a['predicates']), 'UNLISTED_PREDICATE', 'logic predicate missing from predicates list', aid)
        for pid in parser.used:
            require(pid in config['bindings'], 'NO_GRADER', f'no binding for {pid}', aid, 'NO_GRADER')
    require(bool(trees), 'NO_GRADER', 'no invariants supplied', outcome='NO_GRADER')
    order, active = [], set()
    def visit(aid):
        require(aid not in active, 'DEPENDENCY_CYCLE', aid)
        if aid in order:
            return
        active.add(aid)
        for dep in artifacts[aid].get('dependencies', []):
            visit(dep)
        active.remove(aid)
        order.append(aid)
    for aid in trees:
        visit(aid)
    return artifacts, trees, uses, order


def validate_trace(trace, config, artifacts):
    outcome = 'INVALID_TRACE'
    def check(cond, code, msg, path='$'):
        require(cond, code, msg, path, outcome)
    object_keys(trace, ['id', 'scope', 'complete', 'domains', 'steps'], outcome=outcome)
    check(nonblank(trace['id']), 'TRACE_ID', 'trace identity required')
    check(trace['scope'] == config['scope'], 'SCOPE', 'trace/configuration scope mismatch')
    check(type(trace['complete']) is bool, 'COMPLETENESS', 'complete must be Boolean')
    check(isinstance(trace['domains'], dict), 'DOMAINS', 'domains must be an object')
    for cid, domain in trace['domains'].items():
        check(cid in artifacts and cid.startswith('C-'), 'UNRESOLVED_REFERENCE', cid)
        object_keys(domain, ['members', 'complete'], path=cid, outcome=outcome)
        check(type(domain['complete']) is bool, 'COMPLETENESS', 'domain complete must be Boolean', cid)
        members = domain['members']
        check(isinstance(members, list) and len(members) <= 128 and all(nonblank(x) for x in members), 'DOMAIN_MEMBERS', 'up to 128 nonempty identifiers', cid)
        check(len(members) == len(set(members)), 'DOMAIN_MEMBERS', 'duplicate member', cid)
    check(isinstance(trace['steps'], list) and 1 <= len(trace['steps']) <= 256, 'STEPS', '1..256 steps required')
    tables, step_ids = [], set()
    for i, step in enumerate(trace['steps']):
        path = f'$.steps[{i}]'
        object_keys(step, ['id', 'facts'], path=path, outcome=outcome)
        check(nonblank(step['id']) and step['id'] not in step_ids, 'STEP_ID', 'unique step ID required', path)
        step_ids.add(step['id'])
        check(isinstance(step['facts'], list), 'FACTS', 'facts must be an array', path)
        table = {}
        for j, fact in enumerate(step['facts']):
            fp = f'{path}.facts[{j}]'
            object_keys(fact, ['predicate', 'binding_version', 'args', 'state', 'value', 'reason', 'observation'], path=fp, outcome=outcome)
            pid = fact['predicate']
            check(isinstance(pid, str) and pid in config['bindings'], 'UNRESOLVED_REFERENCE', 'unknown predicate binding', fp)
            binding = config['bindings'][pid]
            check(fact['binding_version'] == binding['version'], 'BINDING_VERSION', 'observation uses a different binding version', fp)
            check(isinstance(fact['args'], list) and len(fact['args']) == len(binding['parameters']), 'ARITY', 'observation arity mismatch', fp)
            for arg, parameter in zip(fact['args'], binding['parameters']):
                check(isinstance(arg, str) and arg in trace['domains'].get(parameter['type'], {}).get('members', []), 'ARGUMENT_TYPE', 'observation argument outside typed domain', fp)
            state, value = fact['state'], fact['value']
            check(state in ('known', 'unknown', 'absent', 'runtime_error', 'timeout'), 'OBSERVATION_STATE', 'unsupported evidence state', fp)
            check(nonblank(fact['reason']) and nonblank(fact['observation']), 'EVIDENCE_REFERENCE', 'reason and observation required', fp)
            check(type(value) is bool if state in ('known', 'absent') else value is None, 'BOOLEAN_VALUE', 'known requires exact Boolean; unobserved/error requires null', fp)
            if state == 'absent':
                check(binding['absent_is_false'] and value is False, 'ABSENCE_CONTRACT', 'absence requires reviewed false interpretation', fp)
            key = (pid, tuple(fact['args']))
            check(key not in table, 'DUPLICATE_OBSERVATION', 'ambiguous repeated observation', fp)
            table[key] = Evidence(value, (state + ': ' + fact['reason'],), (fact['observation'],),
                                  (state.upper(),) if state in ('runtime_error', 'timeout') else ())
        tables.append(table)
    return tables


class Runner:
    def __init__(self, trace, tables, budget):
        self.trace, self.tables, self.remaining = trace, tables, budget

    def run(self, node, env, step):
        self.remaining -= 1
        if self.remaining < 0:
            return Evidence(None, ('operation budget exhausted',), (), ('TIMEOUT',))
        op = node[0]
        if op == 'CONST':
            return Evidence(node[1], ('Boolean constant',))
        if op == 'CALL':
            key = (node[1], tuple(env[a] for a in node[2]))
            return self.tables[step].get(key, Evidence(None, ('missing observation: ' + repr(key),),
                                                      (f'{self.trace["id"]}/{self.trace["steps"][step]["id"]}',)))
        if op == 'NOT':
            return negate(self.run(node[1], env, step))
        if op in ('FORALL', 'EXISTS'):
            _, name, cid, body = node
            domain = self.trace['domains'].get(cid, {'members': [], 'complete': False})
            result = Evidence(op == 'FORALL', (f'{op} domain {cid}',))
            for member in domain['members']:
                result = combine('AND' if op == 'FORALL' else 'OR', result,
                                 self.run(body, {**env, name: member}, step))
                if self.remaining < 0:
                    break
            if not domain['complete']:
                result = combine('AND' if op == 'FORALL' else 'OR', result,
                                 Evidence(None, ('incomplete domain: ' + cid,)))
            return result
        return combine(op, self.run(node[1], env, step), self.run(node[2], env, step))


def decision(evidence):
    state = {True: 'HOLDS', False: 'VIOLATED', None: 'UNKNOWN'}[evidence.value]
    outcome = ('TIMEOUT' if 'TIMEOUT' in evidence.failures else 'RUNTIME_ERROR') if evidence.failures else state
    passed = state == 'HOLDS' and not evidence.failures
    return dict(state=state, outcome=outcome, reward=int(passed), passed=passed,
                truth={True: 'TRUE', False: 'FALSE', None: 'UNKNOWN'}[evidence.value],
                result_scope='finite_formula', exploration_state='not_checked',
                reasons=list(evidence.reasons), observations=list(evidence.observations), failures=list(evidence.failures))


def evaluate(corpus, config, trace):
    capabilities = dict(schema='not_checked', static_logic='not_checked', finite_execution='not_checked',
                        authenticity='not_checked', proof='not_checked', policy_correspondence='not_checked',
                        full_core_conformance='not_checked', exploration_verdict='not_checked')
    report = dict(profile=PROFILE, capabilities=capabilities, diagnostics=[], invariants={},
                  truth='UNKNOWN', result_scope='finite_formula', exploration_state='not_checked')
    try:
        require(len(json.dumps([corpus, config, trace], allow_nan=False).encode()) <= MAX_BYTES,
                'LIMIT', 'combined input exceeds 1 MB')
        report['identity'] = identity(corpus, config, trace)
        artifacts, trees, uses, order = compile_corpus(corpus, config, capabilities)
        capabilities.update(schema='passed', static_logic='passed')
        tables = validate_trace(trace, config, artifacts)
        runner = Runner(trace, tables, config['max_operations'])
        combined, results = Evidence(True), {}
        for aid in order:
            value = Evidence(True)
            for i in range(len(tables)):
                value = combine('AND', value, runner.run(trees[aid], {}, i))
            if not trace['complete']:
                value = combine('AND', value, Evidence(None, ('incomplete trace',)))
            for dep in artifacts[aid].get('dependencies', []):
                prior = results[dep]
                if prior.value is not True or prior.failures:
                    value = combine('AND', value, Evidence(None, ('unestablished dependency: ' + dep,), prior.observations, prior.failures))
            results[aid] = value
            report['invariants'][aid] = {**decision(value), 'bindings': {p: config['bindings'][p]['version'] for p in sorted(uses[aid])}}
            combined = combine('AND', combined, value)
        report.update(decision(combined))
        capabilities['finite_execution'] = 'failed' if combined.failures else 'completed'
    except Diagnostic as exc:
        if capabilities['schema'] == 'passed' and capabilities['static_logic'] == 'not_checked':
            capabilities['static_logic'] = 'failed'
        elif exc.code == 'SCHEMA_ERROR':
            capabilities['schema'] = 'failed'
        report.update(state='UNKNOWN', outcome=exc.outcome, reward=0, passed=False)
        report['diagnostics'].append(exc.as_dict())
    except (TypeError, ValueError, KeyError, RecursionError) as exc:
        report.update(state='UNKNOWN', outcome='INVALID_INPUT', reward=0, passed=False)
        report['diagnostics'].append(dict(code='INVALID_INPUT', message=str(exc), path='$'))
    return report


def qualify(results, expected):
    """Operator-owned controls: matching states AND outcomes AND admission/reward."""
    required = {'HOLDS', 'VIOLATED', 'UNKNOWN'}
    valid = (len(results) == len(expected) and required <= set(expected)
             and all(s in required for s in expected))
    failures = []
    for i, (r, state) in enumerate(zip(results, expected)):
        passed = state == 'HOLDS'
        if not (r.get('state') == state and r.get('outcome') == state
                and r.get('passed') is passed and type(r.get('reward')) is int and r['reward'] == int(passed)):
            failures.append(i)
    return dict(qualified=valid and not failures, failed_controls=failures,
                control_set_complete=valid)


def load_json(path):
    with Path(path).open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, 'LIMIT', 'input file exceeds 1 MB', outcome='INVALID_INPUT')
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = value
        return obj
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('invalid JSON constant ' + x)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('--config', required=True, help='operator-owned binding/configuration JSON')
    parser.add_argument('--trace', required=True)
    args = parser.parse_args()
    try:
        result = evaluate(load_json(args.artifacts), load_json(args.config), load_json(args.trace))
    except (OSError, ValueError, Diagnostic, RecursionError) as exc:
        result = dict(state='UNKNOWN', outcome='INVALID_INPUT', reward=0, passed=False,
                      truth='UNKNOWN', result_scope='finite_formula', exploration_state='not_checked',
                      diagnostics=[dict(code='INVALID_INPUT', path='$', message=str(exc))])
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
