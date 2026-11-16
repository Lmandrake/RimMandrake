# RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET

Plan step 5 (`design/plans/2026-11-15-holder-pipeline-fusion-build.md`; spec `design/specs/2026-11-15-holder-pipeline-fusion.md` §3.1, §3.3, §3.4: Option A, the first half of his pick "Resumed session per mod
(Recommended)", "built as the packet version first, falls back to it"). The dispatcher grants the holder lease, starts
each pilot-mod stage run from the packet at the stage the mod is at now (his plan change, ledger OWNER
2026-11-16T05:57:46Z: "It should roughly start where it last was in the pipeline"; never a restart from stage 1), records run.start and run.end itself, and flags a run that ends without a
checkpoint of the fixed shape (done, next, ruled out). The holder works all of its mod's open tickets together.

## spec

- `modledger.launch(root, mod, lease, role)` and `modledger.end_run(root, mod, run, status)` as the acceptance test's
  contract says; `pilot_mods` in modledger.json (the three).
- maturation_dispatch.py launches pilot-mod stage runs through them; the brief carries the packet, then the stage's own
  instructions; the holder's env carries `RM_MODLEDGER_WRITER=HOLDER.<lease>` so it cannot append to another shard.
- Live: one real pilot stage run started from its packet, UNRUN until it runs.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_packet_runs_accept.py` — expected `PASS 10/10`.
Watched failing at filing on 6a171f08f2: `FAIL 9 of 9`; with the stage clause added, on df07a4a7de: `FAIL 10 of 10`
(no launch, end_run or pilot_mods).

## criteria

- the acceptance test passes; selftest_modledger and selftest_maturation_dispatch stay green;
- the live run is recorded, or named UNRUN with its command.
