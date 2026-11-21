# FlowWorks 0.1.0 — in-game acceptance, visit 3

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_THREE_RUN_TWO, game a. Started 2026-11-21 5:41 AM PST.
Wall-time bound 3 hours (to about 8:41 AM PST). 23 checks to run; 8 keep their visit-2 PASS (rerun_relation.py: sc_dig_and_read,
sc_fill_tiers, sc_slime, sc_pit_reads, sc_covered_pit, sc_sluice, sc_one_network, sc_river).

## Progress

- 05:41 precondition `in_game 0.1.0` [measured]; item claimed by the launcher; bridge taken by BENCH. Game a up on the 13-mod
  flowworks tier (all five DLC); FlowWorks deploy in sync (1038 files) at c9e4ad0fa3 (DLL and Source both last at 175293dc5f).
- 05:45-06:28 first pass on the flowworks tier, calm site asserted on every row: PASS sc_fill_front, sc_one_surface, sc_coating_wash,
  sc_hose_look, sc_toss_flame, sc_trench_cover, sc_fetch_fallen, sc_pit_trap_raid, sc_geyser_tub, sc_hole_prison, sc_pawn_height
  (336 s), sc_dig_finds, sc_canal_fire, sc_hung_bridge, sc_ways_out. FAIL sc_ice (cut lands on ThinIce, no crushed ice), sc_islands
  (ISL_raiders_escape), sc_source_pays (SRC_flow_stops_when_empty), sc_garden; UNMEASURED sc_moat_raid (one of two held).
- sc_hung_bridge: first run killed by my 160 s run_row timeout (HARNESS, the reach row needs ~180 s); the second ran on the map the
  killed run left (SITE: no site load) and FAILed SB_load_over_rating, then crashed on a 9P os.replace. Third run, calm site loaded
  first, 490 s bound: 40 rows, 0 FAIL. GRATE_fire_burns_people_above FAILed on the first run and PASSed on the third, same build
  (strange.jsonl; open item GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO).
- 06:30-06:55 FAILs diagnosed by experiment while the game was up:
  - sc_garden: GARDEN_filter_keeps_its_rate read made 63985 = 32 x 2000 - 15. A thirsty colonist drank one tank drink (15 units)
    from the filter's fresh output tank at tick ~40000 (tanks are drinkable by design). SITE: the scene let a colonist drink from the
    tank it counts. Repaired (a07d2f8ea8, then 6fbf4d8c3b: thirst topped up below 0.9, not at the 0.3 drink threshold). Planted
    CALLER_CONV_RATE_SETTING_IGNORED (cycle 4 lane2) in a mutant DLL: the filter row FAIL, 8 batches against [32, 33]
    (evidence/plant/sc_garden_MUTANT_A.json). Real build: every garden row PASS (made 64000). Real DLL redeployed, mod hash
    sha256:f7b24409aa42... again, as on every row.
  - sc_source_pays: the check waited a flat 500 pulses for the pond to reach its wet line; the pond still held 208 L and the sink was
    still drawing (502.6 -> 514.3). HARNESS. Repaired (a07d2f8ea8): the draw is followed while the sink still drains, up to the
    film bound. The repaired check reads FAIL on the offline planted cases film_stuck and endless_pond, PASS on film_drains
    (accept_source_pays_last_decilitre.py ok; selftest_source_pays_scene ok). Live on the real build it now reads the MOD: the pond
    reaches its wet line in 800 pulses, the film drains 1700 pulses, then the sink stops with 1 dL on each of 80 squares (0 L on the
    readout). His ruling POND_PUMP_FIX_LAST_DROP_COUNTS says pump to the last dL. Not fixed (kernel; fix not known):
    RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM.
  - sc_ice: the cut lands on ThinIce and leaves no crushed ice. MOD: RM_GroundClassMath.IceTerrains has no ThinIce, so the spoil is
    never crushed ice; the bar's own red ("cutting ice deletes it with no crushed ice"). Not fixed (the fix is not known: it changes
    dig speed and spoil wherever frozen water is cut): RIMMANDRAKE_FIX_FLOWWORKS_FROZEN_POND_CUT_LEAVES_NO_CRUSHED_ICE.
  - sc_islands: ISL_raiders_escape FAIL in 2 of 2 runs (both leaves lowered, then the east one only): the six sappers stayed on
    the span for 6,000 ticks. Probe (probe_islands_leaf.py, evidence/exp/islands_leaf_probe.json): a colonist on the span walked
    across the lowered west leaf to the bank (canReach True, arrived), so RULED OUT "a lowered leaf carries no walker". SITE,
    presumed [guess ~60%]: the staging gives the raiders no motive to cross; on game b this morning the row passed in 2 polls.
    Unrepaired: RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF.
  - sc_moat_raid: MOAT_two_held_and_captured UNMEASURED: one raider held in the drained moat, the row needs two (that one was
    captured). SITE, presumed [guess ~60%]. Unrepaired: RIMMANDRAKE_STAGE_FLOWWORKS_MOAT_HOLDS_ONE_WHERE_TWO_ARE_OWED.
