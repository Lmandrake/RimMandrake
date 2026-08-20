# ASH'KARR — THE SUNDERED · the world definition

**The single source of truth for the planet.** Everything here has been ruled by the
owner or is derived from a ruling; nothing is a guess left standing. If the map has to
be rebuilt, rebuild it from this file.

- Recipe: `src/RimMandrake/Utils/ashkarr_paint.py` (frozen seed, no parameters)
- Settlement plan: `src/RimMandrake/Utils/ashkarr_settle.py`
- 🔑 **Map contents: `world/ASHKARR_WORLDMAP_*.csv`** — see §9
- Viewer: `python3 src/RimMandrake/Utils/worldview.py world/ASHKARR_WORLDMAP`

⛔ **This is not a generator.** Owner, 2026-08-18: *"We aren't trying to make random
generators that produce alternative planet maps… I just want ONE planetary map that is
as realistic as possible."* No seed sweeps, no variants, no exposed parameters.

⛔ **The savegame is not involved.** Owner, 2026-08-18/19: *"Please don't write to the
savegame file anymore"*, *"DO NOT use the rivers, roads, and settlements in the current
savegame"*, *"Don't respect anything in the seed file, that's just the tilemap we start
with."* The pipeline never opens a `.rws`. The only engine input is **tile geometry**
(`world/world_tiles_sub7b.csv`, `world/world_neighbors_sub7b.csv`), because tile
positions exist nowhere else.

---

## 1. The coordinate system

**The tidal lock is a POINT, not a latitude band.** Measured on both the painted world
and the vanilla source: temperature correlates **−0.98** with angular distance from
(lat 0, long 0) and **+0.10** with latitude.

```
arc   = degrees from the substellar point.  0 = noon · 90 = terminator · 180 = midnight
bear  = degrees around it.  0 = the GRAY flank (downwind) · 180 = the TWILIGHT flank
```

Same convention as `world_relief.py` and `paint_ashkarr.py`. **Do not diverge.**
Any spec written in "normalised latitude" means normalised **arc**.

Grid: **21872 tiles**, the engine's own geodesic grid at subdivisions 7. Self-checks:
exactly 12 pentagons, hex corners agreeing to 1e-16, 60° between neighbour slots.

## 2. Temperature

Owner's ruled endpoints, interpolated on arc, minus a **5.5 °C/km** lapse:

| arc | 0 | 30 | 60 | 90 | 120 | 150 | 180 |
|---|---|---|---|---|---|---|---|
| °C | +70 | +58 | +38 | **+14** | −22 | −58 | **−80** |

## 3. The gazetteer — every named place, in (arc, bearing)

### Water — 8.1% of the planet, three bodies
| name | centre | radius | water level | character |
|---|---|---|---|---|
| **The Scald** | (35, 185) | 10.5 | **perched, ~1410 m** | ⭐ a crater lake, **the one shape ruled round**. Spills through the Spine's notch |
| **The Twilight Sea** | (91, 170) | 22.0 | 0 m, sink | moldy |
| **The Grey Sea** | (92, 8) | 16.5 | 0 m, sink | salt-encrusted, shrinking |
| The Umbra Trap | (158, 62) | 19.5 | — | holds **ammonia**, not water → The Ammonia Flats |

🔴 Water was cut to **a third** of the old 22–28% spec (owner, 2026-08-18). The west
(Twilight) side is deliberately wetter than the east (Grey).

### Ranges — a ridge is a LINE, so it inherits the line's shape
| name | anchors (arc, bear) | crest |
|---|---|---|
| **The Scald Spine** | ring at (35,185), r 15.5, **notched** | 2050 m |
| **The Ashteeth** | (21.5,116) (23.5,142) (24.5,168) (24,203) (22,230) (19.5,254) | 1450 m |
| **The Fall Line** | (26,352) (34,357) (43,2) (52,6) (61,9) | 780 m |
| **The Dew Horn** | (58,148) (64,162) (67,178) (63,196) (57,210) | 1850 m |
| **The Ashfall Range** | (56,338) (63,352) (66,8) (61,24) | 1700 m |
| **The Twilight Crags** | (104,210) (110,186) (108,160) (114,134) | 900 m |
| **The Gray Crags** | (106,340) (112,12) (109,42) (116,68) | 820 m |
| **The South Crags** | (118,250) (127,272) (131,300) (124,322) | 760 m |

