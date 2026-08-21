<!-- status: live -->
# ASH'KARR — THE SUNDERED · the world definition

> 📌 **Corrected 2026-08-20 against `infrastructure/state/canon.yml`:** water is stated
> as **8.14 %** (1,780 of 21,872 tiles) rather than the rounded 8.1 %, and §5b's biome
> census was re-measured from `world/ASHKARR_WORLDMAP_tiles.csv` — the figures printed
> there before were from an earlier paint.

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

Same convention as `world_relief.py` and `ashkarr_paint.py`. **Do not diverge.**
(It was also `paint_ashkarr.py`'s convention; ⛔ that script was DELETED 2026-08-19 —
savegame writing is out. The convention is unchanged.)
Any spec written in "normalised latitude" means normalised **arc**.

Grid: **21872 tiles**, the engine's own geodesic grid at subdivisions 7. Self-checks:
exactly 12 pentagons, hex corners agreeing to 1e-16, 60° between neighbour slots.

## 2. Temperature

Owner's ruled endpoints, interpolated on arc, minus a **5.5 °C/km** lapse:

| arc | 0 | 30 | 60 | 90 | 120 | 150 | 180 |
|---|---|---|---|---|---|---|---|
| °C | +70 | +58 | +38 | **+14** | −22 | −58 | **−80** |

## 2b. The mod agrees about the point, and disagrees about the terminator

**`Alien Worlds - Tidally Locked`** (`7f.alienworlds.tidallylocked`, ACTIVE, requires
`7f.alienworlds`) is **point-keyed, not latitude-keyed** — confirmed from its shipped
C# source, `.../294100/3631364335/Source/PlanetTypeDef.cs`:

```csharp
var effectiveLat = Mathf.Acos(Mathf.Cos(pos.x*Deg2Rad) * Mathf.Cos(pos.y*Deg2Rad)) * Rad2Deg;
return AvgTempByLatitudeCurve.Evaluate(effectiveLat / 90f);
```

That is great-circle distance from **(lat 0, lon 0)**. **Its substellar point and ours
are the same point, computed the same way.** The measured −0.98 correlation in §1 is
this formula, seen from the outside.

🔑 **And the per-tile temperatures we paint SURVIVE.** `tileTemperature` is persisted
world state — `<tileTemperatureDeflate>` sits in the save beside `tileBiomeDeflate` —
not a value recomputed on demand. The mod's only base-temperature patch is on
`WorldGenStep_Terrain.GenerateTileFor`, which runs **once, at order 0**. Its one runtime
patch merely suppresses the day/night swing. Nothing overwrites us at play time.

🔴 **But its curve is much colder than ours in the middle, and that is not cosmetic:**

| | arc 0 | **arc 90 (terminator)** | arc 180 |
|---|---|---|---|
| the mod's `AvgTempByLatitudeCurve` | +70 | **−37** | −80 |
| **§2, ours** | +70 | **+14** | −80 |

Same endpoints, **51 °C apart at the terminator.** Ours is the one that can be right:
the entire faction plan stands on a habitable terminator — the Homestead Defense League
lives on *"the arable margin of the terminator"*, and thirteen of the 72 holdings are
there. A −37 °C terminator deletes them.

⇒ **The importer MUST overwrite `temperature` on every tile.** If it stamps biome and
elevation but leaves temperature to the mod, the world will look right and be
uninhabitable where the people are. This is exactly the kind of defect that passes every
numeric check.

## 3. The gazetteer — every named place, in (arc, bearing)

### Water — 8.14% of the planet, three bodies

