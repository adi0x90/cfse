# Evidence Evaluation

This section is **normative CFSE core**, not an optional extension. It specifies how evidence supports Boolean propositions and security conclusions. It does not mandate an interpreter, observation adapter, reward scale, or new artifact fields. The requirements apply whenever a tool or researcher evaluates evidence or claims an invariant state, verdict, or successful check. Schema-only tools MUST report unsupported evidence evaluation as `not_checked` rather than passed.

## UE-1: Separate proposition, evidence and decision

A Predicate denotes a Boolean proposition and its `returns` MUST remain `boolean`. Whether the proposition is true is distinct from whether sufficient evidence is available to determine it. Evaluators MUST distinguish:

1. The proposition being checked, its inputs, and its scope.
2. Evidence supporting true, supporting false, or insufficient to determine either.
3. Evaluation completion/failure and the resulting claim or admission decision.

The symbols **T**, **F**, and **U** below denote evidence of true, evidence of false, and unresolved evidence. U is not a third Predicate return value, a false value, or an operational error code. This notation does not prescribe a serialization. Implementations MAY use a tagged value, separate status, or another representation that preserves these distinctions.

A formula evaluation result MUST be distinguishable from an Exploration's `InvariantResult`. Formula truth alone MUST NOT be promoted to `HOLDS`, `VIOLATED`, or a confirmed Exploration verdict without the requirements in [Invariant States](01-invariant-states.md) and [Exploration Verdicts](02-exploration-verdicts.md), including executed matched BASE/ATT paths and direct property-specific evidence. Vacuous truth is not evidence of attempted enforcement.

## UE-2: Missing evidence is not falsehood

Evaluators MUST NOT convert missing, unavailable, incomplete, or unresolved evidence into a Boolean value through truthiness, null equality, default denial, or a closed-world assumption that has not been justified for the declared scope. Missing evidence MUST remain U unless other sufficient evidence or a documented inference establishes the proposition.

Known absence is different from absence of an observation. A confirmed absence MAY establish F for an existence predicate, or T for an absence predicate, according to its definition and observation binding. An absent row, unreadable object, failed lookup, or omitted record MUST NOT by itself establish that the underlying object is absent.

The reason for U or evaluation failure MUST be retained, together with the affected proposition/check and the relevant observation reference or identification of what evidence is missing. Malformed input MUST be diagnosed rather than treated as an observed denial or known absence. Contradictory observations MUST NOT be silently resolved by choosing the convenient value; a decisive result requires an explicit, justified reconciliation.

## UE-3: Compose evidence without losing uncertainty

For direct composition of operand evidence with no additional information, evaluators supporting the corresponding logical operators MUST use the following tables. These extend the existing Boolean truth tables to partial evidence; they do not change the underlying Boolean logic.

| A | B | AND | OR | IMPLIES | IFF |
|---|---|-----|----|---------|-----|
| T | T | T | T | T | T |
| T | F | F | T | F | F |
| T | U | U | T | U | U |
| F | T | F | T | T | F |
| F | F | F | F | T | T |
| F | U | F | U | T | U |
| U | T | U | T | T | U |
| U | F | F | U | U | U |
| U | U | U | U | U | U |

| A | NOT A |
|---|-------|
| T | F |
| F | T |
| U | U |

`A IMPLIES B` has the evidence result of `NOT A OR B`. `IFF` compares the truth of Boolean propositions: observed allow IFF unresolved policy and observed deny IFF unresolved policy both yield U. Two unresolved operands MUST NOT compare equal merely because their missing-value markers are equal.

These are compositional evidence tables, not a prohibition on stronger sound reasoning. An implementation MAY derive a definite result from additional evidence or logical relationships, but MUST identify the additional justification and scope. For example, proving a tautology involving repeated occurrences of the same proposition is different from treating two unrelated unknown observations as equal. Implementations MUST NOT advertise proof or additional reasoning they did not perform.

A definite F operand MUST survive an unrelated U in a conjunction; a definite T operand MUST survive an unrelated U in a disjunction. Processing order MUST NOT erase an independently supported result. Implementations MAY short-circuit when sufficient, but MUST NOT claim that skipped checks were performed. Unsupported operators MUST be reported as unsupported/unperformed, not evaluated successfully.

## UE-4: Make scope and completeness explicit

Evidence-based claims MUST identify their observation scope. Evaluators using finite domains or traces MUST declare their completeness assumptions and MUST NOT equate an incomplete or missing enumeration with a complete empty set.

