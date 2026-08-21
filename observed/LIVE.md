
## Def dump, 2026-08-21 — two read-traps measured on the 578-mod dump

- 🔴 **`BiomeDef.wildAnimals` lists ALL 1024 animals on ALL 80 biomes**, with the absent ones
  at `commonality: 0`. A substring search for a defName returns **80 of 80** and means
  nothing. The membership test is `commonality > 0`. Measured against `IceSheet`, `Ocean`
  and `Space` (all zero) versus `Wasteland` 1.2, `ExtremeDesert` 0.5, `ZBiome_DesertOasis` 0.8.
- 🔴 **`PawnKindDef.xenotypeChances` is absent from the dump entirely** — zero of 1736
  PawnKindDefs carry the key. A check on it off the dump is UNMEASURED, never failed.
  `useFactionXenotypes` IS present on all 1736 and is safe to read.
- ⚠️ **`BiomeDef` carries no `texture` field in the dump either**, so a world-texture check
  cannot be done offline from it. Read the mod XML or look at the planet.
