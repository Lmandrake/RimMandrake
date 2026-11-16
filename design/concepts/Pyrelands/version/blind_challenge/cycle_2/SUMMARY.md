# Pyrelands 0.1.0 — blind challenge, cycle 2 (visit 1)

Judge: detached helper RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_TWO_TESTS_FIRST (seat BENCH), blind, new.

## Start time
2026-11-16T21:08:08Z (UTC), written before any mod file was opened.

## Changed files to bars
`git diff --name-only f5e310809f origin/main` over the brief's paths, minus `/blind_challenge/`: 140 files [measured]. The map,
by input (only code diffs and bar text were read before lane 1; tests, validation.py and evidence were not opened):

| changed file(s) | bars whose inputs they touch |
|---|---|
| `Defs/BiomeDefs/Pyrelands.xml` (description: dry ash now "fair ground") | biome_text_says_engineered, inv_art_and_text, ash_fertile_when_watered |
| `Defs/ThingDefs_Races/RM_PyrelandsFauna.xml` (furnace-beast bs 6 -> 9, hunger, draw sizes, combatPower) | furnacebeast_warms, inv_furnacebeast, populations_are_the_biomes_own, inv_animal_roster |
| `Defs/WeatherDefs/BlackRain.xml` (comment), `Source/FireEcologyHook.cs` (black rain douses), `RM_PyrelandsMod.cs` (blackRainDousing switch + slider, bs-9 tooltip) | three_skies, inv_weather, inv_settings_gate, furnacebeast_warms |
| `Source/PyrelandsNoOrdinaryRain.cs` (new), `FireEcologyHook.csproj` | no_ordinary_rain, inv_weather, inv_settings_gate |
| `Source/Kernel/RM_FireEcoKernel.cs` (rain, dousing kernels) | no_ordinary_rain, three_skies, inv_settings_gate, ash_fertility_probe (the probe's kernel file) |
| `Source/Kernel/RM_BurnKernel.cs`, `MapComponent_BurnLine.cs` (herd anchor never fresh) | ullai_graze_old_burns, inv_ullai_herd_giant |
| `Source/PyrelandsAshSand.cs` (ProbeCharred) | ruins_stand_blackened, inv_ruins_scorched |
| `Source/RM_PyrelandsGiants.cs` (classic restore hunger) | furnacebeast_warms, inv_settings_gate |
| `Source/GenStep_PyrelandsFireCast.cs` (comment only) | populations_are_the_biomes_own |
| `Source/SelfTest/Fuzz/PyrelandsFuzz.cs` | ullai_graze_old_burns (its fuzz; opened in lane 2) |
| `Textures/.../FurnaceBeast_Giant_{east,north,south}.png` | inv_art_and_text, furnacebeast_warms |
| `Assemblies/FireEcologyHook.dll(.srchash)` | every C# bar |
| `selftest_pyrelands_defs_offline.py`, `_site.py`, `_settings_sweep.py`, `Utils/selftest_settings_screens.py`, `preflight_pyrelands.py` | biome_text_says_engineered, inv_firebreak_firefoam, inv_settings_gate (their deciders) |
| `selftest_pyrelands_furnace_beast_art.py`, `_round6_*`, `_self_contained.py`, `_ten_scenes_parts.py`, `_walk_digest.py`, `Utils/selftest_pyrelands_burn_cost.py`, `validation.py`, `human_review.py`, `firehawk_rewards_live.py` | stage-6 bars (furnacebeast_warms, populations, walk, burn_line_walks, inv_firehawk_hunt_rewards, ...) |
| locked files changed: `tree.json` (leaves ash_fertile_when_watered, grass_carpets_and_regreens, populations_are_the_biomes_own, ruins_stand_blackened, firehawk_lights_ahead, furnacebeast_warms, no_ordinary_rain, walk_season_on_the_pyre; leaves added firehawk_hunt_rewards, ullai_cross_the_map_as_vanilla_herds), `sheet.md` (same leaves), `scenes.json`, `VERSION.json`, `bars.md` (43 bars) | those leaves, inv_firehawk_hunt_rewards |
| design records (journal, exam, evidence, in_game/visit_1, test_table, gaps, stage records) | none as inputs to logic |

Lane-1 scope therefore: all six offline bars (each has a changed input: the description, the probe's kernel file, the
settings file, the site and sweep tests, the textures; inv_lightning_breaker by its absence check over the changed Defs),
then the kernel-backed stage-6 bars above.

## Lane 1
Inputs read: `tree.json`, `sheet.md`, `plan.md`, `version/VERSION.json`, `version/bars.md`, `record.json` (the inventory
rows' own text: four offline bars are inventory rows and their words live only there), the three settings files, `Defs/`,
`Patches/`, `About/`, the six kernels (`FurnaceWarmthMath.cs` and the five in `Kernel/`), and the RimUtinni patch that adds
the biome's patch-added cast (for body sizes). Not opened: tests, validation.py, evidence, journal, test table.

Command: `python3 design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane1/run_lane1.py` (C# half staged under
`/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c2_lane1/`, Windows dotnet; Python half over Defs and settings).

Result [measured]: **63 rows: 45 PASS, 0 FAIL, 6 INFO, 12 UNSETTLED** (all 12 are `not_kernel` rows for stage-6 bars whose
logic is game-side; none names an offline bar). Offline bars: ash_fertility_probe 4 rows PASS (part-by-part, refusal,
the base-everywhere false pass, 4 000 random lines); biome_text_says_engineered PASS; inv_firebreak_firefoam 2 PASS;
inv_lightning_breaker PASS; inv_settings_gate 11 PASS (gate truth table, every gated kernel inert with the master off,
43 settings saved with their shipped defaults, 17 sliders holding their defaults, every switch declared, world switch
off and labelled); inv_art_and_text: 53 texPaths in our folders resolve, the approval itself is a record (INFO, lane 2).
Kernel-backed stage-6 rows (ruled 70/140/120/190 numbers, bonus clock, black rain putting a grass fire out in 5 beats while
clear sky and vanilla rain do not, ordinary rain swapped, herd anchor never fresh, warmth fall-off, bed ignition, furnace
size 9 vs Zeer 4.5, heat bank, crestfeather 125/400, letter once) all PASS. Weak row noted: `firehawk_drop_is_fuel_and_lawful`
found only 5 drops in 600 random grids, so it exercises little.

## Lane 2 reruns
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending, sealed until lane 1 is committed)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