⛔ Never one spine — **many ranges, dotted with volcanoes**.

### Troughs and lows
**The Salt** (34,288)→(71,320) · **The Ember Sink** (36,96)→(68,74) ·
**The Dew Belt** (38,184)→(89,180) · **the Scald Gate** (49,180)→(39,184), the breach.

### Regions
The Anvil (arc<20, flat-topped substellar plateau) · The Dune Sea (20–40) ·
**The Rust Cathedral** (arc<12.5, bear within 118° of 40 — mechanoids, permanently at
war) · **The Scorch** (12.5–17, broken arcs) · The Pyrelands · The Nightspill ·
The Sunreach · The Ash Verge · The Long Dark · **The Umbra** (>152) ·
The Ammonia Flats · The Salt Gate (the deltas).

## 4. Hydrology — ruled, and it is the heart of the map

1. **Rain condenses at ALTITUDE and on the terminator seam**, never on the nightside;
   moist air is dragged sunward off the terminator and wrung out climbing the ranges,
   so a range rains on its **terminator-facing flank** and the substellar plateau is
   the rain shadow.
2. ⭐ **The Scald is the planet's water source and its river is the driving system.**
   It is a hot lake in the hottest place, so it evaporates hard, the vapour rains out
   on its own Spine, and the whole catchment leaves through **one notch**. The outflow
   carries **~32,000** units of flow — an order of magnitude more than anything else.
   🔴 A lake below sea level cannot emit anything; that is why the Scald is perched.
3. **Rivers evaporate as they go.** Loss per tile is brutal in the deep waste and mild
   in the crater basin. Without this every stream that starts anywhere arrives
   somewhere and the map fills with rivers no climate could feed.
4. **Genuine basins are left endorheic** — only pits shallower than 70 m are filled.
   🔴 Filling every depression guarantees every tile a path to the sea and makes dying
   rivers impossible; that bug produced **zero** salt pans.
5. ⭐ **Every branch ends in a dead salt plain, or a tiny hypersaline pool** if it was
   big when it died.
6. 🔴 **RIVERS DO NOT CONNECT THE BASINS** — owner, 2026-08-19: *"The rivers shouldn't
   connect the basins, they should peter out into salt flats."* Two things enforce it:
   evaporation is set high enough (base **900**/tile in the waste, **×0.16** inside the
   Scald basin) to kill even the 32,000-unit trunk before it reaches a sea, and **no
   river link is ever written into a basin** — a reach that would arrive at one is a
   terminus instead. The Twilight Sea, the Grey Sea and the Scald are therefore
   hydrologically **separate**; nothing flows between them.
   Currently **235 termini, ~1,120 tiles of dead salt plain, 3 hypersaline pools**.
7. **Dayside only.** Nothing feeds the nightside; there, water is locked as ice.

## 5. Vegetation zonation — owner, 2026-08-19

> *"the rivers should be through vicious jungles, then those are bracketed by lesser
> jungles/marshes, then Pyrelands, then desert in the general case (variation by
> location of course)."*

| band | dayside | meridian (arc > 82) |
|---|---|---|
| **on the river** | `AB_FeraliskInfestedJungle` — vicious jungle | `AB_MycoticJungle` / `PoisonForest` |
| **bracketing it** | `AB_MiasmicMangrove` · `COMIGO_GreaterSwamp_Tropical` · `ZBiome_DesertOasis` | `PoisonForest` |
| **then** | **The Pyrelands** — `ZBiome_Grasslands`, whose label is literally *"stormy savanna"* — with `AB_TarPits` interspersed | — (Pyrelands are dayside only) |
| **then** | desert | — |

🔑 **The bands scale with the river.** A creek gets one tile of green; the Scald's trunk
gets a corridor. Flat bands ate the vast desert the owner asked to keep.
🔴 **The Pyrelands are a narrow bracket, not a belt** — owner, 2026-08-19: *"Too much
grassland. Make the grassland into more desert, and make more extreme desert."* Gated to
**arc < 74** and to within **2 tiles of a mid river or 4 of a trunk**. `ZBiome_Grasslands`
went 6.3% → **2.0%** and `ExtremeDesert` 5.4% → **13.4%**.
🔑 **Terrestrial foliage belongs to the Scald**; the meridian gets mycoid and poison
forest. Two greens that mean different things.