**1,780 water tiles of 21,872 = 8.138%**, measured from `world/ASHKARR_WORLDMAP_tiles.csv`
2026-08-20 and rounded to **8.14%** in `_meta.json`. That 1,780 is exactly `Ocean` 1,468 +
`Lake` 312; there is no third water biome. (~~8.1%~~ was this file's rounding; cite 8.14%.)
| name | centre | radius | water level | character |
|---|---|---|---|---|
| **The Scald** | (35, 185) | 10.5 | **perched, ~1410 m** | ⭐ a crater lake, **the one shape ruled round**. Spills through the Spine's notch |
| **The Twilight Sea** | (91, 170) | 22.0 | 0 m, sink | moldy |
| **The Grey Sea** | (92, 8) | 16.5 | 0 m, sink | salt-encrusted, shrinking |
| The Umbra Trap | (158, 62) | 19.5 | — | holds **ammonia**, not water → The Ammonia Flats |

🔴 Water was cut to **a third** of the old ~~22–28%~~ spec (owner, 2026-08-18) — the
arithmetic target was **~8.6%** and the painted result is **8.14%**. The west
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
went 6.3% → **2.0%** and `ExtremeDesert` 5.4% → **13.4%** at the time of that pass;
re-measured 2026-08-20 the realised figures are **1.07%** and **16.37%** — the gate bit
harder than the pass reported. See the census in §5b.
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

Current census — **re-measured from `world/ASHKARR_WORLDMAP_tiles.csv`, 2026-08-20**,
percentages of all 21,872 tiles (this supersedes the census printed here before, which
was taken from an earlier paint): `AB_RockyCrags` 20.30 (4,440) ·
`ExtremeDesert` 16.37 (3,581) · `AridShrubland` 10.98 (2,401) · `Desert` 9.82 (2,147) ·
`AB_MycoticJungle` 8.87 (1,939) · `Wasteland` 7.87 (1,721, the salt plains) ·
`Ocean` 6.71 (1,468) · `PoisonForest` 2.76 (604) · `AB_PropaneLakes` 2.53 (554) ·
`ZBiome_Badlands` 2.50 (546) · `AB_FeraliskInfestedJungle` 2.44 (534) ·
`BMT_FungalForest` 1.94 (425) · `Lake` 1.43 (312) · `AB_MechanoidIntrusion` 1.08 (236) ·
`ZBiome_Grasslands` 1.07 (233) · `ZBiome_DesertOasis` 1.04 (227) ·
`BMT_CrystalCaverns` 0.58 (127) · `AB_GelatinousSuperorganism` 0.44 (96) ·
`Scarlands` 0.41 (90) · `AB_MiasmicMangrove` 0.30 (65) · `AB_TarPits` 0.26 (57) ·
`AB_PyroclasticConflagration` 0.14 (31) · `Volcano` 0.11 (23) · `LavaField` 0.07 (15).
**24 distinct biomes are painted**, out of the 36 defs that survived the owner's cut —
a def can survive the cut and appear on zero tiles.

## 6. Other biome placement

- `AB_OcularForest` — ⭐ **only on the very highest ground, `> 2000 m`**, in tiny patches;
  it *"bleeds small rivers outward"* and its streams run red with spores and toxins.
  ⚠️ *"Active bioweaponry"* is **not** in the record.
  🔴 **Gate reset 2026-08-21, owner's instruction.** It read `>2350 m`, and **the map's
  highest tile is 2266 m** — so the gate was unsatisfiable and the biome is painted on
  **0 tiles**. `> 2000 m` admits **14 tiles** (0.06% of the planet, all `hilliness` 4–5),
  which is the "few highest tiles" the entry always meant.
  ⛔ **The old "that are river sources" clause is dropped as a PRECONDITION and kept as a
  DESCRIPTION.** All three tiles above 2000 m that already carry river flow are `Volcano`
  on the Scald rim, and repainting them would eat the planet's one volcanic province. The
  forest *makes* the streams; it does not need to find them.
  ✅ **The patch to paint: `4299`, `9158`, `9159`** — the Ashfall Range summits at 2190 ·
  2177 · 2117 m. They are the **highest non-volcanic ground on Ash'karr**, they are
  adjacent, and they are currently `ExtremeDesert`. Nine of the other eleven candidates are
  the volcanic province and must be left alone.
- `AB_GelatinousSuperorganism` — **on the terminator**, patches only, never a band.
- One volcanic province only: the **Scald rim** (Volcano · LavaField ·
  `AB_PyroclasticConflagration` · Scarlands · `AB_TarPits`). The rest of the planet is quiet.
- Nightside: `AB_RockyCrags` is the ground (26%), with `PoisonForest`,
  `AB_MycoticJungle`, `BMT_FungalForest`, `HorrorWastes` as lobes and patches;
  `Glowforest` and `BMT_CrystalCaverns` as isolated points past arc 150.
- ⛔ Blacklisted and not used: `SeaIce`, `IceSheet`, `Tundra`, `TropicalRainforest`,
  `Savanna` (the Advanced Biomes one), and the rest of the 29-entry list.

## 6b. 🔴 RAIN — the rule, and the one number that enforces it

**Owner, 2026-08-19:** *"Ban rainfall: v1 (but might still happen on highly mountainous
terrain!)"* The full ruling and its corrections are in
`infrastructure/state/items/D-V2-RAIN.md`. What a reader of THIS file needs:

🔑 **The lever is `rain_mm` in the tile CSV, not the biome weather lists.** Every rain
`WeatherDef` in the game carries a `commonalityRainfallFactor` curve that starts at
**`(0, 0)`** and is evaluated **per tile** on `Tile.rainfall`
(`WeatherDecider.cs:191`). ⇒ **at `rain_mm = 0` a rain weather's commonality is multiplied
by exactly zero and it can never be selected**, on any biome, without patching anything.

⚠️ **18 mm is not 0.** 80.4% of the map sits at ≤49 mm, which suppresses rain by ~98.6% —
*rare*, not *banned*. And `WeatherDecider.cs:185` multiplies rain commonality by **15**
during a large fire, so the residue surfaces exactly when the player is watching a fire.

⛔ **`rain_mm` has no other runtime consumer.** Re-verified 2026-08-21: nothing reads it for
plant growth, fertility or yield. `WorldGenStep_Rivers.cs:131` sums it into river flow, but
that is worldgen and our `river_flow` column is authored — **do not "fix" river flow after
zeroing rainfall.**