- 06:58-07:00 game a on the 23-mod evening_20261113 list; SITTING_20261114_PIT_FIXES loaded (in memory only, never saved).
  PIT_LOOK_1114_LIVE 19 of 19 PASS (the first row's site_checked was false only on my log regex; rerun).
- 07:01-07:29 big pit: `stage` digs ~2,100 cells at ~250 ms a call on the sitting map, so it outlasts one 540 s command (killed
  twice). big_pit_scene.py gained `stage_resume` (digs only the cells not yet at depth; ff767a627d). stage, stage_resume, fill,
  verify: 253 PASS, 1 UNMEASURED (the known label reader row).
- 07:30 OL_OWNER_LOOK_READS: 1174 PASS, 0 FAIL, 0 UNMEASURED, 3 BLOCKED (exit 2). Visit 2's 9 FAILs (goods left in the 2-4 m
  copies) are gone; OL_pour_never_no_room PASS. Two BLOCKED rows are hard-coded in owner_look_regressions.py although their readers
  landed on 2026-11-13 (676c5cd131: ProofPitLabel, ProofOverlays): HARNESS, unrepaired in the bound,
  RIMMANDRAKE_WIRE_FLOWWORKS_OL_TO_READERS_LANDED_EIGHT_DAYS_AGO. The shadow-queue row needs a new C# report.
- 07:33 flowworks tier, calm site: pit_relief_live.py --origin 60,67, RELIEF_CUT_REDRAWS_ITS_SQUARE and
  RELIEF_CUT_REDRAWS_ACROSS_SECTION_EDGE PASS (row OL_OWNER_LOOK_READS__pit_relief).
- 07:34 his full list (315 mods, modlist_swap.py --restore) cold-loading for sc_walk and the walk savegame.
- 07:47-07:52 his full list: sc_walk PASS (calm site verified, 320 s).
- 07:53-07:58 calm site verified; owner_review_stage.py staged the review map and saved FLOWWORKS_OWNER_REVIEW_VISIT3_FULL_20261121_0753
  under save_guard (519 keepers backed up, VERIFIED none changed). Eleven captures looked at (screenshots/review_*.jpg): station 21
  (2 m water) shows pale square blocks (filed for a judge); the planks stations read as ground by design.

## Results (17 PASS, 3 FAIL, 2 UNMEASURED of the 22 run; 23 named in the brief) [measured]

The brief names 23 checks but lists 22 distinct ids plus sc_walk; every listed id ran. Game a on Archmagi, FlowWorks deployed once
(mod hash sha256:f7b24409aa42..., DLL at 175293dc5f; every counted row on it), game 1.6.4871 rev590. Lists: the 13-mod flowworks tier
(all five DLC) for the scenes, evening_20261113 (23 mods) for OL and PIT_LOOK (their save and scene defs), his full list (315) for
sc_walk and the walk savegame. Two mutant DLLs ran only for the planted readings (evidence/plant/), then the real DLL was redeployed.

