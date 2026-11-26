# BOUNDARY: the calibration check of the code-review brief

Code: `src/RimMandrake/rimflow/code_review_calibration.py` (the check) and `judge_cases` in
`src/RimMandrake/rimflow/refusal_contract.py` (the pass mark). Tests: `src/RimMandrake/rimflow/selftest_code_review_calibration.py`,
one test per promise, with the promise's name in its first words.

The check is the `model_check` of the family `code_review` in `infrastructure/state/judge_calibration.json`. It asks
Codex once to sort the 35 claims of `code_review_calibration_set.json` as problem, polish or next_version, against the
review brief and the control store's page only.

## ACCEPTS

- A Codex answer that holds one JSON array of `{id, class, ...}` objects.
- A results path in `$RM_CALIBRATION_RESULTS`. With no path, the check prints only.

## DOES NOT SURVIVE

- A sorter that flips a claim from one run to the next. The calibration reads one answer.
- An answer with no JSON array. It sorts nothing and the row reads UNTESTED.

## PROMISES

- **the-registry-row-declares-the-pass-mark.** The row's `pass_mark` names the ruling
  RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS and `polish_called_problem_max: 0`.
- **the-pass-mark-decides-not-exact-labels.** The row reads CALIBRATED when every agreed real claim is called a Problem
  and no agreed polish claim is called a Problem. The agreed claims are the 10 that carry `agreed: true`. The count of
  exact labels is a reading in the row's `last_run`, and it decides nothing. A run with 33 of 35 exact labels and every
  agreed claim right reads CALIBRATED. A row with no `pass_mark` still needs every planted case as labelled.
- **a-missed-agreed-real-claim-fails-the-row.** One agreed real claim that is not called a Problem reads FAILED.
- **an-agreed-polish-claim-called-a-problem-fails-the-row.** One agreed polish claim that is called a Problem reads
  FAILED. This and the promise before it are the two dangers that the calibration guards: a missed real fault, and
  polish sent back as a Problem.
- **an-unsorted-agreed-claim-reads-untested.** A claim that Codex did not sort gets no row, so the row never reads
  CALIBRATED on a partial answer.
- **the-recorded-run-reads-calibrated.** The recorded answer of 2026-11-26T03:24Z reads CALIBRATED with no new Codex
  call.

## LIMITS

- The Codex call has a 500 s limit. It guards against a hung model process; the first call took 211 s.
