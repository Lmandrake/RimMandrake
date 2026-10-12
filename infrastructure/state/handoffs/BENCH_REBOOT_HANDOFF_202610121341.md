# BENCH_REBOOT_HANDOFF_202610121341 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610120623`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The ratchet pilot loop WORKS end to end overnight: offline fixer agents -> one live-driver agent per pass (fresh `git archive` of ALL of src/ from HEAD, 23-mod tier = ratchet_pilot + mandrake.rm.patches, restore owner's 550 list md5 ee01dae9) -> verify/close. Four live passes (Transient/bench_live_20261012{,b,c,d}/SITTING.md) took GSS 106/106, FlowWorks v2 61/61, river extension 17/0/3, Pyrelands main 20/2/5, and closed 9 items. Owner order for the night: "I'm going to bed, AFK." — ended when he next writes.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Pit-climbing cards (4)** waiting: design/RimMandrake/relative_depth_climb_design_2026-10-12.md §8 (recommended: auto ramp exit where a 4-deep cell touches 2–3-deep; step limit 2; only 4-deep traps). Rewords his 2026-09-17 "you can't climb out. Period." only on his word.
- **Ash ladder** (`ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP`): one long fire takes soil straight to deep ash (vanilla re-burns floor every interval past 7500 ticks); needs his fix choice.
- **Flat dead-end channel fills from the FAR end** (canal kernel pulls a level the whole run in one pulse); canal_fill_front was changed to accept that (conservation instead of mouth-wet). Ask if that's the intended look.
- **Pond units:** 1 pond stock unit = 1 level = 5 tank units (pond 30→22 while tank 0→40). By design, but confirm.
- **Pyrelands creature art of 2026-10-11 (68ee19c27d)** keeps selftest_art_checks red until he looks in game (his card answer: "Not yet; I'll look at it in game").
- **embergrass_regrow:** 34% d3 / 59.8% d7 against 25% / 60% targets — thresholds unruled; regrow harness's 50% survivor cut-off is an agent's guess.
- **Mishap:** a live agent ran `taskkill /IM python.exe` once (pass 1) — any other Windows python running then died.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `CANAL_FILL_FRONT_TRACE_MOUTH_STAYS_DRY` — done (live 5/5); NEXT: ask owner whether far-end-first fill in a flat dead-end channel is the intended look
- `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` — doing; owner ruled 7 card answers 2026-10-12 (in the design doc), pit-climb design + GPT review done; NEXT: put the 4 pit-climb cards (relative_depth_climb_design §8) to the owner, then file Option A build items
- `PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE` — done (ruins_scorched PASS live); NEXT: nothing
- `PYRE_SITE_REBUILD_ANIMA_STILL_SAVED` — closed this wrap (site anima0 tile 5); NEXT: nothing — remaining rows live in ASH_LADDER / BURN_LINE / STATIC_CALL items
- `RATCHET_PILOT_PROVE_THREE_MODS_ONE_LOOP` — doing; all three mods measured on the tier, 9 items closed overnight; NEXT: build the owner review queue (only rows needing him, each saying what he judges — start from 'What the owner should see' above) and write the pilot's verdict into the ratchet design doc
- `SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES` — done (both rows PASS live); NEXT: nothing
- `THEFT_ROW_REPAIR_WITNESS_WALKS_OFF` — done (liquid_checks 7/7 live); NEXT: nothing
- `WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME` — done (breach_wash held 3→0, 6 gated rows PASS); NEXT: nothing
- `WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE` — done (16 pool cells live); NEXT: nothing

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `taskkill /IM python.exe` from WSL kills every Windows python, not your probe (filed: lessons)
- A live-harness `git archive` must include ALL of src/ (Directory.Build.targets) or GSS refuses to go live (filed: lessons)
- A subagent that starts its own background wait parks forever ("Waiting for the review") — resume it with "poll it yourself now, foreground" (see: night-shift-orchestration skill §3)
- `rimflow note --owner-said "Yes."` is refused as too bare; a card answer goes in `--by-card` (see: using-rimflow skill)

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (14) — the next seat's queue

