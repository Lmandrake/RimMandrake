# The Contagion — placement candidates (CONTAGION_BIOME_PLACEMENT_1)

Computed 2026-09-07, offline, against `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles,
30 distinct biomes) — the SAME source `the_contagion.md` §0 cites. **Nothing painted.**
This is the tile list and a preview render for the owner's look, per the item's own gate
("put it to the owner as a rendered worldview before painting") and this repo's
patch-a-curated-artifact rule (diffed to a scratch copy, never touched the committed CSV
or the live game/savegame).

## The rule, as ruled (the_contagion.md's Owed section, 2026-09-06 widening)

> put the Contagion everywhere it reasonably can go, as a world presence — every
> rain-receiving non-green high on the dayside — so long as there is an excuse it is
> sterilized before flowing down. A tall mountain stays its host biome ONLY if it gets no
> rain from the Scald's storms; a peak that rains and stayed clean would seem odd.

Operationalized here as four conditions on a candidate tile, all required:
1. **Dayside**: `arc < 75` (matching the item's own "MEASURED candidate bands" framing;
   Cratercrown itself sits at arc ~48, "mid-dayside").
2. **Non-green**: `biome` not in `{BiomeCypreJungle, AB_FeraliskInfestedJungle,
   ZBiome_DesertOasis}` — the three defNames `the_contagion.md` §230 names as "the green
   below" wanting their own definitions, and hard ban #1 protects. 🔴 **Judgment call,
   flagged**: other green-reading biomes exist on the dayside (`AB_MycoticJungle`,
   `ZBiome_Grasslands`, `BMT_FungalForest`, `COMIGO_GreaterSwamp_Tropical`) that the sheet
   does NOT explicitly name as protected. I excluded only the three explicitly named ones
   — a stricter reading (exclude anything green-looking) would shrink the widened set
   further. Worth the owner's eye on the render.
3. **High**: `elev_m >= 1200` — reusing the sheet's own worked threshold for Ashfall Range
   (35 tiles) and Dew Horn (137 tiles), applied uniformly to every OTHER region as the
   "local peak band" operational proxy. **Except Cratercrown**, see below.
4. **Rains**: `rain_mm > 0` — the widened rule's own instrument, read literally.

## Cratercrown is kept as the sheet's own unconditional core, not re-derived

`the_contagion.md` §0 names Cratercrown's "38 non-green tiles" as *the core* without an
elevation qualifier (unlike Ashfall Range and Dew Horn, both stated with an explicit
`≥1,200 m`). Reproducing "all non-green tiles in the Cratercrown region" against the live
CSV gives exactly 38 (Volcano 18, ZBiome_Badlands 13, LavaField 7) — an exact match to the
sheet's own count, which calibrates this script against a known answer before trusting it
on the wider planet.

🔴 **Found and NOT silently resolved**: applying the widened rain-gate (`rain_mm > 0`)
*inside* Cratercrown's own 38-tile core would drop 25 of them — all 18 Volcano and all 7
LavaField tiles read `rain_mm = 0` in this CSV; only the 13 ZBiome_Badlands tiles show
rain. That contradicts the sheet's own narrative ("a red valley... roofed by a
thunderstorm that has not stopped in a thousand years") for 66% of its own named core.
Likely explanation, not verified: `rain_mm` is vanilla's WORLDGEN-TIME climate estimate
(the R-H1 altitude-rain proxy used to CHOOSE where wet terrain sits), not a readout of the
Contagion's OWN weather table (`Jawa_ScaldDrizzle/Rain/Fog`, already assigned to
`AB_OcularForest` per §0) — once the biome IS Contagion, its own weather assignment
governs actual rain regardless of this column. Under that reading the column is the right
instrument for CHOOSING new territory (no existing biome's weather to lean on yet) but
not for re-litigating already-decided core tiles. **Kept the full 38 unconditionally** on
that reasoning — flagged here explicitly since it is a real interpretive choice, not a
measured fact, and the owner may rule the other way.

## Result: 173 candidate tiles

| source | tiles | region breakdown |
|---|---|---|
| Cratercrown core (unconditional) | 38 | Cratercrown 38 |
| Widened (elev≥1200, non-green, dayside, rain>0) | 135 | Dew Horn 87, Ashfall Range 24, Dune Sea 17, Fall Line 5, Anvil 2 |
| **Total** | **173** | 6 regions |

By biome (what's being replaced): ZBiome_Badlands 107, AridShrubland 29, Volcano 18,
LavaField 7, ExtremeDesert 7, AB_OcularForest 3 (already-Contagion, the donor's current
strays — fold in per the item's own instruction), ZBiome_Grasslands 1, Desert 1.

Two named regions widen the set beyond what `the_contagion.md` §0 originally scoped:
**Dune Sea** (17 tiles) and **Fall Line** (5 tiles) and **Anvil** (2 tiles) were not named
in the sheet's §0 candidate bands at all — they surfaced only once the widened, planet-wide
rain+elevation rule was actually run, which is exactly what "put it everywhere it
reasonably can" asked for.

Dew Horn's widened count (87, elev≥1200 AND rain>0) is LOWER than the sheet's originally
cited 137 (elev≥1200 alone, no rain gate) — the extra rain condition is doing real work:
50 of Dew Horn's high tiles are apparently dry and correctly stay their host biome under
the strict widened rule.

The full tile-by-tile list — tile id, lat/lon, arc, elev_m, rain_mm, biome, region,
hilliness, and which of the two source rules matched it — is in
[`contagion_tile_candidates.csv`](contagion_tile_candidates.csv), 173 rows.

## The donor's current 3 strays

`AB_OcularForest` tiles 4299/9158/9159 (Ashfall Range, elev 2117–2190m, rain 4/8/271mm)
are already Contagion today and already satisfy the widened rule at their current
coordinates — they appear inside the "widened" 135 (Ashfall Range's 24). No tile move is
needed for these three specifically; "fold in" is satisfied by them already qualifying
under the new rule, not by relocating them.

## Preview render

`Transient/contagion_placement_preview_2026-09-07.svg/ASHKARR_WORLDMAP.biome.equirect.png`
(and matching `.svg`) — `worldview.py` run against a SCRATCH copy of the tile bundle with
these 173 tiles repainted to `AB_OcularForest`, everything else untouched. The committed
`world/ASHKARR_WORLDMAP_tiles.csv` was never written to; the scratch copy lived under this
session's scratchpad and the render output alone was kept, under `Transient/` per this
repo's Transient convention. 🔴 Per that same convention, `Transient/` is untracked and
not committed — this doc cites its full native path so the owner can open it directly, and
does not assume the file survives past the standard ~14-day sweep.

## What's still owed (not this pass)

- The owner's look at the render and the two flagged judgment calls (the green-def
  exclusion set; whether Cratercrown's rain=0 tiles stay in the core).
- Painting: `world_mutators`-style bridge calls + `world_commit` against the REAL
  savegame, once the render is approved (or the tile list is adjusted and re-rendered).
- Savegame re-freeze, Saves-keeper backup first (this repo's standing worldmap-repair
  procedure).
- CSV re-count verification post-paint, matching `the_contagion.md`'s own verify block.