🔴 **The measured defect, 2026-08-21.** 596 tiles carry exactly **1668 mm**. Only 271 are
`AB_FeraliskInfestedJungle`; the other 325 are badlands, extreme desert, oases, grasslands,
**31 tiles of `AB_PyroclasticConflagration` and 23 of `Volcano`** — and **235 of them are in
The Dune Sea.** Of the 937 tiles at ≥600 mm, **433 are not mountainous at all** (median
elevation 696 m).

⇒ Awaiting the owner: `RAIN_BAN_SCOPE_1`. Drying them repaints nothing visible — `rain_mm`
does not render on the world map — but it is an edit to an accepted map, so it is his call.

---

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
| Blackstar Company | `Pirate` | 4 | road junctions and ruins; they follow the money |
| Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | 3 | volcanic springs, plus the ruled plateau seat beside the Cathedral |
| Ascendant Helix | `Jawa_AscendantHelix` | 3 | the nightside edge — near the strange biomes, not near the people |
| the Forgotten Arsenal | `Mechanoid` | 0 | hidden; no world-map site, which is the intent |

Every holding's tile and its one-line reason are in `ASHKARR_WORLDMAP_settlements.csv`.

## 7b. ⭐ THE SETDOWN — where the player's clan lands. Sited 2026-08-19

The docs had only *"the habitable ring is ~34–57° of arc"* and left the rest open. ⚠️ **That figure was overruled 2026-08-21 — the ring is 40–57°** (`canon.yml > world.habitable_ring_arc`). ✅ **The Setdown does not move:** arc 56.9 is inside 57 under either reading, which is why the siting was never the thing in dispute.
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
3. ~~`faction_world_spec.md` §4 is still written in latitude bands.~~ **CLOSED
   2026-08-19** — §4 now carries a SUPERSEDED banner with the latitude→arc
   substitution and the two statements in it that are outright false.
4. ~~Is the mod's `TidallyLocked` PlanetTypeDef keyed on latitude at runtime?~~
   **CLOSED 2026-08-19 — it is POINT-keyed, and it agrees with us.** See §2b.

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
   Settlement names and region names also share **one** box list now; they used to
   declutter only against their own kind, which is why `The Ashfall Range` printed
   through `The Claim Jump`. ⚠️ The tradeoff is real and deliberate: with one list, a
   crowded region name can lose its slot entirely rather than overprint. `The Scald
   Spine` is the current casualty.
3. **`AB_GelatinousSuperorganism` smears across the top** of the rectangular map. It is
   honest — the poles genuinely sit on the terminator at arc 90 — but it reads as a
   band. Mollweide shows its true size (0.2%).
4. **Landmarks and tile mutators.** ⭐ **§13 now rules them** — the ~16 hand-placed
   named places, the ban list, and the `Dunes` trap that would have stripped the
   player's own start map of junk, plants and ruins. **The placements are specified
   but not yet written into the recipe.**
5. ~~How this map reaches RimWorld is an open design question.~~ **DECIDED — §12.**
   ⛔ The `WorldGenStep` answer lasted one hour: owner ruled 2026-08-19 that every
   in-game worldgen hook is stripped. **The route is the LIVE BRIDGE** — two companion
   tool methods write the tiles into a generated world before any map exists, and the
   owner saves. CHECK is building it. Untested in game, a build item not a design one.
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
- ⚠️ `faction_world_spec.md` is written on 2026-08-13 premises throughout. §4 is now
  bannered, but the rest of that file still argues from *"worlds are disposable, so we
  will generate many"*. **There is one world and it is frozen.** Read it for reasoning,
  never for coordinates or for scope.

---

## 12. 🔑 HOW THIS MAP REACHES RIMWORLD — the LIVE BRIDGE. Ruled by the owner, 2026-08-19

⛔ **THE `WorldGenStep` ROUTE IS DEAD.** Owner's ruling, 2026-08-19, verbatim:
*"anything aimed at the in-game worldgen should be stripped, anything importing
external worldmaps through the bridge or configuring the game to generate the inputs
for the external worldmap creation should be kept."*

This section used to specify `WorldGenStep_Ashkarr` at order 20, registered by a
`PatchOperationAdd` into the Surface `PlanetLayerDef`. **Struck in full.** It was never
wrong about the DATA — §12.6 and §12.7 stand unchanged and are now more load-bearing,
not less. It was wrong about the DOOR. A `WorldGenStep` is an in-game worldgen hook,
and there are to be none, whether it generates or merely overwrites.

⚠️ **Kept as a struck section rather than deleted**, so that nobody reads §12.6's
`GenerateFresh` vocabulary and reconstructs the step from the evidence. Everything
below the strike is the live route.

