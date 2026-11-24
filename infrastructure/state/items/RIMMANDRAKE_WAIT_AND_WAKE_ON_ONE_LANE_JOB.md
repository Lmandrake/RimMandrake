# RIMMANDRAKE_WAIT_AND_WAKE_ON_ONE_LANE_JOB

One command waits for one lane job, reads its heartbeat, and returns its rows.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 7 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- In the week to 2026-11-23, 111 turns (1.83M) waited for a lane job and 275 turns (4.14M) read a job or the lane `[measured:
  census/tokens.py]`. Each submitter wrote its own loop. None of them read the heartbeat, so a hung job looked like a slow job.

## spec

### What it must do

- `testq.wait_for(...)` and `testq.py wait JOB [--timeout S]`, with the states and exit codes of the acceptance script.
- It prints the failing rows and the outcome, not the whole record (under 40 lines).
- The skill page that tells agents how to use the lane names it as the way to wait.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not hide a hung job: no heartbeat for `HUNG_S` reads `hung`, and `HUNG_S` names its danger and evidence.
- It must not poll the machine over ssh: the queue files on Archmagi are the record.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/wait_lane_accept.py
```

Seen failing 2026-11-23 9:48 PM PST: `FAIL 0/6`, exit 1. A correct build prints `PASS 6/6`, exit 0. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code), registers the page in `src/RimMandrake/Utils/boundary_check.py`, and plants faults that the tests must catch:
a hung job read as waiting; an unknown id waited for; a cancelled job read as done. One fresh reader who did not make the change reads the changed files once.

## How we measure that it helped

Baseline: 111 wait turns and 275 read turns in 7 days. Run `census/tokens.py` 7 days after it is live and compare turns per
100 submitted jobs. Good: half. Guess: 1.5M less a week `[guess ~45%]`.

## How it keeps improving

Wait loops that agents still write by hand (`while`, `sleep` beside a job id in a transcript) name what the command lacks.

## refs

file: src/RimMandrake/Utils/testq/testq.py
