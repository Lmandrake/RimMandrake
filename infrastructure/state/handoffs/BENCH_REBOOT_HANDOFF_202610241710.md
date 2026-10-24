# BENCH_REBOOT_HANDOFF_202610241710 — READ FIRST on wake

Follows `BENCH_HANDOFF_202610240804`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Owner's working method, ruled today and now in CLAUDE.md / debug_process.md: solve geometry and art OFFLINE in Python (compositor drawing real textures as the game layers them, plus checks) before any game time, and every defect the owner finds gets a permanent test that FAILS on the old behaviour and PASSES on the fix. Also: never restore his mod list; only canonical world saves are precious. (see: CLAUDE.md, design/RimMandrake/debug_process.md)

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Delegated calls BENCH took today, his to veto: hose lays with no curve even at lead 0.6 are REFUSED with a player-visible reason (not the kinked fallback); portable ladder E/W = panel 3 (30 deg) inferred from "portable ladder looks approved" (not yet installed).
- Ready for his eyes (read first by the helper): D:\ClaudeWork\rimmandrake\fw_art_geometry_20261024\scrapper\SHEET_scrapper_long_runs.png (Scrapper dash rhythm on long runs).
- RimPulse: six old held sheets (facings_regen_round2, suspension_four_looks, picks1_redo, all_bridge_art, awaiting_pick, water_art_candidates) may be stale; WATER_SCENES_S5 still listed (FOUNDRY says premature). Audit: D:\ClaudeWork\scratch\rimpulse_audit_20261024.md.
- FOUNDRY clone holds ~15 uncommitted src edits (Wastes biome, LeaningScrub aliases, art_eval policy/shadow, deploy_custom_mods.py); left for FOUNDRY to commit.
- Today's art (Modern blue, squat sprinklers, new joins, portable N/S, spikes) is committed but NOT yet deployed/seen live.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `HOSE_CURVE_REBUILD_SMOOTH_AS_PHYSICS` — 47/59 MEASURED; sweep no-fit port 56/4480, free 7/1280, mate 34/400; 126 reel/fixture collisions still drawn; stronger-search recheck 32/114 done. NEXT: dispatch rm-builder to resume steps 1-7 from /mnt/d/ClaudeWork/rimmandrake/scratch/hose_geometry_20261023.md (recheck, continuous coupling, free-length fit, collisions, refuse-with-reason, C#-vs-Python cross-check, review DIRTY hose files).
- `PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE` — owner-approved look installed+published; sliver fix open (r3 attempt shrank stakes, dropped, saved r3_handoff\r3_files.tar). NEXT: redo the sliver fix so the approved render is unchanged except slivers, with a check against the approved render, then close.
- `LADDER_PORTABLE_DECIDE_EAST_WEST_FACING` — owner approved SHEET_ladder_portable.png; panel 3 taken. NEXT: install E/W = ground ladder raised 30 deg, extend facing checks, close.
- `RAIL_LADDER_REDRAW_FAT_RUNG_FENCE` — owner: yellow wood rail ladder DEPRECATED, "The paler ladder is much better and is thick enough". NEXT: retexture RM_Ladder/RM_LadderRaised with the ground ladder's pale wood (keep approved perspectives), palette check, judge, install, owner sheet.
- `PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT` — not started. NEXT: rm-builder per /mnt/d/ClaudeWork/scratch/fw_art_geometry_20261024.md (STOP POINT helper#5), then in order SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE, HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM, MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL, WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE, MODERN_BRIDGE_REDRAW_BRIDGE_NOT_PLUMBING.
- `SCRAPPER_PIPE_REDRAW_VERDIGRIS_DASH_RHYTHM` — long-run sheet built. NEXT: look at SHEET_scrapper_long_runs.png, then show the owner and record his verdict.
- `SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS` — not started (also GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE). NEXT: one rm-builder for both gates: lift-up open/closed graphics, toggle from adjacent cell, god-mode force button, traversable only when open, tests.
- `SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED` — not started (also REVIEW_STAGER_FIX_NUMBER_EVERY_STATION). NEXT: rm-builder: steel = towers + criss-cross cables, heavy = girders, judged over pits; stager numbers every station densely.
- `WET_LADDER_FIX_NO_WALL_WHEN_BRIMFULL` — filed from the live pit/water run. NEXT: fix offline with a failing selftest, live-check after the next deploy.
- `GPT_MAJOR_BATCHES` — batch A (liquid core, 8 items) not started; stop file /mnt/d/ClaudeWork/scratch/gpt_batch_a_20261024.md. NEXT: dispatch rm-builder for batch A, then D, then GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS.
- `MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL` — §7 modcheck hung at tick 1, no tally. NEXT: rerun with python.exe -u after redeploying today's art, then rimflow verify the §7 items; also review DIRTY extensions.py, selftest_extensions.py, validation.py.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- art_eval criteria_ledger CL ids collide across seats (both minted CL-035) and block ./publish. (filed: LESSONS)
- The art pre-push guard rejects installs with reason 'agent-why'; reinstall the same bytes through the art ledger with the owner's words. (filed: LESSONS)
- A peer's uncommitted shared DLL pair or ledger shard makes ./publish refuse; commit the shards first. (filed: LESSONS)
- Helpers stop at maxTurns mid-step (250-300); a "wrap to the next clean boundary" message recovers them. (see: BENCH_HANDOFF_202610240804)

## Closed since the last handoff (13)

- `WATERED_PIT_FIX_NO_WAY_IN` — d9f13cebd5
- `SWIM_DEPTH_FIX_TWO_METRES_WALKED` — d9f13cebd5
- `DEEP_PIT_SWIM_FIX_FIVE_METRES_WALKS` — d9f13cebd5
- `DRAFTED_SWIMMER_FIX_PIT_BOTTOM_ROW` — d9f13cebd5
- `PIT_CLICK_FIX_SHIFTED_ONE_DOWN` — d9f13cebd5
- `SHALLOW_RIPPLE_FIX_DARK_RING_STATIC` — d9f13cebd5
- `GODMODE_LADDER_FIX_ASKS_FOR_WOOD` — d9f13cebd5
- `PIPE_JOINS_REDRAW_RISER_ELBOW_AND_COLLAR` — ade1b1267f
- `SPILL_FILTH_DIAGNOSE_TWO_OF_THREE` — b050b1c41f
- `MODERN_PIPE_REDRAW_FIRETRUCK_RED_RETIRED` — ccbe9e339a
- `SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW` — ccbe9e339a
- `LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND` — df90744424
- `LINES_DRAWBRIDGE_FIX_SELFTEST_DRIFT` — 4ca8ea969d0100ef397303a280c39cb4b69d8de2

## Filed and still open (33) — the next seat's queue

- `LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP` — pipe_levelling_perf_proof on a 325 Base_Player map: main thread froze ~9 min near lay #46 and stayed frame-bound while paused (last Player.log line 'p
- `LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR` — ProofLevelPerf on the 250 rehearsal (8 rigs, 6 links, calls=200): allocKBAvg 8747.8 KB per levelling cycle against the 1024 KB bar (msAvg 15.2, msMax 
- `TILEMAP_GENERATE_FIX_FACTIONLESS_PARENT` — jawa/world_tile_map_generate with the default suggestedMapParent=Settlement creates a factionless Settlement: Base_Faction map (ruins, 110 pawns, site
- `LEVEL_PERF_PROOF_SHRINK_TO_FIT_BUDGET` — pipe_levelling_perf_proof --budget-s 900 cannot run under the 540 s foreground cap, and its Watchdog only checks between calls, so a hung probe call (
- `SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS` — Sluice gate: lifts up to open, toggled from an adjacent cell, god-mode force open/close, open/closed graphics, open=traversable closed=not
- `REVIEW_STAGER_FIX_NUMBER_EVERY_STATION` — owner_review_stage: label and number every station on the map; dense layout (stations close together)
- `SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED` — Suspension bridges: steel = real suspension bridge (towers at anchors, criss-cross cables); heavy = no cables, solid girders; review over pits
- `GRATE_DOOR_REBUILD_LIFTS_LIKE_THE_SLUICE` — Security grate door: open must leave a passable gap; slide up (like the sluice), not two overlapping grates sliding sideways
- `PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE` — Pit spikes drawn over the pale wall band; in water must read as submerged with depth
- `PLANK_COVER_REDRAW_READS_AS_EMPTY_PIT` — Plank-covered pit looks like an empty pit; cover must read as planks
- `HOSE_MATE_REWIRE_CONTINUOUS_COUPLING` — Hose mate: solve coupling point and axis continuously so the 12 mate/splice rows fit
- `HOSE_FIT_HARDEN_FREE_LENGTH_SHORT_LEAD` — Hose G2 fit: free length / unpadded leads so short spans keep the largest lead
- `HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD` — Hose explorer: widen seeds; tankW no-seed above lead 1.4
- `WET_LADDER_FIX_NO_WALL_WHEN_BRIMFULL` — A ladder cannot be placed in a brim-full wet pit: WallRotAt reads the climb depth, which water lifts to 0, so the pit has no wall
- `MODERN_FLANGES_POLISH_DARKER_THAN_THE_BODY` — Modern blue: darker flange rings and galvanised-grey valve handles (masked pass on the recolour)
- `RIVER_COLORS_WIDEN_RED_BLUE_GREEN_DEATH` — FlowWorks river colours: any colour per tile, plus the source ramp red (mountains) -> bluish -> quick fade to thick green -> dies; realizable as per-t
- `NS_TOGGLES_WIRE_SPRINKLER_PIPE_VARIANTS` — selftest_extensions RED: settings pipeStraightVariants + sprinklerSprayEffects (registry cf7b88f400 / 3889ce0da5) have no toggle= component in extensi
- `PUMP_DRAW_DIAGNOSE_CHANNEL_LOSES_EXTRA_LEVEL` — liquid_pump/pump_draws_into_tank live FAIL: 3-cell D=2 channel 6 -> 2 levels in 800 t while moved=3, tank=30000 (3 levels): one level unaccounted. MOD
- `NS_TRIALSITE_REPAIR_ZERO_COLONISTS` — NS_FlowWorks_TrialSite_v1 is saved with 0 colonists: a partial --chains run hits the governor colony_loss stop (GameEnded) once chains sweep their own
- `NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS` — pit_prison_room capture and warden rows UNMEASURED: the chain's own spawned hostile Pirate trips hostile_arrival in safe_advance; declare it as canal_
- `SPRINKLER_HEAD_REDRAW_SEEN_FROM_ABOVE` — Sprinkler head: draw top-down (as the pump is viewed) in every pipe look, so it sits on any pipe/bend without fitting problems
- `WEIR_LOOKS_REDRAW_ONE_PER_PIPE_STYLE` — Weir: one look per pipe style (Scrapper/crude, Industrial, Modern, Futuristic), from owner's four weir photos
- `MODERN_BRIDGE_REDRAW_BRIDGE_NOT_PLUMBING` — Modern bridges: look like modern bridges (concrete/steel deck, real bridge palette), not water-system red/blue
- `HOSE_REEL_REDRAW_FIREHOSE_ON_THE_DRUM` — Hose reel: the hose wrapped on the drum is a firehose (red woven canvas), not a blue hose; red holder is fine
- `MODERN_BOTTLE_REDRAW_SODA_AND_ORANGE_PAIL` — Modern bottle looks soda-like; Modern bucket is orange
- `FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT` — FlowWorks_LadderClimbers.xml still names RSW_ creatures that moved to the RM tier as RM_ (batch 3: RSW_Diplocaulus/Holcorobeus/Platyhystrix/Protosolpu
- `LADDER_PORTABLE_DECIDE_EAST_WEST_FACING` — Portable ladder E/W: GPT v2 (installed) vs ground ladder raised 30 or 55 deg; owner picks on SHEET_ladder_portable.png stations 2-4
- `POND_DRAWN_FIX_VERYSHALLOW_NEVER_MUDS` — plot_D pond_shoreline_recedes live FAIL (MOD presumed): 5x5 WaterShallow pond drawn to stock 0.00/50 by a D=3 channel; all 25 squares stay RM_WaterVer
- `GOLDEN_PONDS_RECONCILE_TWO_FIFTHS` — Golden site P-S2: live pond capacity/stock is 0.4x the sidecar record (D 50/125, K 8/20, S 32/80)
- `ALL_OFF_DIG_DIAGNOSE_POND_STILL_FLOWS` — All FlowWorks toggles off (registry all_off, 218 switches), a D=1 run dug beside a limited pond still fills a full level per cell
- `NATURAL_SLIME_DIAGNOSE_NEVER_SLIPS` — A colonist walks 8 cells of natural RM_SlimeGreenShallow with 0 slips (slip=1.00) while the slime canal wader slips
- `PLOT_D_BODY_PRUNE_STALE_SEA` — Golden site: toggle_recession's fresh pond on plot D (80..84,122..126) joins limitless body 9 (17434 cells) with no water near it
- `MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL` — modcheck FlowWorks run stalls with the game paused at tick 1

## Commits

```
62f1062aca conversations: catch-up 22 record(s)
462ccd05f2 ledger: round-3 owner words on sea faces, Twilight panes, Chill abyss (OWNER shard)
55a843cccf code review: mark world water generator, biome_worldfaces guard and 3 RM sea defs clean (reviewed diff since last clean mark)
fb078d7b36 WORLD_SEA_FACES_INSTALL_PICKED_LOOKS: install confirmed sea faces + round-3 water sheet
d862a8b300 lesson: art guard - re-install a newly added texture through the ledger
86308a0061 art ledger: RM_SpikeStakes_a/b/c re-installed on the owner's ruling ("spikes look great!" on SHEET_spikes.png)
1f6f1be8fd lesson: flush sweep rows; BENCH push blocked by b6a4c87772 art guard
72a5166338 hose explorer: deep search (16 radii, stretched + random restarts), warm upward lead march, preferred-length tier then any length (detours legal), saturate/oracle commands, per-row flush, mate time budget
f516c673b5 Ledger shards
3c7f5aebb7 ledger: MODCHECK_RUN_DIAGNOSE_TICK_ONE_STALL filed; game down; bridge released
b6a4c87772 pit spikes: stakes drawn from a clean per-variant atlas, so no quad carries a neighbour's sliver
ebb210354e Ledger shards (FOUNDRY, OWNER) — committed by BENCH at owner's request to sync both seats
eb9a8e6ee0 DEPLOY_PLANNER_FIX_CRASH_ON_DELETED: planner no longer crashes on a source file deleted mid-run (dangling staged symlink / filecmp race); worktree-deleted tracked files labelled as uncommitted repo deletions, not hand edits, and not pruned by plain --apply; selftest_deploy_deleted (8 cases, failing first)
639ad5df0b ledger: close 4 move-review fix items, note dirty files on SWB_MOVE_VET_UNREVIEWED
ed8d8b3d87 ledger: SWB invented run 4 (tellurox moved, excretor ask filed, fungal weevil label item, tunnel snake dedupe blocked) + lesson sibling-borrowed-picture-gate-refuses
c853b32285 ART_GUARD_RETIRE_PRUNE_DEAD_BRANCH: drop unreachable second refusal in art_guard._authorized; exhaustive 32-case truth-table selftest
c3f7d97ab5 MOVED_FAUNA_HEADERS_FIX_STALE: comment-only header fixes (BedBug no VEF comps + 2 alt graphics wired; Durrok/Mullgoth art no longer placeholder; Misc_Races/Warscar/Stillsand counts and RSW_Ikee history)
02b59b51cb ROSTERS_RENAME_MOVED_PORT_NAMES: rosters RM_Ikee/RM_Korrum; evictions Corpse_RSW_ -> Corpse_RM_ for 6 moved ports; generator canonicalizes moved names via RM_SWBRehome_Aliases.xml; drift selftest
5e14d2e94e lesson: rimpulse stale sheet sources
ecc62098b5 ledger sync: pulse_core/selftest_pulse clean marks
... 205 more: git log --oneline 46ac071680..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-10-24T16:56:32Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/fw_scenes/live/S1_rows.json   pre-existing, BENCH live runs (Transient, untracked shelf)
 M Transient/modcheck/fixtures.json   BENCH live helper modcheck run (generated)
 M Transient/pile_2026-10-22/review_tonight.md   pre-existing at session start, not BENCH this session
 M deployed/config/ModsConfig.before-tier-flowworks.xml   BENCH live helper tier swap (owner: no restore needed)
 M infrastructure/state/modcheck_status.json   BENCH live helper modcheck run (generated)
?? deployed/config/ModsConfig.swap-active.json   tier-swap marker from the 10-21 swap (owner: no restore needed)
?? infrastructure/state/art/sheets/art_eval_shadow_e2e_weepingstones_20261023_sheet_2026-10-23.snapshot.json   pre-existing, art pipeline (FOUNDRY lane)
?? infrastructure/state/art_eval/regen_rounds.json.lock   art pipeline lock file (generated)
?? infrastructure/state/art_eval/runs/modern_style_20261023_r4_ingame/shadow_build.log   pre-existing, art pipeline run log
?? infrastructure/state/art_eval/runs/weir_whitewater_20261023/   pre-existing, art pipeline run
?? src/RimMandrake/FlowWorks/art_source/Ladder/v6/out/   BENCH art helper generated output (derived, not committed)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261024T025509.json   BENCH live helper proof output (derived)
?? src/RimMandrake/FlowWorks/northstar/proof_hose_20261024T031318.json   BENCH live helper proof output (derived)
?? src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261024T024823.json   BENCH live helper proof output (derived)
```

