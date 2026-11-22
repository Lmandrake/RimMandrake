# FlowWorks 0.1.0 — in-game acceptance, visit 4

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_FOUR, game a. Started 2026-11-21 3:48 PM PST.
Wall-time bound 3 hours (to about 6:48 PM PST). 6 checks to run (rerun_relation.py: sc_hole_prison, sc_islands, sc_walk,
OL_OWNER_LOOK_READS touched; sc_source_pays and sc_ice named by the brief, their fixes 2083f92acb and f3f597ccc6 landed since visit 3).

## Progress

- 15:48 precondition `in_game 0.1.0` [measured]; item leased by the launcher; game a bridge taken by BENCH.
- 15:50 FlowWorks deploy dry run: in sync (1038 files) at bdd56c6ff6, the DLL deployed 15:08, game a started 15:47 after it
  [measured], so the running game loads the HEAD build (islands fix bdd56c6ff6, ice f3f597ccc6, sink 2083f92acb, OL wiring 7f87c7714c).
- 15:47-16:00 game a was already cold-loading his full list (315 mods) when I took it, so the full-list work (sc_walk, the walk
  savegame) runs first on this load, then the 13-mod flowworks tier for sc_source_pays, sc_ice, sc_hole_prison, sc_islands, then
  the evening list for the big pit and OL_OWNER_LOOK_READS.

## Exit
```
ingame_rows: {sc_source_pays: unmeasured, sc_ice: unmeasured, sc_hole_prison: unmeasured, sc_islands: unmeasured, sc_walk: unmeasured, OL_OWNER_LOOK_READS: unmeasured}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1625.rws
exit_met: false
```
