# Pyrelands 0.1.0, blind challenge cycle 5

## Start time
2026-11-22T03:01:26Z (2026-11-21 19:01 PST). Judge unit: RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_FIVE_TESTS_FIRST (seat BENCH, detached).

## Changed files to bars
`git diff --name-only 91be0bc987 origin/main -- <the brief's paths> | grep -v /blind_challenge/` lists 363 files [measured]
(the list: `/tmp` at run time; regenerate with the same command). Most are records (in_game visits, evidence, result
files, exam, journal, test table). The ones whose content is a bar's input:

| changed file | bars whose inputs it touches |
|---|---|
| `Source/Kernel/RM_FireEcoKernel.cs` (burrower nudge kinds added) | ashwallow_dives_unharmed, inv_burrowers_heat_dome; it is also the ash_fertility_probe kernel, so that offline bar is in scope |
| `Source/MapComponent_BurnLine.cs` (nudge reads the kernel) | ashwallow_dives_unharmed, inv_burrowers_heat_dome |
| `Source/RM_JobGiver_BurrowOnFire.cs`, `Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml` | ashwallow_dives_unharmed, inv_burrowers_heat_dome |
| `Source/FireHawkRewards.cs`, `Languages/English/Keyed/Pyrelands.xml` | inv_firehawk_hunt_rewards; inv_art_and_text (text) |
| `Defs/DamageDefs/RM_FlamefangVenomBite.xml`, `Defs/HediffDefs/RM_FlamefangVenom.xml` | flamefang_bite_carries_venom, inv_animal_roster |
| `Assemblies/FireEcologyHook.dll` (+ `.srchash`) | every C# bar (the built image of the sources above) |
| `preflight_pyrelands.py` | inv_settings_gate (a kernel the brief names) |
| `selftest_pyrelands_settings_sweep.py`, `selftest_pyrelands_site.py` | inv_settings_gate (deciders) |
| `selftest_pyrelands_defs_offline.py` | biome_text_says_engineered (decider) |
| `validation.py`, `human_review.py`, `wind_burn_live.py`, `firehawk_rewards_live.py`, `venom_dose.py` and the other changed `selftest_pyrelands_*.py` | the stage-6 bars their scenes read (opened only in lane 2) |
| `tree.json` (locked) | no leaf changed: only `root_hash` and the `coverage` stamp moved [measured field by field] |
| `scenes.json` (locked) | controls removed from the scenes of ash_ground_and_blowing_ash, populations_are_the_biomes_own, the herd-thirst scene, ruins_stand_blackened, no_ordinary_rain, flamefang_bite_carries_venom and the furnace-beast size scene (stage-6 bars) |

Lane-1 scope from this map: the 6 offline bars (all; the FireEcoKernel change puts the probe's kernel in scope, and the
settings deciders changed), plus the kernel halves of the stage-6 bars above and of every bar a shipped kernel decides.

## Lane 1
Committed blind, before anything sealed was opened. `python3 lane1/run_lane1.py` (C#: `BlindLane1.cs` compiled with the six
game-free kernels as shipped, per-user Windows dotnet, staged under `D:\ClaudeWork\rimmandrake\scratch\pyrelands_blind_c5_lane1`;
Python: `lane1/lane1_defs.py` on the defs, text and settings). Inputs: tree.json, sheet.md, plan.md, VERSION.json,
bars.md, record.json's inventory rows (the inventory bars' text lives there), the three settings files, Defs/, Patches/,
Languages/ (text is part of inv_art_and_text), the kernels; RimSage for six vanilla texture paths.

Rows: **49; 45 PASS, 3 INFO, 1 UNSETTLED, 0 FAIL** [measured].
- Offline bars: ash_fertility_probe 3 rows PASS (wet fresh vs dry old part by part; refuses with the ash field or the gate
  off; 20 000 random cells, seed 20261121); biome_text_says_engineered 2 PASS; inv_firebreak_firefoam 2 PASS;
  inv_lightning_breaker 1 PASS; inv_settings_gate 7 PASS + 1 INFO (every gate predicate shut with its switch off,
  4 000 random input sets; 44 settings saved with their shipped default; 17 slider ranges hold the default; worldgen ships
  off, labelled unsupported); inv_art_and_text 6 PASS + 1 INFO (60 texture paths resolve, 6 of them vanilla Core seen in
  RimSage; 43 defs labelled and described; 36 keyed keys present; no `{A_B}` slot; the approval itself is a record, INFO).
- Stage-6 kernel halves: 27 rows over furnace warmth, charge and sleep ignition, the hawk's drop (600 random grids), the
  letter and crestfeather, the keep-alive and fire clock, front lines, wind probes (1.49 M cases), black rain, the
  burrower nudge and dome, wet roots, scorch-fruit rolls and the allowlist.
- INFO `compound_slider_corners`: at slider corners past the shipped values the fertility cap 2.0 makes a wet fresh
  scar equal wet old ash, and watered can be set below dry: player tuning, not the shipped experience.
- UNSETTLED `game_side_bars`: 17 bars, all stage 6, have no game-free kernel; each settles by its Stage 6 scene.
- One row was reframed before recording: `wind_probes_never_back_or_sideways` first asked the mean carry DISPLACEMENT to
  sit within 1.5 degrees of the wind at one bearing (a number the bar does not hold); it read 2.4 there because a diagonal
  step is sqrt 2 long. It now asks every probe downwind and the mean carry within 10 degrees at every bearing (worst 5.0).

## Lane 2 reruns
(not started)

## Planted
(not started)

## Faults
(not started)

## Fixes
(not started)

## Steward's decisions enacted
(sealed until lane 1 is committed)

## Tests edited
(not started)

## Unsettled
(not started)

## Exit
(not written)

## Owed
(in progress)
