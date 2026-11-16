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
`lane2/rerun_offline.py` reran every `kind` offline or record test of `test_table.json` with its recorded command:
**21 of 21 PASS, 21 of 21 match their recorded verdict** [measured] (`lane2/reruns.jsonl`), the six offline bars' deciders
among them (T_ASH_PROBE_OFFLINE, T_DEFS_OFFLINE, T_CUT_STAYS_CUT, T_SETTINGS_SWEEP_OFFLINE, T_SETTINGS_SCREENS, T_SITE,
RECORD_ART_SHEET). After the fixes the seven deciders were rerun at `b7b77c929e`: 7 of 7 PASS (`lane2/reruns_after_fix.jsonl`),
and lane 1 again: 45 PASS, 0 FAIL (`lane2/lane1_rows_after_fix.jsonl`).

Also read: the game-side callers of every kernel lane 1 tested (ProbeCell, FertilityPostfix, Patch_FireTick_BlackRainDouses,
PyrelandsNoOrdinaryRain.Postfix_ChooseNextWeather, the gate), checked against vanilla through RimSage (FertilityGrid's
CalculateFertilityAt, WeatherDecider.ChooseNextWeather returning the forced weather first, the full list of rainRate-1
weathers: Core Rain, RainyThunderstorm, FoggyRain, SnowHard, SnowGentle; Odyssey ToxRain, Blizzard, TorrentialRain; Anomaly
BloodRain). The shipped ordinary-rain list is complete [measured].

## Planted
41 faults (`lane2/planted_faults.json`): 14 in the six kernels (at least two per offline bar's kernel file:
RM_FireEcoKernel x8, RM_BurnKernel x2, FurnaceWarmthMath, RM_FurnaceKernel, RM_FireHawkRewardsKernel x2), 13 in game-side
callers (PyrelandsAshField x3, FireEcologyHook x2, PyrelandsNoOrdinaryRain x2, PyrelandsMechanicsGate x2, RM_PyrelandsGiants
x2, PyrelandsAshSand x2), 4 in the settings file, 10 in Defs/About (two or more per changed source file; the comment-only
changes in GenStep_PyrelandsFireCast.cs and MapComponent_BurnLine.cs were not planted). Run with private
`WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/pyrelands_blind_c2_mut/`; restore on signal; tree clean after
(`lane2/planted_results.jsonl`, baseline first, `tree_clean_after: true` last).

[measured] **32 of 41 caught**: 27 by a builder decider, 26 by blind lane 1; 5 caught by lane 1 alone (K_RAIN_LIST_DROPS_FOGGYRAIN,
C_GATE_ROSTER_KEY_TYPO, C_GATE_MASTER_BYPASSED, S_DOUSING_SLIDER_EXCLUDES_DEFAULT, D_BIOME_TEXT_NEGATED_KEEPS_PHRASE), 6 by the
builder's alone (K_FURNACE_WARMTH_NO_FALLOFF: my warmth row never sampled mid-radius; C_PROBE_CELL x2; S_DOUSING_OUT_OF_MASTER;
the two black-rain rainRate faults). D_BIOME_TEXT_NEGATED was red in T_DEFS_OFFLINE only through a mutant-anchor assertion, not
its fact. **9 missed by every offline test**, all game-side callers: three ungated postfixes (now caught after the fix), black
rain's douse never damaging, the rain swap never swapping, the giant's classic restore (size, hunger), the charred-floor probe
(x2). Per the steward's question-8 decision these are owed to Stage 6 (sc_three_skies/P_blackrain, sc_no_rain,
sc_furnace_giant, sc_ruins), not offline Problems.

## Faults
`lane2/faults.json`, each filed as a rimflow item:

