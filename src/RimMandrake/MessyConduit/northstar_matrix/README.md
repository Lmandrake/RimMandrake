# Messy Conduit: Northstar scene matrix (generator, oracle, placer, contact sheets)

Owner, 2026-10-02: *"throwing up a complex series of well defined power grids and then taking a screenshot to
show the various stages of tangling, the power line connections, etc. in a combinatorially useful pattern
absolutely IS possible and valuable."* This folder builds that matrix offline. It never touches the game.

```
python3 matrix.py                          # case count, value usage, pair proof
python3 matrix.py --out <catalog.json>     # every case: scene + lint + oracle + placement plan
python3 matrix.py --prove <catalog.json>   # re-prove pair coverage of a written catalog (exit 1 if a pair is missing)
python3 contact_sheet.py --shots <dir> --catalog <catalog.json> --out <dir>
python3 design_spec.py [--out scenes.json] # the phase-2 design's 109-scene matrix in ITS spec format (design 4.3)
python3 selftest.py [--keep <dir>]         # 47 checks, 15 of them negative controls
```

There are two catalogs. Both are deterministic and both are proved pairwise-complete:

- **`design_spec.py`** (the design's own matrix, `design/RimMandrake/messy_conduit_phase2_design_2026-10-02.md`
  section 4). It has 109 scenes: floor 64 (T16 x S4, with F/P/V/Z set by its formulas), density ladder 16, aerial
  18, hose 9 (an L9 array) and controls 2. It is emitted as `spec_version 1` JSON with `build` ops, `view`, and
  `expect.intrinsic` filled in by `oracle.py` (`parity: core` is left for the C# SelfTest). This pass re-proved
  the design's coverage claims: floor 328 pairs, aerial 78, hose 54, 0 missing. Every scene fits a 40x30 board.
  Mapping notes and two things the design asks for that do not exist yet (a `tangleMin` setting; a powered
  *impassable* building for the device-stub row) are in its docstring.
- **`matrix.py`** (the cross-factor complement). It is a pairwise covering array over all seven axes at once,
  so a topology also meets every style, density, break, aerial and hose value.

## matrix.py: 84 cases, pairwise-complete

| axis | values |
|---|---|
| topology (21) | line, l_chain, tee, cross4, ring, lattice2, lattice3, lattice5, mesh, star, spur, spur_blob, gap, multinet, device_attached, doorway, wall_entry, rock_entry, under_building, canal, long_run |
| tangle (3) | tidy (slack 0.2, sprawlCap 3, 1 cord), ropey (shipped defaults 1.0 / 16 / 3), ratsnest (1.8 / 40 / 3) |
| style (4) | jawa, extcord, cybertek, starwars (only jawa art is installed today) |
| density (4) | 5, 20, 100, 400 conduit cells (a target: the feeder pads up to it, a topology is never shrunk) |
| break (3) | none, live_gap (charged source, one cell missing), dead_gap (same gap, empty source) |
| aerial (3) | none, one_span (2 masts), chain_cut (4 masts, middle span cut) |
| hose (3) | none, flat, plump |

There are 586 value pairs across the 7 axes, and every one of them appears in at least one case. The lower bound
is 21 x 4 = 84, so the set is optimal. The generator is a seeded greedy (AETG-style) search and its output is
byte-deterministic. `matrix.py --prove` re-derives the coverage from the catalog, and the selftest drops one
case and checks that the proof then fails.

## Files

| file | what |
|---|---|
| `scenes.py` | topology library (`t_<name>()`), `compose()` (feeder snake, source battery, break cell, aerial and hose strips) and `lint()` |
| `oracle.py` | expected node graph per scene, computed with `nodal.reduce` from the mock-up (`src/RimMandrake/Utils/mockups/messy_conduit/nodal.py`) |
| `matrix.py` | pairwise covering array, its proof, the catalog |
| `placer.py` | per-scene bridge plan (tool calls, probe commands, placeholders) plus a check against `northstar_driver/tool_schemas.json` |
| `fakegame.py` | runs a plan on an in-memory map, reads the scene back and re-runs the oracle |
| `design_spec.py` | the design's 109-scene matrix in its section 4.3 format, with its formulas re-proved |
| `contact_sheet.py` | labelled sheets and per-image sanity metrics, written to `report.json`, plus design 4.6 `mask_check` and `frame_ok` |

## What the oracle corrects relative to the mock-up (read from `CordWorldAdapter.cs`)

1. **Transmitter buildings hook to every cardinally adjacent conduit cell.** That covers batteries, generators
   and switches (and later `RM_AerialMast`), and it joins those cells into one net. Liveness is therefore computed
   here, by union over conduit adjacency plus transmitter bridges, and then handed to the reducer.
2. **A device buries conduit only if its footprint is unwalkable.** Every device used here is PassThroughOnly or
   Standable (checked against the 1.6 defs in RimSage), so the reducer sees zero-size footprints. With the
   mock-up's own blocking, `under_building` would wrongly read `stub_device`.
3. **Lamps census as `consumer`.** The oracle's `node_types_live` applies that mapping.

The cross-check: on every scene where no transmitter bridges two components, the oracle agrees with an
unaided `nodal.reduce` on every graph field.

## Placement (placer.py)

The recipe is `validation.py`'s, proven in live passes 1 and 2: destroy, then Soil, unfog, unroof, Granite,
walls and doors, conduit (WaterproofConduit on water), transmitters, `battery_set`, connectors, trees,
`map_commit`, frame, 2 ticks, `census` probe, the ON screenshot, `set:enabled=False`, the OFF screenshot,
`set:enabled=True`, cleanup.

Build order matters. A connector picks its transmitter when it spawns: the nearest wire-able transmitter by
squared distance to the transmitter's Position, within 6 cells, scanning z then x (`PowerConnectionMaker`,
decompiled 1.6). So every transmitter is built before any connector. `lint()` and `fakegame.py` emulate that
rule, which is why a wrong hookup or a wrong order shows up offline.

