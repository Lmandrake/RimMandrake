> 🔴 **CORRECTED 2026-08-23 by the owner — read `PAINT_UNDER_MAP_DESTROYS_GAME_1` before
> acting on anything below about painting under a live map.** His words: *"painting under
> a player colony is actually fine to do... it just destroys the player colony. So you must
> create a new one... let's please not record that we cannot paint into an existing game."*
> ⇒ Losing the COLONY is real and expected. "The game becomes unstable / cannot make a new
> colony / the UI breaks" is ONE unreproduced session and he believes it is false. ⛔ Do not
> cite this file as evidence that painting into an existing game is impossible.

<!-- status: live -->
# ASH'KARR — THE SUNDERED · the world definition

> ✅ **THE MAP IS ADOPTED, AND AUTHORING IS OPEN AGAIN — owner, 2026-08-22.** Verbatim, after
> looking at the four-globe sheet: *"That world, upon examination, really isn't very bad at all…
> we're thinking of trying to adopt it."* ⇒ **Ash'karr as it stands IS the v1 planet**, and work
> on it continues: continuity repairs, landmarks, named places, settlements, terrain detail.
>
> ⛔ **This REPLACES the 2026-08-21 freeze banner**, which said the opposite and is struck. The
> freeze lasted one evening and did its job — it stopped a redraft nobody wanted.
> ⚠️ **What did NOT come back:** re-running `ashkarr_paint.py` to regenerate the bundle, the
> reference-match harness (`refmatch.py` stays cancelled), and worldgen, which is out of every
> version and always was. **The map is edited DIRECTLY, one map, in place** — that is the whole
> method, per `the_one_map.md`.
> 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` stands as history, not as a plan.
> Ruling: `WORLD_ADOPTED_AUTHORING_OPEN_1` · supersedes `WORLD_FROZEN_RETHINK_PLANET_1`.


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

### Water — 5.19% liquid, 6.46% counting ice

🔴 **RE-MEASURED 2026-08-22/23. `Ocean` 823 + `Lake` 312 = 1,135 liquid tiles = 5.19%.**
Counting the third water biome `SeaIce` (277), 1,412 tiles = **6.46%**. Which figure applies
depends on the question: **liquid for hydrology, incl-ice for "how much of this planet was
ocean".** Canon: `infrastructure/state/canon.yml > planet.water_pct`.

⛔ **~~8.14% / 1,780 tiles~~ is DEAD** — it counted `Ocean` at 1,468, before the owner's ruling of
2026-08-22 13:04 to *"shrink the meridian water bodies to around half their current size"* and
before the sub-freezing meridian ocean turned to ice rather than drying. There IS now a third
water biome, which this paragraph used to deny.
⛔ **Do not read water from `_meta.json`** — it is a build output of an older pass and still says
8.14. ⚠️ `IceSheet` (80 tiles) is LAND ice and is NOT water: its `water` column is 0 on all 80.
✅ The check that catches all of this: water column = 1,412, `Ocean+Lake+SeaIce` = 1,412, and
elevation ≤ 0 = 1,412 — three routes, one number.
| name | centre | radius | water level | character |
|---|---|---|---|---|
| **Scald** | (35, 185) | 10.5 | ⛔ ~~**perched, ~1410 m**~~ → **−30 m, at sea level** | ⭐ a crater lake, **the one shape ruled round**. 🔴 **It no longer spills: it is a terminal pan.** See the note below |
| **Twilight Sea** | (91, 170) | 22.0 | 0 m, sink | moldy |
| **Grey Sea** | (92, 8) | 16.5 | 0 m, sink | salt-encrusted, shrinking |
| Umbra Trap | (158, 62) | 19.5 | — | holds **ammonia**, not water → Ammonia Flats |

🔴 Water was cut to **a third** of the old ~~22–28%~~ spec (owner, 2026-08-18) — the
arithmetic target was **~8.6%** and the painted result is **8.14%**. The west
(Twilight) side is deliberately wetter than the east (Grey).

### Ranges — a ridge is a LINE, so it inherits the line's shape
| name | anchors (arc, bear) | crest |
|---|---|---|
| **Scald Spine** | ring at (35,185), r 15.5, **notched** | 2050 m |
| **The Ashteeth** | (21.5,116) (23.5,142) (24.5,168) (24,203) (22,230) (19.5,254) | 1450 m |
| **Fall Line** | (26,352) (34,357) (43,2) (52,6) (61,9) | 780 m |
| **Dew Horn** | (58,148) (64,162) (67,178) (63,196) (57,210) | 1850 m |
| **Ashfall Range** | (56,338) (63,352) (66,8) (61,24) | 1700 m |
| **Twilight Crags** | (104,210) (110,186) (108,160) (114,134) | 900 m |
| **Gray Crags** | (106,340) (112,12) (109,42) (116,68) | 820 m |
| **South Crags** | (118,250) (127,272) (131,300) (124,322) | 760 m |

⛔ Never one spine — **many ranges, dotted with volcanoes**.

### Troughs and lows
**Salt** (34,288)→(71,320) · **The Ember Sink** (36,96)→(68,74) ·
**Dew Belt** (38,184)→(89,180) · **the Scald Gate** (49,180)→(39,184), the breach.

### Regions
Anvil (arc<20, flat-topped substellar plateau) · Dune Sea (20–40) ·
**Rust Cathedral** (arc<12.5, bear within 118° of 40 — mechanoids, permanently at
war) · **Scorch** (12.5–17, broken arcs) · Pyrelands · Nightspill ·
Sunreach · The Ash Verge · The Long Dark · **Umbra** (>152) ·
Ammonia Flats · Salt Gate (the deltas).

## 4. Hydrology — ruled, and it is the heart of the map

1. **Rain condenses at ALTITUDE and on the terminator seam**, never on the nightside;
   moist air is dragged sunward off the terminator and wrung out climbing the ranges,
   so a range rains on its **terminator-facing flank** and the substellar plateau is
   the rain shadow.
2. ⭐ **Scald is the planet's water source and its river is the driving system.**
   It is a hot lake in the hottest place, so it evaporates hard, the vapour rains out
   on its own Spine, and the whole catchment leaves through **one notch**. The outflow
   carries **~32,000** units of flow — an order of magnitude more than anything else.
   ⛔ ~~🔴 A lake below sea level cannot emit anything; that is why the Scald is perched.~~

   🔴 **SUPERSEDED 2026-08-21 BY AN OWNER RULING — the Scald is at −30 m and the doctrine
   above is what changed, not the map.** `SCALD_WATER_RULING_1` took option 2 of three and
   `bd5dad0` applied it: all 312 tiles dropped from +1411 m to −30 m. The reason was
   mechanical, not aesthetic — `SurfaceTile.WaterCovered => elevation <= 0f`, so a lake
   perched above sea level **was not counted as water by the engine at all**, and it also
   manufactured 32 false cliffs where a wall of water stood a kilometre above its own
   shoreline. Verified after: water measures 1,780 tiles = **8.14%**, matching
   `canon.yml > planet.water_pct`, and `Cliffs` fell 121 → 104.
   ⇒ **The consequence is real and is accepted:** eight rivers now END in the Scald and
   none leaves it. It is a terminal evaporation pan, not the planet's water source.
   ⚠️ Two independent reviews on 2026-08-22 flagged the map for contradicting this
   paragraph. They were reading a stale paragraph — which is exactly why it is corrected
   here rather than in a commit message nobody will find.
   🔴 **CORRECTED 2026-08-25 BY LIVE MEASUREMENT:** this paragraph and the table above
   both say **−30 m**; `jawa/world_tile_get` reads **−350 m on all 312 Scald tiles** on
   the live planet. The map's elevation was NOT changed to match — this is a doc fix
   only, recording what is actually loaded.
3. **Rivers evaporate as they go.** Loss per tile is brutal in the deep waste and mild
   in the crater basin. Without this every stream that starts anywhere arrives
   somewhere and the map fills with rivers no climate could feed.
7. 🔴 **NO RIVER MAY EXIST ON THE TERMINATOR — owner, 2026-08-22 13:04.** Verbatim:
   *"There should not be rivers on the terminator."* ✅ **The map already complies:** the
   highest arc carrying a river anywhere is **71.52**, and there are **zero** river tiles at
   arc > 74. This is written down so a later hydrology pass does not "repair" the dry
   meridian by feeding it. The meridian's green is fungal and gathers its water from the
   air (§5), so it needs no river and must not be given one.

8. 🔴 **THE MERIDIAN WATER BODIES SHRINK TO ~HALF — owner, 2026-08-22 13:04**, and the Grey
   Sea gets a desiccation halo. Verbatim: *"I would like to shrink the meridian water bodies
   to around half their current size. Around the gray sea I would like there to be some small
   patchy bits of water dotted around as though low-lying regions were still flooded with
   brine while it slowly dessicates away, like the Dead Sea."*
   ⇒ Grey Sea — (92, 8), 0 m sink, already logged *"salt-encrusted, shrinking"* — is the
   subject. **Halving it and scattering brine remnants is the same gesture as the label it
   already carries.** Carried by `MERIDIAN_WATER_HALVED_1` and `GREY_SEA_BRINE_PATCHES_1`.
   ⚠️ **Water is a canon figure** (`canon.yml > planet.water_pct`, 8.14% / 1,780 tiles) and
   this pass moves it. Re-measure and update canon in the same change, or the next audit
   reports a defect that is actually this ruling.

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
   terminus instead. Twilight Sea, the Grey Sea and the Scald are therefore
   hydrologically **separate**; nothing flows between them.
   Currently **235 termini, ~1,120 tiles of dead salt plain, 3 hypersaline pools**.
7. **Dayside only.** Nothing feeds the nightside; there, water is locked as ice.

## 5. Vegetation zonation — owner, 2026-08-19

> *"the rivers should be through vicious jungles, then those are bracketed by lesser
> jungles/marshes, then Pyrelands, then desert in the general case (variation by
> location of course)."*

🔴 **CORRECTED 2026-08-22 — the meridian column of this table is impossible as written, and
the realised map is right where the table was wrong.** **Every river on Ash'karr is dayside:
the highest arc carrying a river is 71.52, and there are ZERO river tiles at arc > 74.** So
"on the river / meridian" describes a place that does not exist. Measured: `AB_MycoticJungle`
1,874 of 1,939 tiles at arc > 82, `PoisonForest` 575 of 604, `BMT_FungalForest` 394 of 425 —
**none of them within three tile-hops of any river, and correctly so.**
⇒ **The meridian green is NOT river jungle. It is the mycoid belt**, and this section's own
closing line already says so: *"the meridian gets mycoid and poison forest. Two greens that
mean different things."* The table contradicted it.

✅ **The dayside rule is obeyed exactly.** Owner, 2026-08-22 12:52: jungle *"ABSOLUTELY
belongs on a desert world but only adjacent to steaming evaporating rivers."*
`AB_FeraliskInfestedJungle` — 534 tiles, 100% dayside — has **222 tiles on a river, 261 one
hop out, 51 two hops out and NOT ONE beyond that.**

✅ **ANSWERED BY THE OWNER, 2026-08-22 13:04 — the rule does NOT bind the meridian, and no
tile moves.** Verbatim: *"mycoid is watered by terminator drift processes & efficient
atmospheric moisture gathering by the fungus, NOT by rain or steaming rivers. There should
not be rivers on the terminator."*

⇒ 🔑 **The mycoid belt has its OWN hydrology and it is not fluvial.** The fungus gathers
moisture from the air; the terminator drift feeds it. **Do not measure meridian green against
distance-to-water — that metric does not apply to it**, and doing so produced a false "93% of
jungle violates the ruling" that would have re-authored 2,968 tiles.
⛔ **And do not "fix" the meridian by giving it rivers.** Rivers on the terminator are now
forbidden outright — see §4 rule 7.

| band | dayside | meridian (arc > 82) |
|---|---|---|
| **on the river** | `AB_FeraliskInfestedJungle` — vicious jungle | ⛔ **n/a — no meridian river exists** |
| **the meridian equivalent, river-independent** | — | `AB_MycoticJungle` · `PoisonForest` · `BMT_FungalForest` |
| **bracketing it** | `AB_MiasmicMangrove` · `COMIGO_GreaterSwamp_Tropical` · `ZBiome_DesertOasis` | `PoisonForest` |
| **then** | **Pyrelands** — `ZBiome_Grasslands`, whose label is literally *"stormy savanna"* — with `AB_TarPits` interspersed | — (Pyrelands are dayside only) |
| **then** | desert | — |

🔑 **The bands scale with the river.** A creek gets one tile of green; the Scald's trunk
gets a corridor. Flat bands ate the vast desert the owner asked to keep.
🔴 **Pyrelands are a narrow bracket, not a belt** — owner, 2026-08-19: *"Too much
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
`ExtremeDesert` 16.36 (3,578) · `AridShrubland` 10.98 (2,401) · `Desert` 9.82 (2,147) ·
`AB_MycoticJungle` 8.87 (1,939) · `Wasteland` 7.87 (1,721, the salt plains) ·
`Ocean` 6.71 (1,468) · `PoisonForest` 2.76 (604) · `AB_PropaneLakes` 2.53 (554) ·
`ZBiome_Badlands` 2.50 (546) · `AB_FeraliskInfestedJungle` 2.44 (534) ·
`BMT_FungalForest` 1.94 (425) · `Lake` 1.43 (312) · `AB_MechanoidIntrusion` 1.08 (236) ·
`ZBiome_Grasslands` 1.07 (233) · `ZBiome_DesertOasis` 1.04 (227) ·
`BMT_CrystalCaverns` 0.58 (127) · `AB_GelatinousSuperorganism` 0.44 (96) ·
`Scarlands` 0.41 (90) · `AB_MiasmicMangrove` 0.30 (65) · `AB_TarPits` 0.26 (57) ·
`AB_PyroclasticConflagration` 0.14 (31) · `Volcano` 0.11 (23) · `LavaField` 0.07 (15) ·
`AB_OcularForest` 0.01 (3).
**25 distinct biomes are painted**, out of the 36 defs that survived the owner's cut —
a def can survive the cut and appear on zero tiles. ⚠️ **Was 24 until 2026-08-21**, when
`AB_OcularForest` was painted on the three Ashfall Range summits under
`OCULAR_FOREST_SUMMITS_1`; those three tiles came out of `ExtremeDesert`, 3,581 → 3,578.

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
- ⛔ Blacklisted and not used: ~~`SeaIce`, `IceSheet`,~~ `Tundra`, `TropicalRainforest`,
  `Savanna` (the Advanced Biomes one), and the rest of the 29-entry list.

  > 🔴 **CORRECTED 2026-08-23 — `SeaIce` and `IceSheet` are BOTH on the planet** and have
  > been since the nightside pass. Measured: **`SeaIce` 277 tiles** (the frozen meridian
  > water, `Twilight Sea` 203 + `Grey Sea` 74) and **`IceSheet` 80** (the ancient-ice pools
  > in `Deadstone`). They were unblacklisted deliberately; this line was never told.

- 🌊 **The meridian coast, authored 2026-08-23** (`ashkarr_shore_and_ice.py`), on the
  owner's ruling *"more variety in the deserts… some arid scrubland against the ocean
  waters… make the frozen ice not have a hard vertical line at the terminator."*
  - **The drained Twilight/Grey Sea floor is zoned by distance to the water that
    survived**, not left as one biome. 369 tiles: **170 `AridShrubland`** against the
    water, **185 `Desert`** one step in, **14 `ExtremeDesert`** left as deep playa. The
    170 shrubland tiles give up their `VEE_SaltPlains` mutator — a salt plain with scrub
    standing on it is a contradiction.
  - **The ice margin interleaves with open water over ~14.5° of arc** instead of ending on
    a line. Before: `Ocean` reached arc 101.51 and `SeaIce` began at 101.64 — a 0.13° gap,
    zero overlap, every water tile freezing at one value. 🔑 The margin is driven by
    **coast proximity**, because real fast ice forms first in sheltered shallow water and
    last in the open — not by noise. Ice total is held at exactly 277: the shape moved,
    the amount did not. Ice masses went 3 → 15 with the largest two at 169 and 91, so it
    is fingers and floes rather than speckle.

## 6b. 🔴 RAIN — the rule, and the one number that enforces it

**Owner, 2026-08-19:** *"Ban rainfall: v1 (but might still happen on highly mountainous
terrain!)"* The full ruling and its corrections are in
`infrastructure/state/items/D-V2-RAIN.md`. What a reader of THIS file needs:

🔑 **The lever is `rain_mm` in the tile CSV, not the biome weather lists.** Every rain
`WeatherDef` in the game carries a `commonalityRainfallFactor` curve that starts at
**`(0, 0)`** and is evaluated **per tile** on `Tile.rainfall`
(`WeatherDecider.cs:191`). ⇒ **at `rain_mm = 0` a rain weather's commonality is multiplied
by exactly zero and it can never be selected**, on any biome, without patching anything.

⚠️ **18 mm is not 0** — this is *why* the ban below had to zero the column rather than lower
it. As measured on 2026-08-20, 80.4% of the map sat at ≤49 mm, which suppresses rain by ~98.6% —
*rare*, not *banned*. And `WeatherDecider.cs:185` multiplies rain commonality by **15**
during a large fire, so the residue surfaces exactly when the player is watching a fire.

⛔ **`rain_mm` has no other runtime consumer.** Re-verified 2026-08-21: nothing reads it for
plant growth, fertility or yield. `WorldGenStep_Rivers.cs:131` sums it into river flow, but
that is worldgen and our `river_flow` column is authored — **do not "fix" river flow after
zeroing rainfall.**

🔴 **The measured defect, 2026-08-21.** 596 tiles carried exactly **1668 mm**. Only 271 were
`AB_FeraliskInfestedJungle`; the other 325 were badlands, extreme desert, oases, grasslands,
**31 tiles of `AB_PyroclasticConflagration` and 23 of `Volcano`** — and **235 of them were in
Dune Sea.** Of the 937 tiles at ≥600 mm, **433 were not mountainous at all** (median
elevation 696 m).

✅ **DONE, 2026-08-21 — `RAIN_DRY_THE_LOWLANDS_1`.** `rain_mm` was set to **0** on
**20,113** rows of `world/ASHKARR_WORLDMAP_tiles.csv`, everywhere except:

```
KEEP rain WHERE ( hilliness >= 4 AND biome NOT IN {Volcano, LavaField,
                  AB_PyroclasticConflagration, Scarlands, AB_TarPits} )
               OR biome == AB_FeraliskInfestedJungle
