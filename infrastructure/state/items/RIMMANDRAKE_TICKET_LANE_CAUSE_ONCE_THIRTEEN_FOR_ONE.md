# RIMMANDRAKE_TICKET_LANE_CAUSE_ONCE_THIRTEEN_FOR_ONE

One cause of the SteveDesktop lane has one ticket; an incident has its own clock and ends by itself.

Filed by `RIMMANDRAKE_CLEAN_STEVEDESKTOP_TICKETS_FIX_THE_FORM_NOT_EACH_COMPLAINT`. The owner, 2026-11-23, evening PST:
*"PLEASE look over ALL the tickets and perform the 'form over specific complaint' procedure: what's REALLY wrong, not
just this one time, but for all times?"* Form 8 of `design/specs/2026-11-23-stevedesktop-work-to-code/forms.md`.

## Finding

The study is `design/specs/2026-11-23-stevedesktop-work-to-code/one_page.md` and `analysis.md` beside it (21 days to
2026-11-23, 8:30 PM PST). M is million weighted tokens (`weighted_v2`).

- The steward filed 50 `STEVE_LANE_UNSTICK_*` tickets in 21 days; 37 were dropped `[measured]`. 13 were one filler brake
  (`RIMMANDRAKE_KEY_STEWARD_ITEMS_ON_CAUSE_NOT_FRESH_NAMES`, whose whole text moved here).
- Two constraints from that ticket: a cause-keyed ticket must outlive `retire` (a dropped item cannot reopen), and
  `ops_watch.steve_incident_unclaimed` ages an open item from its creation, so a reused old item would alarm at once. A bad
  key would merge two stalls and silence the lane's only stall alarm.
- `STEWARD_FIX_LEAVES_THE_LIGHTS_ON`: the steward now retires what a recovered incident left (5bd612281f). Its promise broke
  once (`testq-tick.timer` had no last firing, 2026-11-11 8:07Z), and the cause of that outage is unknown.
- `ingest.repair` filed 31 `HARNESS_REPAIR_*` in 21 days. A repair whose cause the worker now heals by itself (a spoiled map, a
  surprise that stopped a chain) still makes a ticket, and a closed one returns as `_2`, `_3`. He wants no "check again" noise.
- `OPS_STEVE_UNSTICK_UNCLAIMED_ETBS`, `OPS_TESTQ_UNSTICK_ECPK` and `OPS_STEVE_DIAGNOSE_INVALID_MBTX_YAHV` are alarm tickets that
  came back on one id, each with a guard owed; the false stall of `ECPK` after a pause is fixed (`lane_resumed.json`).

## spec

### What it must do

- `lane_ticket.py` (pure) with the contract of the acceptance script; `steward.py` uses it instead of `mint`.
- The ticket of a cause stays open on a wait that names the cause; an incident notes it and ends itself.
- `ops_watch` ages the incident, not the ticket.
- `ingest.repair` files a repair for a cause that the lane heals by itself only after the cause comes back on three jobs in
  24 h; before that it notes the filler host.

## What it must not do

- It must not take a judgement from an agent: what to test, the class of a failure, the cause of a fault.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code.
- It must not tell a launched agent its spend.
- It must not refuse an act for a fault of form that it can repair itself.
- It must not merge two different stalls: another state or another cause is another ticket.
- It must not silence the stall alarm: an incident that nobody takes still reaches Operations in the same minutes as today.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-stevedesktop-work-to-code/acceptance/lane_cause_once_accept.py
```

Seen failing 2026-11-23 9:48 PM PST: `FAIL 0/8`, exit 1. A correct build prints `PASS 8/8`, exit 0. Do not edit the script to pass it. If one of its checks is wrong, repair the check with a planted fault that it
catches and a correct build that it passes, and put both readings on this item.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code), registers the page in `src/RimMandrake/Utils/boundary_check.py`, and plants faults that the tests must catch:
a key that keeps a job id; a key that drops the cause; the ticket age read as the incident age; a return that files. One fresh reader who did not make the change reads the changed files once.

## How we measure that it helped

Baseline: 50 steward tickets, 37 dropped, 31 repair tickets in 21 days. `census/items.py` 7 days after it is live. Good: 4 or
fewer steward tickets and 4 or fewer repair tickets in 7 days, with no stall over 30 min that nobody was told of.

## How it keeps improving

Two tickets with one cause in the reading name a key that is too fine; one ticket with two causes names a key too coarse.

## refs

file: src/RimMandrake/Utils/testq/steward.py
file: src/RimMandrake/Utils/testq/ingest.py
file: src/RimMandrake/Utils/ops_watch.py
