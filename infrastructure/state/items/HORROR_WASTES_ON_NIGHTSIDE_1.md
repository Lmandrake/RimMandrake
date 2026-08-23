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
~~`ashkarr_nightside_pass.py --apply` moved **1,200** of `AB_RockyCrags`' coldest tiles
(arc ≥ 140) to `HorrorWastes`. `AB_RockyCrags` 4,703 → 3,423 and its thermal span narrows,
which was the second reason for doing it.~~

> 🔴 **STRUCK 2026-08-23 — re-measured off `world/ASHKARR_WORLDMAP_tiles.csv`, all three
> numbers are wrong as the world now stands.** The pass was redone as scattered pockets and
> the record was never updated.
>
> | this item said | measured 2026-08-23 |
> |---|---|
> | 1,200 tiles moved | **468** — `Deadstone` 346, `Umbra` 65, `Ammonia Flats` 57 |
> | `AB_RockyCrags` = 3,423 | **4,155** |
> | its thermal span narrows | **unchanged: −82 … +19.8 °C** |
>
> 🔑 **HorrorWastes did not take the cold end.** Of the coldest 500 tiles on the planet,
> **383 are still `AB_RockyCrags`** and 63 are `HorrorWastes`; **177 `AB_RockyCrags` tiles
> are colder than the coldest `HorrorWastes` tile** (−74.9 °C). The pockets were cut from
> *within* the cold band, not off its end.
>
> ⇒ **The thermal-coherence goal is a DIFFERENT problem and has been split out** to
> `ROCKY_CRAGS_SPANS_HUNDRED_DEGREES_1`. Do not weld it back onto this item.

## 🔴 DECIDE's ruling, 2026-08-23 — the TILES are right; the SHELL is the defect

**1. `HorrorWastes` stays at 468 nightside pockets.** Measured −74.9 … −33.9 °C, median
−49.3, arc 125–171. That is *"the night-side where the ancient bioweapons have adapted to the
extreme cold"* — his brief, satisfied. ⭐ And scattered pockets read better for ancient
bioweapon sites than a contiguous band would. **This half is done. Do not resize it.**

**2. The shell is still wrong, and it is worse than this item recorded.** Off the live dump,
2026-08-23:

| field | value | why it is wrong here |
|---|---|---|
| `terrainsByFertility` | `Sand` · `Soil` · `SoilRich` | 🔴 warm sand at −49 °C, between near-black `AB_RockyCrags` rock and pale `SeaIce` |
| `wildPlants` | 🔴 **exactly one: `Plant_Agave`** | a desert succulent on the deep nightside |
| `plantDensity` | 0.5 | high, for a roster of one |
| `animalDensity` | 3.6 | very high — near-empty at high density repeats the `AB_RockyCrags` failure |

⚠️ **CORRECTION to what DECIDE told the owner on 2026-08-22:** she said `HorrorWastes` has
*no plant at all*. That came from `plant_cherrypick_candidates.csv`, which was built **before**
these tiles existed and therefore carries no `HorrorWastes` rows. The biome itself has one
plant, and it is agave. ⇒ **The plant pass never saw this biome**, and the candidate CSV must
be rebuilt before `PLANT_CHERRYPICK_PASS_1` can claim to cover the planet.

**3. ⛔ `BiomeDef.wildAnimals` CANNOT be read from the def dump — this item's "three animals"
claim is UNMEASURED, not measured.** All **80** BiomeDefs report exactly **1024** entries,
byte-identical and alphabetically sorted, `SeaIce` and `AB_RockyCrags` included. That is a
truncation or merge artifact. `Bulwark` / `Terrorworm` / `Visceral` may well be right — but it
did not come from this dump and nobody can re-derive it there.

**Still owed, and none of it is tile work:**
1. A **cold terrain set** for `HorrorWastes`.
2. A **flora roster**, or `plantDensity 0` and a stated reason. Agave must go either way.
3. A **cast** of cold-viable hostiles, landing with the density, not after.

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