- `ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR` — Royalty anima tree spawns on Pyrelands home maps past the wild-plant allowlist (pyre_plant_distribution_correct FAIL)
- `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` — Deep design: natural ponds/lakes as excavated basins filled by the canal engine; conservation round-trip tests; GPT review; owner card
- `FACE_PATCH_FIX_ADDS_TO_A_GHOST` — MandrakePatches HeadSetForFA_Revive.xml: the Conditional's nomatch Add targets a FacialAnimation def that only FACP creates; every load without FACP l
- `PYRE_SITE_REBUILD_ANIMA_STILL_SAVED` — Pyrelands northstar fixture a32c5db7 predates the anima block (reload still has Plant_TreeAnima 1); regenerate it, and give the 180,000-tick waits a f
- `WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE` — FlowWorks rivers: ProofWeirPool pool cells=0 at a weir picked at z=12 by the map edge (works.weir_arrest_and_pool FAIL, 8 components UNMEASURED); SITE
- `THEFT_ROW_REPAIR_WITNESS_WALKS_OFF` — fw_live_checks L6 theft row: lordless villager witnesses walk off before the first theft check, so the row reads caught 0 regardless of the mod; day l
- `SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES` — Scorch-fruit's one roll lands while the grass still stands: 0 fruit in a burned cohort
- `PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE` — Pyrelands ruins: footprints 16% ash; ancient junk and some floors unscorched
- `STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY` — jawa/static_call: coerce Thing/Pawn args by ThingID (furnace warmth bar)
- `PYRE_BURN_LINE_PROVE_TWO_QUIET_DAYS` — Pyrelands burn_line bar: an arm that waits StandingBurnQuietTicks with the burn line on
- `RIVER_SITE_FIX_FISHLESS_ROT_RIVER` — river_site picked an RM_TheRot river whose WaterBody has no fish: weir_fish_draws_stock UNMEASURED ends 8 extension rows
- `ASH_LADDER_FIX_ONE_FIRE_GOES_DEEP` — One Pyrelands fire walks soil straight to deep ash (TryBurnFloor every interval past 7500 ticks on flammable rungs); ground_ash_ladder can never reach
- `WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME` — Weir breach strands the held catch inside the weir's own 2.5-cell held radius when the flow walk stops after one cell; breach_wash FAIL gates 6 river 
- `IDEO_DEITY_HUNT_GOD_WITH_NO_NAME` — Quicktest worldgen NREs in IdeoFoundation_Deity.GenerateTextSymbols for a fixed-ideo faction (1 per worldgen, 23-mod tier); faction and owner mod unkn

## Commits

```
fb002d5f96 Ledger sync: BENCH pass 4 game-state stamps
aa639416c8 BENCH live pass 4: weir breach fix PASS live (heldAfter=0, 6 gated rows PASS), v2 GREEN 61/0
de8daf7d4e Ledger sync: WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME built
a61ef148c0 WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME: criteria + built note
9e879124bf Code review: weir breach strand files CLEAN at e76408e982
e76408e982 FlowWorks weir breach: washed catch strands downstream outside the held radius
20219f37b8 BENCH live pass 3: census PASS, ash ladder MOD (one fire goes deep), regrow 34%/60%, weir fish PASS, breach_wash MOD
c9bc2e7938 HARNESS Pyrelands embergrass_regrow: burn 5000 ticks, not 3000
f3ecb2c3a1 HARNESS northstar_driver: component records keep evidenceFull
fcad2d165b HARNESS Pyrelands plant_distribution_correct: probe hosts on a standing other-roster plant cell
79c59d2588 Ledger sync: river_site fish fix implemented; harness fixes noted
ec13854219 Harness: Pyrelands probe plant from allowlist, evidenceFull + ignition log, regrow burn precondition, river_site prefers fish biomes
6fe37b6ab9 lesson: harness export needs all of src/
62ec3dfaa1 BENCH live pass 2: FlowWorks weir/canal/theft pass, v2 61/61, GSS 106/106, regrow run; file RIVER_SITE_FIX_FISHLESS_ROT_RIVER
5f73808ee9 BENCH live pass 2: Pyrelands main split run (scorch-fruit + ruins A2 pass), tick rate, FA guard live
9905d543b3 Ledger sync: WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE implemented (A1 live re-run owed), review marks
7a2a9c425c FlowWorks weir pool: upstream walk follows the local flow, not an exact quantised step (bank-edge pool=0)
1492e8f48a Ledger sync: scorch-fruit and ruin-sweep items built (A2 live proof owed)
0b14ffc5fa Pyrelands: scorch-fruit rolls after the ashes; late sweep scorches ancient junk
379ab9ad6f night fixes: FACE_PATCH + THEFT_ROW built, WEIR_POOL diagnosis (C#, not harness); ledger, review marks
... 32 more: git log --oneline 652f60dc22..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-12T13:40:06Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/gss_owner_walk_art_sheet_2026-10-11.decisions.json   served sheet / other seat output, not this session's work
 M Transient/biome_ffar/scale_ground_measured.json   served sheet / other seat output, not this session's work
 M Transient/mc_human_review/KEYSHEET.md   served sheet / other seat output, not this session's work
 M Transient/mc_human_review/keysheet.html   served sheet / other seat output, not this session's work
 M Transient/pulse_redesign_2026-10-10/deployed_D.png   served sheet / other seat output, not this session's work
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
?? conversations/2026-10-12-0625-88710e84.md   generated (conversations.py; hourly sweep commits)
?? deployed/config/ModsConfig.before-gss-restore-20261010.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-explosiveknockback.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-flowworks_vepipe.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-kineticarms.xml   generated (modset_builder ModsConfig backups)
?? deployed/config/ModsConfig.before-tier-ratchet_pilot.xml   generated (modset_builder ModsConfig backups)
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Doors/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/Textures/Things/Building/FlowWorks/Excavation/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T034753.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T040637.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T041535.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T042312.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261011T050823.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261011T052325.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/GSS   stray empty-ish path, not BENCH's this session; left alone
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T220702.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261010T230453.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261011T033650.json   generated harness output from 2026-10-10/11 live runs (not committed by design)
?? src/RimMandrake/WreckedMachines/Textures/WreckedMachines/Modules/   untracked art, not BENCH's (artpipe/FOUNDRY); left alone
```