| ~~12.1–12.5, as written 2026-08-19~~ | ⛔ **DEAD** — `WorldGenStep_Ashkarr`, order 20, `PatchOperationAdd` into `/Defs/PlanetLayerDef[defName="Surface"]/worldGenSteps`. Owner's ruling above. Do not rebuild it; the pattern is in git at `16767eb~1` if it is ever needed for something that is not worldgen |

### 12.1 The route: the companion DLL writes the tiles into a world that already exists

```
mod stack active, MLP subcount 7 / coverage 1.0, factions per WORLDGEN_FACTION_CHECKLIST
   -> owner creates a world in game, any seed          (vanilla worldgen runs, untouched)
   -> world screen is up, NO map instantiated yet
   -> CHECK pushes the 21,872 authored tiles over the bridge into the live WorldGrid
   -> owner places the gravship and the six founders
   -> owner saves  ->  THAT save is v1's campaign start
```

🔑 **Why this and not a savegame writer.** Ruled 2026-08-18 after two dead loads and
~2 cold loads burned: an offline `.rws` writer can only validate the parts it already
understands, and both attempts passed every invariant check and still killed the game
on load. The engine writing its own save is consistent by construction, and a bad write
costs a reload rather than a cold load. Full post-mortem in
`infrastructure/state/queue/CHECK.md`, item `worldpaint-live-bridge-route-9d41c7`.

🔑 **Why the world screen and not a live colony.** Both save-editing failures had a
`Map-0-PlayerHome` in the save. Repainting a planet underneath an instantiated map is
the thing that broke; do the write before any map exists.

### 12.2 What the companion needs — two tool methods beside `jawa/world_neighbors`

1. **A batch tile setter** — biome, elevation, hilliness, temperature, rainfall,
   swampiness, pollution, over a run of tile indices.
2. **A link setter** — rivers and roads.

🔴 **The link setter must call `WorldGrid.OverlayRiver(from, to, def)` and
`OverlayRoad(from, to, def)`, never the raw lists.** Read off the assembly 2026-08-19,
not inferred: both are public, both write **BOTH endpoints**, and both maintain the
priority rules. `SurfaceTile.RiverLink` is `{ PlanetTile neighbor; RiverDef river; }` —
`neighbor` is the tile itself, so there is no neighbour-slot index to reconstruct at
all. Hand-writing `potentialRivers` one-sided gives a river the engine only half-sees.
Call rivers **mouth first, then upstream**: `OverlayRiver` ends with
`to.riverDist = max(to.riverDist, from.riverDist + 1)`, so `riverDist` is maintained
incrementally and is order-dependent. No BFS is needed.

Adding a companion tool measured ~10 min plus a ~2 min deploy in a **game-down** window.
The unknown, to be found by doing: **which live caches need explicit invalidation after
a tile write** — the world mesh, the pathfinder's perceived costs, the feature text
meshes. `jawa/refresh_rect` is the map-side precedent for exactly this class of bug.

### 12.3 🔴 THE COST OF THE RULING, and it is real: downstream steps ran against the OTHER planet

The dead route's whole argument for order 20 was that every later worldgen step would
see *our* planet. **The bridge route loses that**, and the loss must be handled rather
than discovered:

| generated against the vanilla world, then we overwrite the ground under it | what to do |
|---|---|
| **Rivers 200 · Roads 600** | ⭐ **OVERWRITE.** We authored both in `_links.csv`. Vanilla's flow into vanilla's coastlines. Push ours after clearing theirs |
| **Factions 500** | ⭐ **OVERWRITE.** 72 holdings are placed by lore in `_settlements.csv`; siting by habitability is banned (§7). Re-`Tile` the existing world objects rather than deleting and remaking them |
| **Landmarks 650 · Mutators 700** | ⚠️ **THE ONE THAT BITES.** These were picked from the vanilla tile's biome and terrain, so after our stamp a Landmark can sit on a biome that forbids it. Decide by LOOKING at the first render; the fallback is to clear and re-roll them after the stamp |
| **Features 1000** | ⭐ **OVERWRITE.** We have 24 named regions in `_tiles.csv`; vanilla named them at random |
| Pollution 450 | harmless; we stamp pollution to zero anyway |
| AncientSites 300 · AncientRoads 400 | ⚠️ decide by LOOKING at the first render |

### 12.4 What the importer must assert before it writes anything

1. 🔴 `Find.WorldGrid.TilesCount == 21872`, or **refuse loudly**. The tile IDs in the CSV
   are not vanilla's: `My Little Planet` (`oblitus.mylittleplanet`, ACTIVE) must be at
   **subcount 7** with **`planetCoverage 1`**. Verified 2026-08-19 in
   `.../workshop/content/294100/3626210061/Worldbuilder/TidallyLocked/Preset.xml`.
   Any other subcount shifts **every** tile ID and silently paints the wrong planet.
   ✅ **These are exactly the slider settings the owner keeps** — they are what makes the
   external pipeline's inputs match the game's grid. See `SCENARIO_SETTINGS_SPEC.md`.
