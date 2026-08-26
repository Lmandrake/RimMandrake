# The Grey Sea — brief for the implementing agent

Owner, 2026-08-26, approved proposals **2, 4 and 5 only**. ⛔ He did NOT take proposal 1
(extending the salt) or proposal 3 (a brine-works economy). **Do not add `VEE_SaltPlains`
anywhere, and do not invent an extraction industry.** Those were declined.

## What the Grey Sea IS — measured, do not re-derive

The planet's **industrial sea**, and it is drying. That is the through-line; everything you
place should serve it.

| | |
|---|---|
| body | **465 tiles: 374 `Ocean` + 91 `SeaIce`**, every one at −350 m |
| span | arc 70–108, temp −6.5 to +30.0 °C |
| **shallowest of the three seas** | max shore-distance **5**; **207 tiles are one hex from shore**, 131 at two |
| ice margin | **38 ocean tiles** touch ice; **52 ice tiles** touch open water; ice sits at arc 98–108, −6.5…+5 °C |
| shore ring | **188 tiles**, the most barren on the planet — AridShrubland 60, **Badlands 47, Wasteland 42**, Desert 33 |
| already on the water | `CoastalIsland` ×37, `VEE_SaltPlains` ×17, `River` ×2 |
| already on the ring | `Coast` ×43, `CoastalIsland` ×27, `VEE_SaltPlains` ×17, **`Stockpile` ×7**, `VEE_MineralDevoid` ×8, `VEE_DeepOreDevoid` ×8 |
| whose sea it is | **3 of the planet's 4 Junker seats** — The Claim Jump (16898), The Slagfield (3226), The Fuel Works (11779) — plus Toll Rock (Blackstar), Tidewatch (Deepwater), Rainshadow and Brine Flats (Homestead) |
| rivers reaching it | **4**: 8081, 11503, 16898, 16902 |
| the industrial gradient | **The Slagfield 29.8 °C at arc 70** … **The Fuel Works 4.9 °C at arc 96** — warm-and-working to frozen-and-abandoned |

Geometry, precomputed in `world/_roads/grey_geom.json`:
`body` · `ring` · `dist` (tile→shore distance) · `ocean` · `ice` · `edge` (ocean touching ice)
· `iceedge` (ice touching ocean) · `flat_shore` (127 tiles, hilliness Flat with 1–5 coast
sides) · `low_shore` (156 tiles, hilliness ≤ SmallHills) · `near_junk` (32 ring tiles within 4
hexes of a Junker seat) · `mouths` · `has_landmark` (⛔ **23 ring tiles already carry a
landmark — never stack on these**).

Also: `world/_roads/now_tiles.csv`, `world/_roads/_muts_now.json`,
`world/world_neighbors_sub7b.csv`.

## GATES — measured off the live roster. The setter enforces none of them; you must.

| def | gate |
|---|---|
| `Junkyard` | **max hilliness SmallHills** ⇒ use `low_shore` (156 tiles). junk density ×15 |
| `Stockpile` · `VEE_MineralDevoid` · `VEE_DeepOreDevoid` · `Coast` · `AnimalHabitat` · `AnimalLife_Increased` · `Fish_Increased` · `RiverDelta` | **ungated** |
| `AncientRuins` | ungated except AB_MechanoidIntrusion |
| `AncientWarehouse` | biome-locked AridShrubland, Desert, ExtremeDesert… (truncated ⇒ verify by read-back) |
| `VEE_RisingWaters` | **max hilliness Flat · requires coastline 1–5** ⇒ exactly `flat_shore` |
| `VEE_AlluvialFan` | max hilliness Flat · coastline 1–6. ⚠️ Mouths 16898 and 16902 are hilliness 4 and 8081 is 3 — **only 11503 (Flat) qualifies**; otherwise use a flat shore tile beside a mouth |
| `Iceberg` | avg temp −100…0 °C · **biome-locked `SeaIce`,`IceSheet`** ⇒ the ice side only |
| `IceDunes` | biome-locked `SeaIce`,`IceSheet` · max hilliness Flat |
| `VEE_DeepSnow` | avg temp −100…5 °C · biome-locked `IceSheet`,`SeaIce`,Tundra |
| `WindyMutator` | biome-locked AridShrubland, Desert, ExtremeDesert, IceSheet, SeaIce, Tundra… |
| `Archipelago` | coastline 2–5 · needs no river · biome-locked (truncated) |
| ⛔ `AB_DerelictClusters` | biome-locked to AB_MechanoidIntrusion, BiomeGrindland, BiomeToxlands — **NOT USABLE here.** Do not try it |

## THE THREE PASSES

**2. THE JUNKER COAST — the planet's breaking yard.**
Three Junker seats and seven `Stockpile` tiles already ring this water. Make it where things
are taken apart rather than built: `Junkyard` on a deterministic share of `low_shore`,
concentrated in `near_junk`; `AncientRuins` and `AncientWarehouse` scattered along the same
shore; `Stockpile` extended beyond the existing seven; `VEE_MineralDevoid` and
`VEE_DeepOreDevoid` pushed further along the ring, because this coast **has** been worked out.
🔑 The Abandoned Mines corridor (authored earlier today, running to The Unfinished Work in
Notch) is where the ore came from — this is where it ended up and was scrapped. Weight the
density toward the Junker seats so the yard has a centre.

**4. THE WADING SEA — 207 of 465 tiles are one hex from shore.**
This is barely a sea; it is a flooded flat, and it should read as something you could walk
into and keep walking. `VEE_RisingWaters` on a share of the 127 `flat_shore` tiles (tides run
far inland); `Coast` extended along the ring; `AnimalHabitat` and `Fish_Increased` through the
d1–d2 shallows; `Archipelago` chains where the coast gate allows.
⚠️ Do not make the whole shallow band uniform — it must read as a gradient into the deeper
middle, not a painted rim.

**5. THE FOUR MOUTHS AND THE COLD END.**
Four rivers arrive and not one is visible — the same defect the Scald had, fixed the same way:
`RiverDelta` + `Fish_Increased` + `AnimalLife_Increased` on each of 8081, 11503, 16898, 16902,
and on the water tiles immediately adjacent; `VEE_AlluvialFan` where a flat tile qualifies.
Then the industrial gradient: `Iceberg` on a share of the 52 `iceedge` tiles, `IceDunes` and
`VEE_DeepSnow` deeper into the 91 ice tiles, `WindyMutator` across the ice and the arid north
shore — so the sea runs warm-and-working in the south to frozen-and-abandoned in the north,
with The Fuel Works standing at 4.9 °C at the cold end.

## HARD RULES

- ⛔ **NO RNG.** `h = lambda t: (t*2654435761) % 100`. A seed is a knob that could roll a
  second planet — out of scope in every version of this project.
- ⛔ **No `VEE_SaltPlains` and no invented brine industry** — the owner declined both.
- ⛔ Mutators only. Never change biome, elevation, hilliness, temperature or rainfall.
- ⛔ Never touch links (roads/rivers), settlements or landmarks.
- ⛔ Never stack on the 23 ring tiles in `has_landmark`.
- ⛔ Leave gaps on purpose — half to two-thirds of eligible tiles. Placing on everything reads
  as generated.
- ⭐ Category conflicts are the system working: a more specific mutator displaces the general
  one in its category. Verify by family, never by exact def.
