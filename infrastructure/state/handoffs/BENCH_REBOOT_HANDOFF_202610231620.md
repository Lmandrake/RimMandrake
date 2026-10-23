# BENCH_REBOOT_HANDOFF_202610231620 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610230517`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Today (2026-10-23) is the owner's **"go as far as you can without me" / no-blocking day** — he confirmed it at ~09:00 PDT before leaving for work. Rules for the day: never park work on a card; take delegated calls (judge agents, `--why "delegated: <class>"`), auto-dispatch a fixer on every bug filed, tag who-found-it on new items, batch everything that needs him into ONE evening list; at day's end re-run bottleneck_measure + trickle_vs_batch (HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM). **BENCH now owns ALL FlowWorks + Gimme Some Slack work** (owner 2026-10-23, seat files 575795bb4e/3713dd99fb); FOUNDRY does none. The plan and wave layout: `Transient/flowworks_takeover_20261023/PLAN.md`; every owed live check, ordered by map: `Transient/flowworks_takeover_20261023/BRIDGE_RUN_1.md` (182 criteria, ~4.5 h). Parallel helpers in ONE clone collide on the FlowWorks DLL / SelfTest csproj — helpers must commit SOURCE only (./publish rebuilds the DLL from committed source) and keep disjoint file sets; the brief template is in this session's scratchpad wave_brief.txt (copy it into the next brief). New pipeline: art goes through skill `rimworld-art-evaluation` (Opus first → GPT targeted second look → reason-driven regen ≤3 → shadow sheet); machine art needs an in-game capture to be judged.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- One evening list for him (no cards while he works): FlowWorks north-star sitting + water scene S5 (`FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING`, `WATER_SCENES_S5_JUDGE_THIRD_DRAFT`, his 2026-10-21 card held them until after the walk); biome-mechanics fluff review rows (`BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL`); whether reels get a hose guide (`REEL_FAIRLEAD_DECIDE_AFTER_THE_WALK`); blood source for the bottle loop's hemopack check; the art-eval pipeline's first shadow sheets.
- Shipped with a flag: weir white water and river-works stakes/silt trap were INSTALLED on a "held — capture owed" pipeline result; reels/well, bollards, pumps installed on his cards; two HoseReviewChecks tolerances were loosened by the reel install (c4551e2c2e) — the reel-link fixer found them not implicated.
- His live walk is the real test of ~25 fixes made today; Bridge run 1 (agent) is proving them now and leaves save RM_fw_walkthrough_20261023e on the new build for his next walk. Press F11 if the UI vanishes (screenshot mode).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS` — built; rehearsal now times out cleanly (d9a1934bd0) but never ran live; NEXT: run its row from BRIDGE_RUN_1.md §2 and close on 0 levels lost
- `PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES` — built and installed on his words (c10fa6c815), UnderCouplerReach regenerated (ef6d9ce8a9); NEXT: judge Bridge run 1's pump-port captures with the art-eval pipeline and close or regen
- `RIVER_MUFFALO_FIX_SHOWS_ITS_REAR` — builder fix proved offline (d356baa2a4); NEXT: capture station R1 on a rebuilt map R in a bridge run and close
- `BRIDGE_RUN_1` (agent, running at handoff) — deploying + proving the owner's walk fixes, Modern-candidate in-game capture, the first-priority proof rows; writes Transient/bridge_run_1_20261023/RESULTS.md; NEXT: read RESULTS.md, run the art-eval pipeline on its captures (Modern candidates first), close what passed, then run the rest of BRIDGE_RUN_1.md §2-§8
- `SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE` + `ANCHOR_BASE_REDRAW_STILL_LYING_FLAT` (helper running at handoff, owns the uncommitted Drawbridge/*.cs + DrawbridgeChecks.cs + render_cables.py edits) — NEXT: check `git log -- src/RimMandrake/FlowWorks/Source/Pits/Drawbridge` for its commit; if the files are still dirty and no helper runs, finish/selftest and commit them
- `MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL` — 13 candidates in Transient/modern_style_20261023/cand_r3/, none installed (GPT wanted an in-game capture); NEXT: re-run the pipeline on Bridge run 1's Modern captures, install the accepted ones, build the shadow sheet
- `NO_BLOCKING_DAY_2026_10_23` — the day's experiment; NEXT: at day's end re-run bottleneck_measure + trickle_vs_batch (HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM) and write the evening list

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Six helpers in one clone: a local winbuild leaves an uncommitted DLL that blocks everyone's ./publish; commit source only (filed: lessons, wave_brief.txt rule).
- Parallel selftest runs collide on the shared SelfTest build folder ("file locked"); retry after ~40 s (filed: lessons 2026-10-23, area H/B).
- Machine art cannot reach ACCEPT from an offline mock — capture in game before spending pipeline rounds (filed: lessons, modern style helper).
- `rimflow close --none-owed` on an item whose live check is still owed is terminal — use built/implemented with the owed criterion instead (see: SIGNS_BARRELS_VERIFY_ON_REBUILT_WALK_OWED).
- F11 is RimWorld screenshot mode (hides all UI) beside the owner's F10 screenshot key (see: KeyPrefs.xml).

## Closed since the last handoff (29)

- `CARD_PICKS_CORRECT_OLDER_ONES_STILL_SAID` — 1611d5fe7175
- `SELFTEST_EXT_LID_ROW_FIX_UNREGISTERED` — 465f61350b
- `SELFTEST_HOSE_P3_SHAPE_FIX_UNHOOK_ADDED` — 465f61350b
- `LADDER_DRAFTS_RETIRE_SEVEN_FOR_ONE` — 34e6494ba613
- `REVIEW_SHEETS_LINK_REPAIR_POINTS_AT_NOTHING` — 1b05e8471d
- `ART_PAINTERLY_RESTORATION_1` — 42678b8eff
- `TANK_FLANGE_FIX_HOVERS_MID_PIPE` — 7d88eac325
- `TANK_STUB_HUNT_POINTS_AT_NOTHING` — 7d88eac325
- `C1_TANK_STUB_PRUNE_PIPE_TO_NOWHERE` — 7d88eac325
- `CREEK_STATIONS_REDESIGN_FORDED_A_PUDDLE` — 7d88eac325
- `PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE` — 7d88eac325
- `FORD_STONES_REDRAW_LOOK_LIKE_A_SMUDGE` — 7d88eac325
- `RIVER_DOME_DIAGNOSE_WHITE_BLOB_AFLOAT` — 3158150111
- `KLUDGED_HOSE_PRUNE_TAIL_TO_NOWHERE` — 3158150111
- `TERRAIN_CROSSES_DIAGNOSE_DARK_BLOTCHES` — 86a4298f22
- `LEVELLING_FILLS_DIAGNOSE_WATER_GOES_MISSING` — c215f9ab1d
- `POLE_CABLE_FIX_FORGOT_TO_SAG` — 1798323af6
- `MODERN_TANK_PORT_REDRAW_COUPLER_FLOATS` — 1798323af6
- `WALK_KEEP_FIX_SNAPSHOT_STAYED_HOME` — 3d06a6028672
- `PROOF_SWEEPS_FIX_OTHER_ZOOS_STILL_OPEN` — 3d06a6028672
- `C1_CORD_REWIRE_BATTERY_GOES_SKINNY_DIPPING` — 3bcca45f4b62
- `HOSE_SELFTEST_REPAIR_STALE_PORTPOINT` — db2c353b32
- `HOSE_BEND_FIX_SHAVES_WALL_CORNERS` — dc0d3621a4
- `HOSE_LEADIN_FIX_STUB_IN_THE_CANAL` — dc0d3621a4
- `PORTABLE_LADDER_REDRAW_STAND_UP_STRAIGHT` — 41c06f6a2b
- `SAND_SHOVEL_DIAGNOSE_DIGS_UNDER_WALLS` — 17e90dc6ca1c2c3699fedb8699f7d3cb6556ae90
- `SUSPENSION_ART_RESKIN_HE_SEES_FIRST` — 41fb948b5ef0b6522f35c473f9fff32c014603ae
- `HOSE_NOZZLE_DIAGNOSE_HUGS_WALL_ENDS` — 4cff1a0718
- `FW_SELFTESTS_MEND_TWO_RED_AFTER_PARITY` — 0df38f45e0

## Filed and still open (59) — the next seat's queue

- `PURGE_CARDS_FIX_WRONG_POCKET` — Art ledger: 19 owner purge events carry card text in said; art.py correct-provenance refuses non-ruling events — extend it to purges or record why the
- `ART_RESOLUTION_MEASURE_AT_MAX_ZOOM` — Re-measure whether stored art resolution >128 px is visible at the MODDED max zoom-in (resexp was vanilla zoom only); until then canvas sizing stays g
- `ART_GUARD_FIX_REFUSES_THE_DELEGATE` — art_guard (pre-push) refuses a delegated art install recorded with --why alone (reason 'agent-why' not mechanical), contradicting delegation_policy.md
- `QUIET_SITE_FIX_JAILBREAK_BY_VANISHING` — HARNESS: validation_core quiet_site profile 'hostiles_removed' vanishes hostile-faction PRISONERS on a review save: liquid_checks --only L2 on save d 
- `JOINT_CHECK_FIX_TAPS_LOOK_LIKE_NOTHING` — HARNESS: joint_check pipe_stub FAILs pipe ends fed by a bleed well (RM_LiquidTap 8-way, map C 25,130) or ending a sprinkler line (RM_SprinklerHead bes
- `WALK_PIPES_PRUNE_TWO_TAILS_TO_NOWHERE` — SITE (walkthrough builder): two real dead-end pipe tails on save d: map C 131,41 (pipe ends capped beside the 'adapter' label, nothing there) and map 
- `RELAY_PROOF_FIX_SITE_WIPES_THE_REVIEW` — HARNESS: validation_hose run_relay (proof_hose --only relay) destroy_batch All + Soil paint over SITE_R (12,97,88,10) on the current map even with --n
- `CENTRE_CELLS_FIX_WALK_THROUGH_WALLS` — HARNESS/instrument: HoseProbe census centreCells disagrees with the drawn pose: reel 104,208 routed round a wall's south end (bbox zmin 205.15, wallCr
- `RIVER_MUFFALO_FIX_SHOWS_ITS_REAR` — Review map R station R1 (review_map_rivers.station_ops r_current): the staged Muffalo spawns facing north and reads as a plain white dome in the water
- `LEVEL_REHEARSAL_FIX_POURS_ON_FULL_PONDS` — HARNESS: pipe_levelling_perf_proof --rehearsal stages its basins (RM_NorthstarProofs.ProofStageBasin, A = x5..95) straight over walk_gaps_proof's fill
- `MAST_PIPE_MEND_STOPS_SHY` — Map R C1 (r2/pole_span_after_fix.png): each ground pipe stops ~0.2 cell short of its Scrapper mast with no drawn join to the riser; also r2/C1_rebuilt
- `CORD_LOOP_UNTANGLE_LASSOED_A_PIPE` — GSS canned slack loop (_Shared/SlackGeometry/CordLayer.AddLoops, LoopsPerCell 0.35; AllClear sees only walkability) is spliced over a cell holding ano
- `UNDER_COUPLER_DECIDE_CORNER_CROWDING` — Modern tall/XTall tanks: south lane-0 and west lane-0 under-coupler pipes meet on open ground below-left of the body (no base plate), even clipped
- `CARGO_UPPER_PORT_DECIDE_NOTHING_UNDER` — RM_UniversalCargoTank Scrapper/Industrial/Futuristic upper W/E hose port (z 1.5): no opaque body on the axis, so no under-coupler is drawn
- `HOSE_SIDEPORT_FIX_AIMS_AT_OLD_MIDPOINT` — A hose arriving from the side at a moved tank port (TankPortGeometry.MovedAlong, ab0204307d) is not re-aimed: its coupling and under-coupler stay at t
- `LEVEL_REHEARSAL_UNSTICK_WAITS_FOR_GODOT` — HARNESS: pipe_levelling_perf_proof --rehearsal on a fresh quicktest map (after walk_gaps --fresh-map) hit a governor stop (hostile_arrival RM_HullBolt
- `ANT_FACTION_SILENCE_KNOCKS_EVERY_LOAD` — Every load of save RM_fw_walkthrough_20261022d opens a 'New faction: Giant ant colony' dialog over the screen — the save lacks a faction some mod on f
- `TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID` — Live r3b (hose_bend_wall_corner*.png, tank_port_met_straight_zoom.png): tank shadows draw as dark T-shaped blocks 1-2 cells away from the tanks while 
- `COUPLER_ART_INSTALL_DRESSED_UP_AT_LAST` — Install regenerated under-coupler art after a live look: Transient/coupler_regen_20261023/picks/<Look>/UnderCollar.png+UnderPipe.png over Textures/Rim
- `PUMPSTATION_COUPLER_MATCH_FIX_STEEL` — Pumping stations take the Scrapper under-couplers (copper under grey-steel / white-red pipework); pick the matching look's set per station style. Sour
- `LADDER_PARITY_BUILD_NO_KEYS_REQUIRED` — Ladder/trench parity (owner card 2026-10-23, option 4 'full parity'): both sides build ladders on demand, use and pick up/move each other's ladders, r
- `FOUNTAIN_SCULPTURES_DESIGN_WATER_MEETS_ART` — v2 brainstorm: artistic fountain sculptures (water spewing, counterpart to fire and glow sculptures) built on overspill
- `FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN` — FlowWorks v1: simple fountain whose water falls out and flows over the ground (overspill), caught in a surrounding ditch and pumped back — full flow-c
- `ART_EVAL_PIPELINE_BUILD_OPUS_GRADES_FIRST` — Automated art evaluation: skill rimworld-art-evaluation + art_eval runner (Opus first, GPT targeted second look, reason-driven regen, shadow sheet)
- `FOUNTAIN_ART_FINISH_WAITS_FOR_A_FAVOURITE` — Fountain art: once a design is picked on Transient/fountain_20261023 (judge or owner), draw its DRY variant + 3 falling-water/jet overlay frames, then
- `SCENARIO_ONLY_FIX_SWEEPS_THE_WHOLE_ZOO` — scenarios_map --build --only X sweeps every other plot's animals and prisoners: run_build sweeps with keep_rects of the --only plots, so --only C5 rem
- `WALK_SAVE_SILENCE_ABSENT_BIOME_OBJECTS` — Walkthrough saves (d/e) load with errors from world objects of biome mods not on the 14-mod walkthrough list (first: SaveableFromNode NRE in WorldObje
- `SHADOW_SHEET_FIX_SHOWS_ITS_PICTURE` — art_eval shadow sheet must show the exact picture the pipeline judged when it has no artpipe job (art_sheet --subjects shows installed + renders by na
- `PIT_PAWN_FIX_CARRIES_A_SUNNY_SQUARE` — Walk save e, boar pit: a pawn in a pit draws a strange square of bright terrain around itself as it moves (texture misalignment visible at the rectang
- `REEL_LINK_FIX_IGNORES_THE_OBVIOUS_PORT` — Walk save e: reel-to-reel hose connected from the left reel's NORTH connector to the right reel's WEST side, over its handle, ignoring its obvious hos
- `LADDER_EW_FIX_LEANS_THE_WRONG_WAY` — Walk save e C12: portable ladders are positioned correctly against the walls but their perspective is reversed for East and West — swap the east/west 
- `HOSE_SPLICE_BUILD_MATES_BY_SLOPE` — Two hoses joined end to end don't mate — they lie on top of each other (walk save e, screenshot Steam 20261023063832_1.jpg). Build a universal joiner 
- `REEL_NOZZLE_FIX_COUPLER_HIDES_UNDERNEATH` — Redrawn reel (south facing, Scrapper): the laid hose's coupler draws BENEATH the reel's drawn open outlet pipe — nonsensical layering; the hose must v
- `TANK_DEBUG_BUILD_FILL_AT_WILL` — God-mode debug actions: empty, or fill to max, every universal container with any FlowWorks liquid (default water)
- `MODERN_LOOK_REDESIGN_BEYOND_RED_ENAMEL` — Whole art review of the FlowWorks Modern style: every Modern texture (pipes, hoses, pumps, sprinklers, containers, joins, couplers, cords) as real pre
- `PIPE_STYLE_PRUNE_WHOLE_RUN_ONLY` — Pipe 'Choose style' offers only the whole connected run, never a single piece
- `WEIR_LOOK_REDESIGN_WHITEWATER_FROZEN_SOLID` — Complete weir review: static white water that matches nothing (must be an animated effect), a single flat blue tint above it, unclear how it works (St
- `WEIR_CATCH_FIX_NO_FREE_FISH` — Weirs must not generate fish; they only capture whatever floats downstream
- `STATION_SIGNS_FIX_LOOK_LIKE_BOOKS` — Walkthrough station signs on save e render as books lying on the ground
- `BARREL_PAIR_FIX_SIZE_MISMATCH` — Two green liquid barrels on one shelf draw at totally different sizes (walk save e, Steam screenshot 20261023064829_1.jpg; owner asked why)
- `INDUSTRIAL_BRUTALIST_AUDIT_POUR_THE_CONCRETE` — Industrial look vs owner's 'brutalist' definition: today it reads as black steel + hazard stripes (tanks, weir timber, drawbridge, suspension, contain
- `HOSE_END_REDRAW_STARES_AT_CAMERA` — Modern free hose end looks horrible: a chunky coupling with its black bore drawn facing the camera although the hose lies flat (art brief C6), plus mi
- `PUMP_PORTS_REDRAW_SIZED_FOR_FAT_PIPES` — Redraw pumps and other connector-bearing fixtures so their pipe/hose connectors match the current (thinner) pipe and hose girth
- `CORD_PLUG_FIX_FINDS_THE_PIPE_SLOT` — GSS power cord plugs into a pump's pipe port (south flange) — cords must favour diagonal approaches that slide underneath the machine, never into a pi
- `BLEED_WELL_BUILD_SWITCH_AND_SAY_WHY` — Bleed well (RM_LiquidTap) and liquid drill: On/Off toggle, a visible status icon with the reason when it can't run, and a god-mode 'give this map a su
- `DRAWBRIDGE_CABLES_FIX_STOP_SHORT` — Drawbridges (timber raised, steel lowered): the support cables from the bollards stop short — visible gaps between cable ends and the deck/mast/pit ed
- `PUMP_STATION_REDRAW_PLUMBED_FOR_GIANTS` — Pumping station (Kludged/Repaired/Wrecked) art is built of ~0.3-0.43 cell pipework and flanged ends vs today's 0.136 pipe; needs a full regen, not a c
- `PIPE_ADAPTER_REDRAW_FLANGE_FOR_A_WHALE` — RM_PipeAdapter_Chemfuel/Propane: flange ~0.56 and brass coupling ~0.37 cell vs hose 0.18; redraw smaller (inventory in items/PUMP_PORTS_REDRAW_SIZED_F
- `ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY` — Styled suspension-anchor bollards read as flat fixtures turned to the rope (art-eval CAM_WRONG, Opus+GPT run drawbridge_cables_20261023b), not upright
- `FLOWWORKS_CODE_REVIEW_FINISH_DIRTY_FILES` — FlowWorks code review: every FlowWorks .cs/.py/.xml file CLEAN (67 not-CLEAN at filing), handed over from FOUNDRY helpers
- `FLOWWORKS_PROVE_OWED_LIVE_CHECKS_ONE_SITTING` — FlowWorks: one bridge sitting for every owed live criterion, incl. the unstaged review-save re-stage and joint-gate live run
- `SIGNS_BARRELS_VERIFY_ON_REBUILT_WALK_OWED` — Live look on the rebuilt walk save: station signs are signboards, paired barrels twin-sized (owed by STATION_SIGNS_FIX_LOOK_LIKE_BOOKS and BARREL_PAIR
- `PUMP_COUPLING_SHRINK_STILL_SIZED_FOR_GIANTS` — Hose coupling at a tank/machine port is drawn x1.5 (RM_MapComponent_Hoses.PortCouplingWiden, widest 0.333 cell) to meet the OLD big flanges; the redra
- `PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN` — No live row for LADDER_PARITY A6: a prisoner in a pit prison with a LOWERED ladder starts vanilla's escape (MessagePrisonerIsEscaping) and climbs out;
- `PIT_BOAR_FIX_SUNBATHES_ON_THE_WALL` — Save e C3 boar pit (38-39,22-23, superdeep D=4): the wild boar standing at 39,23 (pit_report: superdeep, room 4 cells) is DRAWN ~3 cells south, on the
- `KEYSHEET_FIX_ONLY_BUILD_SCRIBBLES_ON_IT` — scenarios_map.py --build --only C5 --no-soak (live, on loaded save e) rewrote the committed review/scenarios/KEYSHEET.md + keysheet.html: save names b
- `REEL_FAIRLEAD_DECIDE_AFTER_THE_WALK` — Hose reel payout guide (fairlead) and pump-side supply swivel: REVIEW.md fix 6 remainder; the reel camera redraw (REEL_TAP_CAMERA_REDRAW_STILL_SIDE_ON
- `SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE` — Raised drawbridge: slack rope loops in rotations N/S read as upright hooks/arches standing above the bollards (art-eval run anchor_bollards_20261023_r
- `ANCHOR_BASE_REDRAW_STILL_LYING_FLAT` — Unstyled suspension anchors (base RM_SuspensionAnchor_Rope/Timber/Steel/Heavy, Graphic_Single drawn rotated) and the styled Heavy anchors are still fl

## Commits

```
0e07d07fd6 conversations: catch-up 1 record(s)
d40ac0210e Ledger: ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY implemented; two follow-ups filed
a27e29baba lessons: ledger-guard rm false deny; art install writes ruling lines
8a7d4b78b7 Ledger: RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS built (fixes 8, 10), REEL_FAIRLEAD_DECIDE_AFTER_THE_WALK filed
86b7fbaf53 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
0fa86c8e83 Drawbridge anchors: upright bollards (Timber/Steel, 4 looks, S/E/N); per-facing rope table Upright post occludes the north-running rope, so attachment differs by facing: Art keys look/mat/facing via RopesFor. Owner by card: "Redraw the anchors as upright bollards? → Redraw, I'll judge after (Recommended)"
9008a7ddff Rebuild RimMandrakeFlowWorks.dll from committed source at landing
e6865e00a2 River works: stake levee ridge + silt-trap wedge in four looks (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8, 10)
dd1b431d48 scenarios_map clear_plots: sweep() honours --only hold rects (SCENARIO_ONLY_FIX_SWEEPS_THE_WHOLE_ZOO)
334ace291f lesson: watchdog every probe-looping live proof
63996a9de7 Ledger: area P harness items (GODOT, ZOO implemented; selftest mend closed; run-sheet notes)
edf1028035 BRIDGE_RUN_1: one ordered bridge run for every owed FlowWorks + GSS live check (pinned)
0df38f45e0 FW selftests green again: drawbridge cable cases listed, chop job and tank dev gizmos covered
02c29c45a4 Rebuild RimMandrakeFlowWorks.dll from committed d945b7bb5e (bridge run 1 deploy)
339585e469 Ledger: area E art handoff note
3af5061cc7 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
99deb7e783 Ladder parity live rows: raid_trench --trees (A5) and ladder_wall climber census (A7)
19479515e8 Ledger: area E takeover (flotsam rows, ferry rope, river scenes built, toggle A5 corrected) + lesson
d945b7bb5e FlowWorks ferry: draw the RM_FerryRope strip post to post (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fix 9)
d356baa2a4 selftest_scenarios_map: offline proof that the map R build turns the R1 Muffalo side-on
... 483 more: git log --oneline 05fad4ed80..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: for     BENCH bridge run 1 (owner card 08:25: Now; I'll step away)

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/fw_scenes/live/S1_rows.json   — proof-run output (Transient, untracked by policy)
 M Transient/pile_2026-10-22/review_tonight.md   — pinned review log, stale edit — next seat commits or leaves
 D infrastructure/state/items/HOSE_SPLICE_BUILD_MATES_BY_SLOPE.md   — Bridge run 1 driver (closing the item)
 M infrastructure/state/ledger/events/BENCH.jsonl   — BENCH helpers (Bridge run 1 / drawbridge) — rimflow writes
 M infrastructure/state/ledger/events/OWNER.jsonl   — BENCH helpers (owner-said writes)
 M src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeArt.cs   — drawbridge follow-up helper (running)
 M src/RimMandrake/FlowWorks/Source/RM_DrawbridgeMath.cs   — drawbridge follow-up helper (running)
 M src/RimMandrake/FlowWorks/Source/SelfTest/DrawbridgeChecks.cs   — drawbridge follow-up helper (running)
 M src/RimMandrake/FlowWorks/art_source/Drawbridge/render_cables.py   — drawbridge follow-up helper (running)
?? deployed/config/ModsConfig.swap-active.json   — live modlist-swap marker (leave)
?? infrastructure/state/art/sheets/art_eval_shadow_e2e_weepingstones_20261023_sheet_2026-10-23.snapshot.json   — art-eval skill e2e run (BENCH; commit with the skill work)
?? infrastructure/state/art_eval/regen_rounds.json   — art-eval pipeline state (BENCH helpers)
?? infrastructure/state/art_eval/runs/slack_coil_20261023/   — drawbridge follow-up helper (running)
?? infrastructure/state/art_eval/runs/weir_whitewater_20261023/   — weir helper run record (BENCH; commit)
?? infrastructure/state/items/closed/HOSE_SPLICE_BUILD_MATES_BY_SLOPE.md   — Bridge run 1 driver (closing the item)
```