| id | class | bar | status | miss_of |
|---|---|---|---|---|
| RIMMANDRAKE_HARDEN_PYRE_GATE_SWEEP_BLIND_TO_OWN_WIRING | Problem (against the test) | inv_settings_gate | FIXED b7b77c929e | 1 |
| RIMMANDRAKE_HARDEN_PYRE_SWEEP_SLIDER_MAY_HIDE_ITS_DEFAULT | Problem (against the test) | inv_settings_gate | FIXED b7b77c929e | 1 |
| RIMMANDRAKE_HARDEN_PYRE_ENGINEERED_FACT_PASSES_A_NEGATION | Problem (against the test) | biome_text_says_engineered (and inv_art_and_text) | FIXED b7b77c929e | 1 |
| RIMMANDRAKE_PIN_PYRE_ORDINARY_RAIN_LIST_RIGHT_BUT_UNTESTED | Polish | no_ordinary_rain (stage 6) | PENDING | 0 |
| RIMMANDRAKE_POLISH_PYRE_PROBE_EXPECTED_SKIPS_POLLUTION_CLAMP | Polish | ash_fertility_probe | PENDING | 1 |

No mod-code Problem was found: every kernel and caller lane 1 and lane 2 read does what its bar says today; the three
Problems are deciders weaker than their criteria (a planted fault inside the bar's own promise stayed green).

## Fixes
One commit, tests only, red first (`lane2/fixes.jsonl`; catching run `lane2/catch_check.py <FAULT> <test>`, rc 0 = caught):
red on the parent `85c4d61bee` (7 runs, rc 1, each fault MISSED), green on the fix `b7b77c929e` (7 runs, rc 0, each CAUGHT,
the new fact named in the output: entry_gated, sliders, gate_wired, biome_text_says_engineered).
- `selftest_pyrelands_settings_sweep.py`: facts gate_wired, entry_gated (five pinned postfixes), sliders; six mutants; 16 of 16 red.
- `selftest_pyrelands_defs_offline.py`: the engineered fact requires "genetically engineered", not negated in its clause; two mutants; 18 of 18 red.
Both files read DIRTY by code_review_status (never marked clean, before and after); no full-file review was spent on them.
`run_selftests.py --only` on both: GREEN 2/2.

## Steward's decisions enacted
Read after lane 1 was committed. Recorded with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM` (OWNER.jsonl):
- Question 4 (2026-11-15 11:50 AM PST): sc_no_rain stays the decider of no_ordinary_rain, owing the forced-weather case.
  Acted on: the untested ordinary-rain list is filed as Polish against that stage-6 bar, not an offline Problem.
- Question 8 (same time): live halves stay in 0.1.0; offline halves alone do not suffice. Acted on: the 9 caller faults no
  offline test catches are recorded as owed to Stage 6.
- Question 2 (the exam retaken on the current tree): read; nothing in this stage depends on it.

## Tests edited
`tests_edited.json`: `selftest_pyrelands_settings_sweep.py` (c9aa7c100b929300 -> 0149eda076c9f0cf) and
`selftest_pyrelands_defs_offline.py` (69e960435dc7fa00 -> cd4d788b7beef591); both stricter only, no assertion removed or loosened.
Shown to the next judge.

## Unsettled
Lane 1: 12 `not_kernel` rows, all stage-6 bars (ash ground, grass, scorch-fruit, populations, ruins, ashwallow, three
skies' look, firefoam, rite hook, walk, the hawk's live drop, the furnace-beast's live warmth); none names an offline bar.
Lane 2: the 9 game-side caller faults no offline test catches (above), owed to Stage 6. My own lane-1 warmth row misses a
no-falloff fault (the builder's T_FURNACE_WARMTH catches it); my hawk-drop row exercised only 5 drops in 600 grids.

## Exit
offline_bars: {ash_fertility_probe: green, biome_text_says_engineered: green, inv_firebreak_firefoam: green, inv_lightning_breaker: green, inv_settings_gate: green, inv_art_and_text: green}
problems_open: 0
exit_met: false

## Owed
- Why exit_met is false: every offline bar is green on the rerun and after the fixes and no Problem is open, but three
  Problems were FIXED in this cycle, so by the rule a new blind judge is owed (cycle 3).
- A new blind judge (cycle 3) on the changed files: the two edited tests above.
- Stage 6: the 9 caller faults above; sc_no_rain's forced-weather case beyond Rain (Polish item); sc_foreign_arrivals (journal).
- Polish items RIMMANDRAKE_PIN_PYRE_ORDINARY_RAIN_LIST_RIGHT_BUT_UNTESTED and RIMMANDRAKE_POLISH_PYRE_PROBE_EXPECTED_SKIPS_POLLUTION_CLAMP.
- Cost of this run: about $10.5 of the $20 bound [measured, the session budget line at the record commit].
