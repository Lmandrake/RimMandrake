# Messy Conduit — offline mock-up renderer (phase 0)

Python 3 + Pillow + numpy only. Renders the overlay model of
`design/RimMandrake/messy_conduit_design_2026-10-02.md` §8 to PNG so the owner can pick
art styles and messiness before any C# exists. Nothing here touches the game.

```
python3 render.py --out <dir> [--seed 1] [--styles cybertek,extcord,starwars,jawa]
                  [--levels tidy,default,ratsnest] [--ss 3] [--cell 80]
python3 selftest.py      # geometry + size + determinism checks, no files written
```

| file | what |
|---|---|
| `scene.py` | the fixed base scene (grid, walls, door, machines, lamp, tree, items, conduit cells), the break test bed, `GRID_KEY` |
| `styles.py` | `STYLES` (strand kinds, decal vocabulary per style) and `LEVELS` (messiness knobs) |
| `render.py` | routing (§8.2), layering (§8.3), break readout (§8.4b), decals, sheet framing, CLI |
| `selftest.py` | checks every style/level: no strand vertex in a blocked cell, deterministic output, a live end exists |

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
