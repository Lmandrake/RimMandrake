# FlowWorks 0.1.0 — in-game acceptance, visit 2

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO, game a. Started 2026-11-19 9:26 PM PST.
Wall-time bound 3 hours (to about 12:26 AM PST).

## Progress

- 21:26 precondition `in_game 0.1.0` [measured]; bridge taken by BENCH; game a running (pid 22256).
- 21:27-21:29 game a stopped, `modset_builder.py --tier flowworks --apply` (13 mods, all five DLC), relaunched, bridge in 25 s.
  FlowWorks deploy in sync (1038 files), companion FRESH (209877e3ebed) [measured].
- 21:30-21:48 concept scenes: PASS fill_front, one_surface, hose_look, toss_flame, coating_wash, hole_prison; FAIL ice, source_pays,
  moat_raid, fetch_fallen, garden, geyser_tub; UNMEASURED trench_cover, islands, pit_trap_raid, pawn_height (timeout 220 s).
- 21:49-21:57 extension chains PASS: dig_and_read, dig_finds, fill_tiers, slime, pit_reads, covered_pit, sluice, one_network;
  sc_canal_fire PASS (x10_canal_fire_live.py, the runner visit 1 used for the `_x10_canal_fire` entry).
- 21:58 sc_hung_bridge FAIL (SB_islands_restore_reach: a bank colonist cannot reach a mid-channel square, needs_bridge_first).
- 21:59-22:04 sc_ways_out PASS (live_session B0,B4; jump-pack row UNMEASURED); its row has site_checked false (no site assertion in that run).
- 22:00 big-pit staging for OL refused on the flowworks tier: its plan names defs of the sitting list (RM_GlowTank, RM_BrineCrock ...);
  OL and PIT_LOOK move to one load of the sitting list.
- 22:05-22:11 sc_pawn_height rerun at 510 s: UNMEASURED (its undug control read None twice). River site founded (tile 1819, problems []).
- 22:13 sc_river R1/R3/R4 PASS; run_row.py gained `--site-log PATH REGEX` (the prep log asserts the site). A guard test of that option
  appended a fake `true` row; I deleted it (it was not a run).
- 22:15-22:45 FAILs diagnosed by experiment (copies run outside rows.jsonl, evidence/exp/): sc_ice HARNESS (no shovel; probe's own
  designation read as a refusal; fixed both, the cut still does not land); sc_geyser_tub HARNESS (geyser_tub_live.py PASS 4/4 on the
  same build); sc_source_pays row asks the pond to stop at the wet line against his ruling "ponds pump to last dL" (longer drain: dry,
  sink still draws 3 L of film). Filed seven items (below).
