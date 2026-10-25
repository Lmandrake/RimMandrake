# BENCH_REBOOT_HANDOFF_202610251635 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610250220`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 Live runs are TARGETED (owner 2026-10-25: "Targeted runs should always have been policy." and test "only on the highest value informative tests"). `modcheck/cli.py run FlowWorks --item <ID> | --chains | --rows`, with `--preview` first; the whole suite needs `--full` and is a daily sweep only (standing_rulings.md §Live runs are TARGETED; design/RimMandrake/focused_testing_plan_2026-10-25.md, Option A built d0bf5d49b4, Option B next). ALMOST_OUT still on but now TWO slots (1 live + 1 offline). Owner order at wrap: "Finish your work completely, then handoff. We need to restore your memory speed settings in BIOS." — the reboot is for BIOS RAM speed.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Built offline tonight, NOT deployed (need one targeted live run): deep-water building + tower supply by swimmers + spikes pierce armour + crushed ice/melter (incl. nightside blue ice blocks) + everyone-pays/hours-of-digging — all in a8f10174f1/961105e0da.
- Proven live tonight: one-drag drawbridge, suspension towers+islands, gravel (4 rows), roof-collapse fix (0 Crush deaths), spike row fixes, swim-out probe (colonists relay-swim safely; run8 swimout_probe.md).
- Decisions BENCH/helpers took that he may veto: ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES (one ice cut melts to 4x the water it removed), RAIDER_BREACH_TUNE_FOUR_TIMES_SLOWER (default x4 labour makes raider breaches 4x slower), tower cost: he picked "keep 300 steel + 6 comps" on the card but typed "no components in towers" — BENCH followed the typed words (SUSPENSION_TOWER_TUNE_NO_CHIPS_IN_STONE).
- Sheets still unruled (served last session, ports die on reboot): modern_bridge, suspension_redesign, sluice_gate_lifts_up, grate_door_lifts_up (Transient/biome_ffar/*_2026-10-24.html).
- Spike look for his eye: D:\ClaudeWork\rimmandrake\live_20261025\run8\spikes_northfix.png

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY` — 4 gravel rows PASS live (run7); gravel recipes, rubble, underwater building unproven; NEXT: run `modcheck/cli.py run FlowWorks --item DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY --preview`, add rows for recipes/rubble if absent, run targeted, close.
- `PIT_DIG_FIX_SAND_SLIDES_BACK_IN` — sand refused live (run7); mud never tested live; NEXT: add/run a targeted mud-refused row and close.
- `PIT_SPIKES_INSTALL_TALLER_AND_FEWER` — installed, row fixes proven live (run8); NEXT: show the owner D:\ClaudeWork\rimmandrake\live_20261025\run8\spikes_northfix.png and close on his word.
- `ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN` — built a8f10174f1, not deployed; NEXT: deploy FlowWorks and run targeted rows GS_ice_cut_yields_crushed_ice, GS_crushed_ice_melts_to_water.
- `DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK` — built a8f10174f1, not deployed; NEXT: set proof runners' labour multiplier to 1.0, then run targeted GS_dig_labour_multiplier_scales_the_cut.
- `DEEP_WATER_BUILD_REFUSED_BY_LIGHT_AFFORDANCE` — built a8f10174f1, not deployed; NEXT: run targeted deepwater_build_* rows after deploy.
- `SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL` — fix built a8f10174f1; NEXT: run targeted tower_supply_swimmers_deliver after deploy.
- `SPIKES_PIERCE_TUNE_LIKE_VANILLA_TRAP` — built a8f10174f1; NEXT: run targeted spikes_pierce_armoured_raider after deploy.
- `SHOVELS_BUILD_NO_DIGGING_BARE_HANDED` — owner: "Shovels now v1."; NEXT: spawn an offline builder (digging code is free now).
- `SUSPENSION_TOWER_TUNE_NO_CHIPS_IN_STONE` — filed from owner words; NEXT: offline build (no components on towers/spans, cost scales with width).
- `DRAWBRIDGE_WIDEN_FOUR_LANES_TO_MATCH` — filed by card; NEXT: offline build.
- `RIM-1` (tickets/RIM-1.md) — code landed 66237b6a91/8ed6489289 from another session, ticket still open; NEXT: run the replay check the ticket names (src/RimMandrake/rimflow/retro_block_frontier.py) and close the ticket. Owner asked BENCH to take it.
- `RIM-2` (tickets/RIM-2.md) — audit done on the Mac (file not on Archmagi); NEXT: re-derive the stale-block list from the ledger, lift/re-state with provenance, put the 7 owner decisions to him as question cards.
- `MODCHECK_TARGETING_BUILD_STOP_AFTER_REUSE` follow-up — Option A closed; NEXT: mark chains core_offline and rivers_switch_flips offline=True (now that validation.py is committed), then file/build Option B.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A pathspec commit takes whole working-tree files, so two helpers sharing a file cannot commit apart. (filed: lessons 20261025T155916Z)
- The calm saved test site has every colonist barred from Mining; dig proofs there get no worker. (filed: lessons 20261025T143644Z)
- A live runner that removes the last colonist ends the game and the next map's terrain staging fails. (filed: lessons 20261025T134304Z)
- Carving a test site out of a mountain leaves overhead roof that collapses on fixtures (owner spotted it). (see: FILL_IN_FIXTURE_FIX_CRUSHES_COLONIST, closed 2070898e05)
- 1.6 TrySpawnYield needs the overload named, not just the method. (filed: lessons 20261025T112730Z)

## Closed since the last handoff (15)

- `MODCHECK_SITE_FIX_RAIDS_KILL_THE_RUN` — d2567be9650c178703e51820fed7fb66a89fc86d
- `MODCHECK_SITE_FIX_MECHS_WAKE_MID_RUN` — d2567be9650c178703e51820fed7fb66a89fc86d
- `DRAWBRIDGE_BUILD_ONE_DRAG_DOES_IT_ALL` — f2b17ca5e3
- `SUSPENSION_ISLANDS_BUILD_TOWERS_COST_PLENTY` — fc4a03ba37
- `FILL_IN_FIXTURE_FIX_CRUSHES_COLONIST` — 2070898e05
- `PIT_SPIKES_TUNE_SOUTH_ROW_TOO_DENSE` — 21b236986f
- `SPIKE_DESCENT_FIX_STABS_NOT_COUNTED` — eabfb55709
- `PIT_SPIKES_TUNE_NORTH_ROW_TOO_SPARSE` — eabfb55709
- `MODCHECK_VERIFY_FIX_SEAT_LOST_ON_WINDOWS` — fd9016648b
- `MODCHECK_SEAT_FIX_DETACHED_RUN_NO_RECORD` — fd9016648b
- `MODCHECK_POLICY_FIX_RECORD_NEEDS_SITUATIONAL` — fd9016648b
- `DIG_SPOIL_DECIDE_FOUR_DEFAULTS_HELD` — 82fa767908
- `MODCHECK_TARGETING_BUILD_STOP_AFTER_REUSE` — d0bf5d49b4
- `MODCHECK_HOLD_FIX_SITUATIONAL_ONLY_ROOF` — d0bf5d49b4
- `HEAVY_BRIDGE_RENAME_TRUSS_LIKE_THE_PHOTO` — ecfb698b75

## Filed and still open (59) — the next seat's queue

- `PIT_DIG_FIX_SAND_SLIDES_BACK_IN` — Pit dig check likely uses vanilla 'diggable' flag, so Sand/SoftSand/Ice/Marshy/RM_DenseMud are diggable; owner rules sand and mud cannot be dug
- `MODCHECK_SELFTESTS_FIX_TWO_RED_AT_HEAD` — selftest_l1_donor_off_round (derived subjects miss RM_BloodyMess, RM_InfectedAerofleet, RM_Scorchpod...) and selftest_run_identity ('same tree WITHOUT
- `PIT_SPIKES_INSTALL_TALLER_AND_FEWER` — Install the x2-size, half-density pit spikes (trial D:\ClaudeWork\rimmandrake\fw_art_geometry_20261024\live_defects\SHEET_spikes_trial_x2size_halfdens
- `FIXTURE_PAWNS_FIX_MISSING_FROM_PITS` — modcheck run5: 6 pawn-fixture rows FAIL with the pawn absent (census {} / not held): pit_cover_fall.heavy_springs_woven_cover, pit_fill_effects.pit_fl
- `BOTTLE_REVERT_FIX_OFF_STILL_REVERTS` — modcheck bottle_revert.revert_off_holds PASS->FAIL run5: boiling bottles changed with the revert OFF
- `ASTROFUEL_MOAT_FIX_DETONATION_COUNT` — modcheck fuel_moat_astrofuel.astrofuel_channel_detonates FAIL run5 (was UNMEASURED): detonations 0 -> 2, 13 cells, 52 burned levels; expectation not m
- `PIPE_FEED_FIX_FAR_TANK_STAYS_EMPTY` — modcheck machinery_pipes.pipe_feeds_far_tank PASS->FAIL run5: far tank unchanged through the pipe (Empty, Job: Store -> '')
- `BOTTLE_LOOP_FIX_NOTHING_FILLS` — modcheck toggle_bottle_loop.bottle_loop_on PASS->FAIL run5: (empty, filled) bottles = (0,0) after 3000 ticks (WorkGiver_FillBottle)
- `CANAL_FIRE_FIX_LIGHT_REFUSED_DRY` — modcheck toggle_canal_fire.canal_fire_on_lights PASS->FAIL run5: light refused at (129,0,131), fluid none F=0 (channel dry when lit)
- `TANK_LOOP_FIX_PROOF_TANK_MISSING` — modcheck toggle_tank_loop.tank_loop_on FAIL run5 (was UNMEASURED): no RM_LiquidTank answered ProofTank at (167,131)
- `TRAP_TRIGGER_FIX_OFF_STILL_GIVES_WAY` — modcheck toggle_trap_trigger.trap_trigger_off FAIL run5 (was UNMEASURED): woven cover gave way with trapTriggerEnabled OFF
- `BENIGN_STOPS_FIX_NOT_IN_RUN_JSON` — modcheck: clockgate.BENIGN_STOPS (resumed fixture-arrival/benign stops) is in-memory only, never written to the run JSON or log, so 'fixture arrival s
- `DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY` — Dig/fill materials per owner direction (owner note on BRIDGES_DIG_DESIGN_THREE_WAYS_EACH 2026-10-25T04:17): rock ground digs to a chunk or gravel; gra
- `REVIEW_MAP_FIX_LADDER_AND_STAKES_UNCOVERED` — selftest_review_map fails: ThingDef RM_LadderSteel and ThingStyleDef RM_BankStake_{Scrapper,Industrial,Modern,Futuristic} have no review-map coverage.
- `ANCHOR_CABLE_ART_REMEASURE_STALE_JSON` — selftest_flowworks_drawbridge_art: art_source/Drawbridge/anchor_cable_art.json no longer matches a fresh measurement of the PNGs. Fix: re-run measure_
- `MODCHECK_PITS_SHEET_REBUILD_DECAYED_UNSEEN` — Rebuild the modcheck Pits format-ratification sheet (old Transient/modcheck/Pits_20260912T231116Z.html deleted by Transient decay) so the owner can ra
- `FLORA_GRADING_SHEET_REBUILD_DECAYED_UNGRADED` — Rebuild the flora legibility grading sheet (old Transient/flora_legibility_sheet_2026-09-17/ and its prefill-only decisions.json deleted by Transient 
- `DESERT_ART_SHEET_REBUILD_DECAYED_UNSEEN` — Rebuild the desert art verdict sheet over the 218 done desertport renders (old Transient/desert_art_verdict_2026-09-20 deleted by Transient decay, nev
- `MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED` — Can colonists reach a mid-channel dug square to Restore ground it, or must they bridge first? Unmeasured; restore row only checks the order is placed
- `ISLAND_FILL_PROBE_COLONISTS_NEED_A_BOAT` — Can colonists reach a mid-channel dug square to Restore ground it, or must they bridge first? Unmeasured; the live restore row only checks the order i
- `DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT` — Live run6: a one-drag steel drawbridge rebuilt on the SAME squares (after destroy_batch site prep) reads winches=1 linked=0, winch=False/powered=False
- `PROOF_SITE_HARDEN_HUGE_TRUNKS_SURVIVE_CLEAR` — validation_core._prepare_site does not call clear_huge_plants: on run6 quicktest maps (3905 RM_HugeTrunkBlocker) drawbridge_proof sites read UNMEASURE
- `LADDER_PRISON_FIX_COLONIST_STAYS_HELD` — modcheck ladder_prison_door.lowered_lets_colonist_out UNMEASURED->FAIL run6: own colonist still held in a pit with a lowered ladder
- `LIQUID_HEAT_FIX_ICY_HUT_NOT_COLDER` — modcheck liquid_heat.liquid_heat_warms_and_chills PASS->FAIL run6: icy hut 0.0 C not colder than the control 1.1 C
- `PIT_CAPTURE_FIX_HOSTILE_NOT_PRISONER` — modcheck pit_prison_room.capture_down_from_the_lip UNMEASURED->FAIL run6: after the capture-down job the hostile is held=True but prisoner=False (cell
- `NATURAL_SLIME_FIX_WALKER_NEVER_SLIPS` — modcheck slime_slip.natural_slime_slips UNMEASURED->FAIL run6: 20 s on RM_SlimeGreenShallow, slips=0, moving=False (walker may never have moved: suspe
- `GRAVEL_REDRAW_ITS_OWN_PILE` — RM_Gravel (FlowWorks Defs/Pits/ThingDefs/RM_Gravel.xml) uses placeholder texture Things/Filth/RubbleRock; needs its own broken-rock pile sprite (stack
- `SITE_SPEC_WIRE_TOWER_COST_KEY` — northstar/site_spec.py lacked FlowWorks setting towerCostMultiplier (in Mod.cs since 2610fc8371); added in the DIG_SPOIL commit; audit that no other s
- `STOCK_SELFTEST_WIDEN_RUNNER_TIMEOUT` — selftest_flowworks_stock.py takes ~255 s, over run_selftests.py 240 s per-test cap: under --only it reports CRASH(timeout) though a direct run exits 0
- `POOL_PIT_FIX_DROWNING_CENSUS_EMPTY` — pit_fill_effects.pit_fluid_effects_per_cell FAIL run7: water pit census empty ({}), expected drowning only; likely same root as toggle_pit_fill_effect
- `BOTTLE_WASH_FIX_LOSES_BOTTLE` — toggle_bottle_dirty.bottle_wash_returns_clean FAIL run7: washing lost a bottle (Empty 0, Dirty 0, FreshWater 1)
- `TANK_POUR_FIX_FILL_MODE_NEVER_RUNS` — toggle_tank_loop.tank_loop_pour_in FAIL run7: pour-in never ran, Fill-mode tank units [0] (WorkGiver_EmptyBottleIntoTank)
- `PUMP_TANK_FIX_DRAWS_TOO_LITTLE` — liquid_pump.pump_draws_into_tank FAIL run7: channel levels 3, expected 6, moved 2
- `TERRAIN_BATCH_FIX_READBACK_REFUSES_PLOTS` — modcheck staging: jawa/set_terrain_batch reports 325/1200 cells did not read back, so plot_A_dug_channel, plot_B_fill_tiers, fire_queue_origin, dig_fi
- `SPIKES_PARITY_FIX_FLOAT32_MIRROR` — fw_scenes_spikes.py layout() runs in Python doubles while RM_SpikeDrawMath.Layout runs float32 (x0+Margin 0.05 vs 0.0499999970): threshold decisions (
- `HOSE_SELFTEST_FIX_TIMING_BAR_FLAKE` — SelfTest S4 (stiffer hose keeps its bound; screenshot solve cheap) failed on a wall-clock bar: full search 26.2 ms > 25 under a normal selftest_flowwo
- `DEEP_WATER_BUILD_REFUSED_BY_LIGHT_AFFORDANCE` — Ordinary builds (wood wall) refused on dug deep water: 'requires terrain that supports: Light'. Owner 2026-10-25 wants building where it is already un
- `SUSPENSION_TOWER_DIAGNOSE_UNSUPPLIED_IN_POOL` — RM_SuspensionTower blueprint placed on dug deep water is never supplied (Steel 0/300, Component 0/6 after ~5k ticks with materials on the bank and idl
- `JOBPROBE_FIX_CANREACH_FALSE_WHILE_REACHED` — jawa/flowworks_job_probe reports canReach=False for a mid-channel fill cell that colonists do reach and work (JawaBenchFlowWorksJobProbeTools.cs:122 u
- `DUG_SUBSTRUCTURE_PROBE_SURVIVES_UNDER_WATER` — Digging through ancient substructure leaves terrain BrokenSubstructure at d6/f6 (full of water) and a wall is accepted there; seen only on test-drive 
- `SPIKES_PIERCE_TUNE_LIKE_VANILLA_TRAP` — Pit spike damage gets armour penetration like the vanilla spike trap (run8: FlakVest turned a hit into a bruise)
- `SUSPENSION_TOWER_TUNE_NO_CHIPS_IN_STONE` — Suspension towers: drop components from towers and spans (components only on drawbridges/winches); keep ~300 steel; tower cost scales with bridge widt
- `DRAWBRIDGE_WIDEN_FOUR_LANES_TO_MATCH` — Drawbridges allowed up to 4 wide (was 1-3), matching the widest plain bridge; winch look/cost to suit
- `MODCHECK_SWAP_FIX_OUTSIDE_TRY` — modcheck runner.run: swap_to_test_list() runs before the try/finally, so a failure after MINIMAL is applied skips restore_full() (Codex review r2, run
- `MODCHECK_SESSION_FIX_STALE_LIST_ACCEPTED` — modcheck runner.run: after composing ModsConfig an already-Playing session is accepted without a restart or a loaded-packageId check, so chains can ce
- `ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN` — Ice and packed snow are diggable and yield crushed ice (acts like gravel on cold maps; supersedes 'packed snow digs as rubble'); warmed crushed ice me
- `DIG_FILL_TUNE_HOURS_OF_SHOVEL_WORK` — Everyone pays gravel/chunks to fill (no free fills for raiders/visitors), and digging or filling a cell takes hours of work
- `SHOVELS_BUILD_NO_DIGGING_BARE_HANDED` — Shovels: digging/filling needs a shovel (hands don't work); raiders need shovels and time, making pit digging a siege option. Target v1 is BENCH's rea
- `UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY` — v2 idea, new mod: utility creatures — trainable animals (and droids/machines) taking commands like 'dig this pit' or 'cut that tree'
- `L1_DONOR_SELFTEST_FIX_UNKNOWN_COMMIT` — selftest_l1_donor_off_round RED: l1_donor_off_round.py:61 Phase 0 commit list names 1f59d0939, not an object in the bench clone (git show exit 128), s
- `RUN_IDENTITY_SELFTEST_FIX_DRIFT_CONTROL` — selftest_run_identity RED on check 'same tree WITHOUT the hold IS drift (control)' (bench 2026-10-25, many dirty FlowWorks files from other helpers; m
- `SUSPENSION_RATING_FIX_PER_LANE_WORDING` — Suspension/truss descriptions say '8,000 kg per span' but the rating is per lane x lane count, every tier (pre-existing; Codex P3 on HEAVY_BRIDGE_RENA
- `FLOWWORKS_DLL_REBUILD_AFTER_SHARED_COMMIT` — FlowWorks DLL + .srchash not committed with ecfb698b75 / deep-water set: the tree held another helper's uncommitted code; next FlowWorks committer reb
- `TRANSFER_LINT_HARDEN_REFUSED_CREDIT_PASSES` — TransferChecks CommittedBlocks lint accepts Move(...)==0 as success and any nested return as an exiting refusal, so a credit on a refused transfer can
- `ICE_ART_RESKIN_BORROWED_RUBBLE_AND_SMELTER` — Crushed ice reuses the RubbleRock texture tinted blue and the ice melter reuses the ElectricSmelter texture tinted; both want their own art
- `RAIDER_BREACH_TUNE_FOUR_TIMES_SLOWER` — At the default dig labour multiplier x4 raiders now pay full fill labour, so a raider trench breach takes about 4x longer than before; re-check raid t
- `ICE_YIELD_DECIDE_ONE_CUT_FOUR_NOTCHES` — One ice cut removes one 10,000 dL notch but its crushed ice melts to 40,000 dL (a 1x1 tank per the card); owner to confirm the 4x water gain or tie th
- `ICE_MELT_TAME_STACK_FLOOD` — A stack of 25 crushed ice melting at once releases 1,000,000 dL as puddles around one cell; consider melting one unit at a time or capping the stack
- `THIRST_BLUEICE_VERIFY_WRONG_MOD_GATE` — RM_Thirst_SnowIce.xml blue-ice bucket recipes gate on MayRequire mandrake.rm.biomes but RM_BlueIce is defined in BlueDesert (mandrake.rm.bluedesert); 

## Commits

```
7404273506 ledger: OWNER stamps; conversation record
961105e0da code review clean marks (ICE_DIG / DIG_FILL files) + rimflow notes and six filed findings
a8f10174f1 FlowWorks: crushed ice + ice melter + dig/fill hours of shovel work; deep-water build, tower supply by swimmers, spike pierce
3c74e355ea ledger: close HEAVY_BRIDGE_RENAME_TRUSS_LIKE_THE_PHOTO at ecfb698b75; note deep-water build, tower supply, spike pierce (built, commit blocked on shared files); file SUSPENSION_RATING_FIX_PER_LANE_WORDING, FLOWWORKS_DLL_REBUILD_AFTER_SHARED_COMMIT; mark truss files clean; lesson on pathspec commits
ecfb698b75 FlowWorks: the heavy suspension bridge is called a heavy truss bridge (defNames kept)
9cf6f0b311 ledger sync: close MODCHECK_TARGETING_BUILD_STOP_AFTER_REUSE + MODCHECK_HOLD_FIX_SITUATIONAL_ONLY_ROOF; file L1_DONOR_SELFTEST_FIX_UNKNOWN_COMMIT, RUN_IDENTITY_SELFTEST_FIX_DRIFT_CONTROL; mark suite/cli/targeting clean
d0bf5d49b4 modcheck targeting Option A: preview, stop-after with NOT_RUN tail, incomplete-catalogue refusal, offline chains, hold on every run
a5c589ba6f ledger: file MODCHECK_TARGETING_BUILD_STOP_AFTER_REUSE (focused testing A then B) + MODCHECK_HOLD_FIX_SITUATIONAL_ONLY_ROOF
bdc6b53033 Focused testing plan: tiered, previewed, tail-cut targeting + reuse (owner 2026-10-25); GPT critique folded in
7e27550d81 Owner: shovels are v1
80da346b1f Standing ruling extended: test only the highest-value informative rows (owner 2026-10-25)
24ab0162f3 Owner cards: crushed ice, everyone pays + hours of digging, shovels, utility creatures (v2), rubble/bills defaults
82fa767908 ledger sync: close 3 modcheck seat/record/policy items at fd9016648b; file 2 runner findings; review marks
fd9016648b modcheck: targeted runs (--item/--chains/--rows; whole suite needs --full); seat-less verify still records; --policy needs --situational
d6eef50541 Owner cards: towers no components + width-scaled cost, drawbridges 4 wide, gate in the drag
4ec79e334f Owner cards: spikes pierce like vanilla, far-bank winch ok, heavy truss rename
0907f4db87 ledger run8: close north-row + descent-stabs, swim-out probe noted (relay swimming, no drowning), 4 items filed; game stamps; lesson calm-site mining disabled
00e4222f4a Standing ruling: live runs are targeted; full suite is a scheduled sweep (owner 2026-10-25)
dae496475e almost_out codex log: spikes rows
930f0fcbe7 ledger: spike descent/north-row notes (built, not deployed @eabfb55709), 2 findings filed; clean marks RM_Spikes.cs, RM_SpikeDrawMath.cs
... 44 more: git log --oneline 7b6dc0d1a8..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-25T14:36:50Z

Working tree clean apart from untracked `Transient/`.

