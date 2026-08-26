# The Twilight Sea — brief for the implementing agent

Owner, 2026-08-26, approved ALL FIVE proposals, to run in the background after the Scald work.

## What the Twilight Sea IS — measured, do not re-derive

The only place on Ash'karr where you can sail out of the day and into the night.

| | |
|---|---|
| body | **604 tiles: 436 `Ocean` + 168 `SeaIce`**, every one at −350 m |
| span | **arc 63 → 120** — 27° into the dayside, 30° past the terminator (arc 90) |
| water temperature | **−11.2 °C to +35.3 °C** — a 46 °C gradient inside one sea |
| the ice margin | **39 open-water tiles** touching **54 ice tiles**, at arc 96–111, −5 to +6.5 °C |
| the two coasts | dayside ring **93 tiles, mean +24.5 °C**; nightside ring **122 tiles, mean −1.5 °C** |
| depth | shallow shelf — max shore-distance **6** (d1 265, d2 193, d3 105, d4 30, d5 10, d6 1) |
| rivers reaching it | **one** (tile 18267, Blackstar Field) |
| on the water now | `CoastalIsland` ×11, `River` ×1. Nothing else. |
| seats around it | 8 — Deepwater Compact ×2 (Boilquay, Deepwater Hold), **Blackstar Company ×2** (Hardpan Yard, Blackstar Field), Seabarter (Trade Moot), Rulla the Deep's Palace (Hutt), Aquifer Station (Homestead), Specimen Hall (Helix, −4.9 °C) |

Geometry files, already computed:
- `world/_roads/twilight_geom.json` — `body`, `ring`, `dist` (tile→shore distance), `mouths`
- `world/_roads/twilight_ice.json` — `ocean`, `ice`, `edge` (open water touching ice), `iceedge` (ice touching open water)
- `world/_roads/now_tiles.csv` — current tile scalars
- `world/_roads/_muts_now.json` — current mutators per tile
- `world/world_neighbors_sub7b.csv` — adjacency

## GATES — measured off the live roster. Enforce these; the setter does not.

| def | gate |
|---|---|
| `Iceberg` | avg temp −100…0 °C · **biome-locked `SeaIce`,`IceSheet`,Tundra…** ⇒ the ICE side of the margin, never open water |
| `IceDunes` | biome-locked `SeaIce`,`IceSheet` · max hilliness Flat |
| `VEE_DeepSnow` | avg temp −100…5 °C · biome-locked `IceSheet`,`SeaIce`,Tundra |
| `WindyMutator` | biome-locked AridShrubland, Desert, ExtremeDesert, **IceSheet, SeaIce**, Tundra… |
| `FoggyMutator` | biome-locked BorealForest, ColdBog, TemperateForest, TemperateSwamp, TropicalRainforest, TropicalSwamp… ⚠️ **`Ocean` is almost certainly NOT in this list — probe two tiles before planning on it, and fall back to `WindyMutator` if refused** |
| `Oasis` | **avg temp 20–60 °C** · biome-locked Desert, ExtremeDesert, Savanna, AB_TarPits… ⇒ dayside shore ONLY |
| `VEE_SaltPlains` | biome-locked Desert, ExtremeDesert, Tundra, AridShrubland, Grasslands… · needs no river |
| `VEE_GravelBeach` | requires coastline (1–6 coast sides) |
| `VEE_RisingWaters` | max hilliness Flat · requires coastline (1–5) |
| `VEE_MarineSanctuary` | requires coastline (1–5) |
| `VEE_LoneIsland` | requires coastline (3–5) · biome-locked · blocks ponds |
| `CoastalAtoll` · `Archipelago` · `Bay` · `VEE_CoralReef` | coastal, biome-locked (truncated ⇒ UNMEASURED, verify by read-back) |
| `VEE_RelictDelta` | biome-locked Desert, ExtremeDesert, AridShrubland, Grasslands… |
| `AB_TarLakes` | **landlocked (0 coast sides)** ⇒ never on a shore tile |
| `AncientRuins` | ungated except AB_MechanoidIntrusion |
| `AncientWarehouse` | biome-locked AridShrubland, Desert, ExtremeDesert… (truncated) |
| `Fish_Increased` / `Fish_Decreased` | ungated; **they displace each other**, never both on one tile |
| `AnimalLife_Increased` · `AnimalHabitat` · `SunnyMutator` · `Coast` · `Lakeshore` | ungated |

## THE FIVE PASSES

**1. THE ICE MARGIN.** The most interesting line on the planet is currently an invisible biome
boundary. A real marginal ice zone is the most productive water there is. `Iceberg` on a
deterministic subset of the 54 `iceedge` tiles; `Fish_Increased` + `AnimalLife_Increased` on
the 39 open-water `edge` tiles; `VEE_GravelBeach` where the ice grounds ashore. Everyone on
this sea fishes the same moving line — that is why Seabarter exists.

**2. THE DAY SHORE AND THE NIGHT SHORE.** 26 °C separates the two coasts of one sea and they
currently look alike. Dayside ring (arc < 90): `VEE_SaltPlains`, `DryGround`, `Oasis`,
`SunnyMutator`, evaporite and glare. Nightside ring (arc ≥ 90): `IceDunes`, `VEE_DeepSnow`,
`WindyMutator`, frost. Split strictly on arc 90 so the terminator becomes legible without
anything being drawn on it.

**3. THE SEA FOG.** Warm water pushing under the terminator into freezing air fogs
permanently. ⚠️ PROBE `FoggyMutator` on two Ocean tiles FIRST. If refused, deliver the same
idea with `WindyMutator` on the `SeaIce` band and the arid shores, and say plainly in the
report that the fog itself was not achievable.

**4. THE DROWNED COAST.** Max shore-distance 6 means a shelf, and the ring already carries 19
`VEE_SaltPlains`. `VEE_RisingWaters` on flat shores, more `VEE_SaltPlains` and `DryGround`,
`VEE_RelictDelta` where a dry channel would reach it, and a chain of `CoastalAtoll` /
`VEE_LoneIsland` former seabed. ⚠️ 28 `CoastalIsland`/`Archipelago` landmarks were placed on
these shores earlier today — do not stack on those tiles.

**5. THE SHIPPING LANE.** Two Compact harbours, two Blackstar pirate seats and the Trade
Moot's Seabarter sit here, and only ONE river reaches it — this sea is fed by trade, not by
land, and it is the planet's only maritime economy. `Fish_Increased` + `VEE_MarineSanctuary`
clusters as the fisheries the Compact holds; `AncientRuins` / `AncientWarehouse` on islands as
old harbour works; `Bay` chains marking anchorages, concentrated where the Blackstar seats can
reach them.

## HARD RULES

- ⛔ **NO RNG.** Hash the tile id: `h = lambda t: (t*2654435761) % 100`. A seed is a knob that
  could roll a second planet, which is out of scope in every version of this project.
- ⛔ Mutators only. Do not change biome, elevation, hilliness, temperature or rainfall.
- ⛔ Do not touch links (roads/rivers), settlements, or landmarks.
- ⛔ Leave gaps on purpose — placing on every eligible tile reads as generated. Half to
  two-thirds for the optional layers.
- ⭐ Category conflicts are the system working: a more specific mutator displaces the general
  one in its category. Verify by family, never by exact def.
