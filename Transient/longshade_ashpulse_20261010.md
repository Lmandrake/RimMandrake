# LONGSHADE_BEDAZZLE_MECHANICS_1 remainder: ash-pulse growth + sand-lock (2026-10-10)

## Mechanism measured (RimSage)
MEASURED from decompiled 1.6 (RimSage, 2026-10-10):
- `GameCondition` has NO plant-growth-rate virtual. Its plant-facing virtual is `PlantDensityFactor(Map)`,
  read only by `WildPlantSpawner.CurrentPlantDensityFactor` via `GameConditionManager.AggregatePlantDensityFactor`
  (wild-plant spawn density, not growth speed). Overridden by ToxicFallout and NoxiousHaze.
- `GameCondition_VolcanicWinter` carries no plant term at all: sky target 0.55, temperature -7 lerp, AnimalDensityFactor 0.5.
- Growth speed is `Plant.GrowthRate` (public virtual getter) = Fertility * Temperature * Light * NoxiousHaze * Drought;
  the two condition factors are HARD-CODED `GameConditionDefOf.NoxiousHaze` / `.Drought` checks, not a virtual.
  `Plant.GrowthRateCalcDesc` (virtual) is the inspect breakdown.
- So the ash-pulse growth surge = a Harmony postfix on `Plant.get_GrowthRate` (+ its CalcDesc line) reading a
  DefModExtension on active conditions; the "more wild growth" half uses the real `PlantDensityFactor` virtual.
- Chaining: `GameConditionManagerTick` iterates backwards and calls `End()`; `RegisterCondition` appends + `Init()`
  (startMessage). Registering follow-on conditions after `base.End()` is safe.

## Ash-pulse growth act
Haze ends -> `RM_GameCondition_SmokeHaze.End` -> `RM_SmokeCalendarExtension` starts `RM_AshPulseCondition` (3~5 d):
growth x1.5 via postfix on `Plant.get_GrowthRate` (+ inspect line), wild density x1.3 via `PlantDensityFactor`.
One "Ash settles" letter. Files: `src/RimMandrake/CreatureBehaviors/Source/RM_AshPulse.cs`,
`src/RimMandrake/LongShade/Source/RM_SmokeCalendar.cs`, `src/RimMandrake/LongShade/Defs/IncidentDefs/RM_SmokeHaze.xml`.

## Sand-lock act
`RM_SandLockCondition` (4~7 d, outlasts the pulse): Sand/SoftSand/RM_DeepSand stop counting as swim/bury ground in
`RM_SandSwimUtility.IsSwimTerrain` and the buried-graphic patch -> every RM sand swimmer breaches with its own wake.
Toggles: LongShade ashPulseEnabled / sandLockEnabled; CreatureBehaviors conditionGrowthEffectsEnabled / sandLockEffectsEnabled.
All numbers PROVISIONAL.

## Validation
`ash_act_problems` in LongShade/validation.py (in static_checks); `selftest_longshade_ashact.py` 7/7 incl. 6 planted defects.
Both DLLs built via winbuild.py, 0 warnings. Owed L2: A5 (ash act live) plus prior A1-A3.

## Owner questions
Should the sand-lock also stop the young sarlacc swimmer on the Swimmer's Road (`CompSarlaccSwimmer`, its own movement,
not covered now), i.e. halt it in place until the wind unpacks the sand, or let it keep travelling as the one thing
the ash cannot stop?

## Shas
969077d2e ash act code+defs+validation; c03f7b921 criteria level tags.
