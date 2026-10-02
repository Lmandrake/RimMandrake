# Messy Conduit — offline mock-up renderer (phase 0)

Python 3 + Pillow + numpy only. Renders the overlay model of
`design/RimMandrake/messy_conduit_design_2026-10-02.md` §8 to PNG so the owner can pick
art styles and messiness before any C# exists. Nothing here touches the game.

```
python3 render.py --out <dir> [--seed 1] [--styles cybertek,extcord,starwars,jawa]
                  [--levels tidy,default,ratsnest] [--ss 3] [--cell 80]
python3 sprawl.py --out <dir>   # 06_sprawl_*: owner excursions vs the 0.38 cap (design §8.6)
python3 nodal.py --out <dir>    # 07_nodal_*: the nodal cord model, the current design (§8.2)
python3 nodal.py --tricky --out <dir>   # 08_tricky_*: tricky configurations (§8.7)
python3 selftest.py      # geometry, size, determinism, sprawl, node reduction, connected-only, tricky rules
```

| file | what |
|---|---|
| `scene.py` | the fixed base scene (grid, walls, door, machines, lamp, tree, items, conduit cells), the break test bed, `GRID_KEY` |
| `styles.py` | `STYLES` (strand kinds, decal vocabulary per style) and `LEVELS` (messiness knobs) |
| `render.py` | per-cell routing (superseded; kept for 01-06), layering (§8.3), break readout (§8.5), decals, sheet framing, CLI; nodal.py plugs in through its `builder`/`after_*` hooks |
| `rope.py` | §8.6: slack, walkability-bounded excursions, loops/figure-8s/heaps, PBD relaxed-rope settle against a signed-distance field of unwalkable cells |
| `sprawl.py` | §8.6 before/after renders on `scene.sprawl_scene()` |
| `nodal.py` | §8.2 the nodal cord model: `reduce` (conduit -> node graph: machines, junctions, terminals, stubs, tangles; needless spurs pruned), `plan` (A* + string-pull: corner, doorway, knot waypoints), `build_nodal` (slack via `rope.sprawl`, capped), stub/downed-wire/power-strip art, debug view, 07 sheets |
| `tricky.py` | §8.7 test beds and the 08 gallery: terminals + downed wire, under rock/water/machine, conduit lattice -> one tangle, needless conduit |
| `export_oracle.py` | writes the scenes + this oracle's graph answers to `MessyConduit/Source/SelfTest/oracle_scenes.json`, which the C# core is tested against (`Utils/selftest_messyconduit.py`) |
| `export_textures.py` | the phase-1a placeholder textures for `MessyConduit/Textures/RimMandrake/MessyConduit/` (+ validator) |
| `selftest.py` | every style/level: no strand vertex in a blocked cell, deterministic output, a live end exists; nodal: reduction census, cords only between connected nodes, never across a gap, no vertex in an unwalkable cell, unrelated edits do not reshuffle, tricky rules |

**Styles:** three families (01 Cybertek, 02 Extension cord, 03 Star Wars) and the Jawa VARIANT of Star Wars (03j); no white in the Star Wars family.

**Nodal routing (07/08, current):** conduit cells → node graph (buried conduit = hidden
edges, stubs where it surfaces; dense fields → one tangle; short spurs → pointless loops) →
one cord per graph edge, A* over walkable cells, string-pulled → corner-rounded → slack
laid by `rope.sprawl` (extra cord 7-16 cells) → break tails at terminals.

**Per-cell routing (01-06, superseded):** conduit cells → graph → chains between junctions/ends → corner-cut
centripetal Catmull-Rom centreline (min bend radius 0.42 cell) → 1-4 strands per run with
lateral offset, low-frequency wander, sag and end tapering into knots → floor loops →
trunk wraps → break tails. Offsets that would enter a wall/machine/rock cell are shrunk.

**Layering (painter's order):** terrain → floor-wire shadows → floor wires (incl. back
half of trunk wraps) → junction/splice/cap decals → grease → hookup wires (elevated
shadow) → walls, door, machines → wall-top wires + staples → lamp, lamp climb → tree →
front half of trunk wraps → items → live break ends (whip, lifted shadow, sparks).

**Determinism:** every choice is seeded by a blake2b hash of (seed, tag, cell/edge); no
global RNG. Same `--seed` → identical PNGs.

**Adding a style:** add an entry to `STYLES` (kinds with `pattern` from `PATTERNS`, plus
junction/splice/cap decal names that `render.decal` knows). For palette passes, change
the `base`/`hi`/`dark` colours only and re-render.
