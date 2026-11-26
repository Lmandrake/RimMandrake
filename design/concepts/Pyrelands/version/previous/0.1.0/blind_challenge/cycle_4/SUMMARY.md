# Pyrelands 0.1.0 blind challenge, cycle 4

## Start time
2026-11-21T00:36:15Z (2026-11-20 4:36 PM PST), before any input was opened.

## Changed files to bars
`git diff --name-only 26c6f53375 origin/main` over the brief's paths, `/blind_challenge/` dropped: 56 files [measured].
Locked files, by id on the changed lines [measured, structural diff of the JSON at both shas]:
- `tree.json`: leaves ash_fertile_when_watered, burn_line_walks, fire_walks_with_wind (new), firehawk_hunt_rewards (coverage of
  inv_firehawk_hunt_rewards), fresh_burn_compounds_with_black_rain, furnacebeast_warms, grass_carpets_and_regreens,
  sand_shovel_yields_glass_sand, scorchfruit_born_of_fire; plus `coverage` and `root_hash`.
- `scenes.json`: sc_ash_watered, sc_burn_compounds, sc_burn_line_walks, sc_fire_walks_with_wind, sc_firehawk_rewards, sc_furnace_giant,
  sc_furnace_hide_bank, sc_grass_regreens, sc_sand_shovel, sc_scorchfruit; `coverage_rest`.
- `record.json`: inv_burn_line_fire_clock; `decisions`. `sheet.md` and `version/bars.md`: the same leaves' sentences (re-pins).
Code and data, by what each file feeds:
- `Source/FireEcologyHook.cs`, `Source/Kernel/RM_BurnKernel.cs`, `Source/MapComponent_BurnLine.cs`, `Source/PyrelandsFireFront.cs`,
  `pyre_burn_sim.py`, `pyre_save_burn_grid.py`, `wind_burn_live.py`, `testdata/pyre_walk_visit1.npz`, `Assemblies/FireEcologyHook.dll(.srchash)`:
  burn_line_walks, fire_walks_with_wind, inv_burn_line_fire_clock, grass_carpets_and_regreens, scorchfruit_born_of_fire, three_skies
  (black-rain dousing), inv_settings_gate (the new wind switch).
- `Source/PyrelandsTuning.cs`, `Source/RM_PyrelandsMod.cs`, `Languages/English/Keyed/Pyrelands.xml`, `preflight_pyrelands.py`: inv_settings_gate,
  inv_art_and_text (text).