```

**1,759 tiles keep rain** — 534 `AB_FeraliskInfestedJungle` (271 of them still at 1668 mm)
and 1,225 non-volcanic mountain across 15 other biomes. **Zero** tiles of `Volcano`,
`LavaField`, `AB_PyroclasticConflagration`, `Scarlands` or `AB_TarPits` carry any rain.
Only `rain_mm` changed; all 21,872 rows and every other column are byte-identical.
⚠️ **The 18 mm floor is gone**: planet-wide `rain_mm` is now min **0**, median **0**,
max 1668; across the 1,759 wet tiles it is min 18, median 69, max 1668.
⚠️ **This also removes SNOW**, which is wanted — `SnowGentle`/`SnowHard` carry the same
curve shape and `Desert`/`AridShrubland` listed them at commonality 4.

---

## 6c. 🔴 TWO THREAT CLASSES, AND THEY ARE NOT THE SAME — owner, 2026-08-22

> ⭐ **CLARIFIED AND PLACED, owner 2026-08-23 — read this before the 08-22 quote below.**
> *"as we go from hot to cold over the terminator, we pass through the mycoid layer, then pass
> into the horror wastes … and only when it becomes truly cold do the horror wastes peter out
> and go into the truly alien methane, ethane, ice as a mineral type regimes. I hadn't intended
> horror wastes to be in the deepest cold."*
>
> 🔑 **`HorrorWastes` is a BAND in the transition, not a polar cap.** The 08-22 phrase *"adapted
> to the extreme cold"* was once read as *the deepest cold* and the warm half of the biome was
> deleted for it (commit `0ccf44fe`). **That reading was wrong and is reversed.**

**THE NIGHTSIDE STACK, hot to cold — this is the authored order and biomes must not interleave:**

| layer | biome | tiles | range |
|---|---|---|---|
| mycoid | `AB_MycoticJungle` · `BMT_FungalForest` | 1,939 · 425 | fades out around −31…−39 °C |
| crags | `AB_RockyCrags` | **1,118** | **−30 … −0.0 °C** |
| **the wastes** | **`HorrorWastes`** | **1,686** | **−55 … −30 °C** |
| alien chemistry | `AB_PropaneLakes` (basins) · `BMT_CrystalCaverns` (highlands) | 1,584 · 577 | below −55 °C |

⭐ **This fixed a second defect for free.** `AB_RockyCrags` was **3,816 tiles spanning −82.0 to
−0.0 °C** — the biggest biome on the planet and not a habitat at all, but a band running from
deep nightside to the terminator, so casting it put a lizard and a snow-thing on one creature
list. It is now a coherent −30 … 0 °C place.

⚠️ **Do not "restore" crags to the deep cold, and do not re-scatter the wastes as pockets.**
The layering is the ruling. The surgical script that made it, and may be re-run safely, is
`src/RimMandrake/Utils/ashkarr_layer_nightside.py`; the tiles CSV is FROZEN and must not be
repainted.


**Verbatim:** *"HorrorWastes should be on the night-side where the ancient bioweapons have
adapted to the extreme cold and produced utterly hostile lifeforms. Wasteland (and others)
are instead contaminated by radiation and more conventional poisoning, as is the
mechanoidintrusion layer. Different threats."*

🔑 **The planet carries two separate legacies of the old war, and a reader must not merge
them.** They look alike from orbit and mean opposite things on the ground.

| | **BIOWEAPON — engineered life, still alive** | **CONTAMINATION — poisoned ground** |
|---|---|---|
| what it is | ancient bioweapons that *adapted*, and are now utterly hostile lifeforms | radiation and conventional poisoning; the weapon was used and left |
| biomes | `HorrorWastes` *(nightside — see below)* · `AB_GelatinousSuperorganism` · `AB_OcularForest` · `Scarlands` | `Wasteland` · `AB_MechanoidIntrusion` |
| the danger | **the wildlife** | **the ground, the air, the water** |
| anomaly entities | ✅ **may be cast here** | ⛔ **may not** |

⛔ **Do not extend the bioweapon class by analogy.** `AB_MycoticJungle` (1,939 tiles),
`AB_FeraliskInfestedJungle` (534) and `PoisonForest` (604) all *read* as infested and are
**not** on the bioweapon list. The owner named four; four is the list.

### 🔴 `HorrorWastes` is not on the map yet, and it goes just PAST the terminator

> 🔴 **SUPERSEDED 2026-08-23 by DECIDE — it IS on the map, and this heading is the last thing
> here that is still true in spirit.** `HorrorWastes` holds **468 tiles**, −74.9 … −33.9 °C,
> median −49.3, arc 125–171, elevation median 753 m — scattered nightside pockets in
> `Deadstone` (346), `Umbra` (65) and `Ammonia Flats` (57), not the contiguous band this
> section proposed. **Do not resize it.**
>
> ⚠️ **And it briefly held 807.** On 2026-08-23 00:16 the owner ruled *"we will use
> HorrorWastes instead of RockyCrags for any tile above 0C"* (`eb7da875`) — a cleanup of
> `AB_RockyCrags`, whose warm end read wrong at +19.8 °C. Correctly applied, it also gave
> `HorrorWastes` 339 tiles at 0.1 … 19.8 °C, so the biome became **two places 20 °C apart
> with no tile in the gap** — `AB_RockyCrags`' own hundred-degree-span defect inherited whole.
>
> 🔑 **DECIDE's ruling: the warm 339 went to `Desert`, and the cold 468 keep the name.** Both
> owner rulings survive — the warm tiles left `AB_RockyCrags` (his 00:16 instruction) *and*
> `HorrorWastes` is cold (his 2026-08-22 instruction). `HorrorWastes` is **bioweapon class**
> per the table above; a Junker scavenging outpost cannot sit on an active bioweapon site, and
> two did — `Cryohaul` and `Ammonia Landing`, both sited as `AB_RockyCrags` and both now
> `Desert` again. `Desert` was not chosen by taste: it already spans −15.0 … +62.4 °C across
> arc 14–115 and **already held 1,324 land tiles in the same 0–20 °C band**, so nothing new is
> asserted about the planet and no def changes. Pass:
> `src/RimMandrake/Utils/ashkarr_horror_is_one_place.py`.
>
> ⛔ **What is still owed is the SHELL, not tiles.** The shipped `HorrorWastes` def was
> authored for the warm band it no longer holds — `terrainsByFertility` `Sand`/`Soil`/
> `SoilRich`, one `wildPlants` entry (`Plant_Agave`), `plantDensity` 0.5, `animalDensity` 3.6.
> All of it reads wrong at −49 °C. Carried by `HORROR_WASTES_ON_NIGHTSIDE_1`.

> 🔴 **OWNER, 2026-08-22, and this NARROWS the placement below — read it first.** Verbatim:
> *"Actually I think HorrorWastes should live closer to the frozen side of the terminator,
> agreed taken from RockyCrags, as that is where the bioweapon comes from. The coldest area
> should have only the MOST alien forms of life, nothing recognizable really."*
>
> ⇒ **Not the deep nightside.** `HorrorWastes` belongs in the **frozen band just past the
> terminator** — the warm end of the cold — because that is where the bioweapon came from and
> where an adapted, still-recognisable horror would live.
> ⛔ The earlier proposal of **arc ≥ 140** is SUPERSEDED and must not be built.
>
> ⚠️ **The figure `arc 100–130` is superseded by a TEMPERATURE band, 2026-08-23 — the intent is
> unchanged.** The owner re-ruled it as a sequence: *"we pass through the mycoid layer, then pass
> into the horror wastes… and only when it becomes truly cold do the horror wastes peter out."*
> Built as **−55 … −30 °C** (1,686 tiles, arc 124–144). ⇒ Arc could not express it: `arc 100–130`
> overlaps the mycoid layer, whose own p25 is **−31.4 °C**, and would put the wastes *inside* the
> layer they are supposed to come after. **Temperature orders the stack; arc only approximated it.**
> ✅ **This doc was RIGHT and the build was wrong for a day.** Commit `0ccf44fe` deleted the warm
> half of `HorrorWastes` as *"never his ruling"* while this paragraph already said the opposite.
> Anyone reconciling the two: **this paragraph wins.**
>
> 🔑 **And the deep nightside is now SPOKEN FOR, as a separate rule.** Beyond that band —
> the coldest ground, arc ≥ 150, −82…−67 °C — carries **only the most alien life, nothing
> recognisable**. That is a casting constraint on `BIOME_CREATURE_CAST_1`, not merely a
> biome boundary: whatever biome holds the coldest tiles, no familiar animal is cast there.
> ⚠️ It is still `AB_RockyCrags` after this carve, so RockyCrags' own cast is now two
> different jobs at its two ends.

**Measured 2026-08-22:** `HorrorWastes` (label *"horror wastes"*, mod *Horrors (Continued)*)
is installed and loaded and holds **ZERO tiles**. The deep nightside it belongs on is
currently almost all `AB_RockyCrags`:

| band | tiles | median temp | dominant biome |
|---|---|---|---|
| arc ≥ 120 | 5,481 | −48 °C | `AB_RockyCrags` 3,387 |
| arc ≥ 130 | 3,916 | −56 °C | `AB_RockyCrags` 2,828 |
| coldest 800 (arc 150–179) | 800 | −82…−67 °C | `AB_RockyCrags` 687 |

⭐ **Carving `HorrorWastes` off `AB_RockyCrags` fixes a second
problem at the same time.** `AB_RockyCrags` currently spans **−82 °C to +19.8 °C** across
4,703 tiles — it is a *band*, not a habitat, and casting it as one creature list would put a
lizard and a snow-thing on the same ground. Splitting its coldest extent off gives both
biomes a coherent thermal range. Carried by `HORROR_WASTES_ON_NIGHTSIDE_1`.

## 7. Factions — 120 settlements

> 📌 **Corrected 2026-08-22: this section said 72.** The map has **120**, across the same
> 12 factions. Homestead Defense League 13 → 37 and Hutt Cartel 8 → 19 on the owner's
> ruling that *"the moisture farmers could definitely be all over the place"*; Free Droid
> Enclaves 3 → 12 and Ascendant Helix 3 → 7 on his later go-ahead. The authoritative count
> is `world/ASHKARR_WORLDMAP_settlements.csv`, and `_meta.json` is regenerated from it.

Counts from `tidally_locked_world.md`'s arc-aware table, which **supersedes**
`faction_world_spec.md` §4 (still written in latitude bands, never rewritten).
🔑 **Placement is lore, not habitability** — siting by comfort puts everything on the
terminator. 🔑 **Small story-critical zones fill first**, or they starve.

| faction | defName | n | where, and why |
|---|---|---|---|
| The Galactic Empire | `Empire` | 3 | the seat/spaceport on the plateau rim; **the Scald Gate**; **the Fall Line pass** — choke points. 🔴 **RULED 2026-08-23, owner: "Only three, as I requested, not a gap."** The other ~7–8 Imperial holdings are ORBITAL and are not world tiles (`faction_roster_v2.md:761`); this is no longer an inference |
| Hutt Cartel | `Jawa_HuttCartel` | 17 | 🔴 **RULED 2026-08-24, owner: the oasis rule binds the PALACES only.** The **palaces** are the greater Hutts and each sits **beside** a near-desert oasis, never on it. ⚠️ **There were 8; the owner cut *Bloatu the Ninth's* and *Zeddo the Patient's* on 2026-08-24, leaving 6** — *"you can raid the well without besieging the town"*. The other **11 — the tolls, markets, kennels, waystations, vaults, the casino, the spicehouse, the skimhouse — hold no water at all**, and that is the point: a lesser Hutt who cannot own a well sells a SERVICE instead. ⚠️ *Mokka the Unpaid's Palace* is the one palace off a well; the name is now canon for why |
| Homestead Defense League | `OutlanderCivil` | 33 | the arable margin of the terminator; stores water, has no source |
| Deep Desert Tribes | `TribeCivil` | 9 | 🔴 **RULED 2026-08-24, owner: *"dwell within the sands only, very far from any other settlement and each other… they prefer the deep desert locations and are very private."*** Re-scattered by farthest-point placement across `Desert`/`ExtremeDesert` at arc 24–39 and **51–60 °C**, every one beyond a 9-hex search for water. **Nearest two tribes went 5.2° → 14.6° apart**, nearest tribe-to-anyone 12.5° → 14.6°. ⛔ Distance alone is not the rule — an earlier pass scattered them to −13.8 °C on the cold side, and a Tusken at −13.8 °C is not a Tusken. Canyons, caves, isolated ridges — **never a water tile**. 🔴 **RULED 2026-08-24, owner: "they do not build roads"** — every road that led to a Tusken holding was removed from the map (91 edges, spurs pruned back to their junctions). ⛔ Do not re-run an MST that reconnects them; a Tusken settlement is reached across open sand or not at all |
| Jawa Trade Moot | `Jawa_IndigenousTribes` | 4 | crawler **circuit** nodes; one anchored on the mine the sandcrawlers were stolen from |
| the Junkers | `Jawa_Junkers` | 5 | 🔴 owner 2026-08-18: past the terminator on the **warm downwind flank**, plus the **old mining fields**. The docs only ever said *"wreck fields, wherever things fell"* — this is a new ruling |
| Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | 5 | **two clusters**: the ore seams, and the plateau beside the Rust Cathedral |
| Deepwater Compact | `Jawa_DeepwaterCompact` | 6 | the seas; **two on the Scald** despite the Empire |
| Wildsteam Clan | `Jawa_WildsteamClan` | 4 | 2 on the Scald's jungles, 1 in the meridian's poison marsh, and ***Sporefall* in the Fever Wood on the road** (owner, 2026-08-24) — tropical swamp at 47 °C, the wettest ground the clan holds |
| Blackstar Company | `Pirate` | 4 | road junctions and ruins; they follow the money |
| Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | 8 — halved around the Cathedral 2026-08-24, see §7d | 🔴 **RULED 2026-08-24, owner.** ⛔ **The one hard rule is DISTANCE FROM ORGANICS — above all from the Empire.** Within that: the **Rust Cathedral is holy to them and they are immune to its pollution and heat**, so the plateau cluster is right and *Second Speaker* now stands on Cathedral ground itself; **volcanic terrain is excellent** and at least one seat belongs on it (*The Free Charge*, moved off the Scald's jungle onto the pyroclastic conflagration above it); and **a few quiet, hidden seats on the dark side are welcome** — *The Trade Socket*, *Vent Nine*, *Coldfire*, *The Cracking Station* stay, and the barren-region ban does not bind them. ✅ Their Geonosian neighbours are the allies they share the Cathedral with, not the organics they avoid |
| Ascendant Helix | `Jawa_AscendantHelix` | 7 | 🔴 **RULED 2026-08-24, owner: the Helix sits where the BIOWEAPON is.** `HorrorWastes`, the mycoid tiles and the poison forests of the terminator host them — *Cold Archive* and *The Revision* in the Horror Wastes, *The Fair Copy* in poison forest, *Specimen Hall* on mycoid, and *The Coil* and *Quiet Lab* moved out of the Homestead belt onto terminator mycoid. ⭐ **One outpost holds the new ocular forest on the Scald's mountainous shore** (*Helix Landing*) — see §7c |
| the Forgotten Arsenal | `Mechanoid` | 0 | hidden; no world-map site, which is the intent |

Every holding's tile and its one-line reason are in `ASHKARR_WORLDMAP_settlements.csv`.

## 7b. ⛔ THERE IS NO CANON START SITE — struck 2026-08-24

🔴 **Owner, 2026-08-24: *"There is no canon start colony for the player yet, strike that
from the lore docs."*** This section used to site THE SETDOWN at tile 2476 / lat −1.028,
lon +56.867 in the Fall Line Barrens, and to hand that lat/lon to the recipe as
`HOME_LATLON` / `HOME_NAME`. **That siting is withdrawn.** Nothing on the map is the
player's home, no doc may name one, and any generator key still carrying those
coordinates is stale rather than authoritative.

⚠️ The reasoning that produced it was not wrong and is not being disowned — a start wants
the map to point somewhere, kin one caravan out, the ship's parts in a second ring, and
water as pressure rather than a resource. **Whoever sites the start next should argue from
those, not inherit an answer.** The habitable ring (arc 40–57, `canon.yml`) is unaffected.

## 7c. ⭐ THE OCULAR FOREST ON THE SCALD SHORE — added 2026-08-24

🔴 **Owner, 2026-08-24: *"Occular forests should added along the mountainous shore of the
Scald, and there should be one Helix outpost there."*** **16 tiles** of `AB_OcularForest`
now break the cooler, outer, mountainous rim of the Scald crater (arc 41–51, 38–43 °C), in
two groves rather than a continuous band, taking only `ZBiome_Badlands` and one strip of
`BiomeCypreJungle` — ⛔ **no oasis tile was converted**, the Scald's seven are the only
fresh water in the hottest country on the planet. *Helix Landing* holds the eastern grove.
⚠️ The three original ocular tiles sit at 22.8 °C; these run 15–20 °C hotter, which is a
deliberate stretch of the biome, not an oversight.

## 7d. ⭐ THE RUST CATHEDRAL IS FLAT, POISONED, AND ENTIRELY THEIRS — 2026-08-24

🔴 **Owner, 2026-08-24.** Three rulings, all applied to the live world:

- ⛔ **No mountains and no hills anywhere in `AB_MechanoidIntrusion`.** All **236 tiles**
  are `Flat`; the 25 that carried hills were levelled. ⭐ Their elevation was already
  606–628 m — the Cathedral was never a range, only labelled as one, so nothing had to be
  dug away. **It is a floor**, and it should read as one.
- ☣️ **The pollution is massive and it bleeds outward.** The 236 intrusion tiles run
  **0.90–1.00**, then a four-ring halo falls **0.66 → 0.46 → 0.30 → 0.18** across 303 more
  tiles, so the poison has an edge that is weather rather than a border. **539 tiles
  total.** ⚠️ **Corrected the same day: this is NOT the only toxic ground on Ash'karr.** A
  measure of the live world found **1,081 tiles already polluted at a median of 0.90**
  before any of today's writes — Desert, ExtremeDesert, `AB_RockyCrags`, Wasteland, mycoid
  and horror wastes, in 300-odd small patches. What the Cathedral now is, is the **largest
  single block by a factor of fifteen**: 1,362 tiles planet-wide sit above 0.5, and the
  biggest connected one is **305 tiles centred on the Cathedral** — 236 the intrusion
  itself, the rest its halo spilling into the Anvil and Scorch. The next largest anywhere
  is 21 tiles, in Sunreach.
- 🤖 **Every Free Droid seat that ringed the intrusion is now INSIDE it.** *Cell Seven*,
  *No Master*, *Vent Forty*, *Vent Twelve*, *The Cracking Yard* and *No Owner* moved off
  the surrounding `ExtremeDesert` and jungle onto Cathedral ground, joining *Second
  Speaker*. **Eight of the twelve Enclaves now stand in the holy poison**, which is only
  possible because they are immune to both it and the heat — the fact that makes the
  Cathedral theirs and nobody else's.
- 🛣️ **Only *No Master* kept a road**, redirected onto its new tile in five hops.
  ⚠️ **CORRECTED 2026-08-25 by CHECK, measured live: it never reached the settlement and it
  never can.** Tile 19350 is `AB_MechanoidIntrusion`, whose biome sets **`allowRoads=false`**,
  so a link written there is stored and drawn as nothing. The road ends at **6486**, one tile
  short in the jungle, and that railhead is the maximum achievable — not a regression to fix.
  The same fact is why the Cathedral can have no road web even if someone wanted one.
  ⛔ **The other five are deliberately unroaded** and the Cathedral has no road web: a
  place organics cannot survive should not be paved for their caravans. Say so if that is
  wrong — reconnecting them is five short paths.

## 7e. THE GREY SEA THINNING AND THE ASHFALL CREEK — 2026-08-24

🔴 **Owner: halve the settlements around the Grey Sea.** Homestead 9 → 5, Trade Moot 6 → 3,
Junkers 7 → 4, and the Free Droid seats on Cathedral ground 7 → 4. **The cut was made on
SPACING, not at random** — every removal was one half of a pair sitting 3.8–4.6° from its own
kin, so what is left reads as scattered holdings rather than a thinned grid. The anchors were
kept: *The Ore Moot*, both Junker stories, and *No Master*, the only droid seat with a road.
The planet went **124 → 108** across the day's cuts.

🔑 **A road does not need a settlement.** The first pass pruned every road touching a removed
holding and severed **12 other settlements** from the net. Corrected: a through-route survives
as a road across open country and only true dead ends are pruned — 7 edges, 0 orphans.

💧 **The Ashfall creek now reaches the Grey Sea.** It fell 1,342 m → 1 m and then simply
stopped, 5.4° short of the water. Three `Creek` links carry it out across tiles at 1 m, laid
**mouth first** because `OverlayRiver` sets `riverDist = max(d, previous + 1)` and the wrong
order gives wrong distances. Rivers reaching no sea: **9 → 8**.

## 8. Roads

🔴 **REWRITTEN 2026-08-25 by CHECK, against the live planet.** The MST below is what
LAID the roads; it is no longer what they are. Owner: *"I would like them to be less 'laser
like.' Have them meander a bit, following easier terrain, especially seeking shade
opportunities or near water sources... it's ok to have other branches that wander off to
nowhere and simply end."* The old paragraph's ⛔ *"no ruler-straight diagonals"* had never
been achieved: **33% of runs measured sinuosity exactly 1.000** — an MST on a sphere IS a set
of great-circle segments.

**How they are laid now.** The MST still fixes the TOPOLOGY — every junction and every
settlement endpoint is unchanged — and each run between two fixed anchors is re-routed over a
comfort field (broken ground · cooler ground · vegetation · water within reach but not the
channel itself), with a hard per-step ascent cap and detours priced in tiles walked **plus**
metres climbed.

| measured | before | after |
|---|---|---|
| edges / tiles | 891 / 878 | **1247 / 1242** |
| longest straight leg | mean 5.8, max 18 | **mean 2.7, max 9** |
| sinuosity median / p90 | 1.106 / 1.203 | **1.168 / 1.421** |
| water · shade · ruin landmarks ON a road | 15 · 6 · 3 | **45 · 24 · 36** |
| dead ends in open country | 2 | **34** |
| steepest single step | 888 m | **629 m** (12 edges over 300 m, was 24) |
| settlements reached | 71 | **75** |

🔑 **THE PENALTY IS ON HOLDING A BEARING, NOT ON TURNING.** A hex path from A to B spends
the same number of steps whether it runs eight tiles of one direction then five of another or
interleaves the two — the length is identical and only the LOOK differs. A turn penalty buys
the laser; a *straight* penalty buys the organic line for no extra distance at all. That one
inversion is what moved the map; four sweeps of the comfort weight before it returned
byte-identical routes.

⛔ **In barren country there is nothing to steer by, and that is not a bug.** The six
neighbours of a Long Sand tile carry comfort 0.12–0.14 and a median elevation step of 2–6 m,
so a comfort weight there scales every candidate equally. Those roads bend because they go
**via things** — 119 waypoints inserted, 45 of them oases — and where there is no thing to go
via they stay straight, which is what a night trail should be.

### The palette: heat is the story — owner, 2026-08-25

All five RoadDefs carry `movementCostMultiplier: 0.5` **identically** (read live off the
defs), so the class costs the player nothing and says everything. 🔑 **The class is MEASURED
off the finished route, never chosen for it** — a road is a day road because it FOUND shade
and water, so the story cannot disagree with the map.

| def | reads as | rule | edges |
|---|---|---|---|
| `StoneRoad` | **day road** — shaded, watered or simply cool; walkable in the light | mean comfort ≥ 0.40 or mean tmax ≤ 20 °C | 455 |
| `DirtRoad` | **dusk road** — passable, but you will suffer. the ordinary caravan net | everything else | 471 |
| `DirtPath` | **night trail** — crossed only in the dark; nothing grows, nothing shades you | comfort < 0.16 **and** tmax ≥ 45 °C | 284 |
| `AncientAsphaltHighway` | **the Ashfall Road** — laid by people who did not care about shade, which is why it is dead | authored, not classified | 37 |

⭐ **The Ashfall Road.** AncientLaunchSite (4000, Scorch) → AncientQuarry (14470, the Anvil)
→ AncientGarrison (20514, the Kiln): 63 tiles of dead-straight asphalt across 71 °C ground,
routed with the comfort weight at ZERO and the straight penalty OFF. It connects nothing alive
and is **disconnected from the living network entirely** — five separate components. Where the
sand has it, it is gone: a tile is buried when it sits more than 5 m below the mean of its
neighbours, because sand accumulates in hollows and is scoured off rises. 37 of 62 edges
survive, in fragments of 4 to 25 tiles.

⛔ **Two settlements cannot be reached and must not be forced.** *Deepwater Hold* (9451)
stands on a **7-tile island** — measured, its passable component holds 7 tiles and does not
contain the mainland. *Hollow Hive* (8497) sits behind a **1,013 m rim** whose only land
approach is a single step of more than 300 m. Both are terrain facts, not routing failures.

⛔ **Never lay a road that cannot be drawn.** `SurfaceTile.Roads` is a biome-FILTERED view, so
a link on a tile whose biome sets `allowRoads=false` is stored and renders nothing — the map
then shows a road stopping in mid-air for no reason a player can see. The inherited network had
one: two `StoneRoad` edges into *The Cracking Station*, a Free Droid seat standing in
`AB_PropaneLakes`. Pruned; the road now stops short of it, visibly.

**The working scripts are `world/_roads/`** — `field.py` (the comfort field), `route.py` (the
cost model and its three measured mistakes), `waypoint.py` (why a track bends), `compose.py`
(class, spurs, strays, the highway), `finalise.py` (integrity + the undrawable-edge prune),
`report.py` (the before/after table above). `roads_import.csv` is what was written;
`rollback_roads.csv` restores the MST.

## 9. 🔑 Where the map contents live

```
world/ASHKARR_WORLDMAP_tiles.csv        ⭐ THE MAP: 21872 rows —
                                        tile, lat, lon, arc, bearing, elev_m, temp_c,
                                        rain_mm, biome, water, river_flow, region
