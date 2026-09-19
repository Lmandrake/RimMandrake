# NIGHTSIDE_BLUE_DESERT_1 — use the Blue desert biome on Ash'karr's night side

Owner idea, 2026-09-05. Investigated by BENCH overnight the same day.

## What "Blue desert" is (MEASURED off defs.sqlite, fingerprint-gated dump)

`BiomeGRimond` — label **"Blue desert"** — from **GRiNDTerra Biomes**
(`grimterra.biomesmod`), live in the current dump (81 BiomeDefs total). Sibling def
`BiomeGRimphire` "Bluefire Mountains" from the same mod, if a paired highland is wanted.
Key fields: implemented, buildable, animalDensity 0.5, plantDensity 0.33 (hasVirtualPlants),
forage RawGrimPepper, movementDifficulty 1.5, custom `workerClass BiomeWorker_GRimWorld`
(irrelevant to us — we hand-paint tiles; worldgen never runs).

## What the ruling needs to decide

1. **Which nightside band.** Current dark-side ladder (measured, `_openers_prep.md`):
   AB_MycoticJungle med −19 °C → HorrorWastes med −44 °C → AB_PropaneLakes med −64 °C.
   A Blue desert slots most naturally as a CLEAN cold desert band between/alongside the
   bioweapon and volatile belts — or as the nightside-lush candidate the lush rule (part 3)
   reserves ("dense, but built of very alien life forms").
2. **The grammar debt.** Placement needs a regime × anomaly reasoning and a conversation
   loop like every other sheet — do not paint it before its sheet exists.
3. **The war-legacy split** applies: if it borders HorrorWastes, its identity must not blur
   the bioweapon/poison distinction.

## Blocked on

The owner's sitting (BIOME_FAUNA_ASSIGNMENT_SITTING_1 covers the review; this can ride it).
