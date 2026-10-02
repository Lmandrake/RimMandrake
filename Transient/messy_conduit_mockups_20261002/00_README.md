# Messy Conduit — phase-0 mock-ups (2026-10-02)

Offline PNGs for the owner to pick from (MESSY_CONDUIT_MOD_1, design §8). No game or bridge
was used. **The current design is the nodal cord model (07, 08; design §8.2, §8.7).** 01-06 are
the earlier per-cell overlay, kept as the style reference (06_sprawl_jawa is the approved look). Renderer, scene and selftest: `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\mockups\messy_conduit\`
(`render.py --seed N` re-renders this exact set; the output is deterministic).

## Files

| file | shows |
|---|---|
| `00_overview.png` | the three families (Star Wars shown as base + Jawa variant) side by side, DEFAULT messiness, same network |
| `<NN>a/b/c_<style>_<level>.png` (NN = 01, 02, 03, 03j) | the base scene at 80 px/cell, messiness 1 tidy-ropey / 2 ropey-jury-rigged (DEFAULT) / 3 rat's nest |
| `<NN>s_<style>_swatches.png` | close-ups at 110 px/cell: every strand type, the default bundle, T and X junctions, splice/joiner, slack loop, capped stub + spare coil, over-a-wall, into-rock grommet, trunk wrap, lamp-post climb, machine hookups, break live vs dead |
| `<NN>t_<style>_break.png` | break readout: 4 frames of the live end (whip + sparks) beside the still dead end, plus a power-off panel where both ends read dead |

| `06_sprawl_<style>.png` | **owner excursions** (§8.6): BEFORE = phase-0 routing capped at 0.38 cell, AFTER = 1.9x slack laid as big walkability-aware loops, figure-eights and heaps that pile against walls/rock, on a new open-floor scene |
| `00_owner_reference_orange_cord.png` | the owner's reference photo for §8.6 |
| `07_nodal_<style>.png` (jawa, extcord, cybertek) | **the nodal cord model** (§8.2): conduit reduced to a node graph, one too-long cord per edge, A* between nodes, slack as loops/figure-8s/heaps; conduit in a wall or rock is never drawn, only the holes where it goes in and comes out |
| `07_nodal_breaks_jawa.png` | the gap at N13 at 110 px/cell: 4 frames of the live end, then generator off (both dead) |
| `07_nodal_vs_percell_jawa.png` | the same conduit drawn by the old per-cell overlay (left) and by nodal cords (right) |
| `07_nodal_graph_debug.png` | the node graph itself: nodes by type, cord edges with planned path and waypoints, buried edges dashed, laid-length ratio per cord |
| `08_tricky_overview.png` | the four tricky-configuration sheets side by side (§8.7) |
| `08_tricky_downed_wire.png` | terminals: every conduit end is a node; a run that ends INSIDE a wall hangs out of it spark-dripping like a downed line (4 frames) vs a dead one hanging still |
| `08_tricky_under_mountain.png` | conduit under rock (cable holes), deep water (cord dives in, ripples) and a 3x3 powered machine (cords plug into power strips at its base); render + graph |
| `08_tricky_grid_tangle.png` | a lattice of conduit under a floor -> ONE tangle node: a swirled heap with power strips (lit / dark) and 4 exit cords; render + graph |
| `08_tricky_needless_loop.png` | 1- and 2-cell spurs and a 2x2 block on a line -> pointless loops in the cord; zigzag -> nothing; ring -> two cords; a 4-cell spur stays a real terminal; render + graph |

**Style structure (owner, 2026-10-02): three families, Jawa is a variant of Star Wars.**

| | family | look |
|---|---|---|
| 01 | Cybertek | sleek silver/graphite metallic, chrome ferrules, hex pods with a cyan light (silver is allowed) |
| 02 | Extension cord | glossy orange/green/brown/yellow/blue, power-strip junctions, plug-into-socket joiners |
| 03 | Star Wars (base) | mostly smooth **matte** black cable (low shine), a few dark corrugated-steel hoses and coiled black cords, greebled boxes. **No white.** |
| 03j | Star Wars: **Jawa variant** | the same matte-black set gone feral: dark/ochre/oil-stained tape, hose clamps, rag caps, a ration-tin box, grease. **No white.** |

## Grid key for 01-03 (columns A.., rows 0.. — printed on every scene; 06-08 carry their own key lines)

| cells | what |
|---|---|
| E3:F4 | generator, the only power source |
| G4..L4, L4:L7 | main line; L4..L7 runs ON TOP of the west wall (stapled), then drops into the room along row 7 |
| H6..J8 | a closed conduit loop around the lamp post at I7; J5 links it to the main line |
| I7 | lamp post; its hookup sags in from I8 and is taped up the post |
| H9..E9 | branch west; wraps the tree trunk at G9 |
| **D9** | **the break** (one-cell gap): E9 live end sparks and whips, C9 dead end lies limp |
| B9..B11 | dead side of the break, feeding the console at C11 (screen off: unpowered) |
| P7 | X junction: north to the workbench N3:P3, south under the door at P10 |
| S7 | T junction: north to the battery bank S3:T3 |
| U7 | end of the main line, hooked into the heater at U8 |
| P12 | lone dead end: a deliberate capped stub (never sparks) |
| E12, R8, N8, K11, M9 | floor items, always drawn over wires |

## Knobs (`styles.py`)

Per level: strands per run (1-2 / 2-3 / 3-4), bundle spread, wander, sag, floor-loop chance,
splice chance, spare-coil chance, extra tape, grease, hookup strand count and hookup sag.
Per style: strand kinds with weights, widths and colours, surface pattern (gloss, metal, rubber,
corrugated, coil, twin-lead, braid, bare copper), junction/splice/cap decals, wander scale and grease.
`--seed` changes every random pick (strand mix, loops, splices) without changing the network.

## What would differ in game (honest limits)

- **Procedural placeholders, not shipping art.** Every texture is drawn from code; the in-game set
  would be ~6 (phase 1a) to ~21 painted strips and decals (§8.6). Treat these as layout, colour and density studies.
- **Static frames.** Sway, whip and sparks are drawn as poses. In game sparks are vanilla
  MicroSparks/LightningGlow flecks; whip is per frame; sway depends on the CutoutPlant shader (unverified, §8.2).
- **Simplified occlusion.** Painter's order here is per layer, not a depth test (§8.3);
  a tree or lamp directly south of a wrap is not tested in this scene.
- **Scene art is a stand-in.** Walls, machines, tree and lamp are not vanilla sprites, and the zoom is
  fixed at 80 px/cell (110 for swatches). Far-zoom shimmer and the LOD swap are not shown.
- **Rat's nest is capped**: sprawl is clamped to 0.38 cell per the clipping rule, so even level 3 stays
  close to its own cells. It can go wilder if that rule is relaxed.
- **Known weak spots:** the trunk wrap reads small at scene zoom (clearer in the swatch). The Star Wars
  coiled cord reads as ribbed black cable at 80 px/cell. Hookups into a machine straight north of the
  conduit hang nearly vertical, so their sag is subtle.

## What the owner is asked to judge

7. Nodal cords (07): is this the look of 06 at a lower cost? Is ~2-3x cord per short edge (7-16 cells
   spare) the right amount of slack?
8. Tricky configurations (08): downed-wire pattern, the tangle, pointless loops for needless conduit.

1. Which families ship, and whether the 03j Jawa variant is the default or the campaign-only set.
6. Excursions: is the AFTER level of 06 the default, or between BEFORE and AFTER?
2. Which messiness level is the default (proposed: level 2).
3. Whether the break readout (live sparks vs limp dead end) reads at a glance.
4. Wire on the wall top and the trunk wrap: keep, change or drop.
