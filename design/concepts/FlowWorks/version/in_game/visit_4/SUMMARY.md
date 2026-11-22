# FlowWorks 0.1.0 — in-game acceptance, visit 4

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_FOUR, game a. Started 2026-11-21 3:48 PM PST.
Wall-time bound 3 hours (to about 6:48 PM PST). 6 checks to run: rerun_relation.py named sc_hole_prison, sc_islands, sc_walk and
OL_OWNER_LOOK_READS as touched; sc_source_pays and sc_ice are named by the brief (their fixes 2083f92acb and f3f597ccc6 landed
since visit 3). The other 25 keep their earlier rows (build_match.py check: 28 of 31 count before this visit's runs).

## Build and lists

- FlowWorks deployed at bdd56c6ff6 (DLL md5 06b39ad42e68, mod hash sha256:33f817434c71...; every counted row names it) [measured].
  The deploy dry run read "in sync (1038 files)" and game a started at 3:47 PM, after the 3:08 PM DLL deploy, so the HEAD build
  ran: the islands fix bdd56c6ff6, the ice fix f3f597ccc6, the sink fix 2083f92acb and the OL reader wiring 7f87c7714c.
- Game a on Archmagi, RimWorld 1.6.4871 rev590. Lists: his full list (315 mods) for sc_walk and the walk savegame; the 13-mod
  flowworks tier for sc_ice, sc_islands, sc_hole_prison; fw_gss_sitting (15 active) for sc_source_pays (its lake row needs the
  river site, built on that tier); evening_20261113 (22) for the big pit and OL. Every list holds all five DLC.
- Two mutant DLLs ran only for the planted readings (evidence/plant/); the real DLL was redeployed after each (md5 06b39ad42e68
  read back). No mod code changed in this visit.

## Results: 5 PASS, 0 FAIL, 1 UNMEASURED of 6 [measured]

| check | verdict | list | notes |
|---|---|---|---|
| sc_walk | PASS | full (315) | 12 of 12 rows, calm site asserted, 170 s |
| sc_ice | PASS | flowworks | 3 of 3: the cut leaves crushed ice, the unfrozen control none, it melts back into the pond (the ice fix holds live) |
| sc_islands | PASS | flowworks | 5 of 5: a lost winch drops its leaf and the raiders now escape (the islands fix holds live; FAIL 3 of 3 on visit 3) |
| sc_hole_prison | PASS | flowworks | 167 s |
| sc_source_pays | PASS | fw_gss_sitting | after a HARNESS repair shown both ways (below); SRC_flow_stops_when_empty PASS at 0 dL (the sink fix holds live) |
| OL_OWNER_LOOK_READS | UNMEASURED | evening_20261113 | 1629 PASS, 0 FAIL, 0 UNMEASURED, 1 BLOCKED (below) |

### sc_source_pays: HARNESS, repaired and shown both ways

- First run (flowworks tier): every row PASS but SRC_lake_reads_endless UNMEASURED: the scene read the lake row on the calm site,
  which has no edge body, so the row could never be read (UNMEASURED on every visit since visit 1). The bar
  source_pays_and_refills needs it. Class HARNESS.
- Repair 9da1303401: when the scene's map has no limitless body, the lake row loads the river site (test_site_saves 'river') and
  reads there; a river site that does not load verified reads UNMEASURED (SITE). selftest_source_pays_scene.py gained the fake
  river loader: PASS on the river map, FAIL under its lake_drops fault, UNMEASURED when the site does not load (0 failed).
- The river site does not load verified on the flowworks tier (cross-ref errors: it holds Gimme Some Slack content), so the
  check ran on fw_gss_sitting.
- Planted, live: a first mutant (TryDebit debits a limitless body) read PASS with the lake stock unchanged: off the path, because
  the exact kernel reads a body through RM_LiquidStock.LevelBodyOf. The second mutant LIMITLESS_BODY_RUNS_DOWN (LevelBodyOf
  returns a limitless body's id) read SRC_lake_reads_endless FAIL (body 1 stock 11790 -> 11784.415). The real build read PASS
  (11790 -> 11790 after the moat took 200000 dL). Both readings are on the row. The item I filed for the not-yet-red repair,
  RIMMANDRAKE_PLANT_FLOWWORKS_ENDLESS_LAKE_ROW_NEVER_SEEN_RED, is closed at 3cf5fdfc07.

### OL_OWNER_LOOK_READS: UNMEASURED, HARNESS, unrepaired

- Big pit staged on the calm site, evening_20261113 list: plan, stage (122 s; visit 3 needed ~28 min before the dig-cost fix),
  fill, verify 253 PASS + 1 UNMEASURED (the known label_onscreen_text reader row). OL with --acts: 1629 PASS, 0 FAIL,
  0 UNMEASURED, 1 BLOCKED. The two rows visit 3 left BLOCKED (label, overlays) now read, after 7f87c7714c.
- The one BLOCKED row, OL_no_surface_shadow_under_sheet, needs RM_SubmergeDraw.ProofSubmerge to report the shadow's draw queue.
  That reader is mod C#, and a check repair may not touch the mod. Owner: RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER
  (open since 2026-11-16; its fix and acceptance test are in its history).
- OL decides no bar; it supports inv_looks, fill_level_legible and pit_reads_as_hole, and 31 held owner statements in
  test_table.json name it as their test. The exit reader first ordered it removed as needless (it read only the bars' decides,
  so a check deciding no bar was needless by default). That was a pipeline defect: fixed test-first in 1c65a6e664
  (RIMMANDRAKE_SPARE_HELD_STATEMENT_CHECKS_FROM_NEEDLESS_REMOVAL, closed: red on the parent reader, green on the fix, 117 pipeline
  checks green at publish). OL now reads not counted with its owner, and every bar is still decided. I did not remove it.
- For the Conductor: building the shadow-queue reader (one C# field, its own item) and then one OL run and one sc_walk run on that
  build would make OL count (sc_walk is a whole-mod check; OL declares only its script, so build_match may not name it
  [guess ~60%]).

## Owed cases from the blind challenge (cycle 4), one by one

- RIMMANDRAKE_PIN_FLOWWORKS_FILM_NEVER_DROWNS_CROPS, _SHEET_SETTINGS_KEEP_THEIR_UNITS, _CONVERTER_CALLER_RATE_AND_SUN,
  _DRILL_CALLER_READS_SETTING: not run this visit. They are cases of sc_garden, which build_match counts from visit 3
  (PASS, untouched since); no check this visit names them. Visit 3's readings stand: the converter rate half shown live both
  ways; the sun half, the drill setting and the door-leak percent not seen by any garden row.
- Planted faults CALLER_CONV_SUN_FACTOR_SKIPPED, CALLER_DRILL_IGNORES_SETTING, CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE: no
  (visit 3, measured with mutants); CALLER_CONV_RATE_SETTING_IGNORED: yes (visit 3). CHANGED_FUZZ_SINK_UNREPORTED: not planted;
  sc_source_pays reads the sink's own drained total (Report) and would see a sink that reports 0 [guess ~70%].
  CHANGED_GLOW_ROOM_SHORT: no; OL does not run glow_tank_live.py [guess ~80%].
- Polish RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH, RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED: not covered.
- Lanes SHEET_GAME_SIDE_NOT_KERNEL, THIRST_GAME_SIDE_NOT_KERNEL, DRILL_RIGHT_MAPS_NOT_KERNEL: unchanged from visit 3 (partly,
  partly, not settled).

## Owed from the road back (unrun.jsonl), one by one

- sc_walk (walk scene): PASS. sc_ice (frozen pond cut): PASS. sc_source_pays (pond never there, film is not a leak, sink stops on
  the last dL): PASS, the film row at 0 dL. OL_OWNER_LOOK_READS (shadow judge, big-pit reset, spare pit): run on a freshly
  staged big pit, the stage reset row absent, OL_pour_never_no_room PASS; the check UNMEASURED on the one BLOCKED row.
- PIT_LOOK_1114_LIVE, sc_fill_front, sc_fill_tiers, sc_garden, sc_hose_look, sc_pit_trap_raid, sc_trench_cover,
  sc_fetch_fallen, sc_geyser_tub: count from visit 3 (PASS), untouched since; not rerun.
- RIMMANDRAKE_JUDGE_FLOWWORKS_PALE_BLOCKS_IN_TWO_METRE_PIT: his full list, TheForge's composed deploy in sync, the review map's
  shallows row on a non-Forge map (AridShrubland): station 21 shows no cell-aligned pale squares; round steam puffs over the vent
  and the pit's inner north face through the water (screenshots/shallows_station21_zoom.jpg). A judge that did not make the
  capture still owes the read.
- RIMMANDRAKE_REBUILD_FLOWWORKS_PITS_AS_RELATIVE_TERRAIN, _MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND,
  _RESEARCH_FLOWWORKS_WATER_LOOK_FIRM_ALREADY_PICKED: the zoomed captures on FLOWWORKS_OWNER_WALK_END_20261120 were not taken.
  The fresh review map on this build holds the same station kinds (canals 7-16, shallows 17-22), captured in screenshots/
  review_*.jpg; the judge read against water_by_depth_target.json is owed to a judge that did not make them.

## The labelled savegame and what was caught before his look

- FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1625, his full list, calm site, under save_guard (545 keepers backed up, VERIFIED
  none changed). The 4:03 PM save of the same map (..._1603) is superseded by it; it is kept.
- Caught and fixed in the sitting: stations 59 and 60 ('steel jetty', 'heavy jetty') were empty pits on visits 3 and 4: the
  scene dragged a 4-square jetty and the mod caps a jetty at 2 squares. Repaired 02df5f8f4a (SITE); both jetties built live
  (anchor 1, decks 2, railed 2) before the _1625 save.
- Caught and filed: sprinkler stations 24-27 never get their four looks and the row capture is off-frame; trench stations 40-41
  have an unarmed shooter. RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_SPRINKLER_LOOKS_NEVER_CHOSEN (acceptance test in its prose).

## Items filed this visit (each --caused-by this item)

RIMMANDRAKE_PLANT_FLOWWORKS_ENDLESS_LAKE_ROW_NEVER_SEEN_RED (closed in the sitting, 3cf5fdfc07),
RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_MAP_SPRINKLER_LOOKS_NEVER_CHOSEN (open, review-map scene),
RIMMANDRAKE_SPARE_HELD_STATEMENT_CHECKS_FROM_NEEDLESS_REMOVAL (pipeline defect, fixed and closed in the run, 1c65a6e664).

## Commits

891d5f4f16 skeleton; 02df5f8f4a review-map jetties (SITE); 9da1303401 sc_source_pays lake row on the river site (HARNESS);
4cdd6d47e9, 3cf5fdfc07 rows and evidence; 1c65a6e664 the exit reader's held-statement rule (pipeline). No offline decider reads concept_scenes.py, selftest_source_pays_scene.py or
owner_review_stage.py (test_table.json), so no red-seen record is owed; the live red reading is on the sc_source_pays row.

## The pipeline's reading (maturation.py next FlowWorks, 5:04 PM PST)

exit met: 30 of 31 in-game checks PASS on checked sites; repaired in the sitting and shown both ways: sc_source_pays; not counted,
every bar still decided: OL_OWNER_LOOK_READS (unrepaired; owner RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER).
Exit tests passing: order, version, hold, exit_met, build_match. Refused only steward_confirms (none in the request: the steward's).

## Exit
```
ingame_rows: {sc_source_pays: pass, sc_ice: pass, sc_hole_prison: pass, sc_islands: pass, sc_walk: pass, OL_OWNER_LOOK_READS: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1625.rws
exit_met: true
```
