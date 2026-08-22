## spec
🔴 **`HorrorWastes` is installed, loaded, and has ZERO tiles on Ash'karr.** The owner named
it as one of four bioweapon biomes and then placed it, 2026-08-22:

> *"HorrorWastes should be on the night-side where the ancient bioweapons have adapted to the
> extreme cold and produced utterly hostile lifeforms."*

Label *"horror wastes"*, from **Horrors (Continued)**. Lore and the threat-class table:
`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` **§6c**.

## ⭐ it fixes a second defect for free
`AB_RockyCrags` is **4,703 tiles spanning −82 °C to +19.8 °C** — the biggest biome on the
planet and not a habitat at all, but a band running from deep nightside to near-terminator.
Casting it as one creature list puts a lizard and a snow-thing on the same ground.
⇒ **Carving `HorrorWastes` off its coldest end gives BOTH biomes a coherent thermal range.**

## measured — where the ground actually is
| band | tiles | median temp | dominant biome |
|---|---|---|---|
| arc ≥ 120 | 5,481 | −48 °C | `AB_RockyCrags` 3,387 |
| arc ≥ 130 | 3,916 | −56 °C | `AB_RockyCrags` 2,828 |
| coldest 800 (arc 150–179) | 800 | −82…−67 °C | `AB_RockyCrags` 687, `AB_PropaneLakes` 99 |

**DECIDE's proposal, for the owner to size:** take the deep nightside from `AB_RockyCrags`
only — roughly **arc ≥ 140**, on the order of **1,000–1,500 tiles** — leaving
`AB_PropaneLakes` (554) and `BMT_CrystalCaverns` (127) intact as their own places.
⚠️ **Do not convert `AB_PropaneLakes` or `BMT_CrystalCaverns`.** They are distinct and the
owner has not asked for them to go.

## the engine constraint
⚠️ A biome change is a `biome` column edit in `world/ASHKARR_WORLDMAP_tiles.csv`. It does
**not** move elevation, so nothing becomes water or land by doing it (`SurfaceTile.WaterCovered
=> elevation <= 0f`).
🔴 **`HorrorWastes` has never generated on this planet — confirm it has `wildAnimals`,
terrain and `animalDensity` that work before committing tiles to it.** A biome with an empty
cast is worse than the RockyCrags it replaced.

## verify
Render and LOOK (`worldview.py`) — the owner's method. Then: `HorrorWastes` tile count is
what he sized; `AB_RockyCrags`' temperature span is materially narrower than −82…+19.8;
`AB_PropaneLakes` and `BMT_CrystalCaverns` unchanged; no tile changed elevation.

## criteria
`HorrorWastes` on the nightside at an owner-approved size, `AB_RockyCrags` thermally coherent,
approved by looking.

## watch out
⚠️ **Biome counts are canon-adjacent.** `canon.yml` carries planet figures; re-measure after.
⚠️ This changes `BIOME_CREATURE_CAST_1`'s biome list from 23 to 24 and re-opens the
`AB_RockyCrags` cast, which is the one already worked. Do this BEFORE casting it.
