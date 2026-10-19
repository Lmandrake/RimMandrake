# CONTAGION_HEAT_JUDGE_SUN_KIND_UNSAID — does the Contagion owe a heat kind?

Found by the four-biome readiness audit, `design/RimMandrake/four_biomes_readiness_2026-10-19.md`.

`SOLAR_HEAT_EXPOSURE_1` rules that every extreme-heat biome declares a heat KIND (`overhead`,
`lowSun`, `ambient`) through `RimMandrake.CreatureBehaviors.RM_SunHeatExtension` on its BiomeDef,
chosen by reading the BiomeDef and the sheet, never from the name.

`RM_Contagion` (`src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml`) declares none. Its
sheet, `design/Jawa/worldbuilding/biomes/the_contagion.md`, puts it on the dayside: p10/median/p90
25 / 32 / 45 °C (max 57), and the sun *"comes through like a sterilizing lamp"*. Its BiomeWorker
range is 20 to 57 °C (`RM_ContagionBiome.cs`). The Pyrelands (median lower) declares `overhead`.

## spec
1. Decide from the sheet whether the Contagion is an extreme-heat biome. If yes, the open dayside
   sun suggests `overhead`; if no, write why in the close note.
2. If yes, add the extension (copy the Pyrelands block, tune `heatOffsetC`), with the
   `MayRequire="mandrake.rm.biomes"` guard the others use.
3. Do not add a new heat hediff. The sun's UV sterilising mechanic is a separate, already-built thing.

## criteria
- The BiomeDef carries a heat kind, or the close note says why it is not extreme heat.
- `selftest_contagion*.py` still pass.

## judgment (FOUNDRY, 2026-10-19, offline) — FOR OWNER REVIEW IN THE MORNING

Read: sheet `the_contagion.md` (dayside p10/median/p90 25/32/45 C, max 57; the Burn is "a white shaft of sterilizing
sun", natives dive for overhangs), `RM_Contagion.xml`, `RM_ContagionWeathers.xml`, and the extension/patch source
(`RM_SunHeatExtension.cs`, `RM_SunHeatPatches.cs`, `RM_WeatherSenseExtension.cs`).
- Extreme heat: yes (p90 45, max 57). Kind: **overhead**. Not `ambient` (no steam or vents; shade does matter, the natives hide
  under overhangs), not `lowSun` (the dayside sun is not grazing; Pyrelands also uses overhead).
- Catch found by reading the patch: sun exposure is multiplied only by `RM_WeatherSenseExtension.SunFactor`, so under the
  standing Bloom (70 of ~80 weather weight) a bare extension would roast full-strength under a thunderstorm. The Bloom now
  carries `sunExposureFactor 0.2`, so the heat bites in the Burn (and the rarer clear spells). The Burn def has none (factor 1).
- Values `heatOffsetC 10`, `0.2` are invented first values. No new hediff. Owner to rule: is 0.2 under the Bloom right, and
  should the Bloom be 0 (Burn-only heat)? Judged best-supported, not owner-confirmed.

## superseded 2026-10-19

Superseded by `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`: the owner ruled (card, 2026-10-19) there are no per-biome heat kinds, so the Contagion owes none. Its Bloom `sunExposureFactor 0.2` stays as a weather factor.