## 5b. The waste is the default state

The dayside is desert unless a river pays for something else:

| arc | biome |
|---|---|
| < 30 | `ExtremeDesert`, unbroken |
| 30–56 | `ExtremeDesert`, `Desert` only where the noise field is high |
| 56–78 | `Desert`, with `ZBiome_Badlands` on the broken ground and `ExtremeDesert` returning in the flattest parts |
| > 78 | `Desert`, with `AridShrubland` only where it is genuinely damp |

Current census, for comparison when this is rebuilt: `AB_RockyCrags` 26.3 ·
`ExtremeDesert` 13.4 · `AridShrubland` 9.0 · `Wasteland` 7.8 (the salt plains) ·
`Desert` 7.7 · `AB_FeraliskInfestedJungle` 6.9 · `Ocean` 6.7 · `AB_MycoticJungle` 4.8 ·
`PoisonForest` 3.0 · `AB_PropaneLakes` 2.5 · `ZBiome_DesertOasis` 2.1 ·
`ZBiome_Grasslands` 2.0 · `ZBiome_Badlands` 1.9 · `Lake` 1.4.

## 6. Other biome placement

- `AB_OcularForest` — ⭐ **only at the tops of mountains** (>2350 m) that are **river
  sources**, in tiny patches; it *"bleeds small rivers outward"* and its streams run
  red with spores and toxins. ⚠️ *"Active bioweaponry"* is **not** in the record.
- `AB_GelatinousSuperorganism` — **on the terminator**, patches only, never a band.
- One volcanic province only: the **Scald rim** (Volcano · LavaField ·
  `AB_PyroclasticConflagration` · Scarlands · `AB_TarPits`). The rest of the planet is quiet.
- Nightside: `AB_RockyCrags` is the ground (26%), with `PoisonForest`,
  `AB_MycoticJungle`, `BMT_FungalForest`, `HorrorWastes` as lobes and patches;
  `Glowforest` and `BMT_CrystalCaverns` as isolated points past arc 150.
- ⛔ Blacklisted and not used: `SeaIce`, `IceSheet`, `Tundra`, `TropicalRainforest`,
  `Savanna` (the Advanced Biomes one), and the rest of the 29-entry list.

## 7. Factions — 72 settlements

Counts from `tidally_locked_world.md`'s arc-aware table, which **supersedes**
`faction_world_spec.md` §4 (still written in latitude bands, never rewritten).
🔑 **Placement is lore, not habitability** — siting by comfort puts everything on the
terminator. 🔑 **Small story-critical zones fill first**, or they starve.

| faction | defName | n | where, and why |
|---|---|---|---|
| The Galactic Empire | `Empire` | 3 | the seat/spaceport on the plateau rim; **the Scald Gate**; **the Fall Line pass** — choke points ⚠️ INFERRED from *"strategic passes"* |
| Hutt Cartel | `Jawa_HuttCartel` | 8 | **beside** a near-desert oasis, never on it — *"you can raid the well without besieging the town"* |
| Homestead Defense League | `OutlanderCivil` | 13 | the arable margin of the terminator; stores water, has no source |
| Deep Desert Tribes | `TribeCivil` | 9 | canyons, caves, isolated ridges — **never a water tile** |
| Jawa Trade Moot | `Jawa_IndigenousTribes` | 7 | crawler **circuit** nodes; one anchored on the mine the sandcrawlers were stolen from |
| the Junkers | `Jawa_Junkers` | 8 | 🔴 owner 2026-08-18: past the terminator on the **warm downwind flank**, plus the **old mining fields**. The docs only ever said *"wreck fields, wherever things fell"* — this is a new ruling |
| Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | 5 | **two clusters**: the ore seams, and the plateau beside the Rust Cathedral |
| Deepwater Compact | `Jawa_DeepwaterCompact` | 5 | the seas; **two on the Scald** despite the Empire |
| Wildsteam Clan | `Jawa_WildsteamClan` | 4 | 2 on the Scald's jungles, 2 in the meridian's poison marsh |
| Blackstar Company | `AM_EnemyPirate` | 4 | road junctions and ruins; they follow the money |
| Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | 3 | volcanic springs, plus the ruled plateau seat beside the Cathedral |
| Ascendant Helix | `Jawa_AscendantHelix` | 3 | the nightside edge — near the strange biomes, not near the people |
| the Forgotten Arsenal | `Mechanoid` | 0 | hidden; no world-map site, which is the intent |

