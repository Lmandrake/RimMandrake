# DARK_FLORA_FIX_WILTS_WITHOUT_A_SUN

Filed 2026-10-20 (FOUNDRY, offline glow-consumer audit). Spec: `design/RimMandrake/glow_consumers_2026-10-20.md` §A.

Under the tidal lock, night-side and deep-dusk tiles have sky glow 0 forever. Vanilla's light factor is
`InverseLerp(growMinGlow, growOptimalGlow, glow)`. With `growMinGlow 0` and the default `growOptimalGlow 1.0` it is 0 at
glow 0, so the plant never grows and (default `dieIfNoSunlight` true) dies after 7.5 days. `WildPlantSpawner` then
re-seeds it, which leaves a churn of stunted plants. Vanilla cave plants (`Glowstool`) set BOTH fields to 0.

Measured offline (static parse of `src/`, factor at glow 0): `RM_TheSump` 10/10 die (each sets min 0 but leaves optimal
1.0), `RM_TheRot` 19/39 (the donor ports under `RM_TheRotPortedCavePlantBase`), `RM_Cauldron` 16/16, `RM_Abyss` 8/10,
`RM_GelatinousSlime` 4/4, and `RM_Wasteland` 9/9 on its night-side tail. The `RUT_` twins' patch-added casts were not
parsed separately.

## spec
- For each plant that its biome sheet makes sunless (chemotroph, nightside-lush, glower), set `growMinGlow 0` AND
  `growOptimalGlow 0`. Never add `diesToLight`. Keep the Cauldron's named photosynthetic underclass light-needing.
- Add a selftest that refuses any plant ThingDef with `growMinGlow 0` and `growOptimalGlow > 0`, unless an allow-list
  names it as deliberately photosynthetic.

## verify
- Rerun `D:\ClaudeWork\rimmandrake\scratch\glowconsumers\nightplants2.py` on the listed biomes. Every sheet-sunless
  plant should read GROWS. `validate_patch.py` should be clean on every touched file.

NEXT: read the Sump, Rot, Cauldron, Abyss and Slime sheets, list which plants are sunless, then set both glow fields on those defs.
