# Roads: making a laid network look walked instead of ruled

Measured on the live Ash'karr planet, 2026-08-25/26, editing 1,247 road edges through
`jawa/world_*` at `programState: Playing`. Companion to `river-networks.md`; the 100-row
`limit` cap and the `world_commit` rule there apply here unchanged.

---

## 1. The five RoadDefs are gameplay-identical. The choice is pure narrative.

Read live off the defs, not inferred:

| def | priority | tilesPerSegment | transition group | movementCostMultiplier |
|---|---|---|---|---|
| `DirtPath` | 10 | 15 | Dirt | **0.5** |
| `DirtRoad` | 20 | 15 | Dirt | **0.5** |
| `StoneRoad` | 30 | 25 | Stone | **0.5** |
| `AncientAsphaltRoad` | 40 | 100 | Asphalt | **0.5** |
| `AncientAsphaltHighway` | 50 | 400 | Asphalt | **0.5** |

⭐ **Every one is 0.5.** A road class costs the player nothing, so it can carry a story for
free. ⚠️ `ancientOnly: true` on the two asphalts restricts *worldgen* from choosing them; it
does **not** stop `world_links_set`/`_import` writing them, and they render — verified live.

⛔ `OverlayRoad` silently refuses a LOWER priority over a higher one. To downgrade, clear the
segment first. `world_links_import` with `clearFirst:true` sidesteps it entirely.

---

## 2. 🔴 Penalise HOLDING A BEARING, not turning

**This is the finding. Everything else is detail.**

A hex path from A to B spends the same number of steps whether it runs eight tiles of one
direction and then five of another, or interleaves the two. **The length is identical and only
the look differs.** A turn penalty buys the first — long straight legs meeting at hard elbows,
which is exactly what reads as "laser". A *straight* penalty buys the second for **no extra
distance at all**.

```python
if cosang > 0.93:  c += STRAIGHT_W      # it held the bearing
c += TURN_W * (1.0 - cosang)            # keep small: only bites on a hairpin
```

Measured on Ash'karr, sweeping `STRAIGHT_W`:

| STRAIGHT_W | longest straight leg (mean / max) | sinuosity |
|---|---|---|
| 0.00 | 13.6 / 18 | 1.094 |
| 0.40 | 5.2 / 8 | 1.148 |
| **0.55** | **3.0 / 5** | **1.223** |
| 0.70 | 2.4 / 3 | 1.258 |
| 1.20 | 1.1 / 2 | 1.314 |

🔑 **`0.55`–`0.70` is the band.** Above ~0.9 every step alternates and it reads as a mechanical
sawtooth. ⛔ It does not degenerate at 0.55 because among the many equal-length interleavings
the terrain terms decide which — the phase of the wander is the ground's, not a generator's.

📌 **Sinuosity is the wrong headline number.** It moved 1.106 → 1.168 while the picture changed
completely. **Longest straight leg is the metric that matches what an eye sees**: 18 → 9 max,
5.8 → 2.7 mean.

---

## 3. ⛔ In barren country there is no gradient. Do not invent one.

Four sweeps of the comfort weight from 0.45 to 0.90 returned **byte-identical routes**. Not a
bug: the six neighbours of a Long Sand tile carry comfort 0.12–0.14, so the weight scales every
candidate equally and never changes the argmin. Elevation is no better — median neighbour step
is **2 m in the Anvil, 3 m in Combs, 6 m in Long Sand**.

✅ **What a desert track actually bends for is a REASON ON THE GROUND.** Insert waypoints the
corridor already contains — a well, the lee of a cliff, a wadi, a ruin — and the meander is
explicable: a reader can see why the road went south, because the cenote is there. On Ash'karr
119 waypoints over 61 runs, 45 of them `Oasis`, took a deep-desert run from sinuosity 1.06 to
1.39 **via three oases**.

🔑 Price the detour in **tiles walked PLUS metres climbed**. Pricing it in tiles alone raised
total ascent 22,130 → 28,532 m (+29%) while the brief asked for *easier* terrain — a well on a
shelf is not worth the climb to reach it.

---

## 4. The three cost-model mistakes, all made here

1. ⛔ **An exponent, not a bounded bonus.** `exp(-3*comfort)` makes a lush tile cost an eighth
   of a barren one, which pays for a seven-tile detour — measured sinuosity **2.49 on an 8-step
   run**. Use `1.0 - W*min(1, comfort/S)` with `W ≤ 0.45`, so a detour must save more than it
   costs.
2. ⛔ **A climb cap tighter than the country.** A 180 m cap made every crags road detour 2.5×
   around a pass a real road would simply climb — and the turn knob looked *inert* because the
   detour was topologically forced. Check whether the direct line is BLOCKED before believing a
   weight has no effect.
3. 🔴 **A cap that is not symmetric.** A road is bidirectional. Capping only the uphill sense
   let a **629 m step** in by laying it downhill. Test `abs(d) > CAP`.

🔑 **Shade is the LEE of relief, not the relief itself.** Walking over a mountain is work;
walking along its foot is shade. Penalise hilliness on the tile, bonus a hilliness-3+ NEIGHBOUR
under low hilliness.

---

## 5. ⛔ Never lay a road that cannot be drawn

`SurfaceTile.Roads` is a biome-FILTERED view (`river-networks.md` and
`WORLDMAP_BRIDGE_SURFACE.md` §78). A link on a tile whose biome sets **`allowRoads=false`** is
stored and renders **nothing** — the map shows a road stopping in mid-air for no reason a player
can see, and no error is logged. On Ash'karr `AB_PropaneLakes`, `AB_MechanoidIntrusion`, Ocean,
Lake, SeaIce and IceSheet all refuse roads: **2,504 tiles**.

```python
dropped = [e for e in edges if not allow[e[0]] or not allow[e[1]]]
```

⚠️ **`allowRoads` is absent from the offline def dump.** It can only be read live —
`world_links_get` returns it per tile.

---

## 6. Verify by reading the planet back, edge by edge

`success: true` on `world_links_import` means the file parsed. It does not mean the planet
moved.

```
world_links_clear  kind=road range=0-21871       # planet-wide; clearFirst only touches rows in the CSV
world_links_import path=<WINDOWS path> apply=true clearFirst=true expectTiles=21872
world_commit
world_links_get    range=... limit=4000          # then diff against the CSV you wrote
```

Ash'karr's acceptance was **1,247 wanted / 1,247 live / 0 missing / 0 extra / 0 wrong def**,
plus every `hiddenByBiome` tile carrying zero roads. `world_links_validate --path <csv>` adds
`asymmetricCount` and `nonAdjacentCount`; ⚠️ its `asymmetric` list mixes rivers in, so read the
`kind` on each row before blaming your own write.

---

## 7. Composition notes that made it read as history

- **Keep the topology, re-route the runs.** Decompose into runs between junctions/endpoints and
  re-route each between its two FIXED anchors. Settlements stay rooted, the graph stays
  connected, and the diff is reviewable.
- **Classify from the finished route, never before it.** A road is a "day road" because it
  found shade and water. The story then cannot disagree with the map.
- **Leave gaps on purpose.** A spur to every ruin reads as generated; roughly half is enough.
  Choose by a hash of the tile id — ⛔ never RNG, a seed is a knob that could roll a second
  planet.
- **A dead road should be disconnected.** Ash'karr's ancient highway is 5 components of its own,
  touching the living net nowhere.
- **Bury it by mechanism, not by hash.** Sand accumulates in hollows and is scoured off rises,
  so an ancient road survives where its tile stands above the mean of its neighbours. The gap
  lengths then come out the length the dune fields actually are.
