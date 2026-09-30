# CAULDRON_MECHANICS_BUILD_1 — tranche 1 report

## Status
Parts 2 and 5 (the parts with a real seam) are built. Built offline only: not deployed and not live-tested.
Commits: `ce76ffae6` (weathers + hediff), `ccdfb81ef` (C# + settings + DLL).
dotnet build: 0 errors, 0 warnings. XML parses. Selftests: 76/78. The only failure is the known `selftest_deployed_biome_refs`.

## Part 2 — weather (BUILT)
- `src/RimMandrake/PoisonForest/Defs/WeatherDefs/RM_CauldronWeathers.xml` has four weathers: RM_ScatterDusk, RM_VentBloom, RM_VapourBank and RM_Dewfall.
  - None of them rains, snows or carries sand.
  - Shadows are near-white, so there are no sun cues (sheet §6).
  - Every weather carries wind (factor ≥0.5).
  - The bloom uses the grey GrayPallFog overlay, not green NoxiousHaze, because green is banned (§6).
- The BiomeDef block drops Fog 90. The new weights are ScatterDusk 60 / VapourBank 20 / Dewfall 12 / VentBloom 8 (INVENTED), and DryThunderstorm 1 is kept.
- The metal-load hediff is `RM_VentMetalLoad`. It is applied by `RM_MapComponent_VentBloomExposure`:
  - It runs on vanilla's 3451-tick cadence and uses the same ToxicResistance × ToxicEnvironmentResistance math.
  - It only hits pawns outdoors and under open sky. Native fauna are exempt.
  - The bloom has `doToxicBuildup=false`, so pawns are not also charged vanilla toxic buildup.
  - It is not lethal and decays at -0.08/day.
- Settings: an on/off toggle and a build-up rate slider.
- Note: "ban 5 = wind" comes from the Leaning Scrub sheet. The Cauldron sheet's ban 5 is "no potable water". Wind was added anyway, and it does not conflict with anything.
- There is no "Blue Desert Haze" implementation in `src/` (the Haze is unbuilt). The shape used instead is vanilla's toxic-weather tick.

## Part 5 — Vexxiss behaviours (PARTLY BUILT)
- `RM_CompVexxissBehaviour` (`src/RimMandrake/PoisonForest/Source/RM_CompVexxissBehaviour.cs`):
  - **Fire warden:** the vexxiss looks for the nearest reachable ground fire. If that fire's `Fire.instigator` is a pawn it can reach and is not of its own faction, it attacks them with vanilla AttackMelee (it won't kill a downed pawn, and the job expires). Otherwise it beats the fire out with vanilla BeatFire. The race needed `giveNonToolUserBeatFireVerb=true` for this, which is set.
  - **Poisons water on touch:** water cells the vexxiss wades through, and the cells touching them, turn into vanilla toxic water. This is the same `SetTerrain` swap Odyssey's toxic-lake mutator uses. The six swap pairs live in the def XML.
  - Settings: three toggles (fire warden, attack the igniter, poison water).
- NOT built: inhaling a vent to pause its production, and prying at gas-tap scaffolds. There are no vent or scaffold defs to hook into until part 3 exists.

## Part 6 — Oomo's Grimace shrine (NOT BUILT)
This is not pure content in this mod, for two reasons:
- Oomo is a campaign god (Ninefold, Jawa lore). The RM_PoisonForest mod "names no other campaign", so a shrine there would break the tier line and belongs in the Utinni layer.
- The spec puts the shrine "in the ruins", which are part 4's unbuilt corroded ruin kit. The "water rites" to tint don't exist anywhere either: Ninefold has no rite or shrine defs.

## Remaining
- **Part 1, soundscape:** needs audio assets. The falter tell (hushing the fauna *ahead of* a bloom) needs to know the next weather in advance, and vanilla's WeatherDecider does not expose that without Harmony or a scheduler. That is a design decision.
- **Part 3, gas/vents:** the Biotech gas grid only has fixed GasTypes (no custom flammable gas without Harmony). Needs design: vent ThingDef + GenStep, how gas ignites with toxic smoke, and the gas-tap scaffold.
- **Part 4, Filter-Works:** depends on the FlowWorks LiquidDef registry and the ruin kit.
- **Part 5 remainder:** vent inhaling and scaffold prying, after part 3.
- **Part 6:** the shrine kit, after the ruins (part 4) exist, and in the Utinni layer.
- Live checks owed: the criterion "weathers live in a quicktest read of weatherCommonalities", and a state read of the fire warden.