world/ASHKARR_WORLDMAP_settlements.csv  120 rows (was 72, re-measured 2026-08-23) — faction, name, tile, arc, biome, why
world/ASHKARR_WORLDMAP_links.csv        every river and road edge
world/ASHKARR_WORLDMAP_meta.json        planet, regions, factions, counts
```

The `.rws` savegames and everything under `world/view/` are **not** sources. The
savegames are the old automated-worldgen mess and are being cleaned up; the renders are
pictures of the CSV above.

## 10. Open questions for the owner

1. **The player start is unsited.** ⛔ **REOPENED 2026-08-24** — the 2026-08-19 siting was struck by the owner; see §7b. ~~The Setdown,
   tile 2476.~~
2. ~~The Empire's three seats are choke points by inference.~~ 🔴 **CLOSED 2026-08-23 —
   owner: *"I confirm (A) is correct. Only three, as I requested, not a gap."*** Three is
   deliberate and is not a shortfall to be filled later. 🔑 **The reason is already in the
   roster and should never have read as an inference:** `faction_roster_v2.md:761` sets the
   Empire's target at **3 SURFACE seats**, because ~7–8 of its ~10 holdings are **orbital**
   and are not world tiles at all. The Empire holds this planet from above; the three seats
   on the ground are the spaceport and the two passes that reach it. ⛔ Do not "correct" the
   Empire's count upward against the Homestead's 37 or the Hutts' 19 — those factions live
   here and the Empire is garrisoning a backwater.
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

1. **The player start is unsited.** ⛔ **REOPENED 2026-08-24, owner — see §7b.** ~~The Setdown, tile 2476, arc 56.9 on
   the gray flank. `ExtremeDesert` vs `Desert` is the one call worth a playtest.
2. ~~Region labels collide on the render.~~ **DONE.** The anchor separation was the
   wrong test — what collides is the projected **text box**. `worldview.py` now tests
   pixel boxes and walks a ladder of vertical offsets, and the looser anchor rule
   surfaced names that had been silently dropped (Scorch, Anvil, Pyrelands).
   Settlement names and region names also share **one** box list now; they used to
   declutter only against their own kind, which is why `Ashfall Range` printed
   through `The Claim Jump`. ⚠️ The tradeoff is real and deliberate: with one list, a
   crowded region name can lose its slot entirely rather than overprint. `Scald
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
| **Features 1000** | ⭐ **OVERWRITE.** ~~24~~ → **71 named regions** in `_tiles.csv`, covering **all 21,872 tiles with none left unnamed** (measured on the live stamp, 2026-08-23); vanilla named them at random. 🔑 The FeatureDef is **`WB_MapLabelFeature`** — `world_features_import` defaults to `'Region'`, which **does not exist** and refuses the whole import. |
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

