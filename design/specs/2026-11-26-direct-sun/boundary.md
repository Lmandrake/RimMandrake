# BOUNDARY: Direct Sun, one geometry model on every map, Design Version 0.1.0

Code: `src/RimMandrake/CreatureBehaviors/Source/RM_SunHeatMath.cs` (`RM_DirectSun`, `RM_SunHeatMath`),
`RM_SunHeatExtension.cs`, `RM_MapComponent_ShadeGrid.cs` (`HeatExtension`, `SunHeatActive`, `EffectiveHeatOffsetC`,
`ResolveSun`, `RebuildHeatLayers`, `BuildGlareLayer`), `RM_SunHeatPatches.cs` (`SunOffsetFor`), `RM_ShadeGear.cs`,
`RM_AirHeat.cs`, the Direct Sun rows of `RM_CreatureBehaviorsMod.cs`, `Patches/RM_DirectSun_LegacyFields.xml`,
`Patches/RM_DirectSun_WeatherSun.xml`; the air-heat rows of the Forge, Terminal Biomes and Greentide settings with
`src/RimMandrake/_Shared/AirHeat/AirHeatSetting.cs`; and every BiomeDef's sun fields.
Items: `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`, `DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL`,
`DIRECT_SUN_SETTINGS_WIRE_FEWER_KNOBS`, written 2026-11-26. Design: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`.
The owner, by card 2026-10-19: *"a pure function of geometry, NOT biome. So: no biome-specific heat, no biome-specific
sun."* Each promise below has a test of its name in `src/RimMandrake/Utils/selftest_direct_sun.py`. This page covers
only these parts of the files named.

## ACCEPTS (the only inputs this is built for)

- **a-fixed-sun-world.** A world whose `PlanetGeometryDef` sets `fixedSun` (Ash'karr's, `RUT_WS_AshkarrGeometry`), or a
  map that pins its sky (`RM_PinnedSunExtension`). The sun elevation E is the tile's arc to the substellar point.
- **a-biomedef-with-or-without-the-extension.** A BiomeDef may carry `RM_SunHeatExtension` for its glare-blind, mirage
  and shade-hop data; without one it reads `RM_SunHeatExtension.Planet`.
- **a-hot-air-biome.** A BiomeDef with `RM_AirHeatExtension` naming a `GameCondition_TemperatureOffset` def.

## DOES NOT SURVIVE (not promised)

- **a-day-night-world.** On a world with a day/night cycle Direct Sun is off (owner, 2026-10-19: "drop sun heat ... when
  the day/night isn't constant anymore"). Following the clock is not built.
- **a-held-mods-own-xml.** The mods the owner holds (Stillsand, Fever Wood, Contagion) still name the removed fields in
  their own files; the load-time strip patch removes them, and their own next build deletes them
  (`RIMMANDRAKE_STRIP_HELD_BIOMES_LEGACY_SUN_FIELDS_AT_LIFT`). The Fever Wood's air heat waits for the same lift.
- **a-pinned-sky-clamp.** A pinned sky clamps its own E for the rendered shadow (the Long Shade 2 to 30 degrees); Direct
  Sun uses the planet's E under one clamp [0, 90], so on a tile above the pinned clamp the drawn shadow and the cast
  shade can differ in length.
- **a-slider-far-from-the-natives-fit.** The natives of a hot-air biome are fitted to the offset in force; a foreign
  plant, or a slider moved far above the shipped value, can stop growing there. The label says plants feel it.

## PROMISES (each one is owed a test of the same name)

- **every-biome-carries-no-sun-field.** No BiomeDef or patch under `src/` gives `RM_SunHeatExtension` a field Direct Sun
  reads (heat kind, offset, scaling, floor, threshold, elevation clamps, body size, path cost, glare floor), parsed as
  XML elements; a held mod's BiomeDef may only if the strip patch removes each such field. So every biome gets the same
  offset and shade at the same E.
- **no-code-names-a-heat-kind.** No C# under `src/` names `RM_HeatKind`, `KindFromElevation`, `GearKindFactor`,
  `EffectiveHeatKind`, `GearKind`, `kindFromElevationEnabled` or the removed threshold fields.
- **the-extension-holds-no-sun-number.** `RM_SunHeatExtension` declares none of the removed fields.
- **removed-fields-are-stripped-at-load.** Each removed field of the extension and of the shade-gear comp that some def
  under `src/` still names has a `PatchOperationRemove` with `success Always` in `RM_DirectSun_LegacyFields.xml`.
- **shade-gear-is-parasol-and-tent.** `RM_SunShield` is not shade gear, and no shade-gear comp outside a held mod
  carries a per-kind factor.
- **hot-air-is-a-vanilla-condition.** The Forge, the Scald and the Greentide carry `RM_AirHeatExtension` naming a
  `GameCondition_TemperatureOffset` of their own mod with a non-zero offset, and no sun number.
- **weather-dims-direct-sun.** The vanilla overcast, rain, fog, snow and storm weathers carry a sun factor below 1.
- **settings-rows-match-the-ruling.** Creature Behaviors has no cover-follows-the-sun toggle, a zenith setting that
  defaults to 55 and a weather switch that defaults on, each saved with that default, and a master labelled "Direct
  Sun"; each hot-air biome mod that is not held has an on/off and a degrees row that writes its condition's offset at
  startup and when the settings window closes.

## PROMISES KEPT BY THE C# SELFTEST

These are named cases of `src/RimMandrake/CreatureBehaviors/Source/SelfTest/Program.cs`, run by
`python3 src/RimMandrake/Utils/selftest_sun_heat.py`; each was seen red on its own planted fault
(`python3 src/RimMandrake/Utils/mutate_creaturebehaviors_fuzz.py "sun:"`, 12 of 12 caught on 2026-11-26).

- "direct sun: the model takes no biome input (same E, same offset and shade in every biome)"
- "direct sun: intensity is 55 x sin E at defaults, 0 at or below the horizon"
- "direct sun: a shadow is h / tan E long; none beside a wall at E 85, about 4 h at E 14"
- "direct sun: a roof, a tent and a parasol cover at every E"
- "direct sun: weather and the strength dial scale Direct Sun only"
- "direct sun: sand glare floors exposure in shade; paved shade is fully cool"
- "air heat: a native plant's upper growth bounds rise by the offset, never below its loaded band"
