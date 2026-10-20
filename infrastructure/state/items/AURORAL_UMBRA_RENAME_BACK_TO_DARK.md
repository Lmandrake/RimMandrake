# AURORAL_UMBRA_RENAME_BACK_TO_DARK — RUT_FuelSnows becomes RUT_Umbra, "Auroral Umbra": dark, perpetual aurora, propane rain

## provenance

- Owner by card, 2026-10-19: "How should this frozen biome be settled? → Back to Umbra, dark". His typed note:
  *"(2) it's totally dark except for the utterly beautiful and wildly active aurora. Let's call it the Auroral Umbra
  then. And look back at the original concept sheet to find out about precipitation. It ruled what's solid, liquid,
  gas at various temperatures."*
- Owner, same day: *"Yes, there should be a perpetual Auroral activity in that biome. Put that in its def now.
  Auroral Umbra is the new name, better than Rimefall. And yes, it should NOT snow, it should rain propane
  (equivalent with chemfuel)."*
- Background: `design/RimMandrake/baroque_biomes_list_2026-10-19.html`, section "Fuel Snows / Umbra".

## the concept sheet's phase ruling (what falls)

`design/Jawa/worldbuilding/worldgen_interactive_def.md:151-155,177-179` (owner, 2026-08-16; echoed in
`worldgen_interactive_build_concepts.md:40-44`): propane liquid −188…−42 °C · ammonia liquid −78…−33 · ethane
liquid −183…−87; the antipodal point carries solid ammonia ice and solid CO₂; every other gas stays gaseous; the
nightside gets no rain and no WATER snow, "but ammonia, propane and ethane may fall there as rain or snow".

On this land (p10/median/p90 −73/−62/−48 °C, coldest −82): propane is liquid everywhere → **propane rain, which
pools**. Ethane is a gas everywhere here (all tiles above −87). Ammonia is liquid on most of the band and solid
only below −78 (the coldest few tiles). Water snow is forbidden. The owner then ruled the result directly: rain
propane, no snow. Ammonia rain and CO₂/ammonia frost on the coldest tiles are NOT built (not asked for).

## what was done (offline; not deployed — game is up on the 380 list)

- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Umbra.xml` is the one def: label "Auroral Umbra", new
  description (no fuel snow, no fuel sea), weathers Clear 60 / `RUT_PropaneRain` 30 / DryThunderstorm 2 / all snow,
  rain and fog 0, small `RM_PropaneShallow` pools (terrainPatchMakers, MayRequire FlowWorks), and
  `PerpetualAuroraExtension`. `RUT_FuelSnows.xml` deleted.
- `src/RimUtinni/UtinniPatches/Defs/WeatherDefs/RUT_PropaneRain.xml`: rain overlay, rainRate 0 (not water: no fire
  dousing, no soaking, no plant watering).
- Weather Suite C#: `PerpetualAuroraExtension`, `MapComponent_PerpetualAurora` (keeps a PERMANENT
  `RM_WS_DarkAurora` on such maps; ends it when switched off), permanent instances use the perpetual glow and run
  the colour sweep N× faster. Mod Settings group "Perpetual aurora": on/off, glow, activity.
- Save safety: `src/RimUtinni/UtinniPatches/Defs/Misc/RUT_UmbraRename_Aliases.xml` (RM_DefAliasDef,
  RUT_FuelSnows → RUT_Umbra by name). Census 2026-10-20 (tileBiomeDeflate; hash 15270 = RUT_Umbra, 3528 =
  RUT_FuelSnows, both checked against capture 2026-10-20T03-35-54Z): `CANONICAL_ASHKARR_START_2026-09-12.rws` and
  `..._AREAFIX2.rws` carry RUT_Umbra on 2,531 surface tiles, RUT_FuelSnows on 0, and neither name as text.
  Nothing breaks in either save; the planned RUT_Umbra→RUT_FuelSnows paint remap is cancelled everywhere.
- Snowmelt: `RUT_ExplosiveGrowthRoster.xml` lists no snowmelt biome now.
- Dead Rimefall patches (target retired `AB_PropaneLakes`) removed from `BiomeNames_Ashkarr.xml` and
  `BiomeDescriptions_Ashkarr.xml`; the duplicate FuelSnows acoustic-scanner payload removed.

## PROVISIONAL numbers (first guesses, tune on sight)

Weather weights 60/30/2; propane rain duration (vanilla default), move 0.95, accuracy 0.9, colours; pool patch
perlin 0.045 / threshold 0.78 (~4% of ground); aurora glow 0.35 (incident: 0.25); activity 8× (a colour every
~470 ticks). The permanent aurora also gives the incident's mood thought permanently (+mood) — judge it live.

## criteria

- A1 L0: `RUT_FuelSnows` is defined nowhere in `src/`; `RUT_Umbra` carries label "Auroral Umbra", no snow weather, `RUT_PropaneRain`, and `PerpetualAuroraExtension`; WeatherSuite builds; validate_patch and the touched selftests pass.
- A2 L2: after deploy and a load, a map on an Auroral Umbra tile shows a permanent dark-side aurora whose colours visibly sweep, lighting the ground; switching "Perpetual aurora" off removes it within an in-game hour.
- A3 L2: on that map the weather cycles between clear and propane rain; it never snows; propane rain does not put out a fire or make pawns soaking wet.
- A4 L2: propane pools (`RM_PropaneShallow`) appear on a freshly generated Auroral Umbra map and burn only from a spark or fire.
- A5 L2: the canonical start save loads with its 2,531 Umbra tiles named "Auroral Umbra" on the world map, and no error mentions RUT_FuelSnows.

## owed

- `RM_` twin / Baroque Biomes home for the Auroral Umbra (none exists).
- Ground is still `RM_PackedSnow`/`RM_PackedIce` (water ice) — fine as rock-hard ice, but "packed snow" reads
  as snowfall; a name/texture look owed with the owner.
- The Chill's creature descriptions still say "grown from the fuel snow" (`RM_TheChillFloorLife.xml`,
  `RM_TheChillCatch.xml`, `RM_ChillWaxProcession.xml`, `RUT_PropaneLakeCatch_Items.xml`,
  `RUT_PropaneCatch_Refining.xml`) — the Chill was left as is by this ruling; text sitting owed.
- New/changed C# is DIRTY for code review (`WeatherSuiteHook.cs`, `WeatherSuiteSettings.cs`).
