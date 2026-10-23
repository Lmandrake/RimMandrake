# BENCH_REBOOT_HANDOFF_202610230517 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610230105`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Order (owner, 2026-10-22 ~20:30): "Up to three subagents." — standing until he changes it. Owner rule tonight (now in standing_rulings.md + CLAUDE.md, a5db3c7f9b/4845fc61fe): **nothing reaches him unread** — look at every item yourself or via a naive Opus judge first; a walkthrough means a zoomed capture of every station/connection/path. Tonight every fix converged only once a FRESH judge or a real measurement looked; makers' own "I looked, green" was wrong 4 times (empty tank sheets, 255/256 joints, floating couplers passing joint_check, ladder west mount). Next step is ONE live batch on save d proving the ~14 built items below, then nothing goes to him without that batch's captures pre-reviewed.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Tonight's hose fixes are live-proven on map C (after.png: Transient/pile_2026-10-22/live_hose_proof/after.png); he has not looked at them in game yet — that look is tomorrow's deciding measurement (trickle_vs_batch.md).
- Joint fittings were never off in his config (absent = default ON); my earlier claim was wrong, told him.
- Hoses still pass under batteries/buildings by his "not yet" (HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE stays his).
- Saves: b (his walk, untouched), c (maps C+R, rebuilt), d (art look staging) — game was up paused on d at wrap; he is switching accounts.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING` — done (217dab3d98, 031b4299a2): art.py install takes --by-card/--per-ruling/--why; 20 correction events appended; NEXT: run `rimflow show ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING` and close it if still open; then take CARD_PICKS_CORRECT_OLDER_ONES_STILL_SAID (110 older keeps)
- `C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING` — built (caa3d759b4), battery moved inland — reasoned, not seen; NEXT: rebuild map R C1 in the live batch and capture the cord
- `C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE` — built (f4033cbd6d); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close
- `CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE` — built (caa3d759b4); offline 8/8 stations on whole-river crossings; NEXT: rebuild map R C11 in the live batch and capture R1/R2
- `FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE` — built (c22c6bb5bd), tint removed; offline render only; NEXT: capture the R2 ford in the live batch and judge by eye
- `HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE` — closed live (HW1 PASS maps C+R); NEXT: none — confirm closed with `rimflow show`
- `HOSE_FITTING_GATE_BUILD_BELIEVED_HOSEMATH` — done (9c9c40f430/8e74648b31): selftest_hose_fittings.py, 43 known-red ports tied to items; NEXT: none; the known reds drain via the TANK_*_REDRAW items
- `HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES` — partial: A4 passed live on map C; A3 owed on map R; joint_check now also fails on map R's known hose-over-hose crossing until the raised-hose fix lands; NEXT: run `northstar/joint_check.py --all-maps` on save d in the live batch and record A3
- `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS` — built; HW1 PASS live; owes A3 (a wall built across a laid hose); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (A3: build a wall across a laid hose)
- `HOSE_TANK_LAY_FIX_ENDS_ON_LID` — built (38d29be950); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (lay a hose onto a tank square)
- `HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED` — built (3e3c44d9fc); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (pause, build a wall, order a hose across it)
- `JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN` — built (6648e51e9a); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close
- `MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS` — built (6199b2ed13), 4 fittings per Modern tank; TankArtEdges.cs NOT regenerated (selftest_tank_art_edges.py red); NEXT: run `python3 src/RimMandrake/FlowWorks/selftest_tank_art_edges.py --write` after checking the measurer ignores fittings, rebuild, commit; then the live look
- `PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO` — built (e3077946c3); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (staged animals/prisoners on maps C and R survive proof_hose)
- `PROOF_REELS_FIX_STILL_STAGED_WEST` — built (3fa1dc487d); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (re-run the four proofs)
- `SCENARIO_REELS_FIX_STILL_FACING_WEST` — done live; NEXT: none — confirm closed with `rimflow show`
- `TANK_FLANGE_FIX_HOVERS_MID_PIPE` — built (f4033cbd6d); its edge table is stale since 6199b2ed13 (see MODERN_TANK_PORT pointer); NEXT: regenerate TankArtEdges.cs first, then zoom C3 north in the live batch
- `TANK_STUB_HUNT_POINTS_AT_NOTHING` — fixed by c750fe9056 (old reel link); NEXT: confirm on C3 north capture in the live batch and close
- `X8C_WALKER_FIX_FELL_THROUGH_THE_FLOOR` — built (514ce98a79); NEXT: in the one live batch (deploy HEAD FlowWorks on fw_gss_sitting, load save RM_fw_walkthrough_20261022d), run its live check and verify/close (validation_v2 X8c row)

- `PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN` + `VALIDATION_HOSE_REELS_FIX_STILL_WEST` — helper stopped mid-edit at wrap; UNTESTED partial edits sit uncommitted in 9 src files (validation_core.py, validation_v2.py, validation_hose.py, liquid_checks.py, live_session.py, raid_trench_proof.py, selftest_proof_hose.py, water_scenes_mock.py, water_scenes_walk.py), copy at D:\ClaudeWork\rimmandrake\patches\zoo_reels_partial_20261022.patch; NEXT: review that diff, finish or `git checkout` only those 9 files (they are BENCH's), run their selftests, commit.
- `Code review of tonight's files` — helper stopped; f1dd2b2abf marked 40 clean, rest PENDING in Transient/pile_2026-10-22/review_tonight.md; NEXT: resume from the PENDING rows of review_tonight.md.
- `No-blocking day 2026-10-23` — owner's pick; NEXT: run the day without blocking cards, auto-dispatch a fixer on each filed bug, tag who-found-it on every new item, then re-run bottleneck_measure + trickle_vs_batch (HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM).
- `TEST_PC_BUILD_SECOND_GAME_AT_HOME` — owner picked "A Windows PC at home"; name/address not given; NEXT: ask him the machine's name, then plan Steam+mods+bridge+SSH.
- `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY` + TANK_SOUTH_PORT/TANK_LANE_FITTINGS/TANK_NS_PORTS/PUMPSTATION_SOUTH_PORT redraws — filed, not started; NEXT: take after the live batch, art through a naive-judge pass before any card.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A test that measures with the function under test is blind (wall seam hid 18 days) (filed: lessons 20261023T024112Z).
- GSS connector test measured pieces the draw code stopped using and run_selftests never ran it (filed: lessons 20261023T024110Z).
- joint_check measures to the port the CODE defines, not to a fitting in the ART — floating couplers passed (see: HOSE_FITTING_GATE_BUILD_BELIEVED_HOSEMATH).
- The 256 reel-joint cases run only inside selftest_flowworks_stock.py's C# app, not the selftest_hose_*.py scripts (filed: lessons, MODERN_REEL_FIX_ONE_JOINT_IN_AIR).
- An image-builder rerun for one building overwrote the other buildings' option sheets after they were checked (filed: lessons, modern art helper).
- A config file omits settings at their default — absent ≠ off (see: JOINT_FITTINGS_RESTORE_SWITCHED_OFF_AT_HOME).
- proof scripts' cleanup deleted every non-colonist pawn on review saves (see: PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO, PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN).
- GPT draws side-wall perspective right only when told to "think about which faces the camera can see" (filed: lessons 20261023T023000Z).

