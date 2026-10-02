# Messy Conduit — offline mock-up renderer (phase 0)

Python 3 + Pillow + numpy only. Renders the overlay model of
`design/RimMandrake/messy_conduit_design_2026-10-02.md` §8 to PNG so the owner can pick
art styles and messiness before any C# exists. Nothing here touches the game.

```
python3 render.py --out <dir> [--seed 1] [--styles cybertek,extcord,starwars,jawa]
                  [--levels tidy,default,ratsnest] [--ss 3] [--cell 80]
python3 load.py --out <dir>     # 05_load_*: load-proportional bundles (design §8.10)
python3 sprawl.py --out <dir>   # 06_sprawl_*: owner excursions vs the 0.38 cap (design §8.11)
python3 selftest.py      # geometry + size + determinism + flow/matching/hysteresis/sprawl checks, no files written
```

| file | what |
|---|---|
| `scene.py` | the fixed base scene (grid, walls, door, machines, lamp, tree, items, conduit cells), the break test bed, `GRID_KEY` |
| `styles.py` | `STYLES` (strand kinds, decal vocabulary per style) and `LEVELS` (messiness knobs) |
| `render.py` | routing (§8.2), layering (§8.3), break readout (§8.4b), decals, sheet framing, CLI |
| `load.py` | §8.10: load scene (solar, smelter, day/off/night), Kirchhoff and spanning-tree flow, watts→strands with hysteresis, junction port matching (planar) + union-find strand kinds, labels, legend |
| `rope.py` | §8.11: slack, walkability-bounded excursions, loops/figure-8s/heaps, PBD relaxed-rope settle against a signed-distance field of unwalkable cells |
| `sprawl.py` | §8.11 before/after renders on `scene.sprawl_scene()` |
| `selftest.py` | checks every style/level: no strand vertex in a blocked cell, deterministic output, a live end exists |

**Styles:** three families (01 Cybertek, 02 Extension cord, 03 Star Wars) and the Jawa VARIANT of Star Wars (03j); no white in the Star Wars family.

**Routing:** conduit cells → graph → chains between junctions/ends → corner-cut
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
