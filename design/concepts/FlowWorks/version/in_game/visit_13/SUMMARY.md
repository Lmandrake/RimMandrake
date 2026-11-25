# FlowWorks 0.1.0, in-game acceptance visit 13 (ArchBig, Archmagi)

Driver: detached BENCH run, item RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_ACCEPTANCE_VISIT_THIRTEEN. Started 2026-11-25 9:34 AM PST.

## Progress

- 09:40 PST: bridge on ArchBig taken. 10 of 22 checks already PASS on Steve2 (testq, mod_sha 617ca4999a). 12 left for ArchBig:
  sc_dig_and_read, sc_dig_finds, sc_fill_tiers, sc_canal_fire, sc_slime, sc_pit_reads, sc_covered_pit, sc_ways_out,
  sc_sluice, sc_one_network, sc_pit_crowd, OL_OWNER_LOOK_READS. Their Steve2 chain readings are COULD NOT LOOK (modcheck's own list, no tier's).

- 10:08 PST: 11 of the 12 PASS on ArchBig (flowworks_list, 20 mods). Walk save staged and looked at (13 row pictures + overview).
  ArchBig swapped to evening_20261113 (23 mods) for OL_OWNER_LOOK_READS (its big-pit plan needs ColdStorage defs).

## What ran

- 22 checks owed. 10 ran on Steve2 through the SteveDesktop lane this morning (testq, 13-mod `flowworks` tier, mod_sha 617ca4999a,
  mod hash f5bace71): sc_coating_wash, sc_fill_front, sc_geyser_tub, sc_hose_look, sc_ice, sc_islands_walker, sc_moat_walkers,
  sc_one_surface, sc_toss_flame, sc_trench_cover_pawns. All PASS. Nine lane chain readings of the other checks are COULD NOT LOOK
  (modcheck's own list, no tier's), and count for nothing.
- 12 ran here on ArchBig, deployed hash f5bace71 = source 617ca4999a (deploy dry run: in sync), each on the calm test site,
  read back as verified:
  - on `flowworks_list` (the small list, 20 mods): sc_dig_and_read, sc_dig_finds, sc_fill_tiers, sc_slime, sc_pit_reads,
    sc_covered_pit, sc_sluice, sc_one_network (extension_proof chains), sc_canal_fire (x10_canal_fire_live.py), sc_pit_crowd,
    sc_ways_out (live_session B0,B4). All PASS on the first run.
  - on `evening_20261113` (23 mods; the big-pit plan places ColdStorage containers, which the small list lacks): OL_OWNER_LOOK_READS on
    the big-pit series (big_pit_scene plan/stage/fill/verify: 253 PASS, 1 UNMEASURED label row with no bridge reader, known):
    1629 PASS, 0 FAIL, 0 UNMEASURED, 0 BLOCKED.
- No FAIL, no UNMEASURED among the 22. No mod change in the sitting. No check repaired or removed. No raid, no flyer.
- Inside sc_ways_out, the row B4_dehydration_rate read FAIL (0.114/day against 0.30). That row decides no bar. Traced to the
  harness (strange.jsonl row 1, polish.md line 1).
- Form repairs to the record: my row writer (run_row.py) stamped tier `flowworks` on the 11 small-list rows; the rows say
  `flowworks_list` now, with `tier_relabelled`, and the writer's default is `flowworks_list`. build_match: 35 count, 0 to run.
- The write guard refused bridge writes once the lock's heartbeat was 20 minutes old (the big-pit plan read every def as
  "unreadable"). Writes ran under `game_lock.py run` from then on. waitalive starts its job outside the holder's process tree, so
  the lock was released to the waitalive job and claimed again after it.

## The owed cases (blind challenge cycle 4)

- RIMMANDRAKE_NOTE_FLOWWORKS_FUZZ_BLIND_TO_ONE_SINK_PATH, CHANGED_FUZZ_SINK_UNREPORTED: sc_fill_front and sc_one_surface PASS
  (Steve2). They read levels, not the kernel's sink report, so they would not have seen the planted `sinkDrained += 0f * total`
  [guess ~75%]. Not played in a game.
- RIMMANDRAKE_NOTE_FLOWWORKS_GLOW_ROOM_RECT_UNPINNED, CHANGED_GLOW_ROOM_SHORT: no check of this visit runs glow_tank_live.py
  (OL_OWNER_LOOK_READS and sc_fill_tiers do not call room_rect), so none would have seen it [measured by reading the commands].
