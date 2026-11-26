# BOUNDARY: the calibration check of the art-eval first pass

Code: `src/RimMandrake/rimflow/art_first_pass_calibration.py`. Tests:
`src/RimMandrake/rimflow/selftest_art_first_pass_calibration.py`, one test per promise, with the promise's name.

The check is the `model_check` of the family `art_eval_first_pass` in `infrastructure/state/judge_calibration.json`.
The check puts each planted picture to the first reviewer (Opus) of the art-evaluation pipeline, with the prompt that
production builds. The check then reads the band that production's policy gives the reply. The band is what
production acts on: GOOD accepts, REALLY_BAD sends the art back, WEAK asks the second reviewer.

## ACCEPTS

- `infrastructure/state/art_eval/regression.jsonl`, the owner's own verdicts. A row with `taste` is not a planted case.
- A results path in `$RM_CALIBRATION_RESULTS`. With no path, the check prints only.

## DOES NOT SURVIVE

- A model that answers the same picture differently from one run to the next. Each case is one answer.
- A regression row whose `expect` is neither ACCEPT nor NOT_ACCEPT.

## PROMISES

- **planted-rows.** Every regression row with no `taste` is one planted case: ACCEPT expects pass, NOT_ACCEPT expects
  refuse. The registry row lists the same cases.
- **band-is-the-answer.** GOOD is pass, REALLY_BAD is refuse, WEAK is `second look`. The model's own `overall` word is
  recorded beside the band and decides nothing. A row with no `abstain` counts `second look` as the wrong answer.
- **weak-is-no-verdict.** The registry row's `abstain` (by the ruling RIMMANDRAKE_RULE_ART_FIRST_PASS_WEAK_IS_NO_VERDICT)
  names `second look` as no verdict: `refusal_contract.judge_row` never counts it wrong. A case is wrong only when the
  first pass accepts a refused picture, sends back a kept one, or answers `malformed`. The row's `decided_share` of the
  refuse cases must come out refuse, else FAILED. With no case decided at all, FAILED. A case that did not run still
  leaves UNTESTED.
- **could-not-look.** A missing picture, or a judge call that failed, leaves its case out of the results. The family
  then reads UNTESTED, never FAILED and never CALIBRATED.
- **malformed-is-not-missing.** A reply that does not fit the schema, after its one re-ask, is the answer `malformed`.
- **blind.** The prompt holds no verdict, no expectation and no provenance of the row.
- **no-second-reviewer.** The check calls the first reviewer only. It files no art job and writes no run record.

## LIMITS

- A wall limit per judge call is production's own (`runner.call_claude`, 420 s; a call took 60 to 120 s). It guards
  against a hung model process. A call that meets the limit did not run.
