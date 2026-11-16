# RIMMANDRAKE_FIX_CONTAGION_COVERAGE_GAPS_TWENTY_FIVE_ALL_SOUND

## spec
Contagion's stage-5 coverage judge (`rm-coverage-judge-1794821839`, verdict 2026-11-16 09:37Z) left 25 gaps, g1-g25, in
`design/concepts/Contagion/coverage_verdict.json`. Every one has `criterion_verdict: sound`, and the judge's reasons say
"every one can be fixed at stage 3": missing scene arms, caps never reached, controls that do not discriminate, starts
not asserted, built-but-unread parts (Repulsor warning, Touched transition message, genome inject, draftprints,
helix contracts, wrecks, burn clock), sheet text the tree does not test. Then judging stopped on spend (3,151,034
tokens against the 3,007,272 limit), raising REFUSAL_NOTHING_COULD_EVER_PASS on `concept:Contagion` (incident
refusals-20261115061558). Rounds so far: 31 gaps (00:15Z), malformed (09:27Z), 25 gaps (09:37Z); 0 late gaps, so the
judge is not inventing new ones.

Fix each gap in the concept files its `smallest_fix` names (`scenes.json`, `tree.json`, `record.json`, `sheet.md`), and
write `coverage_fixes.json` with one claim per gap against that judge run. A gap whose fix needs unbuilt code is filed
and gated as its own item, which is itself the fix (g5, g6 style). Do not edit the judge, its brief or its limits.

Release: `coverage_judge.py release design/concepts/Contagion --after <this id>` is granted, so closing this gives
exactly one more judge look. The concept's charges since its first judge are 7.43M against a park line of 8M (twice
the 4M cap), so that look will most likely park it for the owner with `park_summary.md` if it does not cover.

## verify
The acceptance test below exits 0, and the three concept JSON files still parse.

## criteria
Acceptance test: `python3 -c "import json,sys;d=json.load(open('design/concepts/Contagion/coverage_fixes.json'));g={c['gap'] for c in d['claims']};need={'g%d'%i for i in range(1,26)};sys.exit(0 if d['against']=='rm-coverage-judge-1794821839' and need<=g else 1)"`
exits 0 (1 check). On base it exits 1 (watched 2026-11-16: `against` is still rm-coverage-judge-1794788108, 30
claims). It proves a claim exists for every gap, not that a claim is true: the granted judge look is that oracle.

## refs
file: design/concepts/Contagion/scenes.json
file: design/concepts/Contagion/tree.json
file: design/concepts/Contagion/record.json
file: design/concepts/Contagion/coverage_fixes.json