## 🔴 RE-MEASURED 2026-08-23 02:4x — THE BIOME IS NOW TWO PLACES, 20 °C APART, AND EMPTY BETWEEN

⚠️ **Every number in the section above is stale again.** The item said 468 tiles, arc 125–171.
Measured just now off `world/ASHKARR_WORLDMAP_tiles.csv`:

| | recorded above | measured 2026-08-23 02:4x |
|---|---|---|
| tiles | 468 | **807** |
| arc | 125–171 | **78–171** |
| temp | −74.9 … −33.9 °C | 🔴 **−74.9 … +19.8 °C** |

**What happened, and it was NOT a seat's error.** `eb7da875` (00:16) carries the owner's own
instruction: *"use HorrorWastes instead of RockyCrags for any tile above 0C."* 339 tiles moved.
Its commit body flagged the consequence in one line — *"the span problem moved rather than
went"* — and nobody acted on it.

### 🔑 The distribution is BIMODAL. There is no middle.

| temp band | tiles | arc | |
|---|---:|---|---|
| −74.9 … −60 | 162 | 145–171 | deep nightside |
| −60 … −40 | 250 | 130–151 | |
| −40 … −20 | 56 | 125–135 | |
| **−20 … 0** | 🔴 **0** | — | **nothing lives in the gap** |
| 0 … +10 | 252 | 89–103 | warm terminator |
| +10 … +19.8 | 87 | 78–94 | |

⇒ **468 cold tiles and 339 warm tiles wearing one biome name**, with a 20 °C hole between
them. This is `AB_RockyCrags`' 100-degree-span defect inherited whole, not fixed — and
`ROCKY_CRAGS_SPANS_HUNDRED_DEGREES_1` was closed on the finding that the carve never
narrowed anything. It narrowed nothing because the carve took *pockets from the middle* and
then a second pass *added the warm end*.

### ⭐ And this INVERTS what is owed. The shipped def is not wrong — it is on the wrong half.

The three things this item says are owed — cold terrain, a flora roster, a cold-viable cast —
were all specified against a biome believed to be entirely cold. It is not.

| shipped field | on the **warm 339** (0…+19.8 °C) | on the **cold 468** (−74.9…−20 °C) |
|---|---|---|
| `terrainsByFertility` `Sand`/`Soil`/`SoilRich` | ✅ right | ⛔ warm sand at −49 °C |
| `wildPlants` = `Plant_Agave` alone | ✅ right — agave is a desert succulent | ⛔ dead |
| `Bulwark` · `Terrorworm` · `Visceral`, comfy 0–40 °C | ✅ right | ⛔ all three die |
| its own description, *"A dry region…"* | ✅ right | ⛔ wrong place |

🔑 **The def was authored for the warm band and fits it with no change at all.** Re-terraining
`HorrorWastes` to survive −75 °C would break the 339 tiles it currently fits, to serve the 468
it does not. **One def cannot hold both halves**, and patching it is the wrong move in both
directions.

⇒ **The question this item now turns on is a placement question, not a terrain question:**
what biome do the **cold 468** wear? Terrain, flora and cast all follow from that answer and
cannot be written before it. DECIDE is measuring the installed biome roster for a cold
hostile candidate; if none exists, the cold half needs a def of its own and that is BUILD work
with a spec attached.

⚠️ **Do not "fix" this by moving the warm 339 back to `AB_RockyCrags`.** The owner explicitly
took them off `AB_RockyCrags` at 00:16 and the reason holds — rocky crags at +19.8 °C was the
original incoherence.

## ✅ DECIDE'S RULING, 2026-08-23 02:5x — the biome is ONE place, and the terrain set is spec'd