- `About/About.xml`: inv_art_and_text, biome_text_says_engineered (the mod's own description).
- Tests and harness (`selftest_pyrelands_ash_probe.py`, `_defs_offline.py`, `_settings_sweep.py`, `_site.py`, `_burn_ecology.py`,
  `_wind_burn_rows.py`, `_round6_*`, `validation.py`, `Source/SelfTest/Fuzz/PyrelandsFuzz.cs`): the bars their rows decide
  (ash_fertility_probe, biome_text_says_engineered, inv_settings_gate, burn_line_walks, fire_walks_with_wind).
- Records (`coverage_*`, `exam*`, `journal.md`, `result.*`, `stage.json`, `version/evidence/*`, `version/in_game/unrun.jsonl`,
  `version/locked_bars.json`, `version/next_version/README.md`, `version/run_spend.jsonl`, `version/stage_record.json`,
  `version/test_table.*`, `pilot_throwaway/make_test_table.py`): no bar input; they record stages.
Lane-1 scope: the 6 offline bars, all; and of the stage-6 bars, those with a kernel: fire_walks_with_wind, burn_line_walks,
fresh_burn_compounds_with_black_rain, ash_fertile_when_watered, furnacebeast_warms, inv_firehawk_hunt_rewards.

## Lane 1
Written from the bars (tree.json, sheet.md, plan.md, record.json rows, bars.md), the shipped settings and the named kernels only.
Command: `python3 design/concepts/Pyrelands/version/blind_challenge/cycle_4/lane1/run_lane1.py` (C# `BlindLane1.cs` against
RM_FireEcoKernel, RM_BurnKernel, RM_FireHawkRewardsKernel, FurnaceWarmthMath; Python `BlindLane1.py` over Defs, Patches, Languages,
About and RM_PyrelandsMod.cs).
Result: 68 rows: **25 PASS, 0 FAIL, 5 INFO, 38 UNSETTLED** [measured]. Every UNSETTLED row is `not_kernel` on a stage-6 bar
(32 bars with no kernel, 6 with a kernel half and a game-side half); no offline bar has an UNSETTLED row.
Every offline bar has PASS rows: ash_fertility_probe 4 (+ 4 shared), biome_text_says_engineered 2, inv_firebreak_firefoam 1,
inv_lightning_breaker 1, inv_settings_gate 7, inv_art_and_text 1 (+ 3 INFO).
Two of my own rows were wrong on their first run and were fixed before this record (harness, not mod): the culture check counted
the comma inside the refusal sentence, and the description-overwrite pattern matched a patch that only adds an extension to the
BiomeDef (RM_AcousticPayload_Pyrelands.xml).
INFO worth reading: the slider sweep (compound_slider_sweep) finds the compound ordering fails only at player tunings (watered 2.0
hits the cap 2.0; watered at or below dry); the Pristine Firehawk Crestfeather is drawn with vanilla's ThrumboHorn texture
(art_texture_paths_resolve); 44 settings fields against the record row's "about 47".

## Lane 2 reruns
`lane2/rerun_offline.py` over every `offline` and `record` test of `version/test_table.json`, recorded commands, private
`WINBUILD_ROOT`: **23 of 23 PASS** [measured] (`lane2/reruns.jsonl`). All 7 deciders of the 6 offline bars PASS and match
their recorded verdict. 21 of 23 match the recorded verdict; the 2 that do not: `T_ROUND6_GAPS` recorded FAIL (1 of 18), now
PASS (0 of 18); `T_FURNACE_ART_OFFLINE` had no recorded run, now PASS. After the fix the 7 deciders were rerun at `3962b91eb4`:
7 of 7 PASS (`lane2/reruns_after_fix.jsonl`), and lane 1 again 25 PASS, 0 FAIL (`lane2/lane1_rows_after_fix.jsonl`).

## Planted
42 faults (`lane2/planted_faults.json`): 13 in kernels (RM_FireEcoKernel 9, RM_BurnKernel 4), 13 in game-side callers and
patches (FireEcologyHook 4, MapComponent_BurnLine 2, PyrelandsAshField 4, PyrelandsMechanicsGate 1, PyrelandsFireFront 2),
4 in settings, 2 in tuning, 2 in About.xml, 2 in Keyed, 2 in the preflight, 2 in the biome def, 2 in the burn model. Run by
`lane2/plant_faults.py` (restores on signal, private `WINBUILD_ROOT`), baseline first: every suite green; last line
`tree_clean_after: true` [measured].
**Caught 34 of 42** [measured]: the recorder says 33, and `SIM_fire_makes_two` is a catch it filed as BROKE: T_BURN_ECOLOGY's
own assertion failed (`AssertionError`, its RED CONTROL row), which is the check going red, not a crash. Lane 1 caught 19.
Missed by every suite run: `H_wind_ignores_its_switch`, `H_stamp_caller_skips_gate` (both offline bar inv_settings_gate; fixed,
see Faults), `AB_promises_worldgen` (Polish), and five stage-6 wind and rain faults (`B_line_lit_along_the_wind`,
`FF_line_any_bearing`, `FF_wind_not_from_scar`, `H_carry_never_marked`, `H_douses_under_a_roof`; Polish, owed to the live scenes).
Caught, but not by a decider of the offline bar named: `K_roster_toggle_ignored`, `K_stamp_ignores_master` (lane 1 only),
`K_douse_ignores_gate` (T_FUZZ only): the gate fault class, fixed below. `K_future_stamp_counts` and
`K_rain_hours_zero_still_waters` are fertility-rule faults the probe reports faithfully; T_FUZZ catches them.
`KY_wind_letter_missing` is caught by T_SELF_CONTAINED_OFFLINE.
Not planted: the changed records, data and test files (JSON records, `.npz`, the DLL, the selftests themselves) and the
live-only scripts (`validation.py`, `wind_burn_live.py`, `pyre_save_burn_grid.py`): no offline suite runs them.

## Faults
`lane2/faults.json`: **1 Problem, 2 Polish** [measured]. The Problem is `miss_of: 3` (the decider file and the gate code were
both there when cycle 3 judged).
- `RIMMANDRAKE_REPAIR_PYRE_GATE_DECIDER_FOUR_FAULTS_GREEN`, Problem against the check (class HARNESS), bar inv_settings_gate:
  the three deciders (T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREENS, T_SITE) stayed green under five planted gate faults: the
  kernel MechanicsOn ignoring the roster toggle, BurnStampMay ignoring the master (kernel and caller), BlackRainDouseAmount
  ignoring the gate, and the wind patches no longer reading WindCarries (the wind then carries fire on every map with every
  switch off). The sweep is static and checked the gate where it is spelled, not where it is decided. FIXED.
- `RIMMANDRAKE_NOTE_PYRE_WIND_FAULTS_LIVE_ONLY_TO_SEE`, Polish: five stage-6 wind and rain faults no offline test sees.
- `PYRE_ABOUT_WORLDGEN_WORDLIST_MISSES_PLACING`, Polish: a verb list in T_DEFS_OFFLINE would pass a false About sentence.
No mod fault was found: the mod's code, defs and settings are right on every bar lane 1 and lane 2 could read.

## Fixes
One check repair, two commits, both changing only `src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py`:
`cf9f36d052` (facts kernel_gates, gate_args, wind_reads_pred; 4 mutants) and `3962b91eb4` (each gate predicate shuts on
its own gate argument; 2 mutants). At `3962b91eb4` the repaired decider goes red (rc 1) on each of the five plants, each on
its own new fact, and is green (rc 0, 27 of 27 mutants red) on the real build (`lane2/fixes.jsonl`). Red seen recorded twice
(`maturation.py red-seen Pyrelands T_SETTINGS_SWEEP_OFFLINE`, patches in `lane2/patches/`). A check repair owes no fresh reader.

## Steward's decisions enacted
Read after lane 1 was committed. Acted on: bar fire_walks_with_wind (bar-added 2026-11-17 9:26 AM) judged as one of the 44;
the re-pin of 2026-11-17 9:26 AM taken as the locked text; the holds of 2026-11-16 8:36 PM and 2026-11-17 6:52 AM read as
lifted by their release lines. One ledger event, `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER.jsonl).

## Tests edited
`tests_edited.json`: one file, `src/RimMandrake/Pyrelands/selftest_pyrelands_settings_sweep.py` (sha256 1451129049a0 ->
after, on `df4deb9076` -> `3962b91eb4`). Three facts and six mutants added; nothing removed or loosened.

## Unsettled
- 38 lane-1 rows are `not_kernel` UNSETTLED, all on stage-6 bars; no offline bar has one. They are settled by their live scenes.
- Journal question 4 (is `no_ordinary_rain` decidable offline?): no. Ordinary rain reaches a Pyrelands map by two roads off
  the biome list (a game condition's forced weather, Odyssey's WetClimate mutator, per RM_FireEcoKernel.OrdinaryRainDefNames'
  note); the swap is a Harmony postfix on the weather decider, so the bar stays at Stage 6.
- Journal oddity 8: `sc_three_skies` names `validation.py::cinderfall` as its entry; that function compares cinderfall with
  ash fall (def fields, lightning) and does not force black rain, which is a separate chain (`blackrain`). The scene's action
  forces all three skies. For the Stage 6 driver: check which chains the scene runs [guess ~60% that it needs both chains named].
- `sc_fire_walks_with_wind` sets its wind by `SetWindForTest`, so the wind taken from yesterday's scar on a fresh map is seen
  by no offline or staged test.

## Exit
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: true

## Owed
Nothing from this cycle: the Problem is fixed and shown both ways; the Polish lines are on `version/polish.md`. The live tests
named in Unsettled remain Stage 6's.
`T_SETTINGS_SWEEP_OFFLINE`'s recorded run went stale with the edit; `maturation.py certificate Pyrelands --run --resume`
restamped it (version/test_table.json runs_today). The certificate still refuses inv_sand_shovel and
sand_shovel_yields_glass_sand at `asks_on_empty_game` (validation.py's `sand_carries_the_dig_yield` reads the XML on disk
inside a live chain): already filed as `RIMMANDRAKE_UNMEASURE_SAND_SHOVEL_ROW_PASSING_ON_EMPTY_MAP`, not this cycle's.

Reader (`maturation.py next Pyrelands`, 2026-11-20): "blind cycle 4 (visit 3, total 4): exit met: the block says exit_met true
and every file check agrees (6 offline bars, 9 deciders rerun PASS); lane-1 not_kernel UNSETTLED row(s) deferred to Stage 6".