Coordinates map as game (X0 + x, Z0 + (h - 1 - y)). `expect_game` carries the terminals and device positions in
game cells, so they can be compared with the census `ends`.

**Unverified realizations** (`placer.UNVERIFIED`), for the runner to check on its first pass:
- WaterproofConduit on WaterDeep (an affordance question).
- WoodFiredGenerator spawns unfuelled: its node must read `source` while the battery powers the net.

## Adding a topology

1. Write `def t_<name>()` in `scenes.py`. It returns a `Canvas` whose west entry cell is `(0, entry_y)`. Use
   `c.line`/`c.run` for conduit, `c.dev(...)` for devices (connectors need `hookup=`), and `c.heater_beyond(...)`
   for an end consumer.
2. Append the name to `TOPOLOGY_ORDER`. The matrix regrows: the case count becomes |topology| x 4 (the selftest
   asserts the lower bound). To put the topology into the design matrix as well, map a T level to it in
   `design_spec.T_LEVELS`.
3. Run `selftest.py`. Lint must stay clean at all four densities, the fake-game round trip must give 0 diffs,
   and if the topology has a property with a known answer, add an `O2` check for it.

## What is NOT Northstar-testable, and the cheap proxies

| not testable | why | proxy |
|---|---|---|
| sway motion, whip of live tails, spark and drip timing, hose fill wobble | motion; a paused frame shows none of it, and sparks are tick-thrown flecks (`validation.py` LEARNED) | state reads: sway material and vertex-alpha extremes, the downed-wire state histogram over 600 ticks, `whipDraws` (design section 1.6), hose state after N ticks (section 3.12). Visually, two frames N ticks apart: the pair must differ inside the cord rect and match outside it |
| "does it look messy / good" | taste | the contact sheets, judged by the owner. Tangle stages are lined up per topology across the tidy, ropey and ratsnest cases |
| cord presence from a single frame, with no census | measured useless on the 2026-10-02 shots. A dark-ridge detector reads 0.019 with cords and 0.023 with vanilla conduit, and palette distance reads over 0.5 on bare soil | (a) design 4.6 #2 `mask_check`: census vertices projected to pixels; the 3-px mask must be at least 12% darker than the rest of the frame (needs the census to return laid vertices plus a cell-to-pixel transform). (b) an aligned ON/OFF pair (same camera, same tick): more than 0.2% of pixels changed by more than 40, with median difference at most 4; otherwise UNMEASURED |
| aerial masts and hoses | not built (`RM_AerialMast`, hose kit: phase-2 design sections 2 and 3) | the oracle already carries `aerial` and `graph_with_aerial` (pole liveness, dangling ends at a cut) and `hose`. The plans emit `unbuilt` steps, and the floor parts of the strips (their own battery, stub and heater) are built and checked today |
| styles other than jawa | art not installed (`validation.py` U_other_styles) | `style_art_installed` in each plan; the runner records those frames as UNBUILT art, not as failures |