- CALLER_CONV_SUN_FACTOR_SKIPPED, CALLER_CONV_RATE_SETTING_IGNORED, CALLER_DRILL_IGNORES_SETTING, CALLER_SHEET_DOOR_PERCENT_AS_PERMILLE:
  no stage-6 check decides inv_converters, inv_drilling or inv_overflow_sheet, and none of the 22 exercises a converter, a drill
  or a sheet door, so none would have seen them [measured by reading the commands]. No in-game case was written this visit: the
  cycle's lane 2 reports all 12 caller faults caught offline after its fix, and these bars are outside this stage's exit.
- Lane-1 UNSETTLED SHEET_GAME_SIDE_NOT_KERNEL, DRILL_RIGHT_MAPS_NOT_KERNEL: not settled in game (no check reads crop drowning or
  the survey roll). THIRST_GAME_SIDE_NOT_KERNEL: sc_faucet_drink keeps its earlier PASS; bottle jobs moving exact litres not read.
- Owed from the road back (unrun.jsonl): none recorded.

## Beyond the checks: the walk save and what was seen

- Walk save, staged on `flowworks_list` on ArchBig, calm site (250x250, AridShrubland), owner_review_stage.py under save_guard
  (VERIFIED: no keeper changed; 787 keepers backed up). 79 stations with a sign book each; `walk_twins.py check`: 79 signs,
  0 aftermath, ok. Sluice and grate held open read open=True seals=False; the 0.2 m strip reads 0.20 m (400 L) on all five squares.
- Looked at: the overview and 12 row pictures (screenshots/, JPG under 1 MB). strange.jsonl: 4 rows, all explained, none filed:
  the dehydration row's harness id mismatch; the calm site's Void Monolith beside station 40 (no cover effect: vanilla=0.000);
  the bars row pictures framed off-centre (the picture only, not the save); a vanilla steam geyser.
- polish.md: three lines.
- ArchBig is left running on `evening_20261113` with the big-pit map. The walk save is on ArchBig's Saves folder; its list is
  `flowworks_list` (load it after `modset_builder.py --tier flowworks_list --apply`).

- The 13 checks the change does not touch keep their PASS from earlier rows (early_rows.jsonl and visits 2, 10, 12; build_match counts
  them): sc_source_draws, sc_source_refills, sc_lake_endless, sc_pawn_height, sc_hung_bridge, sc_river, sc_hole_prison, sc_walk_reload, sc_walk_switch, sc_walk_second_order, sc_sprinkler_pump, sc_faucet_drink, PIT_LOOK_1114_LIVE. They are in the exit block as pass and were not run again.

## Items filed

None.

## Why the exit is not met

Every one of the 35 counted checks reads PASS, and build_match counts all 35. `maturation.py next FlowWorks` gives one reason
only: the mod change 033392ed2d (a humanlike's height follows its body size) landed while the mod stood at his walk, and owes one
fresh reader. The brief says the steward run that reads this visit is that reader, and that this run never writes fix_reviews.jsonl.

## Exit
```
ingame_rows: {sc_dig_and_read: pass, sc_dig_finds: pass, sc_fill_front: pass, sc_fill_tiers: pass, sc_one_surface: pass, sc_canal_fire: pass, sc_slime: pass, sc_pit_reads: pass, sc_covered_pit: pass, sc_ways_out: pass, sc_sluice: pass, sc_hose_look: pass, sc_one_network: pass, sc_trench_cover_pawns: pass, sc_ice: pass, sc_pit_crowd: pass, sc_moat_walkers: pass, sc_toss_flame: pass, sc_islands_walker: pass, OL_OWNER_LOOK_READS: pass, sc_geyser_tub: pass, sc_coating_wash: pass, sc_source_draws: pass, sc_source_refills: pass, sc_lake_endless: pass, sc_pawn_height: pass, sc_hung_bridge: pass, sc_river: pass, sc_hole_prison: pass, sc_walk_reload: pass, sc_walk_switch: pass, sc_walk_second_order: pass, sc_sprinkler_pump: pass, sc_faucet_drink: pass, PIT_LOOK_1114_LIVE: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957.rws
exit_met: false
```