⭐ ~~**`tileFeature` is the one genuinely unauthored piece.** Our 24 region names exist only
as CSV text.~~

> 🔴 **CORRECTED 2026-08-23 — this is AUTHORED, and the count is wrong twice over.**
> Measured off `world/ASHKARR_WORLDMAP_meta.json`: the map carries **71 regions, and all
> 71 already have a `features` record** — `{id, name, tiles, mass, kind, lat, lon,
> drawCenter, maxDrawSizeInTiles}`, i.e. exactly the centroid and angular extent this
> paragraph says are missing. **0 of 71 regions lack one.** The importer exists too:
> `w9_run.py` stage 6 calls `jawa/world_features_import` with
> `featureDef: WB_MapLabelFeature`.
> ⚠️ **What IS still true:** none of it has been carried into a game and read back — that
> is `WORLD_PORT_SURVIVES_BRIDGE_1`, and stage 6 has never run. And `w9_run.py`'s own
> comment still says *"the 23 region labels"*, so the importer's stated scope is 23 against
> a map that has 71. **Check the stage handles all 71 before trusting it.**
> ⇒ The gap is a PROOF gap, not an authoring gap. Do not schedule work to invent region
> features; schedule work to prove the import.

The paragraph below is kept for its API description, which is still correct: A `WorldFeature` is a *runtime object*, not a def:
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

