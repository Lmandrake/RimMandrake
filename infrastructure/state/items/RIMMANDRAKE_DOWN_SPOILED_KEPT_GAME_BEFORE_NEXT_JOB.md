# RIMMANDRAKE_DOWN_SPOILED_KEPT_GAME_BEFORE_NEXT_JOB

A kept SteveDesktop game whose map is spoiled goes down before the next job.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 5 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- 33 jobs in 21 days (13.5 lane hours) had a row with a dead colony or a site that could not be held; the game went on to the next job `[measured: census/kinds.py]`. 138 such rows since 2026-11-20.
- Superseded by this item: `HARNESS_REPAIR_CAUSE_CEF341B8`, `_6236AE26`, `_4AFBF8A2_2`, `_F6CADE57`, `_01DAD227_2`, `_E0B6DA41_3`.

## spec

### What it must do

- Built in this run: `worker.SPOILED_RE` and `stop_game_for_next_job` for a row that is UNMEASURED or NOT_RUN and says so.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not stop a game for a FAIL row that only quotes the words.
- The cost is one cold load (the risk: about 8 min).

## verify

### Acceptance test

```
python3 infrastructure/stevedesktop/selftest_steve_worker.py
```

Green 2026-11-23 (`a-spoiled-kept-game-goes-down-before-the-next-job`): spoiled goes down; a quoted FAIL and a clean run keep the game. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The same rule as the red canary; three cases in the test.

## How we measure that it helped

Baseline 33 jobs in 21 days. `census/kinds.py`, 7 days after it is live: no two spoiled jobs in a row on one game.

## How it keeps improving

A spoiled row with other words in `kinds.py` adds its words to `SPOILED_RE`.

## refs

file: infrastructure/stevedesktop/worker.py
