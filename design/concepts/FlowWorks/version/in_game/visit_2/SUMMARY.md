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
