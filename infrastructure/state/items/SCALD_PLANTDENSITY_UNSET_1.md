# SCALD_PLANTDENSITY_UNSET_1 — RM_TheScald leaves plantDensity unset, so its one wildPlants row can never spawn

## the question, MEASURED live 2026-09-26 (Scald load round)

`jawa/biome_probe`, read off the runtime caches (not XML):

| biome | animalDensity | plantDensity | wildPlants |
|---|---|---|---|
| `RM_TheScald` | 0.15 | **0.0** | 1 (`RM_Crowncarpet` 0.4) |
| `RM_GreySea` | 0.1 | 0.14 | 7 |
| `RM_TwilightSea` | 0.1 | unset -> 0.0 | 0 (moot) |
| `RM_PropaneLake` | unset -> 0.0 | unset -> 0.0 | 0 |

`RM_TheScald.xml` carries no `<plantDensity>`, so it defaults to `0f`.
`WildPlantSpawner`'s desired-plant count scales by it, so the biome's single
`wildPlants` row can never fire, and post-harvest regrowth is gated on the same zero.
Same shape as `PROPANELAKE_ANIMALDENSITY_ZERO_1`, on the plant axis.

⚠️ **Not certainly a defect.** `LuminousPigment/Defs/GenStepDefs/RM_GenStep_ShoreMats.xml`
(order 760, `GenStep_ShoreMats`) places crowncarpet by scatter on ocean-shore cells,
which that mod's own `About.xml` calls its franchise-free route. So the biome row may be
deliberate anchoring rather than a spawn route — in which case it is dead but harmless,
and the real question is whether it should be there at all.

## for the owner
Is the Scald meant to grow nothing through the ordinary wild-plant spawner — a boiling
impassable sea, which is plausible — with crowncarpet arriving only via the shore
GenStep? If yes, the `wildPlants` row should probably go, or carry a comment saying why
it stays. If no, `plantDensity` needs a value.

⛔ Not edited unilaterally: a roster row is exactly what `BIOME_SPECIFIC_FAUNA_LAW_1`
and `BIOME_PAINT_ONCE_AT_THE_END_1` say not to "fix" by sweep.