PASS: sc_fill_front, sc_one_surface, sc_coating_wash, sc_hose_look, sc_toss_flame, sc_trench_cover, sc_fetch_fallen, sc_pit_trap_raid,
sc_geyser_tub, sc_hole_prison, sc_pawn_height, sc_dig_finds, sc_canal_fire, sc_hung_bridge, sc_ways_out, sc_garden (scene repaired,
shown both ways), PIT_LOOK_1114_LIVE, sc_walk. (OL_OWNER_LOOK_READS__pit_relief PASS is a supporting row.)
FAIL: sc_ice (MOD, filed), sc_source_pays (MOD after a HARNESS repair, filed), sc_islands (SITE presumed, unrepaired, owner item).
UNMEASURED: sc_moat_raid (SITE presumed, unrepaired, owner item), OL_OWNER_LOOK_READS (HARNESS: 3 BLOCKED rows, owner item).

Visit 2's failures now passing on this build: sc_fetch_fallen, sc_pit_trap_raid, sc_trench_cover, sc_pawn_height, sc_geyser_tub,
sc_hung_bridge, sc_garden (after the scene repair), and OL's 9 FAILs.

Items filed this visit (each --caused-by this item, acceptance test in its prose):
RIMMANDRAKE_FIX_FLOWWORKS_FROZEN_POND_CUT_LEAVES_NO_CRUSHED_ICE, RIMMANDRAKE_FIX_FLOWWORKS_SINK_STOPS_ON_LAST_DECILITRE_FILM,
RIMMANDRAKE_STAGE_FLOWWORKS_ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF, RIMMANDRAKE_STAGE_FLOWWORKS_MOAT_HOLDS_ONE_WHERE_TWO_ARE_OWED,
RIMMANDRAKE_WIRE_FLOWWORKS_OL_TO_READERS_LANDED_EIGHT_DAYS_AGO, RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP,
RIMMANDRAKE_JUDGE_FLOWWORKS_PALE_BLOCKS_IN_TWO_METRE_PIT.

Harness and scene repairs in the sitting (published): a07d2f8ea8 (sc_source_pays follows the drain; sc_garden drinker), 6fbf4d8c3b
(sc_garden thirst top-up), ff767a627d (big_pit_scene stage_resume). No offline decider reads concept_scenes.py or big_pit_scene.py
(test_table.json), so no red-seen record is owed. No mod code changed.

For the Conductor: OL_OWNER_LOOK_READS decides no bar (test_table.json). The rule for a needless check is removal; I did not remove
it, because its rows carry the owner-look regressions that five road-back items close on, and it is not wrong (two readers are not
wired). Your call.

## Owed cases from the blind challenge (cycle 4), one by one

- RIMMANDRAKE_PIN_FLOWWORKS_FILM_NEVER_DROWNS_CROPS: not shown live. No sc_garden row reads a crop under a film.
- RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_KEEP_THEIR_UNITS: not shown live (no garden row changes the door or rain settings).
- RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_CALLER_RATE_AND_SUN: the rate half shown live: GARDEN_filter_keeps_its_rate PASS at 4.1x
  (32 batches) and FAIL with CALLER_CONV_RATE_SETTING_IGNORED planted (8 batches) [measured]. The sun half NOT shown: see below.
- RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_READS_SETTING: not shown (the drilling setting stays on in the scene).
- Planted faults, would the named check have seen them (measured with mutant DLLs on game a, evidence/plant/):
  CALLER_CONV_RATE_SETTING_IGNORED: YES, GARDEN_filter_keeps_its_rate FAIL (8 against [32, 33]).
  CALLER_CONV_SUN_FACTOR_SKIPPED: NO. The still ran all night (made 122000 against 66000, no zero chunk) and
  GARDEN_still_within_its_def_rate PASSed, because it checks only an upper cap per chunk (sc_garden_MUTANT_B_sun.json).
  CALLER_DRILL_IGNORES_SETTING: NO (setting on in the scene; drill rows PASS in mutant A).
  CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE: NO (no garden row reads a door leak; yard row PASS in mutant A).
  CHANGED_FUZZ_SINK_UNREPORTED: not planted live (a kernel fault in RM_FlowKernel.cs); sc_fill_front and sc_one_surface read no
  sink total, so no [guess ~75%]; sc_source_pays reads one.
  CHANGED_GLOW_ROOM_SHORT: no, none of OL, sc_fill_tiers or PIT_LOOK runs glow_tank_live.py [guess ~80%].