For finite-domain direct evaluation, FORALL combines member evidence using AND and EXISTS uses OR. An incomplete enumeration contributes U: a known counterexample still establishes F for FORALL, and a known witness still establishes T for EXISTS. Without such evidence, incomplete enumeration cannot establish universal satisfaction or existential absence. Empty complete domains retain ordinary Boolean vacuity. A finite observation window MUST NOT be presented as proof of an unbounded temporal property.

## UE-5: Evaluation failure is not a security conclusion

Tools MUST distinguish insufficient evidence from an unavailable evaluator/binding, invalid input, parse/static-check failure, runtime failure, and timeout when those conditions arise. Equivalent names are permitted; these failure classes MUST remain separately identifiable in diagnostics or evaluation reports. No new InvariantState enumeration member is introduced.

A failure MUST NOT be silently recoded as a Boolean proposition or a successful check. If a Boolean result is independently determined despite an operational failure, both the justified result and the encountered failure MUST be retained. The failed evaluation MUST NOT be reported as a fully successful execution. A failure in one check MUST NOT erase independently supported findings from another check.

If no experiment executed, record no fabricated execution evidence: use an unexecuted record or `BLOCKED` as specified by the Exploration contract. If execution occurred but the property cannot be determined, use `UNKNOWN` and, absent an independently established targeted violation, `INCONCLUSIVE`. `NOT_APPLICABLE` means not evaluated; it MUST NOT disguise an attempted but unresolved evaluation.

## UE-6: Preserve supported conclusions and gate success

When the confirmed-outcome requirements are met, an independently supported targeted `VIOLATED` state MUST NOT be downgraded solely because another target is `UNKNOWN`. Conversely, `ENFORCEMENT_CONFIRMED` requires every targeted invariant to be supported as `HOLDS`; missing targets, UNKNOWN, skipped checks, or evaluation failures MUST NOT count as demonstrated enforcement.

An unresolved or failed required check MUST NOT earn full credit for demonstrated satisfaction of the property or successful completion of that check. Numeric rewards, partial scores, and task objectives remain application-specific. For example, rewarding a correct report of uncertainty is permitted, but MUST NOT be represented as evidence that the property held. A verified violation may satisfy a violation-detection task; it does not demonstrate enforcement.

These requirements do not force a definite claim when evidence is insufficient. Nor does an evaluator that always returns U, always fails, or rejects everything establish useful correctness. Tools claiming correctness/usefulness qualification MUST include positive, negative, and insufficient-evidence controls appropriate to their supported task and MUST report the qualification scope. Passing a finite control set is not a universal reliability claim.

## UE-7: Knowability predicates do not replace evidence states

A Boolean knowability predicate is a proposition about whether the value can be determined under its stated observation contract. `P-X-KNOWN AND P-X-VALUE` expresses **known and true**, a different proposition from X. If KNOWN is F and evidence for VALUE is U, the conjunction is F while VALUE remains U. Evaluators MUST NOT copy that F back into VALUE or infer a violation of X from the conjunction alone.

Likewise, `P-X-KNOWN IMPLIES P-X-VALUE` is vacuously true when KNOWN is F. It does not establish VALUE or show that an attempted violation was prevented. An author MAY intentionally require knowability as a separate policy obligation; failure of that obligation MUST be attributed to that obligation rather than presented as knowledge of X.

Implementations MUST preserve unresolved VALUE evidence separately and MUST evaluate knowability predicates according to their own definitions and evidence. See the [Predicate contract](../artifacts/supporting/predicate/predicate.md#returns).

## Conformance and record compatibility

These guarantees apply to semantic claims at every applicable core conformance level. They do not require all tools to execute logic; unsupported checks MUST remain `not_checked`. [Conformance](../foundations/conformance.md) still requires a declaration of the checks actually performed. Schema acceptance, content hashes, or a successful formula evaluation MUST NOT be advertised as evidence authenticity, source/binary correspondence, or proof of policy truth.

Existing artifact schemas and the Boolean Predicate return contract are unchanged. Existing `InvariantResult.evidence`, Exploration summaries and recommendations can record uncertainty and reasons; tool-specific operational diagnostics may live in separate evaluation reports. Tools MUST NOT add undeclared fields to closed core artifact objects. JSON Schema alone cannot enforce these semantic guarantees.

The portable [conformance vectors](../../tests/fixtures/uncertainty/cases.json) and [tests](../../tests/test_core_uncertainty.py) exercise the tables, decision-equivalence regression, knowability distinction, failure admission and formula/Exploration boundary. The vectors are test data, not new artifact types. The optional finite-trace runner is one tested implementation; it is not the authority for core meaning.