2. The CSV's row count is 21,872 plus a header. Verified: the file is 21,873 lines.
3. 🔴 **No map may be instantiated.** Refuse if `Find.CurrentMap != null`.
4. Write through the **`Tile` object** — `.PrimaryBiome`, `.elevation`, `.temperature`,
   `.rainfall`, `.hilliness`, `.swampiness`, `.pollution` — never the raw
   `tileBiome[]`-style arrays. Confirmed off the assembly: `Tile.pollution` is a
   **`float`**, so the old `/65535` scale dispute between `worldmap.py` and
   `apply_world.py` does not arise on this route. (⛔ `apply_world.py` was DELETED
   2026-08-19 — savegame writing is out; the dispute is now moot on both sides.)
5. 🔴 **`WaterCovered` is `elevation <= 0`, and there is no sea-level setting.** Write
   elevation and biome **together, in both directions**, or you get an `Ocean` tile that
   behaves like ground.
6. ⚠️ **`SurfaceTile.Roads` / `.Rivers` return `null`** when the tile's biome sets
   `allowRoads` / `allowRivers` false. An authored road crossing such a biome is stored
   and invisible. Check `_links.csv` against the biome table before debugging a
   "missing" road.

### 12.5 Settlements and features — the two APIs, read off the assembly

**Settlements**, from `FactionGenerator` lines 41–48 — note the def is **not**
`WorldObjectDefOf.Settlement`:

```csharp
WorldObject wo = WorldObjectMaker.MakeWorldObject(layer.Def.SettlementWorldObjectDef);
wo.SetFaction(faction);
wo.Tile = <PlanetTile>;
if (wo is INameableWorldObject n) n.Name = <our name>;
Find.WorldObjects.Add(wo);
```

**Features**, from `FeatureWorker.AddFeature`: `new WorldFeature(def, layer)` → set
`.name` → set `grid[t].feature = f` for every member tile → set `drawCenter` and
`maxDrawSizeInTiles` → append to `Find.WorldFeatures.features`. `AssignBestDrawPos` is
`protected`, so we supply the centroid ourselves — `_meta.json` already carries
`drawCenter` and `extent` for all 24 regions. `Tile.feature` is a **`WorldFeature`
object reference** at runtime, so the old "uniqueID or list index" question is moot;
for the record it is the **uniqueID** (`WorldFeatures.ExposeData` →
`GetFeatureWithID`).

### 12.5b Faction RELATIONS are ours to set too — ruled 2026-08-19

⭐ **The same logic that made settlements ours makes NPC↔NPC relations ours.** Owner,
2026-08-19: *"We're going to manually write these settlements ourselves via the live
bridge."* A relation between two NPC factions has **no `FactionDef` field at all** — there
is no "permanent ally" to declare — so it is either an importer action or it is fiction.

