# FlowWorks 0.1.0 — in-game acceptance, visit 10

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_TEN, ArchSmall on Archmagi.
Bridge taken 2026-11-24 5:50 AM PST; bound 8:50 AM PST.

## Build and lists

- Source 78f51ace1d, RimWorld 1.6.4871 rev590. The mod's C#, defs and settings did not change in the visit; only live scenes did.
- Lists: 13-mod flowworks tier (26 checks), fw_gss_sitting (sc_source_pays), evening_20261113 (OL_OWNER_LOOK_READS, PIT_LOOK_1114_LIVE).
- The lane's rows in rows.jsonl (Steve1) are its own; the rows with `instance` b are this run's.

## Results [measured]: 27 PASS, 0 FAIL, 2 UNMEASURED of 29

- UNMEASURED sc_walk: needs his full list; ArchSmall cannot hold it beside ArchBig. Owed on ArchBig.
- UNMEASURED sc_hung_bridge, outcome UNRESOLVED: one run read the under-deck floor path found=False and its ordered colonist
  never moved; 27 other runs of that row on this build PASS, two of them whole scenes with 0 FAIL. Filed:
  RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS (three theories ruled out there; the row now reads the
  cause when it fails). One sighting, not serious: no hunt opened. Bars inv_bridges and hung_bridge_spans wait on its class.
- The other 27 PASS. OL_OWNER_LOOK_READS 1629 PASS, 0 FAIL, 0 BLOCKED; PIT_LOOK_1114_LIVE 19 of 19.

### Scene repaired in the sitting (no mod code touched)

- sc_moat_walkers, class HARNESS (UNMEASURED on Steve1 five times and here once): the scene ordered its colonist 4 ticks after the
  staged pour, before the mod's reach labels followed (canReach False at tick 4, True at tick 61). 8eab92b6c2 waits for reach.
  Planted (the leaf stays down): MW_raised_leaf and MW_drained FAIL. Real build: 6 of 6 rows PASS.
- suspension_bridge_proof.py: UND_floor_path_walks_under now records reach, band, pawn, cells and three later reads on a miss.
  Its verdict is unchanged.
- cheaper_why written for sc_moat_walkers and sc_walk.

## Owed cases

- The road back: sc_moat_walkers PASS; sc_pit_crowd PASS (first live run; it decides no bar).
- The four blind-cycle Problems and the caller faults (converters, drill, sheet): sc_garden PASS, 8 rows, on this build. No
  planted fault of lane2 was played in a game this visit; what each check would have seen is as visit 3 recorded.
- Fuzz and glow Polish lines: sc_fill_front and sc_one_surface PASS; CHANGED_GLOW_ROOM_SHORT is not run by any of them (visit 3).
- The five lane-1 not_kernel rows: as read by the scenes only; still unsettled offline (crops killed, the survey roll, FluidDef numbers).

## Beyond the checks

20 captures looked at (depth ladder, fill tiers, pits, sluice, spikes, the big pit's seven copies). Six strange things in
`strange.jsonl`: one filed, five explained. Small copies in `screenshots/`. No raid, no flyer.

## The savegame

No new savegame; the walk save stays visit 4's (his full list; its staged scenes were not re-checked on this build):
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`

## Items filed

RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_source_pays: pass, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover_pawns: pass, sc_hung_bridge: unmeasured, sc_ice: pass, sc_pit_crowd: pass, sc_moat_walkers: pass, sc_hole_prison: pass, sc_toss_flame: pass, sc_islands_walker: pass, sc_walk: unmeasured, sc_garden: pass, OL_OWNER_LOOK_READS: pass, sc_geyser_tub: pass, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
