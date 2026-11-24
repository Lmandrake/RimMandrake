# RIMMANDRAKE_END_EVERY_LANE_PAUSE_ITSELF_FORTYNINE_HOURS

Every pause of the SteveDesktop lane names its end, and the tick lifts the pause at that end.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 4 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- Asked jobs waited 142.7 h under a pause in 21 days. One pause had no end and stood 49.3 h `[measured: census/idle_why.py]`.

## spec

### What it must do

- Built in this run: `testq.py pause --hours | --until-unit`, the default end, auto pauses that retry, `LS.step` in the tick.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not resume onto a machine under test (the risk): `--until-unit` names the job that must be over.
- Not built on purpose: moving work to ArchSmall while the machine is paused; the Archmagi half of the lane is switched off (`archmagi.stop`).

## verify

### Acceptance test

```
python3 src/RimMandrake/Utils/testq/selftest_lane_stop.py
```

Green 2026-11-23. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The promises `every-pause-has-an-end`, `a-unit-pause-waits-for-its-unit`, `a-hand-pause-is-extended-not-refused`.

## How we measure that it helped

Baseline 49.3 h with no end. `census/idle_why.py`, 7 days after it is live: 0.

## How it keeps improving

A pause that the tick lifted too early (a job refused in the pauser's work) names a pauser that needs `--until-unit`.

## refs

file: src/RimMandrake/Utils/testq/lane_stop.py
file: src/RimMandrake/Utils/testq/testq.py
