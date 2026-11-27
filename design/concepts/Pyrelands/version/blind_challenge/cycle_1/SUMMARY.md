# Pyrelands 0.2.0 — blind challenge, cycle 1

Unit: RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_ONE_TESTS_FIRST (seat BENCH, detached).

## Start time
2026-11-27T17:44:56Z (UTC), before any mod file was opened.

Blindness note: the launcher's brief told me to read the brief whole, and the brief carries the
"Steward's decisions" section in its own text, so I read that section before lane 1. It holds dated
Conductor hold/release/re-pin lines on 0.1.0 (no findings, no test results). Nothing else on the
sealed list was opened before lane 1 was committed.

## Lane 1
STOPPED at an easy spot by the pipe stop order ct_000271 (2026-11-27 09:48 AM PST), before any lane-1 test was written or run.
No lane1_rows.jsonl exists yet. Lane 2 has not started; nothing on the sealed list except the brief's own Steward's
decisions section was opened.

Read so far (lane-1 inputs only): tree.json, sheet.md, plan.md, version/VERSION.json, version/bars.md,
version/locked_bars.json (ids), record.json inventory rows of the six offline bars that tree.json lacks, scenes.json
coverage_rest rows of those bars (bar-id grep), design/validation_walks/RimMandrake/Pyrelands.md north star;
RM_PyrelandsMod.cs, PyrelandsMechanicsGate.cs, PyrelandsTuning.cs (constants), PyrelandsAshField.cs,
RM_FireEcoKernel.cs, RM_FurnaceKernel.cs, FurnaceWarmthMath.cs, RM_RoofWitherKernel.cs, RM_FoamPathKernel.cs,
RM_FireHawkRewardsKernel.cs, RM_BurnKernel.cs (pace, WindProbes, CarryPlan), RM_FireHawkKernel.cs (signatures).
Every kernel file is Verse-free (System only), so each compiles standalone with dotnet.exe as the pilot did.

Plan for the carrying run (lane-1 rows to write):
- ash_fertility_probe (C#, RM_FireEcoKernel): AshFertility fixed cases (dry 0.70, watered 1.40, dry fresh 1.20, wet
  fresh 1.90 = "wet plus burn 190%"); BurnBonus fades linearly to 0 at freshBurnDays and has no rain input; ProbeLine
  parts differ between a wet fresh cell and a dry old cell, consistent=True when the grid agrees, refused= when the
  gate or ashWaterFertilityEnabled is off; sweep of every ash slider range (dry 0..1, watered 0.4..2, bonus 0..1.5,
  days 1..20, rain hours 0..72) with cap 2.
- Lane-1 observations to turn into rows: (a) at the slider top (ashWateredFertility 2.0 = FertilityCap 2) a wet fresh
  scar no longer out-grows wet old ash: the cap eats the bonus (INFO, a setting's edge, not shipped behaviour);
  (b) ProbeLine's refusal text still says "or the Baroque Biomes roster toggle", which PyrelandsMechanicsGate no longer
  reads (text only).
- mechanics_switch_plain_no_biome (Python, RM_PyrelandsMod.cs): no 'Enable outside' / crossBiome setting; every
  mechanic switch default on; labels that name a biome: "Only RM_FE grasses grow wild on Pyrelands" (the wild-plant
  allowlist) and "Pyrelands can generate on new worlds" (worldgen placement, biome data); class each as mechanic or
  biome data against the bar's words.
- inv_settings_gate (Python): each field's initializer = Scribe default = shipped snapshot, each scribed once (key
  scorchFruitChancePerCell is a documented rename), every slider range holds its default, every Masters.Declare name is
  a real field, every field is either Declared or Independent, biomeGenerationEnabled ships off and labelled unsupported.
- inv_firebreak_firefoam, inv_lightning_breaker (Python): no Firebreak terrain def, no FirebreakDefName, no breaker or
  fulgurite def anywhere in the mod; the firefoam sprayer def stays.
- biome_text_says_engineered (Python): RM_Pyrelands description says genetically engineered.
- inv_art_and_text, crestfeather_has_its_own_look (Python): every texPath in Defs resolves to a file under Textures
  (or is a named vanilla path); the crestfeather's texPath is its own folder with a real PNG, no ThrumboHorn, no tint.
- Stage-6 kernels (C#): FoamPath (target is always in the way, burning and hittable), Furnace (charge step sign, clamp,
  warmth falls to 0 at the radius, sign threshold), RoofWither (deaths spread over 0.6..1.4 x witherTicks, damage
  conserved: total dealt = maxHp at death, never above), FireHawkRewards (one letter a game, chance), BurnKernel
  (CarryTicks(100) = 0.1.0's 1200, faster at the default 200, clamped; WindProbes never sideways or back; CarryPlan
  merge lights nothing). Every other stage-6 bar: one not_kernel row.

## Lane 2 reruns
(not started)

## Planted
(not started)

## Faults
(not started)

## Fixes
(not started)

## Steward's decisions enacted
(not started)

## Tests edited
(not started)

## Unsettled
(not started)

## Exit
offline_bars: {ash_fertility_probe: red, biome_text_says_engineered: red, inv_firebreak_firefoam: red, inv_lightning_breaker: red, inv_settings_gate: red, inv_art_and_text: red, mechanics_switch_plain_no_biome: red, crestfeather_has_its_own_look: red}
problems_open: 0
exit_met: false

## Owed
The whole cycle: lane 1 (rows above), then lane 2. Item RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_ONE_TESTS_FIRST stays open (LEFT OPEN note).
