# RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS

## spec
Found by the Codex review of `RIMMANDRAKE_FOLD_FRAME_JUDGE_INTO_PRELOOK` (2026-11-18, finding 8). The owner's ruling
(standing_rulings.md §A refusal carries its path to pass, 2026-11-12: *"ANY refusals must be as detailed as the evidence
they are rejecting and include the fixes and paths towards passing that are attainable and reasonable."*) binds every judge,
and scene_look_judge_brief.md asks a refusal-contract record for every ODD, WRONG or COULD NOT SEE. The north-star frame
judge (`src/RimMandrake/Utils/northstar_driver/judge_cli.py`) predates the contract: a pass-2 NO turns a bar FAIL with a
one-sentence `why` and writes no record (`refusal_contract.py submit` is never called). Gap older than the fold; the fold
did not widen it.

Build: for each bar a frame judge FAILs (or leaves UNMEASURED on UNJUDGEABLE), write the contract record
(`family: scene_look_judge_brief`, clause = the bar id, evidence = the judged capture, observed = the judge's why,
would_pass, smallest_fix, criterion_verdict) and submit it with its `given` (the bar text and the capture), as the brief's
own records do (`selftest_judge_brief_records.py`). Ask pass 2 for `would_pass` / `smallest_fix` / `criterion_verdict`
only when it says NO or UNJUDGEABLE, so a YES costs nothing extra.

## criteria
- Acceptance test (offline): a mock-judge selftest where one bar is NO, one UNJUDGEABLE and one YES: exactly two records
  are submitted (through a fake `submit`), each passes `refusal_contract.py check`, none for the YES; watched failing on
  the base (no record written).

## verify
- `python3 src/RimMandrake/Utils/northstar_driver/selftest_judge_open_look.py` and the new selftest green; one real run
  through `judge_cli.py` stores its records in refusals.jsonl.

## refs
file: src/RimMandrake/Utils/northstar_driver/judge_cli.py
file: design/RimMandrake/scene_look_judge_brief.md
file: src/RimMandrake/rimflow/refusal_contract.py
