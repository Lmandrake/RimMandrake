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

## 🔴 MEASURED 2026-08-22 — `HorrorWastes` AS SHIPPED IS A HOT, DRY BIOME WITH THREE ANIMALS

Read from the live dump before committing any tile to it:

- **Its own description is desert, not ice:** *"A **dry region**, contorted by alien fauna and
  flora to be unrecognizable. A terrible place of disease, Horrors and suffering."*
- **Its terrain is `Sand`, `Soil`, `SoilRich`** — sand will read wrong on a −56 °C nightside.
- **Its entire cast is THREE animals**, and none survives the ground it is being sent to:

  | animal | comfy range | survives −56 °C? |
  |---|---|---|
  | `Bulwark` | 0 … 40 °C | ⛔ no |
  | `Terrorworm` | 0 … 40 °C | ⛔ no |
  | `Visceral` | −40 … 40 °C | ⛔ no |

⇒ 🔑 **The owner's concept is sound and the def does not implement it.** He wants *"ancient
bioweapons that have adapted to the extreme cold"*; the shipped biome is a hot dry horror
region. **Placing it unchanged yields empty ground.**

**What that actually costs, and it is not much:** we are re-casting every biome anyway
(`BIOME_CREATURE_CAST_1`), and this is one of the four biomes licensed to draw on the 14
anomaly entities. ⇒ **Treat `HorrorWastes` as a SHELL we fill, not a biome we inherit.**
Owed alongside the tiles: a cold terrain set, and a cast of cold-viable hostiles.
⚠️ Its `animalDensity` is **3.6**, which is high — a near-empty cast at high density is the
`AB_RockyCrags` failure repeated, so the cast has to land with the tiles, not after.

## ✅ TILES PLACED 2026-08-22 — and the terrain defect is now MEASURED
`ashkarr_nightside_pass.py --apply` moved **1,200** of `AB_RockyCrags`' coldest tiles
(arc ≥ 140) to `HorrorWastes`. `AB_RockyCrags` 4,703 → 3,423 and its thermal span narrows,
which was the second reason for doing it.

🔴 **Its ground colour proves the terrain is wrong for where it now sits.** Sampled from the
real terrain textures (`biome_fit.py`, 25 biomes):

| biome | ground rgb | |
|---|---|---|
| `HorrorWastes` | **[97, 82, 67]** | warm sand — `Sand`, `Soil`, `SoilRich` |
| `Desert` | [130, 111, 88] | ⚠️ **its nearest neighbour in colour** |
| `AB_RockyCrags` — what surrounds it | [29, 27, 30] | near-black rock |
| `SeaIce` — its other neighbour | [155, 164, 172] | pale blue-grey |

⇒ **In game, the ground a pawn stands on will be warm sand between black rock and ice.** The
def is a *dry* horror biome (its own description: *"A dry region"*) and nothing about it was
authored for −56 °C.

⚠️ **CORRECTION, 2026-08-22 — this is an IN-GAME defect only; the world render is fine.**
DECIDE told the owner he would see a warm sand patch on the map. He will not.
`worldview.py` uses its own `BIOME_COLOR` palette, chosen *"for SEPARATION first and mimicry
second"*, and **both new biomes already have entries** — `HorrorWastes` `#7c0f31` dark
crimson, `SeaIce` `#cfe4ee` pale. 🔑 **A biome's map colour and its ground terrain are
different fields and one says nothing about the other.** The ground-colour table above is
evidence about the *map surface a pawn walks on*, and it stands.

**Still owed before this closes:**
1. **A cold terrain set** — it must not sit at [97,82,67] between [29,27,30] and [155,164,172].
2. **A cast.** Its three shipped animals (`Bulwark`, `Terrorworm`, `Visceral`) all die at
   −56 °C, and `animalDensity` is **3.6** — near-empty at high density is exactly the
   `AB_RockyCrags` failure being repeated. Carried by `BIOME_CREATURE_CAST_1`; it is one of
   the four biomes licensed to draw on the 14 anomaly entities.
