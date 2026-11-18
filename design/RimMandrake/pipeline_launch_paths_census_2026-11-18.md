# Pipeline launch paths census, 2026-11-18

Item `RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED`. The owner, 2026-11-18 ~10:27 AM PST: *"I think we may need to
have Dispatch have a "pause all pipeline items" setting we can easily toggle (non-code-editing) for situations like
this. We really don't want work starting (or failing to start) when we expect otherwise. And perhaps some kind of "up
next" feature we can ping that says what WILL happen in some amount of time if we do nothing, so we can confirm using
its own code..."*

Every path that can START pipeline work on a mod without a person typing a launch, read from the code at
`9a77bdcc47` (origin/main, 2026-11-18 10:40 AM PST). For each: does `enabled: false` in `maturation_dispatch.json`
stop it, does a Conductor journal hold (`kind hold` line in `design/concepts/<Mod>/journal.md`) stop it, does the
owner hold (`mod_owner_hold.json`) stop it, and does the new pipeline pause (`maturation_dispatch.py pause`) stop it.

## What happened at 10:25 AM [measured]

The Graffiti hold commit `31a4d3a06e` was committed at 10:24:34 PST. The dispatch clone (`/home/mandrake/rm/dispatch`)
pulled `b581be7487` at 10:24:37, which does **not** contain the hold (`git merge-base --is-ancestor` false; the hold
line is absent from its `journal.md`). The 10:25:04 tick read that tree and launched the road-back fixer
`rm-detached-bench-rimmandrake-settle-tribute-rival-band-ne-1795026309` (filed by the 10:19 steward run before it was
stopped). The 10:25:55 pull brought the hold in; the 10:29 tick decided Graffiti `held`. So the journal hold IS a
launch block in the tick, but it travels by git: it binds only once its commit reaches the dispatch clone, about a
minute later, and a hold written while a tick reads the old tree loses that tick. The pause below is a file in the
dispatch state folder (`D:\ClaudeWork\rimmandrake\dispatcher\maturation\pause.json`), read by every tick at the moment
it decides, with no git hop.

**Ruling on the journal hold (by evidence): it stays a real launch block in the tick**, documented as "binds once its
commit is in the dispatch clone, a minute or so after landing". It is not made advance-only: the 10:29 tick proves it
blocks the road-back fixer, and the earlier fix `RIMMANDRAKE_HONOUR_CONDUCTOR_HOLD_ROAD_BACK_FIXER_IGNORED_IT` made it
block fixers on purpose. For "stop now", use `pause <Mod>`.

## The paths

| # | Path (where it starts) | What it starts | `enabled: false` | journal hold | owner hold | pipeline pause |
|---|---|---|---|---|---|---|
| T1 | rm-maturation-dispatch.timer, `decide` offline build | capped offline builder (opus, cap_usd) | stops | stops (row `held`) | stops (mod dropped from advancing) | stops |
| T2 | tick, `decide_blind` | blind judge (blind_cap_usd) | stops | stops | stops | stops |
| T3 | tick, `decide_ingame` | live driver on a game (ingame_cap_usd) | stops | stops | stops | stops |
| T4 | tick, `cert_red_decide` | builder on red deciders, items filed | stops | stops when the gate reads the hold [guess ~70%, not traced] | stops | stops |
| T5 | tick, `cert_rerun_decide` | zero-token `certificate --run` unit (no model) | stops | stops when the gate reads the hold [guess ~70%, not traced] | stops | stops |
| T6 | tick, `pilot_holders` | one holder run on a pilot's road-back items | stops | stops (row `held` is not routed) | stops | stops |
| T7 | tick, `AUT.resolve` steward | steward run per hand-step state (steward_cap_usd) | stops | stops (`HOLDS` rows pass) | stops | stops |
| T8 | tick, `AUT.resolve` / `_road_back` / `_stop_tickets` fixer | one fixer run per road-back or stop ticket (fix_cap_usd) | stops | stops once in the clone (the 10:25 leak is the git hop above) | stops | stops |
| T9 | tick, autolock / autorepin | a commit on the concept (no run, no model) | stops | stops | stops | stops |
| T10 | tick, `slow_chores` | `backfill-cost`, finishing a dead run | not stopped (bookkeeping, no new work) | not stopped | not stopped | not stopped, by design |
| T11 | tick, `AUT.widen` | seeds a stage record for a discovered concept (a write, no run) | not stopped | not stopped | stops (held concepts are not seeded) | not stopped, by design (no run starts) |
| D1 | rm-dispatcher, Designer / DesignerCodex `chain_next` after a stage closes | a Designer run on the concept | not stopped (different file) | not stopped | stops (`owner_held`) | stops |
| D2 | rm-dispatcher, `chain_sweep` (orphaned concepts) | a Designer run | not stopped | not stopped | stops | stops |
| D3 | rm-dispatcher, run-now job at launch (any requester) | a Designer run | not stopped | not stopped | stops (consumed) | stops (refused while paused) |
| D4 | rm-dispatcher, scheduled slot of a pipeline role | a Designer run with no concept | not stopped | not stopped | not stopped | stops (pause all) |
| R1 | rm-red-dispatch.timer | one fixer per nightly red item (pipeline machinery, not a mod) | not stopped (its own `enabled`) | not stopped | not stopped | stops (pause all) |

Out of scope (they do not start pipeline work on a mod; the pause leaves them alone): the other Dispatcher roles
(Conductor, Operations, Producer, Auditor, Innovator, Artist), rm-findings-judge, rm-arteval-autojudge,
rm-artpipe-idle-fill, rm-ops-reds (files items, launches nothing), rm-deadman, rm-selftests-nightly, and every hand
command (`maturation.py launch`, `maturation_dispatch.py pilot-launch`, `designer_cleanse.py run`, `role_launch.py
run-now` by a person; a run-now is still refused at launch while paused, D3).

## Defects found

- **A Conductor hold in the journal binds only after a git hop** (the 10:25 leak): fixed by the pause, which binds
  the tick it is written; the journal hold's delay is documented in `src/RimMandrake/rimflow/roles/conductor.md`.
- **`enabled: false` raised the paused alarm**: its rows read decision `disabled`, class `paused`, so
  `maturation.paused` (OPS_MATURATION_MOD_PAUSED) counted every mod that would have launched; and it needed a code-file
  edit. The pause is a planned stop: class `planned`, counted by no alarm.
- **Nothing outside the tick honoured `enabled`**: D1 to D4 and R1 ran on while it was false. The pause covers them.
- No path was found that nothing could stop: every T path is cut by `enabled`, and every D path by the owner hold.

## How each check is proven

`selftest_pipeline_pause.py` (written first, watched failing on the base): a pause blocks T1 to T9 (each a row the
tick would have launched), D1 to D4 and R1; a live run is untouched; `--stop-live` stops and records it; no idle,
paused or stalled reading while paused; `--until` resumes by itself and says so; an unreadable pause file reads PAUSED
(never running). `maturation_dispatch.py next` forecasts with the tick's own `_tick` on a moving clock; the selftest
checks its first predicted launch equals what the following `tick --apply` launches, per tick layer, and that a
forecast with one layer dropped fails.
