## spec
🔴 **DECIDE authored the renormalization; the deploy is BUILD's** — owner's ruling 2026-08-23,
*"deciding that they get deployed for the next game load is still BUILD, as he handles the
'game build' that's being loaded."*

**Deploy `src/Jawa/Jawa_Patches/Patches/PlantTolerances_Ashkarr.xml`** (committed `b28bb508`),
and 🔑 **deploy it in the SAME build as `BiomeFlora_Ashkarr.xml` or the flora load proves
nothing.** 642 of 669 plants stop at `minGrowthTemperature` 0.0 °C and half this planet is
colder, so without this patch a perfectly correct roster grows nothing and scores as a bad
roster. The two are one test.

**What it does.** 577 plants refitted onto the climate of the biome they were assigned. The
biome sets the band — p05…p95 of its tiles plus a 15 °C swing allowance — and the plant's
shipped width only buys a capped (40 °C) hardiness bonus on top. The rule and its rejected
first version are documented in `design/Jawa/mods/plant_tolerances.py`.

⚠️ **Four fields move together, not the two the parent item names.** `Plant.cs:361` computes
growth as `InverseLerp(minGrowthTemperature, minOptimalGrowthTemperature, cellTemp)`, so a
patch that moves only the outer pair leaves the plant at ~0 growth — alive, present and still
indistinguishable from a bad roster.

## Watch out
⚠️ **This patch is 1.7 MB / 577 operations wrapping 2,308 inner conditionals**, and every one
is an xpath probe at load time. **That cost is real and the call to accept it is yours.** It is
structured that way on purpose: `PlantProperties` defaults `minGrowthTemperature` to 0 in C#,
so the def dump reports a value for every plant whether or not the XML declares the node —
the `Conditional`/`nomatch Add` pair is required and cannot be collapsed to a bare Replace.
⚠️ **`SWING = 15.0` is a JUDGEMENT, not a measurement.** `ASHKARR_WORLDMAP_tiles.csv` holds one
annual `temp_c` per tile while `PlantUtility.cs:93` gates spawning on the tile's *seasonal*
Min/MaxTemperature, which we do not hold. It is the first number to revise from the load.

## verify
`AB_PropaneLakes` (median −59.8 °C) and `AB_MechanoidIntrusion` (+62.5 °C) — generate a map at
each and count living plants. **Bare ground at a correct roster is the failure this closes.**
Zero red errors naming `PlantTolerances_Ashkarr`.

## criteria
- [ ] Deployed alongside `BiomeFlora_Ashkarr.xml` in one build.
- [ ] Both extreme biomes grow visible plants.
- [ ] No red errors, and `BiomeDef` count still 80.
