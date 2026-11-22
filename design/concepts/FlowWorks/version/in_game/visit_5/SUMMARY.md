# FlowWorks 0.1.0 — in-game acceptance, visit 5

Driver: detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_FIVE, game a. Ran 2026-11-21
6:42-8:00 PM PST (bound 9:42 PM).

Why this visit: the steward's decision of 2026-11-21 6:32 PM PST. In-game checks that count from a build older than the C#
they exercise run again before his walk. The test table now declares `exercises`, and `rerun_relation.py` named 24 of 31
checks as touched [measured]. This visit ran those 24.

## Build and lists

- FlowWorks deployed at bdd56c6ff6 (the visit-4 build). The deploy dry run read "in sync (1038 files)", and no mod source
  changed since [measured]. Every row names it.
- Game a. Lists: the 13-mod flowworks tier for 22 checks; evening_20261113 (22 mods) for PIT_LOOK_1114_LIVE on his sitting
  save SITTING_20261114_PIT_FIXES (loaded with --ignore-missing-mods, as visit 3); his full list (315 mods, Camera+ in it)
  for sc_walk. Every list holds all five DLC.
- No mod code changed in this visit.

## Results: 23 PASS, 1 FAIL of 24 checks run, last row each [measured]

| check | verdict | runs | notes |
|---|---|---|---|
| sc_fill_front, sc_one_surface, sc_pawn_height, sc_toss_flame, sc_coating_wash, sc_geyser_tub, sc_fetch_fallen, sc_pit_trap_raid, sc_garden | PASS | 1 | concept scenes, calm site verified |
| sc_trench_cover | PASS | 2 | run 1 HARNESS (mine): my 250 s shell timeout killed sc_pawn_height (which needs 338 s) and the next calm-site load timed out at the menu |
| sc_hole_prison | PASS | 2 | run 1 FAIL "awake prisoner gets no ordinary meal delivery", run 2 PASS, same build: intermittent, filed RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO |
| sc_moat_raid | PASS | 2 | run 1 UNMEASURED: the drain held 1 raider and the capture row asks for 2 (the scene's own rule); run 2 held 3, captured 2 |
| sc_dig_and_read, sc_dig_finds, sc_fill_tiers, sc_slime, sc_pit_reads, sc_covered_pit, sc_sluice, sc_one_network | PASS | 1 | extension_proof chains, calm site |
| sc_canal_fire | PASS | 1 | calm site loaded and verified first |
| sc_hung_bridge | **FAIL** | 1 | GRATE_fire_burns_people_above: grate 5 vs solid 13 burns. Class MOD, below |
| PIT_LOOK_1114_LIVE | PASS | 1 | 20 rows PASS, 0 FAIL, on his sitting save |
| sc_walk | PASS | 1 | his full list, 192 s |

Not run (untouched by the change since their rows, `rerun_relation.py`): sc_source_pays, sc_ways_out, sc_hose_look, sc_ice,
sc_islands, sc_river, OL_OWNER_LOOK_READS (its last row stays UNMEASURED, not counted, owner
RIMMANDRAKE_REPORT_SUBMERGE_SHADOW_QUEUE_JUDGE_CANNOT_SEE_ORDER, as in visit 4).

### sc_hung_bridge: MOD, not fixed in the sitting

- The row compares fire attaches on riders of a grated deck and of a solid deck over a burning chemfuel pit. The row's own
  intent is that solid-deck riders stay unburnt. They burn in every run: solid 13 (this visit), 10, 6 and 8 (visit 3's three
  runs) [measured]. So the verdict is a coin flip: visit 3 read FAIL once and PASS twice, and its PASS counted.
- Known and open: GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO (cause: RM_LiquidFire.ApplyInfernoEffects gives a solid-deck rider
  the same in-cell attach as a grated one). I added today's readings to that item. Its 2026-10-29 block reason (an expired
  companion test profile) is stale.
- Not fixed here, because the fix is not known to be enough. The proposed gate covers only the in-cell attach; the beside and
  halo attaches in the same function also reach deck riders. The code is Verse-bound, so no offline test shows it red and
  green. A fix plus a live proof that the row is no longer chance would not finish in this visit.

## Owed cases from the blind challenge (cycle 4)

- The four Problems (FILM_NEVER_DROWNS_CROPS, SHEET_SETTINGS_KEEP_THEIR_UNITS, CONVERTER_CALLER_RATE_AND_SUN,
  DRILL_CALLER_READS_SETTING): sc_garden PASS on this build. As visit 4 said, the garden rows show the converter rate live; the
  sun half, the drill setting and the door-leak percent are not read by any garden row [guess ~70%, from visit 4's reading].
- Planted faults: no plant ran this visit. Visit 3 and 4's readings stand: CALLER_CONV_RATE_SETTING_IGNORED seen; the sun factor,
  the drill setting and the door permille not seen; CHANGED_FUZZ_SINK_UNREPORTED not planted; CHANGED_GLOW_ROOM_SHORT not
  seen (no check runs glow_tank_live.py).
- The lanes SHEET_GAME_SIDE_NOT_KERNEL, THIRST_GAME_SIDE_NOT_KERNEL, DRILL_RIGHT_MAPS_NOT_KERNEL: unchanged from visit 4.

## Owed from the road back (unrun.jsonl)

- sc_walk PASS, PIT_LOOK_1114_LIVE PASS (pour labels 100, 1000 and 2048000 read), sc_fill_front PASS, sc_fill_tiers PASS,
  sc_garden PASS, sc_pit_trap_raid PASS, sc_trench_cover PASS, sc_fetch_fallen PASS, sc_geyser_tub PASS: all on this build.
- sc_hose_look, sc_source_pays, sc_ice: not run (untouched since their visit-3 and visit-4 PASS rows).
- OL_OWNER_LOOK_READS and its zoomed-capture judge reads (pit relief, water by depth, pale blocks): not run this visit; the
  judge reads of captures stay owed to a judge that did not make them.

## Beyond the checks

No exploration or extra screenshots this visit: the run spent its time on the 24 checks and their reruns. Four strange things,
each explained or filed (`strange.jsonl`).

## The savegame

No mod change since visit 4, so the walk savegame is visit 4's, staged on the same build and his full list:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws`
(13.6 MB, 5:29 PM PST) [measured].

## Items filed this visit

RIMMANDRAKE_TRACE_FLOWWORKS_AWAKE_PRISONER_MEAL_SKIPPED_ONE_RUN_IN_TWO (sc_hole_prison intermittent; acceptance test: three
PASS runs in a row). The sc_hung_bridge line goes back on the existing GRATE_FIRE_FIX_SOLID_DECK_BURNS_TOO.

Game a was left at the main menu on his full list; bridge released at 7:58 PM PST.

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_canal_fire: pass, sc_slime: pass, sc_pawn_height: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_sluice: pass, sc_one_network: pass, sc_trench_cover: pass, sc_hung_bridge: fail, sc_moat_raid: pass, sc_hole_prison: pass, sc_toss_flame: pass, sc_fetch_fallen: pass, sc_walk: pass, sc_pit_trap_raid: pass, sc_garden: pass, OL_OWNER_LOOK_READS: unmeasured, sc_geyser_tub: pass, sc_coating_wash: pass, PIT_LOOK_1114_LIVE: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT4_FULL_20261121_1727.rws
exit_met: false
```
