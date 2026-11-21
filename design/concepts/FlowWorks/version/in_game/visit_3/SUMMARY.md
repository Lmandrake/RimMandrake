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