Every holding's tile and its one-line reason are in `ASHKARR_WORLDMAP_settlements.csv`.

## 7b. ⭐ THE SETDOWN — where the player's clan lands. Sited 2026-08-19

The docs had only *"the habitable ring is ~34–57° of arc"* and left the rest open.
It is now decided, and it is in the recipe as `HOME_LATLON` / `HOME_NAME`.

| | |
|---|---|
| **tile** | **2476** — lat −1.028, lon +56.867 |
| **arc / bearing** | **56.9 / 358.8** — the outer edge of the habitable ring, on the **GRAY (downwind) flank** |
| **region** | The Fall Line Barrens |
| **ground** | `ExtremeDesert`, 276 m, **38.6 °C**, **18 mm** of rain, flat, with the tail of the Fall Line breaking to 583 m within ~2 tiles |
| **water** | **none.** Nearest river tile 26°, nearest sea further. The Scald is over the horizon and over a mountain range |

Why here and nowhere else — each of these is the reason, not a nice-to-have:

1. 🔑 **The campaign has a direction built into the ground.** Everything the clan
   needs lies **outward** toward the terminator; everything that will kill them lies
   **sunward**. No other tile in the ring makes the map itself point somewhere.
2. **Kin are one caravan out, not zero.** The Jawa Trade Moot's anchor **The Ore Moot**
   — *the mine the sandcrawlers were stolen from* — is **5.3°** away.
3. **The parts are the second ring.** The ship needs a thruster, a fuel tank and a
   pilot console; the Junkers squat the worked-out mining fields at **The Claim Jump
   10.4°**, **Tailings End 12.1°**, **The Slagfield 15.1°**. The v2 flight goal has a
   destination on the map from turn one.
4. **The Empire is a presence, not a garrison next door** — Ashgarrison at **16.2°**.
5. ⭐ **Water is the campaign's pressure, not a resource on the map.** No river, no
   oasis, no coast. This is what the water doctrine asks for and no wetter tile gives.
6. **The Fall Line is the range that things fall along.** The clan lives in its
   barrens; that is where a dead gravship was found and woken.

⚠️ `SCENARIO_SPEC.md` requires the start biome to be Desert / ExtremeDesert /
AridShrubland. `ExtremeDesert` is the harshest of the three and grows nothing —
that is the intent, but it is the one choice here worth a playtest before it is final.

🔑 **Resolved by lat/lon, never by tile number**, so it survives a geometry rebuild;
the recipe **aborts** if that lat/lon stops being `ExtremeDesert`, because the home
site is a decision and not an output.

## 8. Roads

A **minimum spanning tree** between the holdings plus **shortcuts** wherever the tree
detour exceeds 1.9× direct — a pure MST makes caravans cross the planet to reach a
neighbour. Cost rises with altitude, across the green, into the dark (arc > 96) and
across the Anvil, so nothing rules a straight line through any of them.
⛔ No rectangular roads, no ruler-straight diagonals.

## 9. 🔑 Where the map contents live

```
world/ASHKARR_WORLDMAP_tiles.csv        ⭐ THE MAP: 21872 rows —
                                        tile, lat, lon, arc, bearing, elev_m, temp_c,
                                        rain_mm, biome, water, river_flow, region
world/ASHKARR_WORLDMAP_settlements.csv  72 rows — faction, name, tile, arc, biome, why
world/ASHKARR_WORLDMAP_links.csv        every river and road edge
world/ASHKARR_WORLDMAP_meta.json        planet, regions, factions, counts
```

The `.rws` savegames and everything under `world/view/` are **not** sources. The
savegames are the old automated-worldgen mess and are being cleaned up; the renders are
pictures of the CSV above.

## 10. Open questions for the owner

1. ~~The player start is unsited.~~ **CLOSED 2026-08-19 — see §7b.** The Setdown,
   tile 2476. The one thing left to confirm by play is `ExtremeDesert` vs `Desert`.
2. The Empire's three seats are choke points by inference; the docs say only *"roads,
   strategic passes"* and the spaceport.
