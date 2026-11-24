# RIMMANDRAKE_COUNT_LANE_RESULTS_WHERE_VISITS_DECIDE

A finished visit job of the SteveDesktop lane becomes rows of the open visit, by program.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 1 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- The visit feed sent 32 jobs. 22 ended DONE. 12 of them gave 163 PASS and 3 FAIL rows. No visit folder holds one of the 32
  job ids `[measured]`. Of 1,819 rows in all visits' `rows.jsonl`, 1 has `game: stevedesktop` `[measured]`. The visits ran
  the same checks again on ArchBig or ArchSmall.
- The proofs half of this form is built: `ingest.ingest_proofs` (this study's 12 jobs since 2026-11-18 had no reader).

## spec

### What it must do

- A module `src/RimMandrake/Utils/testq/visit_rows.py` maps a done visit job to rows by the `testq` blocks of the mod's
  test table, with the build identity of the game that ran the job (`build_match.identity`). The contract is the head of the
  acceptance script.
- `ingest.py` writes the rows of a `BENCH.visit` job into the open visit's `rows.jsonl`, once, and lands them.
- The in-game stage counts such a row like any row: the build match is the door.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not count a row from another build (the risk of the study: "It could count a result from another build. Keep the
  build check."). An identity that could not be read counts nothing and says so.
- It must not write in a visit that another run is driving without that visit's own lock.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/count_visit_rows_accept.py
```

Seen failing 2026-11-23 9:48 PM PST: `FAIL 0/12`, exit 1. A correct build prints `PASS 12/12`, exit 0. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code), registers the page in `src/RimMandrake/Utils/boundary_check.py`, and plants faults that the tests must catch:
a row of another build counted; an UNMEASURED row read as PASS; a second write; a check whose second chain is absent. One fresh reader who did not make the change reads the changed files once.

## How we measure that it helped

Baseline: 0 of 22 finished visit jobs counted; 1 of 1,819 visit rows from SteveDesktop. Run
`census/visits.py` (the study's script) 7 days after it is live. Good: every DONE visit job has its rows, and no check of an
open visit runs on an Arch game when its SteveDesktop row counts. Guess: 1.5M less a week `[guess ~40%]`.

## How it keeps improving

The reading `visits.py` names each visit job with no row; each such job names a missing block or a build mismatch.

## refs

file: src/RimMandrake/Utils/testq/ingest.py
file: src/RimMandrake/rimflow/build_match.py
