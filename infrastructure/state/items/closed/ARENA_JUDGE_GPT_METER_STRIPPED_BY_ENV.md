# ARENA_JUDGE_GPT_METER_STRIPPED_BY_ENV

## Finding
GptConsult passes RM_GPT_CALL_LOG=<work>/calls.jsonl; the default work root sits under clones_root and judge_env
dropped any value naming clones_root, so no judge GPT call was metered (3 pilot calls, 0 records).

## Status (2026-10-30, FOUNDRY builder)
Already fixed at 62d8f964f2: judge_env(own=) keeps an `extra` path inside the call's own workspace, and
run_sandboxed passes own=work. 62d8f964f2 is an ancestor of the final vet / trial_tasks.json build 903d0fce81 and
arena_judge.py has not changed since, so the vetted hash already carries the fix; no edit, no re-vet. The 02:41Z
"held" note assumed an edit was still needed; it was not.

## criteria
- A1 L0: `run_selftests.py --only src/RimMandrake/Utils/arena/selftest_arena_judge.py` passes, including "RM_GPT_CALL_LOG reaches gpt_consult inside the sandbox" and "the judge's GPT call is metered, as harness spend" (PASS 55.6s, 2026-10-30).
- A2 L1: in the trial, each real GPT judge call appends one record with arm=harness to the real gpt_calls.jsonl (count of records = count of GPT judge calls).
