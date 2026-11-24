# `scene.judge`: turn a kept run into one of the seven outcomes, outside the game

**For:** it reads a run's folder and gives the verdict. The game records; Python judges. No game is needed.

## Accepts

| argument | meaning | example |
|---|---|---|
| `run_dir` | the folder of one run: the commit hash, the contract, the trace, the receipts | `s.run_dir` |
| `rejudge` | judge a kept trace again, with the contract as it is now | `False` |

## Returns

A `Verdict`:

| field | meaning |
|---|---|
| `outcome` | one of SUCCESS, MOD FAILURE, RANDOM MISS, ENVIRONMENT FAULT, APPARATUS FAULT, UNRESOLVED, COULD NOT LOOK |
| `counts_for_bar` | `True` only when the run was started by `scene.py accept` from a clean tree, in an unmarked game process, and carries no stamp |
| `first_failed` | the first condition that did not hold, with the tick and the recorded values |
| `evidence` | each point of the evidence contract: held or not (the trace is complete with no dropped row, the build in every receipt is one build, each condition's values were readable, no run ended `unknown`, the exposure happened) |

It checks the evidence first. When a point fails, the outcome is COULD NOT LOOK and it does not judge the conditions. A
forbidden condition that held is a MOD FAILURE in any run.

Receipt: `game` and `build`: copied from the receipts inside the run, marked "of the run"; `did: []`; `hands: []`; `could_not_look`: each evidence point that failed, with its cause;
`stamps`: copied from the run.

## State changes

It writes `verdict.json` in the run's folder. With `rejudge`, it writes a new file beside the first and keeps the
first. It does not write the verdict ledger; `scene.py accept` does that with this verdict.

## Refuses

| name | when | repair |
|---|---|---|
| `NO_TRACE` | the folder has no trace file | the run did not record; run the scene |
| `NO_CONTRACT` | the folder has no contract | the run was not opened with a contract |
| `CONTRACT_MISMATCH` | the trace was recorded for a contract with another hash, and `rejudge` is not set | pass `rejudge=True` to judge on purpose with the new contract |

An incomplete trace is not a refusal. It is the outcome COULD NOT LOOK.

## Example (FlowWorks visit 9, `sc_moat_raid`, run T161018: raider Human21212 read held, left the drained moat and cut a warden)

```python
v = scene.judge(s.run_dir)
# outcome        MOD FAILURE
# first_failed   forbidden: a raider outside the moat after sluice_open
#                tick <T>: Human21212 Position <cell on the rim>, CurJobDef AttackMelee
# counts_for_bar True
```

On visit 9 the cause was not read, because the values of that tick were not kept. With the trace of `s.run`, the same
run can be judged again after the row's rule changes, with no game:
`python3 src/RimMandrake/Utils/scene.py judge <run_dir> --rejudge`.

## The red check

`test_judge_refuses_*` (one for each row), `test_judge_incomplete_trace_is_could_not_look`,
`test_judge_forbidden_effect_is_mod_failure_in_any_run`, `test_judge_stamped_run_does_not_count`,
`test_judge_success_needs_exposure`. Planted faults: a judge that gives SUCCESS on a trace with no closing record; a
judge that lets a TUNED run count.

## Limits

It judges only what was recorded. It cannot tell an ENVIRONMENT FAULT from UNRESOLVED unless the record shows what
spoiled the opportunity; with no such record the outcome is UNRESOLVED. It makes no taste call: a picture is for a
judge agent.