**Our exposure: 1,083 tiles — 5.0% of the planet — are `ExtremeDesert` AND `Flat`.**
⚠️ **Updated 2026-08-24:** this used to read *"and THE SETDOWN IS ONE OF THEM"* and rest its
whole argument on tile 2476. **There is no canon start tile any more (§7b), so the exposure
is now a general one** — whatever tile the start eventually takes, if it is `ExtremeDesert`
and `Flat` and vanilla's Mutators step at order 700 rolls `Dunes` on it, the opening map has
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
| ~~**The Setdown**, one tile adjacent~~ | `Ruins` or `AbandonedColonyOutlander` | ⛔ **UNSITED 2026-08-24 — the start site was struck (§7b), so there is no home tile to sit beside.** The idea survives the siting: the dead gravship's ruin is the campaign's backstory on the map, and it goes one tile from wherever the start lands, never on it — the ship needs 4,057 clear substructure cells. `ashkarr_populate.py:85` still pins it to 2476 and is now stale |
| **Scald Gate** | `Valley` | the one breach in the Spine. No biome list — gated on `minHilliness: Mountainous` only, which the Spine satisfies |
| **The Ore Moot** | `AncientQuarry` | *the mine the sandcrawlers were stolen from.* Mountainous; ore-rich |
| **Sarlacc Ground** | `sw_Sarlacc` | ships in Star Wars Animal Collection; blacklists ice only, `maxHilliness: Mountainous`, and combos onto Dunes/Sandy/Hollow/Chasm/Valley/Cavern — authored for exactly this |
| **Rust Cathedral** | `AncientLaunchSite` / `AncientGarrison` | mechanoid, permanently at war |
| the Scald rim volcanics | `LavaLake` · `LavaCrater` | `LavaField` only — the one volcanic province |
| the salt pans (`Wasteland`) | `DryLake` or `VEE_SaltPlains` | ⚠️ **verify**: `DryLake` whitelists Desert/ExtremeDesert/AridShrubland, and our salt pans are `Wasteland`. It may not be legal there |
| the oases (`ZBiome_DesertOasis`) | `Oasis` | temp range **20–60 °C**; our arc 30–60 band runs 38–58 °C, so it fits — but it does **not** fit sunward of that |
| the deep waste, a few | `AncientHeatVent` | desert-exclusive, and a heat plume on the hottest world in the setting is the right kind of joke |
| the Junkers' fields | `Ruins` · `AbandonedColonyTribal` | wherever things fell |
| **The Kiln**, the five-tile dead core | ✅ **settled 2026-08-23 by the owner with CHECK** — read the landmark bundle for the value | *the Hutt seat the Pykes killed with a parcel their own manifest cleared.* The region is already named for it |