🔴 **The one that must be set: `Jawa_GeonosianFoundryHive` ↔ `Jawa_FreeDroidEnclaves` are
FORMALLY ALLIED, with trade.** Ruled 2026-08-17 (`FACTION_SPEC.md` §"the Geonosian Foundry
Hive's story"), and it **supersedes** `faction_roster_v2.md`'s *"Cold / no trade"*. The
shared history stands — they worked the same company site — but it produces alliance, not
grievance. ⇒ *"The cruellest ground on Ash'karr is the one place with a functioning
peace."* If the importer does not set it, worldgen rolls something arbitrary and the
plateau's whole point is lost.

**The API:** `Faction.SetRelationDirect(other, FactionRelationKind.Ally)` — public,
read off the assembly at `Faction.cs:653`. ⚠️ It runs the same
`Notify_RelationKindChanged` notifier as an organic change, so set it **before any map
exists**, exactly like every other import write (§12.4 rule 3).
⚠️ And remember the thresholds (`FactionRelation.cs:28,33,38`): Ally is `goodwill >= 75`,
Hostile is `<= -75`, and hostility only *ends* at 0. Setting the kind directly avoids
having to reason about the number, but anything that later damages the relation is
subject to that hysteresis.

### 12.6 The complete per-tile gap list

Confirmed against the 1.6 assembly and the on-disk save schema, 2026-08-19. ⚠️ In 1.6
the arrays no longer live on one flat `WorldGrid` — they live on a **`PlanetLayer`**,
and only `Class="SurfaceLayer"` carries the real ones (the two `OrbitLayer`s carry
`tileBiomeDeflate` and nothing else). A naive search for `tileBiomeDeflate` finds the
orbit layers first.

| per-tile state | in the bundle? | who supplies it |
|---|---|---|
| `tileBiome` · `tileElevation` · `tileTemperature` · `tileRainfall` | ✅ | authored |
| **`tileHilliness`** (uint8 enum `Undefined 0, Flat 1, SmallHills 2, LargeHills 3, Mountainous 4, Impassable 5`) | ✅ **added 2026-08-19** | authored — see §12.7 |
| **`tileSwampiness`** (byte/255 → 0.0–1.0) | ✅ **added 2026-08-19** | authored — see §12.7 |
| `tilePollution` (uint16/65535) | ❌ | **zero everywhere.** Ruled: this planet's problem is heat and thirst, not toxin |
| `tileFeature` (uint16 WorldFeature id, **65535 = none**) | ⚠️ names only | ⭐ **UNAUTHORED — the real remaining gap.** See below |
| `tileRiverOrigins` / `…Adjacency` / `…Def` | ⚠️ `_links.csv` gives (a, b, def) | ⭐ **not written at all.** Call `WorldGrid.OverlayRiver(a, b, def)`; the engine builds these on save. See §12.2 |
| `tileRoadOrigins` / `…Adjacency` / `…Def` | ⚠️ same | same |
| `tileRiverDistances` (uint8, hops to nearest river) | ❌ | ⭐ **no BFS needed.** `OverlayRiver` maintains `riverDist` itself — but call mouth-first, upstream-after, or the numbers are wrong |
| `tileMutatorTiles` / `tileMutatorDefs` | ❌ | **let vanilla roll them** (§12.3). The old save carried ~1.4 per tile |
| `World.landmarks` — `Dictionary<PlanetTile,Landmark>`, keys `"<tileId>,<layerId>"`, values `{def, name}` | ❌ | vanilla places them; we add a named few |

🔑 **There is no neighbour-slot problem. There is no slot.** An earlier attempt to
reconstruct the engine's `GetTileNeighbors` ordering *offline* scored 0.197 against a
0.161 random baseline and was recorded as a blocker. It was never one, and the reason
is stronger than "the importer runs in-game so it can ask": read off the assembly
2026-08-19, `SurfaceTile.RiverLink` is `{ PlanetTile neighbor; RiverDef river; }` — the
link holds **the tile**, not an index into anything. The slot exists only in the
serialized save, which we no longer write.
⚠️ **And the save's "one undirected edge owned by the lower-index tile" (origin < target
on 1.000, reciprocity 0.000) is FALSE of the live object graph.** `OverlayRiver` and
`OverlayRoad` append to **both** endpoints. Write the lists by hand, one-sided, and the
engine half-sees the river. Use the Overlay methods — §12.2.
RiverDefs `Creek/River/LargeRiver/HugeRiver`; RoadDefs `DirtPath/DirtRoad/StoneRoad/
AncientAsphaltRoad/AncientAsphaltHighway`.

⭐ **`tileFeature` is the one genuinely unauthored piece.** Our 24 region names exist only
as CSV text. A `WorldFeature` is a *runtime object*, not a def:
`{def (FeatureDef), uniqueID (int), name (string), drawCenter (Vector3 on the unit
sphere, where the label is drawn), maxDrawSizeInTiles (float), layer}`. `FeatureDef`
(25 ship) supplies `workerClass`, `minSize`/`maxSize`, `rootBiomes` and a `nameMaker`
RulePack. So the recipe must emit, per region: a `FeatureDef` to borrow, a centroid, an
angular extent — and the importer must build the records and the per-tile uint16 map.
**Until it does, vanilla's `WorldGenStep_Features` will already have named our 24
regions at random** — under the bridge route it has *finished* by the time we write.
That is why §12.3 rules Features as ours to overwrite. The exact API is in §12.5.

✅ **The four things this section used to flag as UNCERTAIN are settled**, read out of
`Assembly-CSharp.dll` on 2026-08-19 rather than inferred — `RiverLink`/`RoadLink` shape,
`tileFeature` (it is the **uniqueID**, and moot anyway: `Tile.feature` is a
`WorldFeature` object reference at runtime), settlement placement (§12.5), and the
pollution scale (`Tile.pollution` is a **`float`**; the `/65535` disagreement between
`worldmap.py` and the deleted `apply_world.py` was a save-format question that this route
never asks — ⛔ `apply_world.py` was DELETED 2026-08-19 and there is no save-write side
left to disagree with). Decompile with `ilspycmd -p`; the bodies that matter are
`RimWorld.Planet/WorldGrid.cs` lines 390–511, `RimWorld.Planet/SurfaceTile.cs`,
`RimWorld.Planet/Tile.cs`, `RimWorld/FactionGenerator.cs` lines 41–48 and
`RimWorld/FeatureWorker.cs` line 30.
### 12.7 Hilliness and swampiness — the rulings behind the two new columns

Neither is a function of elevation in vanilla; `WorldGenStep_Terrain` rolls both from
their own noise stacks. On a hand-authored planet they are ours, and **nothing
recomputes them at load — unwritten, hilliness stays `Undefined`.**

**Hilliness is LOCAL RELIEF, not height.** A 2 km plateau is flat to stand on; a 400 m
escarpment is not. Calibrated against this planet: land relief runs p50 = 132,
p80 = 231, p90 = 325, p95 = 439, so cuts at **110 / 210 / 380** give

