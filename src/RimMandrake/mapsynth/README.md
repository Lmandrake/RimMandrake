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
| fit | `interior_fit.py` | **Pass 1** for the chosen #15 Falcon Halo hull: does each function pod physically hold its real VFE-Factory machine set at true footprints, plus hoppers, apron, Factory Booster and Heatsink banks? Area feasibility only. |
| skeleton | `skeleton_15.py` | Lays the load-bearing skeleton on #15 — ring corridor, rear causeway, pod doors, thermal spine, power switches, heat vents, and the seven filtered belt-trunk classes. |
| build sheet | `build_sheet_15.py` | **Pass 2** — re-packs each pod with a mandatory 1-tile working aisle around every machine, turning the fit-check into a buildable sheet. |
| render | `render_single.py <name>` | One design, large, with ~3× fonts. |
| render | `render_skeleton.py`, `render_build_sheet.py` | The #15 skeleton and build sheet drawn over a dimmed base hull. |

## Retired 2026-08-20

`ship_layout.py` · `verify_coverage.py` · `geom_check.py` · `render_ship.py` ·
`render_ship2.py` — moved to
`infrastructure/disposing/code_2026-08-20/` and pending deletion. Nothing in
`disposing/` may be cited, run or copied from; treat them as absent. The
coverage numbers they produced are recorded in
`design/Jawa/worldbuilding/ship_deck_plan.md` and
`src/RimMandrake/mapsynth/runs/designs_report.json`; the live coverage verifier is
`ship_designs.py`, and the surviving renderers are `render_single.py`,
`render_skeleton.py` and `render_build_sheet.py`.

## Directories

- `runs/` — generated grids (`*.npy`), plans (`*.json`), sheets and reports. Derived; regenerable.
- `authored/` — the hand-authored map fixture and its before/after renders, left over from
  the abandoned offline map-improvement line. Not part of the gravship pipeline.

## Notes

- The design that won is **#15 Falcon Halo (hollow)**; the exported result lives at
  `design/Jawa/worldbuilding/ship_build/exported/Gravship_v1.xml` (and `.png`).
- Constraints are read from `ship_deck_plan.md` and `Factory_lore.md`, not assumed. If a
  limit changes there, change it in `ship_designs.py` and re-run the verifier.
