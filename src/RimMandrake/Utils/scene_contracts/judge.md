# `scene.judge` judges a kept run outside the game

## Accepts

| argument | meaning |
|---|---|
| `run_dir` | folder containing `run.json`, `receipts.jsonl`, `trace_<request>.jsonl` and `contract.json` |
| `rejudge` | apply the current checker again to the original evidence. Default `False` |
| `checks` | the scene's own check rows, computed after its session: a list of `{"id", "verdict", "text"}`, where the verdict is `PASS`, `FAIL`, `INVALID` or `UNMEASURED`. Default `None` |

The script can save a checker in `contract.json` using `c.to_tree(condition)` for each condition. For example, a
recording of a pawn's health before and after an act can use this checker.

```python
from scene import cond as c

checker = {
    "kind": "A",
    "exposure": c.to_tree(c.value("Human12", "health.summaryHealth.SummaryHealthPercent") < 1),
    "success": c.to_tree(c.value("Human12", "health.summaryHealth.SummaryHealthPercent") < 0.9),
}
```

The checker selects a call with `request` when several traces are kept. See the [judge boundary](../../../../design/specs/2026-11-23-scene-judge/boundary.md)
for the other keys. A named track can be read with a probe `{"p":"track","name":"health"}`. `c.count("damage", victim="wardens")`
counts matching events so far. `c.seq("damage", "death")` tests for those entries in order. `c.before("damage", "death")`
and `c.after("death", "damage")` compare first entries. A tap must have been armed to show a measured zero. The landed
writer records tracks and acts. Tap and alias-link records are exercised by offline fixtures.

A scene that decides its bar by rows that it computes after its session passes those rows as `checks`. Otherwise the judge
reads only the contract. The judge keeps the rows as `checks.json` beside the trace, and a later judgement reads that file.
A `FAIL` row makes the run no SUCCESS, also when the contract's success holds: in kind A it is MOD FAILURE. With no `FAIL`
row, an `INVALID` row (the opportunity was not staged) is an APPARATUS FAULT and an `UNMEASURED` row gives COULD NOT LOOK.
`selftest_scene_library.py` refuses a committed scene that prints rows (a `def row`, or a "failing row" summary) and
calls `scene.judge` without `checks=`.

## Returns

A verdict with `outcome`, the classifier `row`, `first_failed` with the condition, tick and observed values, and
`evidence`. Its receipt carries the recorded game, build and stamps. The judge makes no bridge calls.
`counts_for_bar` requires SUCCESS on an accepted, unstamped run with an identified commit.

## State changes

`verdict.json` holds the first verdict. Rejudging appends a line to `verdict_history.jsonl` with the outcome, the
checker version and hash, and whether the checker changed. The first verdict stays in place.

## Refuses

| name | when |
|---|---|
| `NO_TRACE` | the selected call has no trace file |
| `NO_CONTRACT` | there is no `contract.json` |
| `BAD_PLAN` or `BAD_CONDITION` | a checker key or condition is invalid |
| `CONTRACT_MISMATCH` | the checker changed and rejudge was left off |
| `NO_VERDICT` | a rejudgement has no original verdict |
| `EVIDENCE_CHANGED` | the selected call or its kept evidence changed, the rows differ from the kept `checks.json`, or rows come for a run already judged without them |
| `BAD_CHECKS` | a check row has no id, or its verdict is not one of the four words |

Incomplete evidence gives COULD NOT LOOK. A rejudgement that needs an unrecorded track or tap names it and leaves
history alone.

## Command and checks

`python3 src/RimMandrake/Utils/scene.py judge <run_dir> [--rejudge]`

`python3 src/RimMandrake/rimflow/scene_judge.py [--rejudge] <run_dir>`

Exit codes are SUCCESS 0, MOD FAILURE 1, RANDOM MISS 2, ENVIRONMENT FAULT 3, APPARATUS FAULT 4, UNRESOLVED 5,
COULD NOT LOOK 6, and named refusal 7. `selftest_scene_judge.py` checks each code and all nine classifier rows.

## Limits

Tracks show end-of-tick values. The judge can only use the recorded parts of the call and the facts its checker
names. Questions about appearance still go to a reader of the picture.
