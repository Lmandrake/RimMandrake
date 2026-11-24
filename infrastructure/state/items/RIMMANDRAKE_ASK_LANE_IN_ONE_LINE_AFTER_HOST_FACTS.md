# RIMMANDRAKE_ASK_LANE_IN_ONE_LINE_AFTER_HOST_FACTS

One command asks the SteveDesktop lane for a check, after a program read what that host has.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 3 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- `testq.py submit` has 24 settings. 51 of 143 submit calls were help text; 17 were refused by the tool `[measured]`.
- In 7 days, 16 of 61 asked jobs died of our own setup, and 14 measured nothing `[measured]`.
- Each missing thing was learned by a failed job: a mod (`ray1203.simplecamerasetting`), a save (the Pyrelands site), a
  package (`numpy`, then `lxml`), a companion (50 jobs), a driver ("live check owed", "no proof_hose result").
- The Claude logins of SteveDesktop died on 2026-11-23 (system 2:37 AM, steven 8:54 AM PST; lukas ends 1:24 AM on
  2026-11-24). The keep-alive said `renewed` each day, while `refresh_expires` never moved `[measured: ~/.claude-accounts/health.json]`.
- Superseded by this item: `RIMMANDRAKE_TAG_GSS_LIVE_CHECKS_FOR_STEVE_NONE_OF_203_CAN_GO`, `HARNESS_REPAIR_CAUSE_8135787B_2`,
  `HARNESS_REPAIR_CAUSE_C1B99C19_2`, `ACCOUNT_KEEPALIVE_VERIFY_STILL_BREATHING`.

## spec

### What it must do

- `host_facts.py`: one ssh read each hour of installed package ids, saves, Python packages, staged companions, free disk and
  the seconds that each Claude login has left. A file with its age. The contract is the head of the acceptance script.
- `ask.py` and `testq.py ask ITEM`: the whole `submit` command line from the item's live-proof lines, the test table and the
  tier. It holds the job until its companion is staged (keep one staged companion for each source hash).
- The filler, the visit feed and `submit` read the same facts. A chain with no driver on the lane is never in the rotation.
- A login with under 3 days left raises one alarm that names the account.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not read a stale file as "absent" (the risk: good work refused).
- It must not choose the purpose, and must not ask a check that nobody asked for.
- It must not change the keep-alive of `claude-remote-control`; it reads the login's end.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/ask_lane_accept.py
```

Seen failing 2026-11-23 9:48 PM PST: `FAIL 0/11`, exit 1. A correct build prints `PASS 11/11`, exit 0. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code), registers the page in `src/RimMandrake/Utils/boundary_check.py`, and plants faults that the tests must catch:
a stale file read as absent; a missing package read as present; a chain with no driver sent; exit 3 and exit 4 swapped. One fresh reader who did not make the change reads the changed files once.

## How we measure that it helped

Baseline (7 days to 2026-11-23): 16 of 61 asked jobs killed by setup, 14 asked and 12 filler jobs that measured nothing, 51
help calls. Read `census/kinds.py` and `census/submits.py` again 7 days after it is live. Good: 5 or fewer setup deaths, 10 or
fewer help calls. Guess: 3M less a week `[guess ~45%]`.

## How it keeps improving

Each setup death in `kinds.py` with a fact that the file could have held names a fact to add.

## refs

file: src/RimMandrake/Utils/testq/testq.py
file: infrastructure/stevedesktop/preflight.py