**Applied:** `src/RimMandrake/Utils/ashkarr_horror_is_one_place.py --apply` moved the 339 warm
tiles to `Desert`. Freeze restamped; `world/ASHKARR_WORLDMAP_settlements.csv` resynced (19 stale
`biome` values, 17 of them pre-existing drift from the shore/ice pass); `canon.yml`
`biome_tile_counts` re-derived (it was stale in 25 places and had no `HorrorWastes` row);
planet re-rendered and looked at.

| | before | after |
|---|---|---|
| `HorrorWastes` | 807 tiles, **94.7 °C span**, bimodal | **468 tiles, 41.0 °C span** (−74.9 … −33.9, median −49.3) |
| `Desert` | 4,309 | 4,648 — span **unchanged** at 77.4 °C |
| climate hole | −20 … 0 °C, 0 tiles | ✅ none wider than 10 °C |

⭐ **It also un-broke two settlements.** `Cryohaul` and `Ammonia Landing` (the Junkers) sit at
+6.7 and +6.2 °C, and both were sited *as `AB_RockyCrags`* — *"past the terminator on the warm
downwind flank, scavenging the cold swirl."* The 00:16 pass had put a Junker scavenging outpost
on top of an active bioweapon site. Zero settlements sit on the cold 468.

### 🔑 Terrain — MEASURED colours, and one candidate deliberately rejected

Sampled from the real terrain textures via `design/Jawa/fauna/biome_palette.json`:

| terrain | rgb | |
|---|---|---|
| `AB_ForsakenSands` / `AB_FineForsakenSands` | **[30, 29, 34]** | what `AB_RockyCrags` uses — the near-black rock all around it |
| `Ice` | **[155, 164, 172]** | `SeaIce` / `IceSheet`, its other neighbour |
| `AB_Ice` | [151, 167, 191] | pale blue |
| `AB_SnowOverRocks` | **[234, 232, 230]** | frost over stone — the brightest ground installed |
| `AB_DarkMud` | [33, 26, 20] | dark warm organic |
| `AB_Obsidian` | [46, 46, 46] | ⛔ **rejected: too close to [30,29,34] to read as a different place** |

**The spec, for BUILD — what the ground must READ as, in fertility order:**

1. **bare frozen ground** at the bottom — `AB_Ice` [151,167,191] or `AB_PackedIce`
2. **frost over stone** in the middle — `AB_SnowOverRocks` [234,232,230]
3. **dark organic breaking through the frost** at the top — `AB_DarkMud` [33,26,20]

🔑 **The read is *dark biological muck breaking through frost*, not a snowfield.** That is what
separates it from both neighbours: brighter than the near-black crags, and broken/dirty rather
than the flat pale sheet of `Ice`. ⚠️ **`AB_PackedIce`, `AB_PackedSnow` and `AB_DarkGravel` are
UNMEASURED** — they are not in the 68-entry palette, which only covers terrains already used by
a placed biome. Sample them before substituting one.

⛔ **`Sand` / `Soil` / `SoilRich` must go**, and so must `Plant_Agave` — a desert succulent at
−49 °C. `plantDensity` 0.5 is for a roster of one and is wrong either way.

### Still owed, and it is now writable because the biome is one place
1. ✅ **Cold terrain set** — spec'd above. → BUILD.
2. ⏳ **Flora roster**, or `plantDensity 0` with a stated reason. Agave goes either way.
   ⚠️ `plant_cherrypick_candidates.csv` was built before these tiles existed and has no
   `HorrorWastes` row, so `PLANT_CHERRYPICK_PASS_1` has never seen this biome.
3. ⏳ **A cast** of cold-viable hostiles landing WITH `animalDensity` 3.6, not after — carried by
   `BIOME_CREATURE_CAST_1`, one of the four biomes licensed to cast anomaly entities.
   ⛔ Its three shipped animals (`Bulwark`, `Terrorworm`, `Visceral`) are all comfy 0–40 °C.
   ⚠️ That trio is still **UNMEASURED** — `BiomeDef.wildAnimals` reads as 1024 identical
   alphabetical entries for all 80 BiomeDefs in the dump. It is a truncation artifact.
