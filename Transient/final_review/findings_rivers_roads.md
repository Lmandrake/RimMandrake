# WORLDMAP_FINAL_REVIEW_1 Phase 1 — rivers + roads lane, measured audit

Read-only. Data: `Transient/final_review/world_links.json` (link graph, fresh 2026-09-11,
21,872 tiles, `hiddenByBiomeCount: 15`), `world_tiles_live.csv` (21,872 tiles — header is
`tile,lat,long,biome,elevation,temperature,rainfall,hilliness,swampiness,pollution`; **no
`riverDist` column despite the task brief's description** — riverDist came from
`world_links.json`'s per-tile `riverDist` field instead, which is present and populated),
`world_objects.json` (96 settlements). All numbers below are counted in Python from these
three files (`csv`/`json` modules), not grepped. Scripts:
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/8b5fa332-4f43-4047-b07c-aeb73b83f10f/scratchpad/audit.py`
(rivers + graph build) and
`/tmp/claude-1000/-mnt-d-Luke-dev-Rimworld/8b5fa332-4f43-4047-b07c-aeb73b83f10f/scratchpad/rivroad_part2_9f3a.py`
(roads + settlement reachability); both scratchpad, not the repo.

Design truth consulted: `design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §4
hydrology (Scald is a −350 m terminal pan on the map, but per the R1 lore ruling that
−350 m reading is an accepted engine artifact — "RimWorld cannot render an ocean at
altitude" — and the Scald is meant to be the water SOURCE, rivers reading as leaving it)
and `design/Jawa/worldbuilding/data/river_graph_2026-09-07.md` (the prior, now-stale,
elevation-only pass that found the opposite — 9/9 Scald boundary edges read as INFLOW on
2026-09-07). **`the_seas.md` (named in the brief) contains no river/Scald content** — it
is a short 84-line file with zero hits for "river" or "scald"; hydrology truth lives in
`ASHKARR_WORLD_DEFINITION.md` and the river_graph doc instead.

Biome caveat: **`riverDist` is meaningful only for river-graph tiles and the handful of
coastal seed tiles** — 20,745 of 21,872 tiles (94.8%) read `riverDist == 0` simply
because the flood-fill that sets it never touched them (see
`river-direction-is-riverdist` memory: seeded from coastal water, floods upstream along
river links only). Treating a non-river land tile's `riverDist == 0` as "at a mouth"
would be wrong; all river audits below are scoped to the 335 tiles that actually carry a
river link.

---

## RIVERS

### 1. Graph build (context for all river audits below)
326 unique river-link edges, touching 335 distinct tiles, forming **11 connected
components** — sizes [118, 115, 38, 14, 10, 10, 8, 6, 6, 5, 5]. (The 2026-09-07
`river_graph` doc measured 308 tiles / 16 components on an earlier data pull — the live
graph has since changed, most likely from work around the 2026-09-10 landmark-rename
backup seen in git status. This report uses only the live 2026-09-11 numbers.)

### 2. Uphill-flow check
**Method:** `riverDist` is the direction truth (memory `river-direction-is-riverdist`:
0 at the mouth, rising upstream; links themselves are symmetric/directionless). For
every river edge, the tile with the lower `riverDist` is downstream. Flagged where the
downstream tile's elevation is *higher* than the upstream tile's (physically wrong —
water should not gain elevation moving downstream).

**Verdict: MEASURED, mostly explained.** Of 324 directed edges (2 edges tied on
`riverDist`, excluded — see §4), **71 uphill violations (21.9%)**. Of those, **8 are the
known Scald −350 m elevation artifact** (every edge touching a `RUT_TheScald` tile shows
a huge fake elevation drop/rise because the Scald is pinned to −350 m by design, not
real terrain — see R1 section below). Excluding Scald-touching edges: **63 uphill
violations out of 315 non-Scald directed edges (20.0%)**, consistent with the
2026-09-07 doc's own caveat that this is "a noisy coarse-grid DEM" (per-river violation
rates there ranged 0–100% on small samples).

**15 worst non-Scald offenders (downstream tile, downstream elev → upstream tile,
upstream elev, elevation gained flowing "downstream"):**
```
11946(1407m) <- 11947(780m)   +627m
4380(321m)   <- 17343(1m)     +320m
11334(606m)  <- 675(312m)     +294m
3640(603m)   <- 19400(352m)   +251m
21327(464m)  <- 2341(308m)    +156m
15153(269m)  <- 15156(133m)   +136m
15156(133m)  <- 11914(1m)     +132m
12462(724m)  <- 9225(605m)    +119m
1174(265m)   <- 14325(148m)   +117m
6239(301m)   <- 21307(205m)   +96m
2795(70m)    <- 14335(1m)     +69m
14325(148m)  <- 7653(99m)     +49m
2795(70m)    <- 14331(29m)    +41m
14325(148m)  <- 2793(112m)    +36m
14345(62m)   <- 14344(31m)    +31m
```
**Corrective:** re-grade elevation along these 15 reaches (or re-derive `riverDist` from
a smoothed elevation pass) before calling the river DEM final; the 8 Scald-touching
"violations" need no fix — they are the accepted −350 m rendering artifact, not a defect.

### 3. Orphan segments
**Method:** for each of the 11 river components, check whether it touches a water-body
biome (`RUT_GreySea`/`RUT_TwilightSea`/`RUT_TheScald`/`RUT_PropaneLake`/
`AB_PropaneLakes`/`RUT_NightsideIce`) or contains a `riverDist == 0` tile (a land
terminus/salt-pan mouth, valid per design — "genuine basins are left endorheic").

**Verdict: MEASURED CLEAN — 0 orphan components.** All 11 components reach either a
named water body or a proper `riverDist == 0` land terminus. No corrective needed.

### 4. `riverDist` consistency (monotonicity along components)
**Method:** `|riverDist(a) − riverDist(b)|` for every river edge; the seeding algorithm
should produce a delta of exactly 1 per hop, with departures only at confluence tiles
(the `max()` merge rule can leave a shorter tributary arm 0–2 off at the junction).

**Verdict: MEASURED CLEAN.** Delta histogram over 326 edges: `{0: 2, 1: 322, 2: 2}` —
**98.8% of edges differ by exactly 1.** The 4 exceptions are all at a single confluence
node (tile 14323, `riverDist=19`, `BiomeCypreJungle`) where branches of differing
tributary length merge — exactly the expected `max()`-rule signature, not a defect.
`riverDist` on this hand-authored world is real, computed, and internally consistent
(contrary to the standing memory's worry that the frozen-world rivers script "may never
have set riverDist at all" — it clearly has).

### 5. Mouth/source census
**Method:** mouths = river tiles with `riverDist == 0`; sources = degree-1 (leaf) river
tiles whose single neighbor has strictly higher `riverDist`.

**Verdict: MEASURED.** **11 mouth tiles:** 3154, 3450, 3473, 6643, 8331, 11946, 12366,
15127, 16634, 16893, 16897 (mix of named-sea mouths — 3450 `RUT_TwilightSea`, 6643/16893/
16897 `RUT_GreySea` — and land/salt-pan termini, matching design intent). **59 leaf
(degree-1) tiles total**; **48 read as clean sources** (riverDist ≥ their one neighbor's);
the other **11 leaves are exactly the 11 mouth tiles themselves** (degree-1 termini, not
an anomaly — every mouth is naturally a leaf of its component). No corrective needed.

### 6. R1 test — do Scald-rim river components trend AWAY from the Scald by `riverDist`?
**Method:** the Scald (`RUT_TheScald`) sits at a fixed −350 m in the live data (an
accepted rendering artifact per `ASHKARR_WORLD_DEFINITION.md` §4 — not to be "fixed" by
regrading). R1's lore ruling requires rivers to *read as leaving* the Scald despite that
elevation artifact — i.e. by `riverDist`, the Scald end of each boundary edge should be
**upstream** (higher `riverDist`) of its land neighbor, not downstream. Found the 9
Scald-boundary river edges live (8 `RUT_TheScald` tiles carry a river link:
1310, 2931, 8493, 11943, 15175, 17342, 19361, 19369) and compared `riverDist` across
each boundary edge.

**Verdict: MEASURED PASS, with one partial defect.** **8 of 9 boundary edges (89%) read
as OUTFLOW** — the Scald-side tile has the *higher* `riverDist`, i.e. reads as the
upstream source, water leaving it — matching R1 intent. This is a reversal from the
2026-09-07 elevation-only pass, which found 9/9 as INFLOW; whatever repaint work
happened since then succeeded on `riverDist` for 8 of the 9 links. Table (scald_tile
riverDist -> land_tile riverDist):
```
17342(40) -> 17343(39)  OUTFLOW
11943(2)  -> 777(3)     INFLOW  <-- the one exception
2931(32)  -> 7791(31)   OUTFLOW
1310(30)  -> 15141(29)  OUTFLOW
11943(2)  -> 11947(1)   OUTFLOW
19361(37) -> 19404(36)  OUTFLOW
19369(9)  -> 2014(8)    OUTFLOW
8493(13)  -> 19371(12)  OUTFLOW
15175(26) -> 15173(25)  OUTFLOW
```
**Corrective:** tile 11943 has two river branches — one already flipped to outflow
(→11947) and one still reading inflow (→777, `riverDist` 2 vs 3). Renumber the 777 arm's
`riverDist` upward (per the `river-direction-is-riverdist` memory: renumber `riverDist`,
never the links or elevation) so it also reads ≥3, matching the rest of the junction.

### 7. Rivers crossing biomes whose sheets exclude rivers (the 15 `hiddenByBiome` tiles)
**Method:** every tile in `world_links.json` with `hiddenByBiome: true` — these carry a
real geometric river link (`potentialRivers` non-empty) but `allowRivers: false` for
their biome, so the engine hides the river rendering there.

**Verdict: MEASURED, all 15 named.** 8 × `RUT_TheScald` (1310, 2931, 8493, 11943, 15175,
17342, 19361, 19369 — expected, the Scald's own river-hiding rule, already covered in
§6), 4 × sea (3450 `RUT_TwilightSea`; 6643, 16893, 16897 `RUT_GreySea` — expected, these
are the mouth tiles from §5), 3 × `AB_PyroclasticConflagration` (11090, 11092, 21311 —
**not** a mouth or Scald tile; a volcanic-rim biome silently swallowing 3 river-link
renders). **Corrective:** confirm the 3 `AB_PyroclasticConflagration` river hides are
intentional (a lava-flanked biome plausibly should hide rivers) or move those 3 links off
that biome if the river was meant to be visible there.

---

## ROADS

### 1. Connected components
**Method:** union-find over the 1,235 unique road-link edges (1,275 distinct road
tiles).

**Verdict: MEASURED.** **47 components** — one giant network of **1,122 tiles**, and
**46 small components (2–9 tiles each)** disconnected from it: sizes
`[9, 7, 7, 6, 6, 6, 6, 5, 5, 5, 4, 4, 3x15, 2x22]` (full list in the audit script output).
**Corrective:** the 46 disconnected fragments (124 tiles total) are candidates for
either linking into the main network or removal — 15 worst (smallest, most orphaned)
are the size-2 pairs, e.g. `[3341, 8200]`, `[16420, 16421]`, `[1528, 16448]`,
`[8258, 8263]`, `[301, 9087]`, `[938, 12910]`, `[6045, 17615]`, `[17906, 17910]`,
`[3398, 17953]`, `[2378, 21548]`, `[6298, 11159]`, `[3147, 8008]`, `[12118, 12119]`,
`[3943, 21213]`, `[5619, 13735]`.

### 2. Per-settlement road reachability
**Method:** [approximate] — no full hex-neighbor export was available in this data
pull (`potentialRoads`/`potentialRivers` list only tiles that already carry that link
type, not every hex neighbor), so "within 1 tile" is a calibrated great-circle distance:
the 95th-percentile arc-distance of all 1,561 known-adjacent tile pairs (river+road
edges combined) is **1.55 degrees**, used as the 1-hex threshold.

**Verdict: MEASURED (approximate distance metric).** 74/96 settlements sit directly on a
road-graph tile. **18 settlements (18.75%) have no road tile within ~1 hex:**
```
Oilpalm (4271, Wildsteam Clan)          2.33 deg
Hollow Hive (8497, Geonosian Foundry)   4.00 deg
Bitterleaf (6645, Wildsteam Clan)       4.42 deg
The Fair Copy (5912, Ascendant Helix)   5.24 deg
Razorsand (13357, Deep Desert Tribes)   5.42 deg
Warthorn (16641, Wildsteam Clan)        6.80 deg
The Long Camp (11559, Deep Desert)      9.20 deg
Quiet Lab (21037, Ascendant Helix)      9.38 deg
The Free Charge (21547, Free Droid)     9.39 deg
Barno (18341, Deep Desert Tribes)       10.25 deg
Stone Moot (6308, Deep Desert Tribes)   11.25 deg
Deepwater Hold (9451, Deepwater Compact) 12.40 deg
Duneward (13737, Deep Desert Tribes)    14.50 deg
Redscarp (6570, Deep Desert Tribes)     14.75 deg
Sufferband (13520, Deep Desert Tribes)  15.52 deg
```
(+3 more beyond 15, all Deep Desert Tribes/Ascendant Helix/Free Droid, full list in
script output.) **Note:** 6 of the 18 are Deep Desert Tribes — a nomadic faction may be
roadless by design; verify intent before treating those as defects. **Corrective:** for
the remainder (Wildsteam Clan jungle seats, Ascendant Helix, Geonosian, Free Droid,
Deepwater Compact holds), either extend a road spur or confirm each is meant to be
road-isolated.

### 3. Orphan road stubs
**Method:** degree-1 (dead-end) road tiles; flagged if no settlement lies within ~3
hexes (3 x the 1.55 deg calibration = 4.66 deg, same caveat as §2 — approximate, not a true
hex-BFS hop count). Landmark proximity was **not** computed — 3,414 landmarks over
21,872 tiles (~1 every 6.4 tiles) makes "within 3 tiles of a landmark" nearly always
true and not a useful discriminator; scope limited to settlements.

**Verdict: MEASURED (approximate distance metric).** **154 dead-end road tiles**; **90
of them (58%) have no settlement within ~3 hexes.** 93 of the 154 dead ends sit in a
road component smaller than 20 tiles (i.e., mostly the same disconnected fragments from
§1, not stubs hanging off the main network). **15 worst (farthest from any
settlement):**
```
6064  (RUT_NightsideIce)   19.10 deg
6065  (RUT_NightsideIce)   18.91 deg
16421 (RUT_BlueDesert)     18.45 deg
117   (RUT_NightsideIce)   18.44 deg
16310 (RUT_NightsideIce)   18.34 deg
6037  (RUT_BlueDesert)     17.70 deg
14166 (RUT_NightsideIce)   17.61 deg
16420 (RUT_BlueDesert)     17.15 deg
17967 (AB_MycoticJungle)   16.01 deg
14133 (RUT_NightsideIce)   15.60 deg
12914 (AB_MycoticJungle)   15.58 deg
938   (AB_MycoticJungle)   15.00 deg
8003  (RUT_BlueDesert)     14.63 deg
15371 (AB_MycoticJungle)   14.56 deg
3384  (AB_MycoticJungle)   14.22 deg
```
**Corrective:** these read as leftover/decorative road fragments on the dark-side ice
and mycotic-jungle terminator rather than roads serving any settlement — candidates for
removal, or confirm they serve an unlisted landmark before cutting.

### 4. Roads crossing water/impassable biomes
**Method:** first checked the game's own gate (`allowRoads` per tile, from
`world_links.json`) — the mechanically correct test. Then, separately, checked road
edges against named "open sea" biomes (`RUT_GreySea`/`RUT_TwilightSea`/`RUT_TheScald`)
and against `Impassable` hilliness.

**Verdict: MEASURED CLEAN.** **0 road edges touch a tile with `allowRoads: false`**
(every biome sampled — including `AB_PropaneLakes`, `RUT_NightsideIce`, `RUT_BlueDesert`,
`RUT_TheScald`, `RUT_GreySea`, `RUT_TwilightSea`, `RUT_PropaneLake` — reads
`allowRoads: true` for every tile checked). **0 road edges touch open sea**
(`RUT_GreySea`/`RUT_TwilightSea`/`RUT_TheScald`). **0 road edges touch `Impassable`
hilliness.** (42 road edges do cross `AB_PropaneLakes`/`RUT_PropaneLake`/
`RUT_NightsideIce`/`RUT_BlueDesert` tiles — biome names that sound like water, but the
engine explicitly allows roads there and none of it is the named open seas, so this is
not a defect.) No corrective needed.

---

## UNMEASURED
- True hex-adjacency for the "within 1/3 tiles" road-reachability checks — no full
  neighbor list was exported, so distance is approximated via a calibrated great-circle
  threshold (see Roads §2–3 methods). Exact hex-hop counts would need a genuine
  adjacency export.
- Whether the 3 `AB_PyroclasticConflagration` river-hide tiles (Rivers §7) are
  intentional design or an oversight — needs an owner/design call, not a data check.
- Whether tile 11183 (flagged `river_flow` in the old 2026-09-07 pass with no link row)
  still exists as a gap in the live graph — not re-checked this pass; the live graph
  size (335 tiles) differs from the old 308, so this needs a fresh look if it matters.
- Landmark-based orphan-stub reachability (Roads §3) — not computed, see method note
  (density makes it a weak discriminator without real hex-adjacency).