⛔ **Never place:** `Iceberg`, `IceDunes`, `Crevasse`, `FrozenRuins`, `VEE_DetachedIceberg`,
`VEE_IceSpires`, `VEE_GlacialMoraine`, `VEE_PermafrostBasin` (all ice-gated) ·
`VEE_Cenotes` (explicitly blacklists all three deserts) · `VEE_Mangrove`,
`VEE_TemperateGrasslands`, `VEE_CoralReef`, `VEE_BurnedForest` (temperate/wet) ·
`AB_MagmaticQuagmire`, `AB_MutagenicSprings` (need biomes we do not have).
🔑 The coastal shapes — `Bay`, `Cove`, `Fjord`, `Peninsula`, `Harbor`, `CoastalAtoll` —
**are** whitelisted for dry biomes, so they are legal, but only on a tile touching one
of the three waters. They should be rare: this planet is 8.14% water (1,780 of 21,872 tiles).

#### ⭐ THE KILN — the blast is already drawn on the frozen map (owner, 2026-08-23)

> **Owner, verbatim:** *"'The Kiln' was an old Hutt settlement, the most powerful on the planet, but
> they messed with the wrong crime syndicate and ended up with a massive Thermal Detonator released
> in a cargo shipment, taking out the entire area to this day."*

🔑 **Nothing needs to be edited on the map for this to be true**, and that is the whole reason to
record it here. Measured against `world/ASHKARR_WORLDMAP_tiles.csv` (frozen), the **Kiln** region is
**878 tiles**, arc 40–60°, elev 1–776 m, 34–53 °C, and it breaks down as **418 `ExtremeDesert` · 412
`Desert` · 20 `ZBiome_Badlands` · 10 `AridShrubland` · 7 `PoisonForest` · 6 `ZBiome_Grasslands` · 5
`Wasteland`**. Those five `Wasteland` tiles are the entry:

| tile | arc | bearing | elev | temp | hilliness |
|---:|---:|---:|---:|---:|---:|
| 650 | 43.4 | 247.6 | 1 m | 48.3 °C | 1 |
| 6323 | 41.1 | 248.9 | 1 m | 49.5 °C | 1 |
| 11181 | 42.6 | 249.2 | 1 m | 48.7 °C | 1 |
| 11182 | 42.8 | 245.5 | 79 m | 48.2 °C | 2 |
| 11183 | 41.9 | 247.2 | 1 m | 49.0 °C | 1 |

**A contiguous five-tile blob — 2.3° of arc, 3.7° of bearing — of dead flat ground at sea level, the
hottest and lowest in the region, and the ONLY `Wasteland` in 878 tiles that are otherwise sand.**
That is a crater, and it was on the map before the story existed. ⇒ **The Kiln is sited here.** The
detonation is why the region carries the name; §5b's *"the waste is the default state"* is doing the
work, and no tile changes.