3. `faction_world_spec.md` §4 is still written in latitude bands and contradicts this
   file. It was ordered rewritten and never was.
4. Is the mod's `TidallyLocked` PlanetTypeDef keyed on latitude at runtime? If so it
   disagrees with the measured point-lock and one of them has to move.

---

## 11. State of play — handoff, 2026-08-19

**Done and committed.** The map exists, is complete, and renders. Nine rounds of
owner review are folded into §1–§10 above. Commits: `808e181` (viewer) →
`f421383` → `f769c49` → `1458964` → `ce41ab1` → `f672372` → `66e6c93`.

**The whole pipeline, three commands:**

```
python3 src/RimMandrake/Utils/ashkarr_paint.py                  # rebuild the map (~30 s)
python3 src/RimMandrake/Utils/worldview.py world/ASHKARR_WORLDMAP --png --no-tooltips
python3 src/RimMandrake/Utils/worldgeom.py --selftest           # prove the geometry
```

`ashkarr_paint.py` holds every design decision and is the only file to edit for content.
`ashkarr_settle.py` holds the faction plan. `worldview.py` is the renderer and knows
nothing about Ash'karr. **Nothing opens a `.rws`.**

**🔴 The loop is LOOK, not measure.** Change the recipe, rebuild, render, open the PNG,
judge it by eye. Every defect that mattered in this work — compass-circle seas, comb
rivers, rectangular roads, bullseye biomes, rivers that could not die — passed its
numeric checks while the picture was obviously wrong.

### 🔴 The map was never actually frozen — found and fixed 2026-08-19

`despeckle()` iterated a bare `set()` of biome-name strings, and dissolving one speck
changes what the next speck sees, so the **order** of those names decided the outcome.
Python randomises string hashing per process. **Three rebuilds produced three different
planets** (roads 80 / 82 / 84 links) and every one of them passed every acceptance
check. The committed CSV was one arbitrary sample, not THE map.

Fixed by `sorted(set(...))`, a name-based tie-break in the ring vote, and pinning
`PYTHONHASHSEED` by re-exec at the top of the recipe. Two consecutive rebuilds are now
**byte-identical**. Re-freezing moved **107 tiles of 21872** and reshuffled which
Homestead holding got which name.

🔑 **The lesson generalises: "it renders the same" is not "it rebuilds the same."**
Before trusting any future rebuild, run it twice and `md5sum` the three CSVs.

### What is NOT done, in the order it probably matters

1. ~~The player start is unsited.~~ **DONE — §7b.** The Setdown, tile 2476, arc 56.9 on
   the gray flank. `ExtremeDesert` vs `Desert` is the one call worth a playtest.
2. ~~Region labels collide on the render.~~ **DONE.** The anchor separation was the
   wrong test — what collides is the projected **text box**. `worldview.py` now tests
   pixel boxes and walks a ladder of vertical offsets, and the looser anchor rule
   surfaced names that had been silently dropped (The Scorch, The Anvil, The Pyrelands).
3. **`AB_GelatinousSuperorganism` smears across the top** of the rectangular map. It is
   honest — the poles genuinely sit on the terminator at arc 90 — but it reads as a
   band. Mollweide shows its true size (0.2%).
4. **Landmarks and tile mutators are not authored at all.** The map has biomes,
   elevation, rivers, roads and settlements; it has no landmarks.
5. **Nothing has been tested in game**, because nothing writes a savegame any more.
   How this map reaches RimWorld is an open design question, not a solved one.
6. The four questions in §10 are still open.

### Traps a fresh agent will otherwise walk into

- ⛔ **Do not "fix" the Scald's roundness.** It is a crater and it is the one shape
  ruled round.
- ⛔ **Do not fill every depression** in the hydrology. That silently makes dying
  rivers impossible and produced zero salt pans for two rounds.
- ⛔ **Do not threshold anything against raw `arc`.** Warp it first (`thb`), or the
  zone comes out as a ring around the planet.
- ⛔ **Do not warp a placed mass additively.** `blob + 0.22*noise` painted one
  mechanoid cluster over 6.7% of the planet. Multiply.
- ⛔ **Do not site settlements by habitability.** It puts all of them on the terminator
  and contradicts the faction plan.
- ⚠️ `faction_world_spec.md` §4 is still written in latitude bands and contradicts this
  file. It was ordered rewritten and never was.