| Flat | SmallHills | LargeHills | Mountainous | Impassable |
|---|---|---|---|---|
| 36.4% | 37.6% | 19.3% | 6.5% | **0.2% (42 tiles)** |

⭐ **The crags floor to SmallHills regardless of relief.** `AB_RockyCrags` is 26% of the
planet and its relief p50 is only 140 — by relief alone, most of the broken country
printed *Flat*. Biome sets a floor; relief only raises it.

🔴 **Impassable exists in exactly one place: the Scald Spine crest, outside the Gate.**
It makes the Spine expensive to cross and bends traffic toward the one breach.
⚠️ **It does not seal the crater, and this file will not pretend it does** — the ring is
broken, and manufacturing a contiguous wall would be inventing terrain to serve a
sentence. Everywhere else Impassable is banned: this is a caravan game whose distances
are the story, and stray impassable tiles just break routes.

**Swampiness is a property of the green, and the green is a property of the rivers.**
A table on biome, zero on everything else — mangrove 0.85, greater swamp 0.80,
feralisk jungle 0.45, mycotic 0.40, poison forest 0.35, propane lakes 0.30, fungal 0.25,
oasis 0.20, grassland 0.05. **The desert is 0.0 and the salt pans are 0.0.**
Result: 5,010 tiles non-zero, planet mean 0.081.

---

## 13. LANDMARKS AND TILE MUTATORS — ruled 2026-08-19

**114 LandmarkDefs and 336 TileMutatorDefs are live** on this install (45 + 87 vanilla;
the rest from Vanilla Landmarks Expanded, Alpha Biomes, Geological Landforms, Star Wars
Animal Collection and others). About **62 landmarks and 110 mutators survive** a filter
for our biomes. This is not a shortage; it is a curation problem.

### 13.1 🔴 The trap that matters most: `Dunes` is the anti-Jawa mutator

Read straight out of
`...\RimWorld\Data\Odyssey\Defs\TileMutators\TileMutators_Natural.xml`:

```xml
<defName>Dunes</defName>
<preventsLandmarks>true</preventsLandmarks>
<biomeWhitelist><li>ExtremeDesert</li></biomeWhitelist>
<maxHilliness>Flat</maxHilliness>
<junkDensityFactor>0</junkDensityFactor>
<plantDensityFactor>0</plantDensityFactor>
<geyserCountFactor>0</geyserCountFactor>
<preventGenSteps>
  <li>ScatterRuinsSimple</li> <li>ScatterShrines</li>
  <li>AncientUtilityBuilding</li> <li>AncientLandingPad</li>
</preventGenSteps>
```

A `Dunes` tile has **no junk, no plants, no ruins, no shrines, no ancient structures, no
geysers and no landmark.** On a campaign whose entire economy is scavenging wrecks, that
is not "harsh terrain" — it is the mutator that deletes the game's content from the tile.

**Our exposure: 1,083 tiles — 5.0% of the planet — are `ExtremeDesert` AND `Flat`, and
🔴 THE SETDOWN IS ONE OF THEM.** Tile 2476 is `ExtremeDesert`, hilliness `Flat`. If
vanilla's Mutators step at order 700 rolls `Dunes` there, the player's opening map has
nothing on it to scavenge. Exactly one faction holding sits on eligible ground.

⇒ **RULING. `Dunes` is banned on the start tile and every tile adjacent to it,
unconditionally. Everywhere else it stays.** A dune sea that is genuinely empty is
correct — the Dune Sea *should* punish anyone who crosses it, and that is 5% of the
planet doing its job. The defect is not the mutator; it is that the player's home was
about to be one of them.
⚠️ The importer must enforce this, because it cannot be enforced by a def.

### 13.2 🔑 A LandmarkDef has no biome field. The legality gate is elsewhere.

`LandmarkDef` has **13 fields and not one of them is `biomeWhitelist`, `minHilliness`
or `averageTemperatureRange`.** A landmark is legal exactly where its `mutatorChances`
entry marked `Required="True"` is legal — **the mutator carries the constraints, and
the landmark inherits them.** Anyone reading `LandmarkDef` alone to decide "can this go
here" will get the wrong answer every time.

`comboLandmarkMutators` is the merge case: extra mutators applied when a landmark lands
on a tile that already has one, which is what sets `isComboLandmark` in the save.
`category` is a free string for world-UI grouping and is **not** a constraint.

### 13.3 Ash'karr's landmarks are NAMED PLACES, not scenery

⭐ **Vanilla rolls the scenery; we hand-place only what the gazetteer already names.**

| ~~§12.4 lets `Landmarks` (650) and `Mutators` (700) run, because by order 20 they are picking against our biomes and our hilliness. A second step at **order 660** adds ours.~~ | ⛔ **DEAD 2026-08-19 — written on the `WorldGenStep_Ashkarr` route.** There is no order 20 and no order 660; there are no worldgen steps at all |