🔑 **The map already tells the aftermath too.** There is **no Hutt holding anywhere in the Kiln** —
the Cartel never came back. The only four settlements in the region are Homestead Defense League
moisture farms — **Dryhold** (14351), **Stillwater Farm** (655), **The Sumps** (413) and
**Whistledew** (979) — people who arrived afterwards, farm the edge of it, and do not dig in the
middle.

✅ **The landmark question is CLOSED — the owner settled it with CHECK, 2026-08-23**, and this doc no
longer poses it. What was open: tile 11183 carries `DryLake` while being `Wasteland`, which §13.3's
own table suggests may be illegal, and the blast core had nothing marking it. ⇒ **Whatever now sits on
the core is recorded by that work, not here** — read the landmark bundle rather than this paragraph,
which is deliberately not restating a value it did not measure. 🔑 **The lore never depended on the
answer:** the crater is the ground, not the landmark.

**The faction half of this — why the Cartel has no capital and never will again — is
`faction_roster_v2.md` § 1. Hutt Cartel, "THE KILN".** 🔴 **It was the PYKE SYNDICATE — canon,
owner's ruling 2026-08-23**, and not as an outside attacker: Pykes are **7% of the Hutt Cartel**,
its paid spice handlers, negotiators and officers, so the parcel arrived on a correct manifest
cleared by the people whose job was to clear it. **The Cartel employs them to this day.**

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

### 13.5 🌋 THE SCALD'S MUTATOR LAYERS — written 2026-08-25, three authored passes

The Scald was 312 identical `Lake` tiles carrying only 6 `River` and 2 `RiverDelta`
mutators — nothing else. That emptiness was the defect; three owner-approved passes
zoned it. Written live over the bridge with `jawa/world_mutators_set`, verified tile by
tile with `jawa/world_mutators_get`, no RNG anywhere — every choice is
`h(t) = (t * 2654435761) % 100` against the tile id, so the layout is reproducible from
`world/_scald/scald_plan.json`, never rolled.

**(2) The Boil — heat from below.** The Scald sits inside the planet's only volcanic
province; this is what justifies it evaporating enormously and gives the Deepwater
Compact's seats a reason to hold water nobody can drink.
- `AB_GeothermalHotspots` on all **3** `AB_PyroclasticConflagration` rim tiles (the def
  is biome-locked to that biome plus `BiomeGRimphire`, neither of which is water — so
  it could only ever go on those 3, never on the lake itself).
- `SteamGeysers_Increased` on all **30** lake tiles within 2 hexes of the volcanic rim.
- `VEE_SulfuricLake` on **17** of those 30 nearvolc tiles that carry no river (a
  deterministic ~half).
- Volcanic rim land tiles (12 total: Volcano ×6, `AB_PyroclasticConflagration` ×3,
  `LavaField` ×3) split `VEE_ToxicVents` (**7**) / `VEE_SmokeVents` (**5**).

**(3) The Nine Mouths — make the inflows visible.** Nine rivers die in the Scald and
none used to be visible arriving.
- `RiverDelta` on all 9 mouth tiles (777, 2014, 7791, 11947, 15141, 15173, 17343, 19371,
  19404) — this **displaced** the `River` mutator on each, which is the engine's own
  category-conflict resolution (`AddMutator`), not a defect.
- `Fish_Increased` + `AnimalLife_Increased` on the 9 mouth tiles and on the **13** lake
  tiles immediately adjacent to a mouth (the fan reaching into the water) — the only
  places life exists in this hypersaline basin.
- `VEE_AlluvialFan` was **not used anywhere**: it gates on hilliness Flat plus a
  coastline, and every one of the 9 mouth tiles measures hilliness 4–5 (measured live),
  and no ring tile bordering a mouth measures Flat either. Zero eligible tiles, not an
  oversight.

**(4) The Brine Ladder — zone the water**, by shore distance (`dist` in
`scald_geom.json`):
- **Shallows** (dist 1–2, **132** tiles): `Fish_Increased`.
- **Mid brine** (dist 3–4, **90** tiles): left bare on purpose — the gradient reads
  better with a neutral middle than with a mutator on every tile.
- **Dead heart** (dist 5+, **90** tiles, none of them mouth-fan tiles — the two sets
  never overlapped): `Fish_Decreased` on all 90, plus a lethal ~third (**28** tiles,
  none carrying a river) split `VEE_SulfuricLake` (**14**) / `ToxicLake` (**14**).

`VEE_SulfuricLake` therefore carries **31** tiles total (17 from the Boil + 14 from the
Dead Heart) — the two purposes share one def, one mutator family.

**Tried and dropped: `VEE_MarineSanctuary`.** Its "coastline 1–5 coast sides" gate has
no documented meaning for an inland lake — `World.CoastDirectionAt`, which
`jawa/world_mutators_audit` uses to judge coastal mutators, answers **false** for every
Scald tile because it detects adjacency to *ocean*, not to a lake's own shore. Written
to 2 probe tiles (2941, 15200), committed, and audited with `marineMutators` including
the def name: both came back as offenders and nothing else on the planet did (baseline
`Coast` offenders were already 0), so the layer was rolled back (`action=remove`) rather
than rolled out further. `jawa/world_mutators_audit` reports `offenderCount: 0` after.

**Measured landed vs intended, read back from the live planet, 100% on every def:**
`AB_GeothermalHotspots` 3/3 · `SteamGeysers_Increased` 30/30 · `VEE_SulfuricLake` 31/31 ·
`ToxicLake` 14/14 · `VEE_ToxicVents` 7/7 · `VEE_SmokeVents` 5/5 · `RiverDelta` 9/9 ·
`Fish_Increased` 141/141 (9 mouths + 132 shallow, the 13 fan tiles fall inside the
shallow zone) · `AnimalLife_Increased` 22/22 (9 mouths + 13 fan) · `Fish_Decreased`
90/90.

Working scripts: `world/_scald/plan_scald_mutators.py` (the deterministic tile-list
builder), `world/_scald/apply_scald_mutators.py` (the bridge writer), and
`world/_scald/verify_scald_mutators.py` (the read-back diff). Their docstrings carry the
gate reasoning and the traps hit; `world/_scald/scald_plan.json`,
`scald_apply_report.json` and `scald_verify_report.json` are the frozen record of what
was intended and what landed.

**Gate check against source, after the fact.** A source-level audit of `ToxicLake`
confirmed `biomeWhitelist: {Glowforest, Scarlands}` (not `Lake`) and, separately,
`canSpawnOnRiver: false` as an explicit XML field, not an inference. `Tile.AddMutator`
evidently does not enforce the biome whitelist at all — it is proven live on `Lake`
tiles regardless — but `canSpawnOnRiver: false` is real and this pass already respected
it: every `ToxicLake` tile above was chosen from `deep_no_river`, tiles carrying no
`River`/`RiverDelta` mutator. `Marshy`'s whitelist was confirmed as exactly
`{Grasslands, TemperateForest, Tundra}` (shorter than earlier guessed, not longer) —
moot here since Marshy was never used. `VEE_AlluvialFan`/`VEE_MarineSanctuary`/
`VEE_SulfuricLake`/`VEE_ToxicVents`/`VEE_SmokeVents` could not be located in any XML
source reachable offline (a `VEE_`-prefixed def with no matching mod content on disk) —
their gates stay UNMEASURED by source and are trusted only from the live behaviour
recorded above (the `VEE_MarineSanctuary` probe, the zero-candidate `VEE_AlluvialFan`
check).

---

## Stamping the bundle onto a live planet — measured 2026-08-23 by CHECK

The whole bundle went onto the owner's generated world at `Page_SelectStartingSite`,
before a landing site was picked. **21,872 tiles matched, 0 mismatched, 100.0%**
(`jawa/world_tile_validate`, which reads RAW fields). Order and results:

| step | tool | result |
|---|---|---|
| tiles | `world_tile_import` | 21,872 applied, 0 skipped |
| rivers + roads | `world_links_import` `clearFirst:true` | 293 rivers, 1,373 roads |
| named regions | `world_features_import` **`featureDef: WB_MapLabelFeature`** | 71 created, 21,872 named, 0 unnamed |
| settlements | `world_settlements_import` `clearExisting:true` | 120 placed, 35 generated ones removed |
| mutators | `world_mutators_set` clear, then add per def | 74 defs, 9,717 assignments, 0 failures |
| landmarks | `world_landmarks_set` `forced:true` | 51 defs, 569 tiles, 0 failures |
| commit | `world_commit` | 8 draw-layer steps, 0 failed |

⚠️ **Water came out at 6.46% (1,412 tiles), not the 8.14% this file and `the_one_map.md`
both carried.** The live planet agrees with `_tiles.csv` exactly; the DOCS were stale.

### 🔴 `world_features_import` sizes labels unusably for a 71-region planet

It derives `maxDrawSizeInTiles` from each region's extent. On this bundle that produced
**8.8 → 99.6 tiles, median 28.3** — and a 99.6-tile label on a globe showing ~70 tiles
across is **wider than the planet**. The owner's word was *"WILDLY too large world labels
crowding"*, and they visibly intersected the sphere and overprinted each other.