## Closed since the last handoff (7)

- `PREREVIEW_ENFORCE_EYES_BEFORE_HIS_EYES` — 4845fc61fe
- `JOINT_FITTINGS_RESTORE_SWITCHED_OFF_AT_HOME` — c8f8307b34
- `JOINT_CHECK_FIX_ALL_MAPS_SAW_ONE` — f58ceac1d8
- `MODERN_REEL_FIX_ONE_JOINT_IN_AIR` — 5bed576967a1259ae0c5ed23f5b63de373905008
- `MAP_R_BUILDER_FIX_FORTY_BANKS_REFUSED` — 6a010b3dec
- `SCENARIO_MOCK_HARDEN_INKS_THE_REAL_KEYSHEET` — 17586b65cafd
- `HOSEPROBE_SUMMARY_FIX_WANDERED_OFF` — bb70179f9d

## Filed and still open (40) — the next seat's queue

- `RYCRIT_RESTORE_DEF_AND_ART_BOTH_MISSING` — Rycrit: RSW_Rycrit has no def and an empty texture folder (art helper saw it 2026-10-22, never filed)
- `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL` — Owner reviews every biome's special mechanics, rites and items for fluff (inventory: design/RimMandrake/special_mechanics_review_2026-10-22.md)
- `MODERN_TANK_REDRAW_NOT_JUST_RED_PAINT` — Modern FlowWorks tanks/reels redrawn as real modern products (poly tanks, boxed reels), not recoloured Jawa art
- `PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT` — Redraw the portable ladder so it stands up against the pit wall (vertical profile)
- `PIT_LID_FIX_VICKY_PEEKS_THROUGH` — Pawn beneath a concealed pit's lid draws on top of the lid with a dark square
- `HOSE_JOINTS_REPAIR_ENDS_MISS_THE_NOZZLES` — FlowWorks: hose/reel/connector joints visibly broken on the walkthrough save (ends miss reel nozzles, stubs float, junction stubs)
- `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS` — FlowWorks: laid hose drawn under a battery and through a wall on the walkthrough save
- `HOSE_LOOK_DECIDE_OVERGROUND_OR_UNDERPIPE` — FlowWorks: keep over-ground hoses (fix the joints) or draw hoses under like pipes? (owner's question; audit answers it)
- `TEST_SWITCH_FIX_NO_SCRIBE_NO_PEACE` — FlowWorks settings registry red: depthEngineLiveForTests has no Scribe key (selftest_extensions, selftest_settings_registry, validation_v2 O2 FAIL sin
- `TEST_PC_BUILD_SECOND_GAME_AT_HOME` — Second RimWorld test machine: a Windows PC at home (owner). Needs its name/address, then Steam+mods+bridge+SSH setup for the test belt
- `PHONE_SENDS_ENFORCE_STILL_HONOR_SYSTEM` — Phone images (chat_review.py PNGs sent with SendUserFile) have no mechanical pre-review gate; propose a PreToolUse hook on SendUserFile requiring a pr
- `REVIEW_SHEETS_LINK_REPAIR_POINTS_AT_NOTHING` — .claude/skills/review-sheets (tracked symlink) points at /mnt/d/Luke/dev/review-sheets, which no longer exists (skill now in MandrakeWorkflows/skills/
- `HOSE_CLEAR_FIX_WALL_SEAM_LOOPHOLE` — FlowWorks hose: Clear/WallDepth lets a hose lie on the seam between two wall cells (drawn through a wall)
- `SCENARIO_REELS_FIX_STILL_FACING_WEST` — FlowWorks stagers build every hose reel West (rot 3) although reels turn; 10 walkthrough hoses U-turn to targets behind the reel
- `MODERN_PUMP_REDRAW_SAME_RED_DIFFERENT_DAY` — Modern FlowWorks pump, sprinkler, containers, hose ends and joins are the same red repaint; redraw as real modern products
- `TANK_FLANGE_FIX_HOVERS_MID_PIPE` — joinFittings flange at a pipe entering a tank from the south is drawn ~0.5 cell below the tank skid, mid-pipe (map C C3 north, pipe 17,43 -> tank 17,4
- `TANK_STUB_HUNT_POINTS_AT_NOTHING` — FlowWorks: a sideways pipe stub under the tank at C3 north (17,44) ends in air (audit D4); offline cause not found
- `PROOF_REELS_FIX_STILL_STAGED_WEST` — Proof stagers still build every reel West via validation_core.reel_west (proof_hose, lines_proof, walk_gaps_proof, pipe_levelling_perf_proof): use ree
- `JOINT_CHECK_WIDEN_PIPE_STUBS_UNSEEN` — Joint check covers hose ends and reel links only: pipe-to-tank/machine stubs, risers and flanges (SectionLayer_RM_PipeCentreStubs, RM_LiquidJoins) are
- `ART_INSTALL_WIRE_BY_CARD_FLAG_MISSING` — art.py install has no --by-card flag, so two helpers recorded card picks (tank picks fb34c9bc2d, ladder 41c06f6a2b) under --owner-said with a '(by car
- `PROOF_HOSE_SWEEP_FIX_ATE_THE_ZOO` — proof_hose.py destroy_bulk nonColonists (l.642, l.708) runs on walkthrough saves with --no-fresh-map: save c map C lost all 9 staged non-player pawns 
- `CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE` — C11 on map R tile 1246: R1 (n=9) and R2 (n=4) crossings run ALONG a shoreline inlet at z 105, not across the river (RV.crossings sorts narrow first); 
- `C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING` — C1 map R: the battery-to-pump PowerConduit pair (bank row) draws as a blue GSS cord arcing north over the river. Look/MOD (GSS cord sag direction). Ca
- `C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE` — C1 map R tall tank (Fill): a dead-end L pipe stub under the tank beside the trunk outlet, and the pump pipe meets the tank at its skid (the sign promi
- `HOSE_TANK_LAY_FIX_ENDS_ON_LID` — MOD: a hose laid to a tank's own square ends ON the tank 0.207 cell off its port (joint check FAIL free_on_port x4, save d staging); snap to the port 
- `MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS` — MOD art: Modern tall/IBC/XTall tanks draw narrower than the 2x2 footprint with no fitting at the hose port; coupler sits ~0.3 cell off the wall, bare 
- `MODERN_REEL_SHADOW_FIX_BOX_TOO_BIG` — MOD: Modern FA hose reel casts a hard-edged square shadow much larger than its slim pedestal art (stored E, laid N, laid S)
- `CELL_RECT_SHOT_FIX_COLONIST_BAR_PHOTOBOMBS` — HARNESS: jawa/clear_ui + rimworld/screenshot_cell_rect still capture the colonist bar across the top of tall rect shots
- `FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE` — RM_FordStones reads as a dark smear (map R R2 capture R_S2_ford_zoom.png): the def's <color>(128,124,112) halves an already mid-brown texture (mean RG
- `HOSE_FITTING_GATE_BUILD_BELIEVED_HOSEMATH` — Offline image gate: every hose port has an opaque drawn fitting at that point
- `TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT` — Tall/cargo tanks: hose ports on the SOUTH side have no drawn fitting
- `PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN` — validation_v2 (8 sites, run by live_session --current-map), liquid_checks, raid_trench_proof, water_scenes_walk and prep_site still destroy_bulk nonCo
- `VALIDATION_HOSE_REELS_FIX_STILL_WEST` — FlowWorks/validation_hose.py (run by proof_hose's hose/maze/relay/carry blocks) still stages reels West via V.reel_west_ops (l.157, 333, 578, 752); it
- `CARD_PICKS_CORRECT_OLDER_ONES_STILL_SAID` — Art ledger: 110 more owner keeps (live BENCH+FOUNDRY shards, archives not read) carry 'by card' inside said (Pit ramp 10-15, Venomvine Q4 10-16, Uvak 
- `HOSE_WORLD_SNAPSHOT_FIX_STALE_WHILE_PAUSED` — MOD: RM_MapComponent_Hoses.World() caches the CordWorld per TICK, so buildings placed while paused are invisible to CheckInstall/route planning until 
- `ARTLEDGER_SELFTEST_DIAGNOSE_CROWD_CRASH` — selftest_art_ledger_fixes.py CRASHed once (uncaught RuntimeError, rc 1) in an 8-test run_selftests --only batch beside selftest_art_provenance.py's ow
- `LADDER_DRAFTS_RETIRE_SEVEN_FOR_ONE` — src/RimMandrake/FlowWorks/art_source/LadderPortable: the installed RM_LadderPortable_* are byte-identical to gen_a8.py's output (chain gen, gen_a2, ge
- `TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY` — Tall/cargo/XTall tanks, Scrapper/Industrial/Futuristic looks: west/east hose lane ports have no drawn fitting (gap 0.16-0.43 cell)
- `TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR` — RM_LiquidTank (all looks) north+south and UniversalCargoTank (non-Modern) north: hose ports couple 0.4-0.6 cell from any drawn art
- `PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE` — Pumping stations (Kludged/Repaired): the one hose port (south, Position+FacingCell rule) sits 0.18-0.20 cell off the art

## Commits

```
b0cb793f0a conversations: catch-up 43 record(s)
ce8a4bda5d Ledger + code-review shards at BENCH wrap-up
fca025bc6b reel_intake_geometry: inner loop no longer shadows the rotation k; 2-space block re-indented, unused enumerates dropped; output unchanged (--check OK)
41e1a6f8ff pipe_levelling_perf_proof: LAYOUT doc said both reels are built West; rig_ops faces each at its lip (West, East)
ccaa90ba1a HoseProbe: RelayEnd's Round-7 summary back on RelayEnd (WallCrossJson had two, RelayEnd none); HoseWallSeamChecks S4 header said west-facing reels, the sweep rolls every facing. Comment-only; FlowWorks SelfTest 840/840, hose 182/182 + 403/403; DLL rebuilt (HOSEPROBE_SUMMARY_FIX_WANDERED_OFF)
9250d9f1cc Ladder art source: gen_a8 rebuilds A7's north itself (it read OUTDIR/optA7_north.png, failing unless gen_a7 ran first; output byte-identical, = installed art); dead sh_n / THICK=5 / duplicate cx removed. Ledger shard carries two filed review items plus peers' pending events.
542a7899ea Code review: 40 files changed tonight marked clean (full or diff-scoped); progress in review_tonight.md
8f836efb69 Review fixes: proof_hose HW1 reads an unanswered census as HARNESS, not 'no laid hose' SITE; Rites validation no longer claims set_setting refuses static fields (BRIDGE_STATIC_SETTINGS_FIELDS_1 fixed that)
4426b0715b Review fixes: DeepDrill validation drops unused REPO; DivingInteraction validation docstring/toggle-count comment were stale, temperature check no longer TypeErrors on a missing hatch row
1e65643aa8 Transient: pin review_tonight.md (code review progress skeleton)
ce8c095ce1 selftest_tank_art_edges: measure Modern tall/IBC/XTall body under the hose fittings (TANK_FLANGE_FIX_HOVERS_MID_PIPE) Fittings reach the canvas edge and bury the wall; the outline comes from modern_port_fittings' base, pinned pixel-equal to the installed PNG. Table unchanged (0 insets were the fittings, not the tank), so no DLL rebuild.
ae1da74c40 Ledger: VEE_FLORA_VENTS_BUILD_XML_FIRST prep note, lease released
ef02a5ba11 Ledger: note RimPulse L1 checks wait on the deploy item
f35ddc1d7e Ledger: six RimPulse defect items implemented
490c8ccee7 RimPulse review fixes: a recovered occurrence stays recovered when its window later closes; digest lists recovered incidents; services light
bc123a9e3f Ledger: VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR built
6b37f42706 lesson: staged new files can vanish from a shared clone's index
ca5da37844 Settings screens selftest: register SolarMirrors' new 'Solar panels' group (scope Now: read every power tick)
be3f911980 DeepDrill: DLL built from committed source (tile resource ports)
df5bc20e2f DeepDrill: port VEE deep-ore rich/devoid, mineral devoid, spacer component deposits (RM_ mutators)
... 166 more: git log --oneline e623626548..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-23T04:27:41Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/pile_2026-10-22/art_helper_day.md   BENCH art helper (day notes, Transient)
 M Transient/pile_2026-10-22/belt_failures.md   BENCH belt helper (Transient log)
 M src/RimMandrake/FlowWorks/northstar/liquid_checks.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/live_session.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/raid_trench_proof.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/selftest_proof_hose.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/validation_v2.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/water_scenes_mock.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/northstar/water_scenes_walk.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/FlowWorks/validation_hose.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
 M src/RimMandrake/Utils/validation_core.py   BENCH zoo/reels helper, stopped mid-edit — untested partial (see pointer)
?? deployed/config/ModsConfig.swap-active.json   BENCH tier marker — KEEP (restores owner's list via modset_builder --restore)
?? src/RimMandrake/FlowWorks/northstar/deep_lake_proof_result_20261022T153940.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134328.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134727.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T134835.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135233.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135310.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135339.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135449.json   BENCH belt helper — proof result dumps, disposable
?? src/RimMandrake/FlowWorks/northstar/live_session_result_20261022T135550.json   BENCH belt helper — proof result dumps, disposable
```