- 22:16-22:22 game a on the 23-mod `evening_20261113` list (its tier holds the sitting save's defs); loaded SITTING_20261114_PIT_FIXES
  (in memory only, never saved).
- 22:26 PIT_LOOK_1114_LIVE 19 PASS, 0 FAIL, 1 UNMEASURED (body cover is a look, by design). The script exited 1 for that, read as FAIL:
  fixed test-first (selftest_pit_look_exit_codes.py red then green), the first row re-derived UNMEASURED with a note, rerun UNMEASURED.
  Item RIMMANDRAKE_SPLIT_PIT_LOOK_EXIT_UNMEASURED_READ_AS_FAIL.
- 22:27-22:31 big pit staged on the sitting map; OL 1155 PASS, 9 FAIL, 1 UNMEASURED, 3 BLOCKED. The 9 FAIL are goods that staging never
  left in the 2-4 m copies (reset method gone, d=16 not 8); deep water keeps minified goods (experiment). Item
  RIMMANDRAKE_REPAIR_FLOWWORKS_BIG_PIT_STAGE_RESET_METHOD_GONE. A first OL call of mine passed `--acts x,z` literally and crashed
  before reading; I removed that row (not a run).
- 22:33-22:39 back on the flowworks tier, calm site verified (load_site.py); owner_review_stage.py staged the review map and saved
  FLOWWORKS_OWNER_REVIEW_VISIT2_20261119_2237 under save_guard (451 keepers backed up, VERIFIED none changed). Five zoomed captures
  looked at (screenshots/review_*.jpg): labels sit over their pits, the four sprinkler looks read alike; filed for a judge.
- 22:47-22:55 his full list (316 mods): sc_walk PASS, 12 of 12 rows (reload digests, pond pays again, no leftovers, log clean).
- 22:56-23:01 flowworks tier again, calm site verified, sc_ways_out rerun PASS with its site asserted.

## Results (18 PASS, 8 FAIL, 5 UNMEASURED of 31) [measured]

Game a on Archmagi, FlowWorks deployed at mod hash sha256:97ced4aec366... (one deploy, every row), game 1.6.4871 rev590. Lists: the
13-mod `flowworks` tier (all five DLC) for most rows; `evening_20261113` (23 mods) for OL and PIT_LOOK (their scene defs and save);
his full list (316) for sc_walk.

PASS: sc_dig_and_read, sc_dig_finds, sc_fill_front, sc_fill_tiers, sc_one_surface, sc_canal_fire, sc_slime, sc_pit_reads,
sc_covered_pit, sc_ways_out, sc_sluice, sc_one_network, sc_river (R1; R3, R4 also PASS), sc_hose_look, sc_toss_flame, sc_hole_prison,
sc_coating_wash, sc_walk.

FAIL, each diagnosed in the sitting and filed (item prose has the evidence):
- sc_ice: HARNESS. No shovel staged; the probe's own second designation read as a mod refusal. Both changed in a copy: the cut still
  does not land in 6000 ticks and the ice is gone. RIMMANDRAKE_STAGE_FLOWWORKS_ICE_SCENE_SHOVEL_LEFT_AT_HOME.
- sc_source_pays: SRC_flow_stops_when_empty. With a longer drain every square is under the wet line, yet the sink still draws film
  (3 L, 53 L left), as his ruling "ponds pump to last dL" says it must. The row looks wrong, not the mod [guess ~75%].
  RIMMANDRAKE_REPIN_FLOWWORKS_SOURCE_PAYS_STOP_AT_LAST_DECILITRE.
- sc_garden: GARDEN_walled_yard_lies_level, maxDl 461 against a mean of 312; cause not found (relief, unsettled sheet or the kernel).
  RIMMANDRAKE_PROBE_FLOWWORKS_GARDEN_YARD_SHEET_NOT_LEVEL.
- sc_geyser_tub: HARNESS. geyser_tub_live.py on the same build and map PASS 4 of 4.
  RIMMANDRAKE_REWIRE_FLOWWORKS_GEYSER_SCENE_READS_GEYSER_NOT_POOL.
- sc_fetch_fallen: one raider fell and was held; no ladder came. RIMMANDRAKE_FIX_FLOWWORKS_RAIDERS_LEAVE_FALLEN_NO_LADDER_LIVE.
- sc_moat_raid: nobody swam with the bridge raised; two swam in the bridge-down control. RIMMANDRAKE_PROBE_FLOWWORKS_MOAT_RAIDERS_SWIM_ONLY_WHEN_BRIDGED.
- sc_hung_bridge: SB_islands_restore_reach, a bank colonist cannot reach the mid-channel square. RIMMANDRAKE_FIX_FLOWWORKS_ISLAND_RESTORE_NEEDS_BRIDGE_FIRST.
- OL_OWNER_LOOK_READS: 1155 PASS, 9 FAIL; the 9 are goods staging never left in the 2-4 m copies (the stage's reset method is gone),
  read by OL as "drawn whole over the liquid". RIMMANDRAKE_REPAIR_FLOWWORKS_BIG_PIT_STAGE_RESET_METHOD_GONE.

UNMEASURED: PIT_LOOK_1114_LIVE (19 PASS, 0 FAIL; body cover is a look, UNMEASURED by design), sc_trench_cover (the raid never came
within 3 squares of the trench), sc_islands (its control: a held winch fell anyway), sc_pit_trap_raid (nobody fell, 11 raiders seen),
sc_pawn_height (its undug control read None twice).

Pipeline fix in the sitting: pit_look_1114_live.py exited 1 on an UNMEASURED-only run; fixed test-first, published f24f71dba4,
item RIMMANDRAKE_SPLIT_PIT_LOOK_EXIT_UNMEASURED_READ_AS_FAIL closed. The visit runner (visit_2/run_row.py) merges build_match identity
and takes `--site-log` (a prep step's log asserts the site); load_site.py and load_save.py write that log.

## Owed cases from the blind challenge (cycle 4), one by one

- RIMMANDRAKE_PIN_FLOWWORKS_FILM_NEVER_DROWNS_CROPS: not shown live. sc_garden ran but no row of it reads a crop under film.
- RIMMANDRAKE_PIN_FLOWWORKS_SHEET_SETTINGS_KEEP_THEIR_UNITS: not shown live (no sc_garden row changes the door or rain settings).
- RIMMANDRAKE_PIN_FLOWWORKS_CONVERTER_CALLER_RATE_AND_SUN: partly. GARDEN_filter_keeps_its_rate PASS (32 batches in its window) and
  GARDEN_still_within_its_def_rate PASS (the still's drops fall to 0 at night and return), both at the default throughput setting.
- RIMMANDRAKE_PIN_FLOWWORKS_DRILL_CALLER_READS_SETTING: not shown (GARDEN_drill_* PASS with the drilling setting on; no row turns it off).
- Planted faults, would the named check have seen them: CALLER_CONV_SUN_FACTOR_SKIPPED, likely no: the still row checks drops within
  the def rate, and a still that runs at night stays within it [guess ~65%]. CALLER_CONV_RATE_SETTING_IGNORED, no: the setting stays at
  its default [guess ~85%]. CALLER_DRILL_IGNORES_SETTING, no: the setting stays on [guess ~85%]. CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE,
  no: no door leak is read [guess ~75%]. CHANGED_FUZZ_SINK_UNREPORTED, no for sc_fill_front and sc_one_surface (neither reads a sink
  total); sc_source_pays reads one [guess ~70%]. CHANGED_GLOW_ROOM_SHORT, no: none of the three checks runs glow_tank_live.py [guess ~80%].
- Polish RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH, RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED: not covered by
  this visit's runs (as above).
- Lane 1 SHEET_GAME_SIDE_NOT_KERNEL: not settled live (no crop death read; the yard sheet FAILed its level row).
  THIRST_GAME_SIDE_NOT_KERNEL: not settled (only the faucet drink runs). DRILL_RIGHT_MAPS_NOT_KERNEL: not settled (the scene sets the yield).

## Owed from the road back (unrun.jsonl)

Every one ran this visit: sc_walk PASS, PIT_LOOK_1114_LIVE UNMEASURED (pour_label rows PASS), sc_fill_front PASS, sc_fill_tiers PASS,
sc_garden FAIL, sc_hose_look PASS, sc_pit_trap_raid UNMEASURED, sc_source_pays FAIL, sc_trench_cover UNMEASURED,
OL_OWNER_LOOK_READS FAIL, sc_fetch_fallen FAIL.

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: fail, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: unmeasured, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover: unmeasured, sc_hung_bridge: fail, sc_ice: fail, sc_river: pass, sc_moat_raid: fail, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: fail, sc_islands: unmeasured, sc_walk: pass, sc_pit_trap_raid: unmeasured, sc_garden: fail, OL_OWNER_LOOK_READS: fail, sc_geyser_tub: fail, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT2_20261119_2237.rws
exit_met: false
```
