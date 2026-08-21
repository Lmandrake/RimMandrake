# ASH'KARR — every named thing on the surface

**Working sheet for sketching the map. 2026-08-20.**
Sources: `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` (§3 gazetteer, §13 landmarks) ·
`world/ASHKARR_WORLDMAP_meta.json` (24 features, with centres and draw sizes) ·
`world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles) · `world/ASHKARR_WORLDMAP_settlements.csv` (72).

⚠️ **TRANSIENT.** A scratch sheet, not doctrine. The definition doc stays authoritative.

---

## How to read the positions

```
arc   = degrees from the substellar point (the sun is always overhead at arc 0)
          0 = noon · 90 = terminator · 180 = midnight
bear  = degrees around that point.  0 = GRAY flank (downwind) · 180 = TWILIGHT flank
lat/lon = the same place in ordinary globe coordinates. substellar = (0, 0)
```

Temperature is a pure function of arc: **+70 °C at 0 · +38 at 60 · +14 at the terminator ·
−22 at 120 · −80 at midnight**, minus 5.5 °C per km of altitude.

**"size" below is `maxDrawSizeInTiles` from meta — roughly how wide the label should be drawn.**
Planet is 21,872 tiles, 8.1% water.

---

## 1. Water — 3 bodies, and they are hydrologically separate

| name | shape & size | lat / lon | what & why |
|---|---|---|---|
| **The Scald** | round crater lake, 312 tiles, size 27.5 | −0.8, −35.5 | ⭐ **perched at 1,410 m** — a hot lake in the hottest place. The planet's water source. Ringed by its own Spine, spills through one notch |
| **The Twilight Sea** | irregular sink, 851 tiles, size 48.8 | 17.7, −91.0 | sea level, on the **twilight (wet) flank**. Largest standing water. Moldy |
| **The Grey Sea** | irregular sink, 617 tiles, size 48.2 | 7.7, 89.5 | sea level, on the **gray (dry) flank**. Salt-encrusted and shrinking |

🔑 **Nothing flows between them.** Rivers evaporate and die in salt before reaching any basin.

---

## 2. Ranges — 8 massifs. A ridge is a LINE, so it takes the line's shape

| name | shape & size | lat / lon | crest | what it does |
|---|---|---|---|---|
| **The Scald Spine** | **ring**, notched, 361 tiles, size 32.9 | −4.9, −35.2 | 2050 m | the crater wall around the Scald. The notch is the only way out |
| **The Ashteeth** | arc of 6 anchors, 333 tiles, size 39.8 | −1.2, −14.5 | 1450 m | teeth sunward of the Scald, toward the Anvil |
| **The Dew Horn** | curved line of 5, 491 tiles, size 51.2 | −0.4, −60.2 | 1850 m | the twilight-flank rain-catcher — highest, wettest |
| **The Ashfall Range** | line of 4, 390 tiles, size 39.0 | 0.7, 60.6 | 1700 m | the gray-flank counterpart |
| **The Fall Line** | line of 5, 251 tiles, size 35.2 | 2.1, 44.2 | 780 m | low ridge; **the range things fall along**. Its pass is the road off the plateau |
| **The Twilight Crags** | line of 4, 384 tiles, size 26.2 | −17.5, −108.4 | 900 m | past the terminator, twilight side |
| **The Gray Crags** | line of 4, 576 tiles, size 69.7 | 21.6, 115.6 | 820 m | past the terminator, gray side. Widest sprawl |
| **The South Crags** | line of 4, 432 tiles, size 53.1 | −49.4, 163.1 | 760 m | deep nightside, southern |

⛔ **Never one spine.** Many ranges, dotted with volcanoes.

---

## 3. Regions and wastes — 13, sunward to midnight

| name | shape & size | lat / lon | arc band | what it is |
|---|---|---|---|---|
| **The Anvil** | flat-topped plateau, 642 tiles, size 29.5 | 0.0, 0.0 | 1–20 | the substellar plateau. +70 °C, rain shadow, dead flat on top |
| **The Rust Cathedral** | lobe, 236 tiles, size 20.7 | 5.1, 5.1 | 1–20 | ⭐ **mechanoid ground, permanently at war.** Sunward of the Anvil's edge. `AB_MechanoidIntrusion` |
| **The Scorch** | broken lobe, 90 tiles, size 23.2 | 16.4, 4.6 | 9–25 | `Scarlands` — burned, cracked ground on the Anvil's gray shoulder |
| **The Dune Sea** | huge belt, 1,725 tiles, size 65.2 | 0.0, 4.3 | 20–40 | the great sand ocean ringing the Anvil |
| **The Pyrelands** | narrow bracket, 233 tiles, size 20.8 | 18.6, −55.8 | 40–69 | "stormy savanna" — the thin green fringe **beside rivers only**, with tar pits |
| **The Fall Line Barrens** | patch, 551 tiles, size 32.7 | −0.0, 46.2 | 40–57 | ⭐ **the clan's home ground.** Flat extreme desert under the Fall Line |
| **The Dew Belt** | belt, 833 tiles, size 47.5 | −3.8, −65.0 | 46–91 | the damp twilight-flank margin below the Dew Horn |
| **The Salt** | trough, 501 tiles, size 45.9 | 1.2, 105.4 | 69–117 | dead salt flats on the gray flank, near sea level |
| **The Salt Gate** | narrow neck, 97 tiles, size 9.0 | 31.6, −57.5 | 61–69 | ⭐ **smallest named place.** The deltas — where rivers spread and die |
| **The Sunreach** | huge lobe, 1,333 tiles, size 84.5 | −2.0, 114.5 | 96–124 | **largest named region.** Past the terminator, gray side |
| **The Nightspill** | huge lobe, 1,201 tiles, size 87.7 | −4.1, −114.8 | 96–124 | its twilight-side twin |
| **The Umbra** | cap, 1,268 tiles, size 41.4 | 0.0, 180.0 | 152–180 | ⭐ **the midnight cap.** −80 °C. Centred exactly on the antisolar point |
| **The Ammonia Flats** | basin, 818 tiles, size 33.6 | 20.1, 169.8 | 136–179 | ⭐ **the propane/ammonia lakes** — 554 tiles of `AB_PropaneLakes` in a frozen depression beside the antisolar point. Not water. The doc also calls this depression **The Umbra Trap** |

---

## 4. The one great river

**The Scald trunk.** ~29,000 units of flow — an order of magnitude bigger than anything else.
Leaves the Scald through the Spine's notch at **arc ~51, bearing ~142** and runs **sunward**
along bearing ~145 all the way to **arc ~11**, close to the substellar point.

- **Shape:** a single winding green corridor ~40° of arc long, cutting across the Dune Sea.
- **What grows on it:** `AB_FeraliskInfestedJungle` — vicious jungle, the only true jungle
  on the dayside — bracketed by mangrove and oasis, then a thin Pyrelands fringe, then desert.
- **Rivers elsewhere:** 238 river links total — 113 HugeRiver, 103 Creek, 12 LargeRiver, 10 River.
- **How they end:** **235 termini, ~1,120 tiles of dead salt plain, 3 hypersaline pools.**
  Every branch peters out. None reaches a sea.

**Roads:** 837 road links — a minimum spanning tree between the 72 holdings plus shortcuts.
Cost rises with altitude, across green, into the dark, and across the Anvil, so no straight lines.

---

## 5. The player's start

**THE SETDOWN** — tile 2476, lat −1.03 / lon +56.87, **arc 56.9 / bearing 358.8**.
Region: The Fall Line Barrens. `ExtremeDesert`, 276 m, **38.6 °C, 18 mm rain**, flat.

- **No water at all.** Nearest river 26° away; the Scald is over the horizon and over a range.
- Sits on the **gray (downwind) flank**, at the outer edge of the habitable ring.
- Everything the clan needs is **outward** toward the terminator; everything that kills them
  is **sunward**. The map itself points somewhere.
- Nearby, in order: **The Ore Moot 5.3°** (kin) · **The Claim Jump 10.4°**, **Tailings End 12.1°**,
  **The Slagfield 15.1°** (the ship's parts) · **Ashgarrison 16.2°** (the Empire).
- ⭐ The dead gravship was found and woken here.

---

## 6. Settlements — 72, in 12 factions

One line each: how many, roughly where, and why there.

| faction | n | where, and why |
|---|---|---|
| **Homestead Defense League** | 13 | arc 65–90, the arable terminator margin. Vaporators and cisterns; **stores water, has no source** |
| **Deep Desert Tribes** | 9 | arc 72–79, canyons, caves and isolated ridges. **Never a water tile** |
| **Hutt Cartel** | 8 | arc 68–84, **beside** a near-desert oasis, never on it — *"raid the well without besieging the town"* |
| **the Junkers** | 8 | split: 5 past the terminator (arc 96–100) on the warm downwind flank; 3 squatting **worked-out mining fields** at arc 66–70 |
| **Jawa Trade Moot** | 7 | arc 62–76, sandcrawler **circuit** nodes across the near-desert; anchored on the stolen mine |
| **Geonosian Foundry Hive** | 5 | **two clusters** — 2 on the ore seams (arc 63), 3 subterranean beside the Rust Cathedral (arc 12–20) |
| **Deepwater Compact** | 5 | the water, all of it: 2 on the Scald (arc 39–51), 2 on the Twilight Sea, 1 on the Grey Sea |
| **Blackstar Company** | 4 | arc 63–79, road junctions and ruins. They follow the money |
| **Wildsteam Clan** | 4 | 2 in the Scald's jungles (arc 56–65), 2 in the meridian's poison marsh (arc 80) |
| **The Galactic Empire** | 3 | **choke points only** — the plateau rim, the Scald Gate, the Fall Line pass |
| **Free Droid Enclaves** | 3 | 2 on volcanic springs (arc 42–43), 1 beside the Rust Cathedral, which is sacred to them |
| **Ascendant Helix** | 3 | arc 104–105, cold isolated labs on the nightside edge — near the strange biomes, not the people |
| **the Forgotten Arsenal** (Mechanoid) | **0** | ⭐ **hidden. No world-map site, and that is the intent** |

### The named holdings, if you want them on the sketch

- **Empire (3):** Sunspire *(the seat & spaceport, plateau rim, arc 23)* · Oxalate Watch *(the Scald Gate)* · Ashgarrison *(the Fall Line pass)*
- **Hutt (8):** Spicehead · Sarlacc Ground · Itunt · The Yards · Wellsong · The Tollgate · Bantha Cross · Greasepalm
- **Homestead (13):** Dewhome · Condenser Flats · Bell Cistern · Mistcatch · Stillmarket · Rainshadow · Vaporfall · Longfurrow · Cistern Hill · Greenline · The Dripworks · Marrowfield · Aquifer Station
- **Deep Desert Tribes (9):** Duneward · Stone Moot · Redscarp · The Dry Moot · Barno · The Long Camp · Ashfoot · Knife Canyon · The Blind Wells
- **Jawa Trade Moot (7):** **The Ore Moot** *(the stolen mine — the anchor)* · Crawler Ground · Ridge Cache · Wreck Circuit · Sandmoot · The Bartering Rock · Tin Camp
- **Junkers (8):** The Fuel Works · Cryohaul · Ammonia Landing · Warmside Camp · Bonepick Station · **Tailings End · The Slagfield · The Claim Jump** *(the three mining fields)*
- **Geonosian (5):** The Unfinished Work · Oxide Deep *(oxalate seams)* · The Godmouth · Founder's Kiln · Hollow Nave *(at the Cathedral)*
- **Deepwater (5):** Butora · Anchor Deep *(the Scald)* · Deepwater Hold · Coldquay *(Twilight Sea)* · Tidewatch *(Grey Sea)*
- **Wildsteam (4):** Steamreach · Rego *(Scald jungle)* · Marrowmarsh · Sporefall *(poison marsh)*
- **Blackstar (4):** Blackstar Field · The Contract Camp · Toll Rock · Hardpan Yard
- **Free Droids (3):** The Trade Socket · Vent Nine *(volcanic springs)* · No Master *(at the Cathedral)*
- **Ascendant Helix (3):** Helix Landing · The Coil · Quiet Lab

---

## 7. Hand-placed landmarks — cap ~16

Named places get a landmark; everything else is vanilla scenery.

| place | landmark | why |
|---|---|---|
| **The Setdown**, one tile adjacent | `Ruins` / `AbandonedColonyOutlander` | where the dead gravship was found |
| **The Scald Gate** | `Valley` | the one breach in the Spine |
| **The Ore Moot** | `AncientQuarry` | the mine the sandcrawlers were stolen from |
| **Sarlacc Ground** | `sw_Sarlacc` | ships in Star Wars Animal Collection |
| **The Rust Cathedral** | `AncientLaunchSite` / `AncientGarrison` | mechanoid, at war |
| **the Scald rim volcanics** | `LavaLake` · `LavaCrater` | the one volcanic province |
| the salt pans | `DryLake` / `VEE_SaltPlains` | ⚠️ may not be legal on `Wasteland` — verify |
| the oases | `Oasis` | fits arc 30–60 only |
| the deep waste, a few | `AncientHeatVent` | a heat plume on the hottest world |
| the Junkers' fields | `Ruins` · `AbandonedColonyTribal` | wherever things fell |

⛔ **Never place** any ice landmark. Coastal shapes (Bay, Cove, Fjord, Peninsula, Harbor) are
legal but should be **rare** — the planet is 8.1% water.

---

## 8. What the ground actually looks like — 24 biomes

| % | biome | where |
|---|---|---|
| 20.3 | `AB_RockyCrags` | **the nightside floor**, arc 78–180 |
| 16.4 | `ExtremeDesert` | the dayside default, arc 1–84 |
| 11.0 | `AridShrubland` | the damp terminator margin |
| 9.8 | `Desert` | arc 56–78 |
| 8.9 | `AB_MycoticJungle` | the meridian and nightside lobes |
| 7.9 | `Wasteland` | ⭐ **the salt pans** — 1,721 tiles where rivers died, arc 37–138 |
| 6.7 | `Ocean` | the two seas |
| 2.8 | `PoisonForest` | meridian marsh |
| 2.5 | **`AB_PropaneLakes`** | ⭐ **the Ammonia Flats**, arc 136–179 |
| 2.5 | `ZBiome_Badlands` | broken ground |
| 2.4 | `AB_FeraliskInfestedJungle` | ⭐ **the Scald river corridor** — the only true jungle |
| 1.9 | `BMT_FungalForest` | nightside patches |
| 1.4 | `Lake` | the Scald, exactly 312 tiles |
| 1.1 | `AB_MechanoidIntrusion` | the Rust Cathedral, exactly 236 tiles |
| 1.1 | `ZBiome_Grasslands` | the Pyrelands fringe |
| 1.0 | `ZBiome_DesertOasis` | 227 tiles, arc 13–84 — **the Hutt wells** |
| 0.6 | `BMT_CrystalCaverns` | isolated nightside points, arc 146–164 |
| 0.4 | `AB_GelatinousSuperorganism` | terminator patches only |
| 0.4 | `Scarlands` | the Scorch, exactly 90 tiles |
| 0.3 | `AB_MiasmicMangrove` | river brackets |
| 0.3 | `AB_TarPits` | in the Pyrelands, arc 81–106 |
| 0.1 | `AB_PyroclasticConflagration` · `Volcano` · `LavaField` | ⭐ **the Scald rim, arc 19–50, bearing ~200 — the one volcanic province on the planet** |

---

## 9. Named in the lore but NOT on the current map

Worth knowing before you sketch — these have **zero tiles**:

| name | status |
|---|---|
| **The Ash Verge** | listed as a region in the definition doc §3. Absent from the tiles, the meta and the painter |
| **The Long Dark** | same — named as a region, never realised |
| **The Ember Sink** | named as a trough `(36,96)→(68,74)`. Not stamped |
| **The Umbra Trap** | the ammonia depression `(158,62)`. Realised as **The Ammonia Flats**; the name itself isn't used |
| **The Ashteeth** | in `meta.json` as a massif (333 tiles) but **not stamped into the tiles' `region` column** |
| `AB_OcularForest` | §6 wants it on mountaintops >2350 m that are river sources. **0 tiles** |
| `Glowforest`, `HorrorWastes` | §6 names them as nightside points/lobes. **0 tiles** |
| `COMIGO_GreaterSwamp_Tropical` | §5 names it as a river bracket. **0 tiles** |

Also: the census printed in §5b of the definition doc is **stale** against the current CSV
(it says RockyCrags 26.3 / ExtremeDesert 13.4 / AridShrubland 9.0; the map now has
20.3 / 16.4 / 11.0).
