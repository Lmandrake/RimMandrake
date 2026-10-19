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