**The fix, applied and confirmed by looking:** rescale every feature after importing.

```python
# for each feature from jawa/world_features_get:
new = max(5.0, min(16.0, current * 0.30))
jawa/world_features_set {action:'update', featureId:<id>, maxDrawSizeInTiles:new}
# then jawa/world_commit
```
Result: **5.0 / 8.5 / 16.0** min/median/max — labels read cleanly, no clipping, no crowding.

⛔ **This is NOT persisted in the bundle.** There is no label-size column in `_tiles.csv`,
so **a re-import re-breaks it** and this rescale must be re-run every time. Filed as
`FEATURE_LABELS_SIZED_UNUSABLY_1`.

### 🔴 The magenta tiles are missing MOD art, not our bundle and not the stamp

Five tiles render bright magenta. They are exactly the five sarlacc landmarks:

| landmark | tiles | region |
|---|---|---|
| `sw_DeadSarlacc` | 1837, 15623, 20456, 15905 | Glare · Dry Marches · Kiln · Pale Flats |
| `sw_Sarlacc` | 2920 | Dew Belt |

**Star Wars Animal Collection (Continued)** (`mlie.starwarsanimalcollection`, active)
declares both LandmarkDefs pointing at `World/Landmarks/Landmark_DeadSarlacc` and
`Landmark_Sarlacc` — and **ships neither.** The mod has no `Textures/World/Landmarks/`
directory at all and no file matching `*sarlacc*` anywhere in its `Textures/`.

⭐ **Everything else was cleared by measurement, not assumption:** all 17 `VEE_*` landmark
icons are present (`VEE_SulfuricLake.png` included — an early hypothesis that died on the
check), and all three `AB_*` icons are present. Ludeon-expansion landmarks ship inside
`resources.assets` and correctly have no loose PNG.

⇒ Two ways out, both cheap: **drop the 5 landmarks**, or **draw the two textures**
(`generating-rimworld-sprites`). Nothing about the stamp needs redoing either way.

## 14. THE TWILIGHT SEA — five mutator passes stamped, 2026-08-26

The Twilight Sea (604 tiles: 436 `Ocean` + 168 `SeaIce`, arc 63→120, the only place on
Ash'karr where a ship crosses from day into night) got five owner-approved mutator
passes over the live bridge, from `world/_twilight/BRIEF.md`. Scripts, plan and both
report JSONs live in `world/_twilight/`. **Measured counts below are LANDED, read back
from `jawa/world_mutators_get` after `jawa/world_commit` — not the `added` count the
setter reports, which is not proof of anything (see project doctrine).**

| pass | defs landed | count |
|---|---|---|
| 1. The ice margin | `Iceberg` (iceedge tiles, temp −100…0 °C, coast_count 3-5) | 5 |
| | `Fish_Increased` (39 open-water edge tiles ∪ pass-5 shipping lane) | 59 |
| | `AnimalLife_Increased` (39 open-water edge tiles) | 24 |
| | `VEE_GravelBeach` (ice grounding ashore, coast_count 1-6) | 20 |
| 2. Day/night shore | `VEE_SaltPlains` (dayside ring, arid biomes, no river) | 29 |
| | `Oasis` (dayside ring, temp 20-60 °C) | 3 |
| | `SunnyMutator` (dayside ring) | 26 of 44 intended — 18 displaced by `WindyMutator`, same "Weather" category, see below |
| | `WindyMutator` (nightside ring ∪ SeaIce band ∪ dayside arid shore — see pass 3) | 139 |
| | `DryGround`, `IceDunes`, `VEE_DeepSnow` | **0 — measured empty, not a bug** |
| 4. Drowned coast | `VEE_RisingWaters` (flat ring, coast_count 1-5) | 41 of 51 — 10 displaced by `CoastalAtoll`, same category |
| | `CoastalAtoll` (former-seabed ring) | 8 of 9 — 1 displaced by `Bay` |
| | `VEE_LoneIsland` (former-seabed ring) | 5 |
| | `VEE_RelictDelta` | **0 — measured empty**, see below |
| 5. Shipping lane | `VEE_MarineSanctuary` (Ocean near Boilquay/Deepwater Hold) | 15 |
| | `AncientRuins` / `AncientWarehouse` ("islands" = former-seabed ring) | 6 / 5 |
| | `Bay` (ring near Blackstar Field/Hardpan Yard) | 4 |

**Pass 3, the sea fog, was REFUSED as specified in the brief.** `FoggyMutator`'s full,
untruncated `biomeWhitelist` — read directly from
`Defs/Odyssey/TileMutators/TileMutators_Modifiers.xml`, not the live roster's truncated
note — is `BorealForest, ColdBog, TemperateForest, TemperateSwamp, TropicalRainforest,
TropicalSwamp, Grasslands, Glowforest, Scarlands`. **`Ocean` is not in it.** The live
2-tile probe the brief demanded (tiles 18500, 900) reported `success: true` with no
errors regardless — that is NOT evidence, because `Tile.AddMutator` (what
`jawa/world_mutators_set` calls) never calls `TileMutatorDef.IsValidTile` at all; the
write cannot fail on a gate that is never checked. FoggyMutator was removed from both
probe tiles immediately after the probe. Pass 3 shipped as the brief's own specified
fallback: `WindyMutator` on the SeaIce band and the dayside arid shores, folded into
pass 2's `WindyMutator` write above rather than a separate pass.

**Category conflicts (`SunnyMutator`↔`WindyMutator`, `VEE_RisingWaters`↔`CoastalAtoll`↔
`Bay`) are the system working, exactly as the brief warned — not a defect.**
`Tile.AddMutator` displaces an earlier same-category mutator when the new one's priority
ties or wins, so writing several coastal/weather flavours to overlapping tiles in one
session means the LAST family member written is the one that survives on each shared
tile; every displaced tile still carries a sibling from the same family. Confirmed by
direct read-back (e.g. tile 4571 carries `CoastalAtoll` where `VEE_RisingWaters` was
displaced; tile 13411 carries `Bay` where `CoastalAtoll` was displaced).

**Two gates read empty on measurement, not by mistake:**
- `DryGround` / `IceDunes` / `VEE_DeepSnow` need biome `Scarlands`/`BorealForest`/
  `Tundra`/`SeaIce`/`IceSheet`. Ash'karr's nightside ring — measured over all 122
  tiles — is `AridShrubland`/`AB_RockyCrags`/`AB_MycoticJungle`/`Desert`/
  `ZBiome_Badlands`/`AB_TarPits`/`PoisonForest`. The planet's biome assignment is
  coarser than its per-tile temperature field: the night shore is 26 °C colder but was
  never painted a cold biome, so these three defs have no legal home there at all.
- `VEE_RelictDelta` needs `Desert`/`ExtremeDesert`/`AridShrubland`/`Grasslands`/
  `TemperateForest` and Flat hilliness. Every ring tile within 3 hops of the sea's one
  real river mouth (18267, Blackstar Field) is `AB_MiasmicMangrove` or `Wasteland` —
  neither qualifies, so "a dry channel reaching the sea" has no eligible tile near the
  only place a channel could plausibly reach.

🔴 **`jawa/world_mutators_audit` scans the WHOLE PLANET, not the sea you're working on**
— there is no tile-range parameter. The first live run of `apply_twilight_mutators.py`
put `VEE_SaltPlains` into the audit's `marineMutators` list (it is not actually
coastal-gated — its live-roster note is about NOT touching Ocean, the opposite of a
marine check) and flagged 313 pre-existing, unrelated inland `VEE_SaltPlains`
placements across the rest of the planet as "offenders"; the auto-remove loop deleted
48 of them plus 2 pre-existing lake-adjacent `VEE_GravelBeach` tiles elsewhere (the
audit's coastal check only recognises `Ocean` neighbours, never `Lake`). All 50 were
identified from the run's own report and restored live before any further work
continued — see `world/_twilight/twilight_apply_report.json`'s `final_audit_INCIDENT`
block for the full tile list and `world/_twilight/apply_twilight_mutators.py`'s header
for the mechanism. **Never pass a def to `marineMutators` without confirming its OWN
gate actually is a coastSidesRange, and always intersect any reported offender against
your own written tiles before removing anything** — a whole-planet audit is a loaded
gun on a repo four seats share.

**Final state, measured:** `jawa/world_mutators_audit` with `marineMutators` restricted
to the six genuinely coastal-gated defs used here (`Iceberg,VEE_GravelBeach,
VEE_RisingWaters,CoastalAtoll,VEE_LoneIsland,Bay`) and `limit=500` reports
`offenderCount: 13`, **all 13 pre-existing elsewhere on the planet** (biomes like
`Volcano`, `AB_PyroclasticConflagration`, `AB_FeraliskInfestedJungle` — nowhere near
the Twilight Sea) and **none on a tile this session wrote.** The 28
`CoastalIsland`/`Archipelago` landmark tiles placed the same day were excluded from
every candidate pool in every pass, not only the drowned-coast pass the brief called
out by name.
