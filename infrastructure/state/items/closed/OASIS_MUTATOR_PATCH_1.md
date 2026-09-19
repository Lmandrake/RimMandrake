# OASIS_MUTATOR_PATCH_1 — the vanilla Oasis mutator, adapted

Spec: `design/Jawa/worldbuilding/biomes/weeping_stones.md` §0 (donor inventory) and
the architecture ruling. Three patches:

1. Add `ZBiome_DesertOasis` to `TileMutatorDef Oasis`'s `biomeWhitelist`.
2. Strip `SnowGentle`/`SnowHard` from the biome's `baseWeatherCommonalities`
   (donor absurdity at 35 °C; §6 ban).
3. Re-point `foragedFood` off `RawAgave` — target decided by the flora roster;
   `additionalWildPlants` (vanilla palms/grass/reeds) swaps to blade-flora AFTER
   `WEEPING_STONES_ROSTER_1`.

⚠️ A patch that matches nothing logs nothing — validate with validate_patch.py
(--live AND --defs) and prove the whitelist change against the live game, not the
repo copy.
