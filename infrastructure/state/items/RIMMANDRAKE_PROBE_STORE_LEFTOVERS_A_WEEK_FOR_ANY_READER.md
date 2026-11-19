# RIMMANDRAKE_PROBE_STORE_LEFTOVERS_A_WEEK_FOR_ANY_READER

## spec

Census class 5 ("could not tell"). Under `/home/mandrake/rm/relentless/`: `books` (a comment in `checker_box.py` near
line 325 borrows it), `release`, `tmp4vj6r3_q`, and in `store/`: `boxrun.jsonl`, `broker`, `breaker.json`,
`circling.jsonl`, `exams`. Last writes 2026-11-04 to 2026-11-06 (measured 2026-11-19); their writing modules were deleted
2026-11-18. Two that looked like leftovers are live and stay: `transcripts` (written today by `scratch_clone.py`) and
`store/evidence_shadow.jsonl` (written by `rimflow close`, `evidence_gate.py`). Do: from 2026-11-19, record access times
for a week (`find ... -newerat 2026-11-19`; ext4 here is relatime, so check the mount first), then move the unread ones
to `D:\ClaudeWork\retired-trees\` with a manifest; never delete.

Found by `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` (2026-11-19, BENCH); index: `design/RimMandrake/retired_eras_index_2026-11-18.md`.

## verify

Acceptance test, run from the repo root:

    for p in books release tmp4vj6r3_q store/boxrun.jsonl store/broker store/breaker.json store/circling.jsonl store/exams; do
      test -e /home/mandrake/rm/relentless/$p && echo "still here: $p"; done; true

prints nothing once done (each moved, or kept with a named reader on this item). Watched failing 2026-11-19 BENCH: all 8
still here.

## criteria

- A1: each of the 8 paths is moved to retired-trees with a manifest, or kept with the reader that was found.
- A2: nothing that read one fails after the move (a week of ops_watch with no new alarm naming it).

## refs

none: on-disk store paths outside the repo
