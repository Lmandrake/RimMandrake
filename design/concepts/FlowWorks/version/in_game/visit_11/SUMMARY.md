# FlowWorks 0.1.0 — in-game acceptance, visit 11

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_ELEVEN, ArchBig on Archmagi.
Bridge taken 2026-11-24 5:21 PM PST; bound 8:19 PM PST.

## Build and lists

- Deployed source 68cd40dd4e (deploy dry run: in sync; ArchBig launched 5:10 PM, after the DLL's 5:04 PM write), RimWorld 1.6.4871 rev590.
  The mod's C#, defs and settings did not change in the visit.
- Lists: the 13-mod flowworks tier (sc_pit_crowd, sc_canal_fire, sc_hung_bridge, sc_pit_reads, sc_covered_pit, sc_sluice, first
  sc_ways_out); then flowworks_list, his walk list of 20 mods (sc_walk, second sc_ways_out, sc_hole_prison, sc_moat_walkers, the
  walk save). The swap set aside a stale BENCH marker of a gimmesomeslack_walk swap from 2:00 PM (renamed .stale-20261124T1830-visit11).
- The SteveDesktop lane's rows in rows.jsonl are its own (game Steve1/Steve2). Its sc_trench_cover_pawns, sc_toss_flame and
  sc_islands_walker PASS at 55e9b3b0ea count: since then only SelfTest/PitCoverBeneathChecks.cs changed. Its sc_hole_prison and
  sc_moat_walkers PASS at b393204851 predate the WallReach C#; both ran again here and PASS. Its COULD NOT LOOK rows are superseded.

## Results [measured]: 12 PASS, 0 FAIL, 1 UNMEASURED of 13

- UNMEASURED sc_ways_out, ENVIRONMENT FAULT twice (13-mod tier and flowworks_list): Cherry Picker loads on every FlowWorks tier of
  ArchBig and his config lists ThingDef/Apparel_PackJump; its live prefix CherryPicker.Patch_Wear.Prefix on Pawn_ApparelTracker.Wear
  (jawa/harmony_patches) refuses the jump pack. jawa/pawn_gear and the vanilla debug action both left it unworn on 12 of 12 pawns;
  the broadshield and shield belt wore at once. So case B4_access_jump_pack_in_no_fall could not ask; ladder, gear, no-gear and
  rescue-ladder cases PASS. ArchSmall (no Cherry Picker config) passed it in visit 10; the brief gives ArchSmall to another run, and
  the lane has no testq block for this check. Filed RIMMANDRAKE_RUN_FLOWWORKS_WAYS_OUT_WHERE_CHERRY_PICKER_KEEPS_JUMP_PACK (its
  effect turns green on the first sc_ways_out SUCCESS row). Bars inv_pit_access and ways_in_and_out stay undecided until it runs.
  The runner read rc 0 as PASS on both runs; I corrected both rows (runner_note on each) before any use.
- The other 12 PASS.

### Check repaired in the sitting (no mod code touched)

- sc_hung_bridge, class HARNESS: the under-deck miss read (added in visit 10) called jawa/pawn_get with pawnId=, which the companion
  refuses; the refused call withheld the row's own FAIL as UNMEASURED, so a real miss could never read FAIL. Repaired 00a965aa56
  (pawn=). Planted fault dig(P(5,40)) left at 1 notch (evidence/plant_und_dig_1notch.patch): before the repair UNMEASURED
  (evidence/und_plant.json), after it FAIL rc 1 (evidence/und_plant_repaired.json). Real build after the repair: 40 rows, 0 FAIL,
  UND_floor_path_walks_under PASS (the row's `repair` field).
- red-seen: `maturation.py red-seen FlowWorks sc_hung_bridge` refused, by its own rule, a fault planted in the test file, and a C#
  plant would never reach the deployed build. The red run is recorded by hand in the row's `repair.planted`. No offline decider
  reads suspension_bridge_proof.py.

## Owed cases

- The road back, RIMMANDRAKE_TRACE_FLOWWORKS_UNDER_DECK_PATH_MISS_ONE_IN_28_RUNS: sc_hung_bridge PASS twice; loop_und.sh 12:
  12 of 12 UND_floor_path_walks_under PASS (evidence/und_loop.log); plant FAIL after the repair (above). No miss in 14 runs.
- The four blind-cycle Problems (film never drowns crops, sheet settings units, converter rate and sun, drill setting): their
  check sc_garden keeps its visit 10 PASS (78f51ace1d holds fix 48864bd58c; rerun_relation: untouched). Not run again here.
- The six planted faults of cycle 4: none was played in a game. Each is C# or a harness file that the game loads only from a build;
  what each check would see is as visit 3 recorded. CHANGED_GLOW_ROOM_SHORT is in glow_tank_live.py, which none of this visit's
  checks runs.
- Fuzz and glow Polish lines: sc_fill_front, sc_one_surface keep their visit 10 PASS.
- The three lane-1 not_kernel rows (sheet, thirst, drill maps): not settled here; no row of this visit reads them.

## Beyond the checks: the labelled savegame and what was caught

- The walk save is staged on flowworks_list (his walk list), calm site, by owner_review_stage.py under save_guard (VERIFIED: no keeper
  changed; 723 keepers backed up). 79 numbered stations, a sign book on each (walk_twins.py check: 79 signs, 0 aftermath, ok).
- Fixed in the run, a67c360104: the stager wrote number labels and no sign book (walk_twins read visit 4's save COULD NOT LOOK);
  it now places reviewmap.sign_book per station (selftest red 3, then green). objects_sheet.choose_look matched only "whole connected
  run", and the live pipe menu reads "<Look>: the whole line" (selftest_choose_look_rows.py red 1, then green).
- Caught, filed, not fixed (mod): Choose style on a sprinkler line throws InvalidCastException (PipeLook MapLineGraph: a pipe
  Thing reached through Touching is classed Pipe and cast to IntVec3). Stations 24-27 wear Scrapper, all four.
  RIMMANDRAKE_FIX_FLOWWORKS_LINE_LOOK_CAST_THROWS_WHEN_TANK_TOUCHES_PIPE, with the known fix. Not fixed here: a C# change sends
  every check that reads the mod's C# back, past the bound.
- Caught and re-staged: at the default origin, north-south stations 69, 74, 75 were bare pits (ProofBuild "Anchor: Too close to
  map edge", read as success). Re-staged with --origin 24,100: every deck reads back. Stager fault filed:
  RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_STAGER_NS_ROW_IN_EDGE_BAND_READ_AS_BUILT.
- Filed: RIMMANDRAKE_TRACE_FLOWWORKS_TWO_NOTCH_STRIP_READS_FIVE_THOUSAND_LITRES (station 17 reads 1,000 L a square on 5 squares,
  2,000 L staged; the same in visit 4).
- Looked at: the overview and all 13 row pictures (screenshots/, JPG copies under 1 MB). strange.jsonl: 6 rows, 4 filed, 2 explained.
- No raid, no flyer.

## Items filed

RIMMANDRAKE_RUN_FLOWWORKS_WAYS_OUT_WHERE_CHERRY_PICKER_KEEPS_JUMP_PACK, RIMMANDRAKE_FIX_FLOWWORKS_LINE_LOOK_CAST_THROWS_WHEN_TANK_TOUCHES_PIPE,
RIMMANDRAKE_FIX_FLOWWORKS_REVIEW_STAGER_NS_ROW_IN_EDGE_BAND_READ_AS_BUILT, RIMMANDRAKE_TRACE_FLOWWORKS_TWO_NOTCH_STRIP_READS_FIVE_THOUSAND_LITRES

## Exit
```
ingame_rows: {sc_canal_fire: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: unmeasured, sc_sluice: pass, sc_trench_cover_pawns: pass, sc_hung_bridge: pass, sc_pit_crowd: pass, sc_moat_walkers: pass, sc_hole_prison: pass, sc_toss_flame: pass, sc_islands_walker: pass, sc_walk: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT11_SMALL_20261124_1859.rws
exit_met: false
```
