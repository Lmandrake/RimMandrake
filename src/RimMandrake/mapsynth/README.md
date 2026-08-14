# mapsynth/ — offline gravship design, verification and rendering

Python scripts that lay out **gravship hulls** on a tile grid, check them against the
game's real constraints, and render readable sheets to look at before anything is
built in-game. Nothing here talks to RimWorld; it all runs offline on numpy + Pillow.
Outputs land in `runs/`.

## The pipeline

| stage | script | what it does |
|---|---|---|
| canvas + rules | `ship_designs.py` | Topology canvas and coverage verifier. Holds the two constant sets — VANILLA (verified) and EXPANDED (Bigger Gravships) — grav-engine / extender radii, tile caps, colours and labels. **Every other script imports its constants.** |
| generate | `build_designs.py` | Builds the candidate hull topologies, verifies each, and enforces the full required region set from `ship_deck_plan.md` (command, thrusters/power, fuel, water, shuttle bay, plus all six Factory wings). Prints FAIL on any design missing one. |
| generate (early) | `ship_layout.py` | The first hand-blocked 64×92 hull. Superseded by `build_designs.py`; kept as the origin of `ship_grid.npy`. |
| check | `verify_coverage.py`, `geom_check.py` | Standalone sanity passes on `ship_grid.npy` — tile counts, lateral extent, whether an on-keel extender can reach the widest wing row. |
| fit | `interior_fit.py` | **Pass 1** for the chosen #15 Falcon Halo hull: does each function pod physically hold its real VFE-Factory machine set at true footprints, plus hoppers, apron, Factory Booster and Heatsink banks? Area feasibility only. |
| skeleton | `skeleton_15.py` | Lays the load-bearing skeleton on #15 — ring corridor, rear causeway, pod doors, thermal spine, power switches, heat vents, and the seven filtered belt-trunk classes. |
| build sheet | `build_sheet_15.py` | **Pass 2** — re-packs each pod with a mandatory 1-tile working aisle around every machine, turning the fit-check into a buildable sheet. |
| render | `render_designs.py` | All candidates as one comparison sheet with engine/extender coverage halos. |
| render | `render_single.py <name>` | One design, large, with ~3× fonts. |
| render | `render_skeleton.py`, `render_build_sheet.py` | The #15 skeleton and build sheet drawn over a dimmed base hull. |
| render | `render_ship.py`, `render_ship2.py` | Early renderers for `ship_grid.npy` (`ship2` also draws `placements.json`). |

## Directories

- `runs/` — generated grids (`*.npy`), plans (`*.json`), sheets and reports. Derived; regenerable.
- `authored/` — the hand-authored map fixture and its before/after renders, left over from
  the abandoned offline map-improvement line. Not part of the gravship pipeline.

## Notes

- The design that won is **#15 Falcon Halo (hollow)**; the exported result lives at
  `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml` (and `.png`).
- Constraints are read from `ship_deck_plan.md` and `Factory_lore.md`, not assumed. If a
  limit changes there, change it in `ship_designs.py` and re-run the verifier.
