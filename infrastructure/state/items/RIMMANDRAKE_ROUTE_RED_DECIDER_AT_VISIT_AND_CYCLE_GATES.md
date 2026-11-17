# RIMMANDRAKE_ROUTE_RED_DECIDER_AT_VISIT_AND_CYCLE_GATES

## spec
At the in-game visit gate (decide_ingame) and the blind cycle gate (decide_blind), cert_wait reads the certificate before
every launch. Since 02935fc15c41 a certificate that refuses only stale stamps gets the one zero-token rerun
(cert_rerun_decide); a certificate that refuses a decider recorded red (clause green) only put "waiting on its
certificate" for ever: no item, no builder, no alarm. Measured 2026-11-17 12:13 PM PST: Gimme Some Slack at in-game
visit 2, T_STUB_ART_CENSUS red (a8d27a3f6b added 26 Junction_*_p* textures with no census rows).

Decided (Conductor, Evidence-for-Ask, note of 2026-11-17 on this item): a red offline decider found at a later gate
takes the offline build's red-decider route as it stands (cert_red_decide, then execute's cert_launch): the item owing
each red decider (reused when one is open: its known_red mark, the item the route filed before, or an open item under
the exact name the route would file), ONE offline builder on them with the offline build's cap, ceiling, account gate
and max_live, booked as offline_build spend. No new stage and no stage move (the Dispatch step never moves a record, and
the spec draws no road from Stage 4 back to Stage 3). The builder's brief names the gate it stands at
(`certificate <Mod> --to <gate>`). When the slot is taken the row reads slots_full, waiting on "a free slot for one
offline builder on red deciders ..." (also after prioritise's launch-priority pass), never a certificate wait. After the
builder ends with the same reds the mod reads stopped (PAUSED, OPS alarm), never a second automatic try, exactly as at
the offline build. Stale-only certificates keep the zero-token rerun. A held (journal hold) or paused (coverage stop)
mod is untouched. At in-game acceptance the builder is not a live-game driver: it takes a run slot and no game.

## refs
file: src/RimMandrake/rimflow/maturation_dispatch.py (cert_wait, cert_red_decide, cert_launch, cert_brief, decide, prioritise, add_blind, add_ingame)
file: src/RimMandrake/rimflow/selftest_maturation_dispatch.py (cert_red_gates_main, --cert-red-gates)
related: RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES (500aea1a81, 02935fc15c41), RIMMANDRAKE_GREEN_GIMMESOMESLACK_T_STUB_ART_CENSUS_RED_DECIDER

## criteria
- At both gates, a certificate with a red decider (with or without stale stamps beside it) and a free slot -> one
  launch whose row carries cert_reds and no cert_rerun_key; execute files nothing when the item is already open under
  the route's own name, and launches exactly one builder whose brief names the item, the `--run` rerun and the gate.
- The builder's launch is booked stage offline_build; at in-game acceptance it holds no game (a second mod's visit on
  the one game still launches when a slot is free).
- While its unit is live: live; after it ends with the same reds: stopped with a Needs Conductor line, no launch.
- Slot taken (max_live reached by another mod's live run, or by an earlier mod on the advancing list): slots_full,
  waits_on names the offline builder and the red deciders; decision is never "certificate".
- Stale stamps alone at either gate: the zero-token rerun as before (cert_rerun_key, no cert_reds).
- A journal hold (owed blocked) or a coverage stop (resolve pauses it): no cert_reds launch, no file, no builder.
- Every existing dispatch selftest still passes; the one old check that asserted "the wait stands" beside a red decider
  is restated to this ruling (no rerun beside a red decider; the red route instead).

## verify
python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --cert-red-gates   # failed on base, ALL PASS after
python3 src/RimMandrake/Utils/run_selftests.py --only selftest_maturation_dispatch selftest_dispatch_pilot_holder selftest_maturation_autonomy
python3 src/RimMandrake/rimflow/maturation_dispatch.py status   # GimmeSomeSlack no longer reads a certificate wait
