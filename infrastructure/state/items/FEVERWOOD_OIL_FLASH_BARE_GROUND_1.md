# FEVERWOOD_OIL_FLASH_BARE_GROUND_1

## spec
**Defect (MEASURED run17, 2026-10-03):** `oil_boil.a_spark_in_the_haze_flashes_and_burns_it_off` read
`flashed=True firesBefore=0 firesAfter=0 conditionEnded=True`. `RM_GameCondition_OilBoil.Flash`
(`src/RimMandrake/FeverWood/Source/RM_OilBoil.cs`) lights cells with `FireUtility.TryStartFireIn(c, map, size, null)`,
which refuses any cell whose `ChanceToStartFireIn` is 0 (no flammable terrain or thing — bare soil, stone, a
cleared pad). So a flash over bare ground starts no fire while its letter says "fire ran along the haze (0 cells)".
The haze itself is the fuel by design.

**Fix (C#, after the current deploy window):** pass a `flammabilityChanceCurve` whose value at 0 is > 0
(e.g. `(0,0.5),(1,1)`) so a hazed cell ignites regardless of ground fuel (vanilla evaluates the curve before the
`num > 0` gate; impassable-edifice interiors and no-fire filth still refuse). Optionally word the letter by `lit`.
The script assertion `firesAfter > firesBefore` stays as is: it is the bar.

## criteria
`oil_boil.a_spark_in_the_haze_flashes_and_burns_it_off` PASSES live after a deploy carrying the fix.