- Polish RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH, RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED: not covered.
- Lane 1 SHEET_GAME_SIDE_NOT_KERNEL: partly; the walled yard sheet lies level live (GARDEN_walled_yard_lies_level PASS); no crop death
  read. THIRST_GAME_SIDE_NOT_KERNEL: partly; the faucet drink takes 15 units from its tank, and a colonist drinks from a plain tank;
  bottle jobs not run. DRILL_RIGHT_MAPS_NOT_KERNEL: not settled (the scene sets the yield).

## Owed from the road back (unrun.jsonl), one by one

- sc_walk (walk scene): PASS. PIT_LOOK_1114_LIVE (pour labels): PASS, 19 of 19. sc_fill_front: PASS. sc_fill_tiers: kept PASS
  (untouched since visit 2, rerun_relation). sc_garden: PASS after the scene repair. sc_hose_look: PASS. sc_pit_trap_raid: PASS.
  sc_source_pays (both items): FAIL, now on the mod (last dL). sc_trench_cover: PASS. sc_fetch_fallen: PASS. sc_geyser_tub: PASS.
- OL_OWNER_LOOK_READS (five items): run on a freshly staged big pit on the evening list: 1174 PASS, 0 FAIL, 0 UNMEASURED, 3 BLOCKED;
  the stage reset row is absent (verify 253 PASS); OL_pour_never_no_room PASS. pit_relief_live.py --origin 60,67: both RELIEF rows PASS.
  NOT done: the zoomed captures on FLOWWORKS_OWNER_WALK_END_20261120 and the judge reads against water_by_depth_target.json
  (wall-time bound; a judge that did not make them must read them before his look).

## The exact-tier rerun (08:05-08:47), and where the visit stops

`build_match.py check` read only 11 of 31 rows as counting: the first pass ran on the 13-mod list game a already held at 05:41, whose
order puts mandrake.rm.patches before mandrake.rm.flowworks, and a minimal-list row counts only on the list modset_builder.py builds
for its tier (flowworks before patches). Not a verdict: the same 13 mods. I swapped game a to the exact tier (a stale evening swap
marker of mine refused the first write; removed; game a force-stopped twice while it loaded his full list by mistake) and reran:
PASS sc_fill_front, sc_one_surface, sc_trench_cover, sc_geyser_tub, sc_coating_wash, sc_toss_flame, sc_canal_fire; FAIL sc_ice
(same MOD reading). Then sc_hose_look, sc_garden and sc_source_pays each stalled after the calm site load (160 s, game paused at
tick 3, bridge answering, no dialog: screenshots/desktop_stall_0846.jpg): UNMEASURED, HARNESS, cause not found. At 8:47 AM PST, past
the 3-hour bound, I stopped. Not rerun on the exact tier list: sc_islands, sc_moat_raid, sc_dig_finds, sc_fetch_fallen,
sc_pit_trap_raid, sc_hole_prison, sc_hung_bridge, sc_ways_out, sc_pawn_height, sc_hose_look, sc_garden, sc_source_pays. Their
first-pass readings (above) stand as evidence; build_match does not count them.

## Exit
```
ingame_rows: {sc_dig_finds: pass, sc_fill_front: pass, sc_one_surface: pass, sc_source_pays: unmeasured, sc_canal_fire: pass, sc_pawn_height: pass, sc_ways_out: pass, sc_hose_look: unmeasured, sc_trench_cover: pass, sc_hung_bridge: pass, sc_ice: fail, sc_moat_raid: unmeasured, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: pass, sc_islands: fail, sc_walk: pass, sc_pit_trap_raid: pass, sc_garden: unmeasured, OL_OWNER_LOOK_READS: unmeasured, sc_geyser_tub: pass, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT3_FULL_20261121_0753.rws
exit_met: false
```
