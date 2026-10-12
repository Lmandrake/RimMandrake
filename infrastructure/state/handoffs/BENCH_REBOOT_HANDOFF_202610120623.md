# BENCH_REBOOT_HANDOFF_202610120623 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610111752`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner adopted the RATCHET WORKFLOW (design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md, §G = his rulings) and the pilot is Pyrelands + FlowWorks + GimmeSomeSlack loaded and pushed TOGETHER, owned entirely by BENCH for this experiment only (item RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP; FOUNDRY stays off those mods). Subagents are allowed freely until Wed 2026-10-14 16:00 PDT, then one-at-a-time returns (memory: subagent-limit-one-at-a-time). Owner review = only rows that need HIM, each saying what he judges; never hand him an unexplained sheet (today's 4-row/151-row GSS sheet fiasco).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Tap clamp is live (his pick C, installed + placement fixed), but in game it bites the short stub into the tap rather than the enemy run — he should judge Transient/bench_live_20261011/shots/tapclamp_*_crop.png.
- Pilot baseline (22-mod ratchet_pilot tier): clean load, GSS 106/106, FW validation_v2 61/61, Pyrelands NOT GREEN 9/11/13 on a site that failed its own preflight — mostly site, not proven bugs.
- FlowWorks real bugs found live: tank theft never spotted (tank blocks witness LOS), pump pour no faster than gravity. Pit-room coupling patch measured redundant (delete it).
- All 2026-10-11 rulings: design/RimMandrake/gss_flowworks_rulings_2026-10-11.md (#1–#20). Telemetry rulings: §12 of Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md.
- Ratchet design Q5 (status surface: RimPulse lines vs hub tab) never asked.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES` — done (VE pipe tab PASS live 2026-10-11); NEXT: nothing — remove from any pilot list
- `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` — validated; live partial (pipe looks save/load PASS, build-menu picker not driven; off-hose spill seen, cleaning half untested since water spills as surface fill); NEXT: drive the four-look picker and a cleanable-filth spill live in the pilot run, then verify
- `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` — validated; live FAIL on pump pour speed (PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY) and tank theft (LIQUID_THEFT_FIX_TANK_HIDES_ITSELF), UNMEASURED wakes/bottles/pit-exposure (harness); NEXT: fix those two bugs and the three harness gaps, then rerun on the ratchet_pilot tier
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — proposed, owner said go 2026-10-11 ~23:00; NEXT: claim it, fix the Pyrelands golden-site preflight + the 4 BENCH findings (theft LOS, pump pour, canal mouth dry, river site finder), rerun all three on the ratchet_pilot tier, then build his review queue (only rows needing him, each stating what he judges)
- `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED` — validated; C3 PASS live, C4 full-list overhead + C5 three live fixes owed; NEXT: run C4 on the owner's full list at a game-down when he's away

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A live harness run used a stale export (D:\Luke\dev\_rmscratch\bench_val_20261011, 14:31) and resurrected fixed bugs — always export the harness from HEAD (see: Transient/bench_live_20261011/SITTING.md)
- Review-sheet builder read a pre-rename 7-day-old def dump and missed every code-drawn texture; 4 rows served for 120 PNGs (see: design/RimMandrake/ratchet_evidence_2026-10-11/)
- ./publish refuses when another clone committed files that exist untracked/modified here; compare blob hashes, drop identical copies, merge JSON caches, then republish (see: this handoff)
- Grafana under a DETACHED supervisor gave every plugin its own visible console window (see: src/RimMandrake/Utils/telemetry/supervise.py comment)
- rimflow close --sha HEAD records the literal string "HEAD" (see: using-rimflow skill)

## Closed since the last handoff (5)

- `RIVER_NOTE_REPAIR_NAMEERROR_STILL_THERE` — c593401e50
- `PIT_CHAINS_REPAIR_STALE_SINCE_RULING` — 8931525e4b
- `EXT_FLUID_SET_REPAIR_ASKED_TOO_LATE` — 8931525e4b
- `GOLDEN_SITE_REBUILD_RIVER_RUNS_DRY` — 8931525e4b
- `EXT_LIQUID_REDS_HUNT_FIVE_AT_ONCE` — 2f31d27732

## Filed and still open (16) — the next seat's queue

- `TELEMETRY_BUILD_DESIGN_ALREADY_PICKED` — Telemetry MVP build per Transient/weekly_cleaning_2026-10-11/08_telemetry_deep_design.md (owner picks in 00_SUMMARY.md)
- `TELEMETRY_BUILD_EVERY_TICK_ACCOUNTED` — Build the hybrid telemetry stack (VictoriaMetrics + SQLite + Grafana + RimPulse alerts) on E:, 1 s test tier + flight recorder; design Transient/weekl
- `TELEMETRY_DUPLICATES_RETIRE_AFTER_QUIET_WEEK` — Design 08 P5, due after telemetry has run a week (from 2026-10-11): fold obs_events' transport/timeout/outcome into rimbridge_client._evidence and ret
- `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` — FlowWorks: enact the 2026-10-11 hose-port reversals - rigid universal pipe with wire-style art picker (#1, #8), switched-off hose drains out its open 
- `FLOWWORKS_TABS_RECONCILE_PIPES_WITH_PIPES` — FlowWorks build-menu placement follows convention: tanks, pipes, hose reels and adapters go where the major pipe mods put theirs (ruling #4)
- `TPS_VERDICT_FIX_SIX_SECONDS_NOT_THIRTY` — JawaBench sampler + tps_record reader: the sustained low/high TPS verdict counts 6 windows, which is 30 s at the 5 s cadence but only 6 s at the test 
- `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` — FlowWorks liquid networks L1-L3 (design/RimMandrake/liquid_network_semantics_design_2026-10-11.md §6): one transfer service with conservation fixes, c
- `TAPCLAMP_REDRAW_BITES_DOWN_AT_LAST` — GSS power-tap clamp v3: install owner picks (C, all four looks) and draw the upright clamp with its jaws on THEIR wire
- `TANK_LOOP_REBUILD_BOTTLES_FIND_THE_RIVER` — extensions.py toggle_tank_loop: tank_loop_on FAIL (2026-10-11, units 0..5 rose, never fell) is HARNESS/SITE: RM_FillBottleWorkGiver (prio 50, 60-cell 
- `MODCHECK_SETUP_UNMEASURED_FIX_READS_AS_FAIL` — modcheck runner.py ~529-538 records any chain-SETUP ExpectationFailed as FAIL + finding, ignoring an 'UNMEASURED:' prefix. FlowWorks extensions.py rai
- `DIG_RESET_REPAIR_ROLLED_DEPTH_REMEMBERS` — RM_NorthstarProofs.ProofResetRect resets excavation but not RM_DigDiscoveryState.rolledDepth (saved, only grows; RollsAt needs newDepth > rolledDepth)
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — Ratchet pilot: Pyrelands + FlowWorks + GimmeSomeSlack loaded and pushed together around the loop; BENCH owns everything for this experiment (FOUNDRY: 
- `LIQUID_THEFT_FIX_TANK_HIDES_ITSELF` — FlowWorks liquid theft: a witness never sees a 2x2 tank except through its Position cell (LineOfSight ends at tank.Position; the tank's own cells bloc
- `PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY` — FlowWorks basic pump on Pour drains a Dump tank at 5 units/cycle = the gravity rate (ruling Q3: pour is the FAST drain) - live L2 20 vs 25 per 1000 ti
- `RIVER_SITE_FIX_GEYSER_ON_EVERY_TILE` — river_site.py rejects every river tile with a steam geyser anywhere in the 130x130 plot grid: extension_proof's river half never gets a site
- `CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY` — extension_proof plot_C canal_fill_front FAILs in all three 2026-10-11 runs (mouth F=0 with a 300/300 source beside the dug channel); tar_front_lags_wa

## Commits

```
2bdc06cfbe Reassign four pilot findings to BENCH (pilot ownership)
fdccee2a5e BENCH live sitting 2026-10-11: summary, Pyrelands pilot baseline (NOT GREEN 9/11/13, site gate B refused), bridge released
ac27053b84 BENCH live: VE pipe tab A2 PASS (closed); ratchet pilot baseline GSS 106/106 + FlowWorks v2 61/61 on the 22-mod tier
ac600ae3df BENCH live: FlowWorks extension_proof dry half 90/7/32 (triaged); river half got no site; river_site drops rejected maps (HARNESS)
bfdab3ece2 BENCH live: FlowWorks owed checks recorded (ledger A2/A8 pass, A3/A7 fail, picker/sluice/T1); flowworks_vepipe tier
337aa7316f BENCH live: FlowWorks tier run 1 (v2 GREEN 61/61, hose scenes PASS); two MOD findings filed (liquid theft LOS, pump pour rate)
a66f9aebf0 BENCH live: GSS tier checks (proof_all 106/106, tap clamp v3 look, theft A2/A3, chemfuel ignite, cstyles A1, telemetry C3); ratchet_pilot tier
c4bd7af75a Ratchet pilot: BENCH owns Pyrelands+FW+GSS for this experiment only (owner)
b3780ead18 Ratchet pilot = Pyrelands + FlowWorks + GSS together (owner)
64106489e4 Ratchet design: owner rulings Q1-Q4 (Pyrelands pilot; keep accepted state; park features; process not spend)
5d60714542 Code review: FlowWorks 319/319 CLEAN after the rulings #18/#19, bottle-loop, pit-exposure and review-fix passes
9ea6febbab FlowWorks verify-pass fixes: hose component removal restored; touching-fluids test can fail; door comment
4170757f10 Ratchet workflow + token burst design v2: pilot-first after GPT skeptical review; dispositions and owner questions
1a662098d9 Code review + ledger sync: 7 FlowWorks northstar harness files CLEAN; extension-proof findings closed, three follow-up items filed
d2da7cbfc9 FlowWorks extension proof: a forced cut with no find is UNMEASURED until ProofResetRect clears rolledDepth (HARNESS)
e87c567430 Ratchet workflow + token burst design: draft and measured evidence (GPT consult pending)
5b83586cbd FlowWorks extension proof: first_find_sends_letter judges first-ness independently of the letter (HARNESS)
f20cfd35a5 FlowWorks extension proof: first_find_sends_letter is UNMEASURED unless the find was a first find (HARNESS)
3d305bab4a FlowWorks re-review fixes: pit route picks a reachable ladder; wet-door postfix leaves floor orders refused
13f14d7f72 FlowWorks extension proof: pond recharge counts stock plus channel fill (HARNESS)
... 119 more: git log --oneline e040d31259..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-12T06:18:53Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/gss_owner_walk_art_sheet_2026-10-11.decisions.json   served sheet output, not session work
 M Transient/biome_ffar/scale_ground_measured.json   served sheet output, not session work
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   served sheet output, not session work
?? conversations/2026-10-02-1217-54206aec.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-1952-4b4a687b.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-02-2332-d58606e4.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-03-1458-7ed5ddfd.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2105-400ef7dc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-04-2219-962263b0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-05-1426-fab8a134.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-0601-5ab77072.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-06-1305-ecebcb6f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0058-b305fb53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0059-c857706d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0120-033b16fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-0547-d6861da6.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-07-1520-6a6f7a30.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0001-cc216258.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0158-8aeef5fc.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0215-c4ae9260.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-0217-3acaea39.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1348-bac7589f.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-2294fe53.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1411-3ffd55d0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-52caf5c0.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1413-658e0588.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1414-b4b8553c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-08-1428-de9591de.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-0450-85e0a0f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-09-1308-818639f9.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0040-5e2fd376.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0049-58eabd09.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-0440-c71b568d.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-1341-91d07ad1.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-10-2102-71d8c9eb.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-0052-2f152d1c.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1934-f086ce1a.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-1953-24347684.md   generated (conversations.py; hourly sweep commits)
?? conversations/2026-10-11-2000-edefebc8.md   generated (conversations.py; hourly sweep commits)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   generated (modset_builder ModsConfig backups)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   unreferenced 2026-10-07 artpipe collect; left untracked on purpose (FW review agent)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   unreferenced 2026-10-07 artpipe collect; left untracked on purpose (FW review agent)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   generated (proof result outputs)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   generated (proof result outputs)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   generated (proof result outputs)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   generated (proof result outputs)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   generated (proof result outputs)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   generated (proof result outputs)
?? src/RimMandrake/GSS   stray 7-byte file from 2026-10-11 02:01, not this session's; inspect before deleting
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   generated (proof result outputs)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   generated (proof result outputs)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   generated (proof result outputs)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   another seat's (not BENCH session work)
```

