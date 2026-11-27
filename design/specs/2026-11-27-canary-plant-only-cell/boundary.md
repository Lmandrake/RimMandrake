# BOUNDARY: the vanilla canary's choice of cell, Design Version 0.1.0

Code: `_empty_cell` and `_plants_by_cell` in `src/RimMandrake/Utils/modcheck/validity.py`, as `canary` in the same file
calls them. Item: `STEVE_LANE_MONITOR_PAUSE_FINDINGS` (findings `STEVE_LANE_CANARY_RED_8A39DE` and
`STEVE_LANE_CANARY_RED_F99275`). Written 2026-11-27. This page covers the choice of cell only, not the rest of the
canary or of validity.py. Each promise has a test of its name in `src/RimMandrake/Utils/modcheck/selftest_canary.py`.
The test `plant_only_cell_when_no_bare_cell` was seen red on the parent. The choice keeps no state between calls, so the
page has no LIFE CYCLES.

## ACCEPTS (the only inputs the choice is built for)

- **a-playing-session.** A rimdrive session on a loaded map. `things_at(x, z)` gives the defNames that
  `rimworld/get_cell_info` lists on one cell, and it raises a RuntimeError off the map. `jawa/list_things` with
  `group=Plant` and a rect gives each plant's `def`, `x` and `z`.
- **an-anchor.** An (x, z) on the map. The rings reach 12 cells out.

## DOES NOT SURVIVE (not promised)

- **a-plant-read-cut-short.** A plant read that the limit cuts short can leave a plant-only cell unrecognised. Then a
  later cell is taken, or the canary is red. This is never wrong, only red where it could be green. The limit is four
  times the cells of the square.
- **pawns.** `get_cell_info` does not list pawns, so a cell with only a pawn on it reads bare. That was true before this
  page, and the cleanup never removes pawns.

## PROMISES (each one is owed a test of the same name)

- **bare-cell-first.** A cell that holds nothing is taken first, in ring order, and then no plant read is made.
- **plant-only-cell-when-no-bare-cell.** When no cell in the rings is bare, the first cell whose things are all plants
  on that cell is taken, after one plant read. The canary's Item-only cleanup leaves the plants there.
- **never-on-a-non-plant-thing.** A cell that holds anything that is not a plant on that cell (an item, filth, a
  building) is never spawned on or cleaned.
- **no-usable-cell-is-red.** When no cell is bare or plant-only, or the plant read is refused, the canary is red, names
  "no empty or plant-only cell", and spawns and destroys nothing.
- **plant-read-never-negative.** Near the map's low edge, the plant read's rect starts at 0 or more and keeps the far
  edges of the square.