🔴 **Under the bridge route the scenery rolls against the VANILLA planet, not ours.**
Landmarks (650) and Mutators (700) have already finished by the time the importer
stamps a single tile, so every one of them was chosen from a biome and a hilliness we
are about to overwrite. §12.3 states this correctly and calls it **the one that bites**;
this section used to state the opposite three hundred lines later. ⇒ **The importer
clears and re-rolls landmarks and mutators AFTER the stamp, then adds ours** — there is
no generator ordering left to lean on. Decide the re-roll by LOOKING at the first
render, per §12.3.

**Cap the hand-placed set at ~16.** A landmark that is everywhere is wallpaper; the
whole value of one is that it means a specific place on this specific planet.

| our named place | landmark | note |
|---|---|---|
| **The Setdown**, one tile adjacent — never the home tile itself | `Ruins` or `AbandonedColonyOutlander` | ⭐ **where the dead gravship was found and woken.** The campaign's own backstory, on the map. Not on 2476: the ship needs 4,057 clear substructure cells |
| **The Scald Gate** | `Valley` | the one breach in the Spine. No biome list — gated on `minHilliness: Mountainous` only, which the Spine satisfies |
| **The Ore Moot** | `AncientQuarry` | *the mine the sandcrawlers were stolen from.* Mountainous; ore-rich |
| **Sarlacc Ground** | `sw_Sarlacc` | ships in Star Wars Animal Collection; blacklists ice only, `maxHilliness: Mountainous`, and combos onto Dunes/Sandy/Hollow/Chasm/Valley/Cavern — authored for exactly this |
| **The Rust Cathedral** | `AncientLaunchSite` / `AncientGarrison` | mechanoid, permanently at war |
| the Scald rim volcanics | `LavaLake` · `LavaCrater` | `LavaField` only — the one volcanic province |
| the salt pans (`Wasteland`) | `DryLake` or `VEE_SaltPlains` | ⚠️ **verify**: `DryLake` whitelists Desert/ExtremeDesert/AridShrubland, and our salt pans are `Wasteland`. It may not be legal there |
| the oases (`ZBiome_DesertOasis`) | `Oasis` | temp range **20–60 °C**; our arc 30–60 band runs 38–58 °C, so it fits — but it does **not** fit sunward of that |
| the deep waste, a few | `AncientHeatVent` | desert-exclusive, and a heat plume on the hottest world in the setting is the right kind of joke |
| the Junkers' fields | `Ruins` · `AbandonedColonyTribal` | wherever things fell |

⛔ **Never place:** `Iceberg`, `IceDunes`, `Crevasse`, `FrozenRuins`, `VEE_DetachedIceberg`,
`VEE_IceSpires`, `VEE_GlacialMoraine`, `VEE_PermafrostBasin` (all ice-gated) ·
`VEE_Cenotes` (explicitly blacklists all three deserts) · `VEE_Mangrove`,
`VEE_TemperateGrasslands`, `VEE_CoralReef`, `VEE_BurnedForest` (temperate/wet) ·
`AB_MagmaticQuagmire`, `AB_MutagenicSprings` (need biomes we do not have).
🔑 The coastal shapes — `Bay`, `Cove`, `Fjord`, `Peninsula`, `Harbor`, `CoastalAtoll` —
**are** whitelisted for dry biomes, so they are legal, but only on a tile touching one
of the three waters. They should be rare: this planet is 8.14% water (1,780 of 21,872 tiles).

### 13.4 What is NOT settled

- ⚠️ **The shortlist cannot be read from `Data/` alone.** Six ACTIVE mods patch the
  vanilla biome whitelists — More Vanilla Biomes, Star Wars KotOR Resources, GRiNDTerra
  Biomes, Advanced Biomes (Continued), Comigo's Greater Swamps, Vanilla Gravship
  Expanded — adding and removing `ZBiome_*`, `AB_*` and `VEE_*` entries. Any legality
  call must be made against the **patched** defs, not the shipped ones.
- ⚠️ **Mutator arbitration is inferred, not decompiled.** A conflict appears to be a
  shared string in `categories`, resolved by `priority` (Oasis 1, DryLake/lava 2,
  coastal and mountain 5, Cavern 10), with `overrideCategories` letting a mutator claim
  a different category — every coastal mutator declares `overrideCategories: Mountain`
  so it beats plain `Mountain`. The resolving method body was **not** read.
- ⚠️ Whether `preventsLandmarks` stops a mutator landing on a tile that already has a
  landmark, or the reverse, is untested — and it decides whether our order-660
  placements survive the order-700 roll.
- **The Sarlacc is designed twice.** `research/Jawa/rimworld_sarlacc_encounter_current_design.md`
  specifies a bespoke C# encounter controller, while `sw_SarlaccLair` already ships as a
  landmark with `extraGenSteps: sw_SarlaccPit`. 🔑 **v1 takes the mod's landmark**; the
  bespoke encounter is v2 and belongs in `design/V2_DREAMS.md`, not in a queue.

