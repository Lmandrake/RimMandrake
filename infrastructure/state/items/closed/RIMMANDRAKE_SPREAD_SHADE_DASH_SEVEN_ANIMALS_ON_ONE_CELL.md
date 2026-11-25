# RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL

## spec

Mod CreatureBehaviors (composed into RimMandrake.Biomes). Wild animals that dash out of the sun stop on the same cell.
Measured on the Pyrelands walk save `PYRELANDS_0.1.0_VISIT8_WALK_FULL.rws` (2026-11-24): cell (68,27) holds 5 ullai and 2
ashwallows, cell (188,47) holds 4 ashwallows, all on job Wait in the shade. On `PYRELANDS_0.1.0_VISIT5_WALK_FULL.rws`: 4 and
3 fire wasps on one cell each (their jobs were not read). A player sees a heap where a herd should be.

Cause, read in `src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs`: `TryFindEscape` sends every animal to the one cell
`graph.nearestShade[idx]`, nothing asks whether another animal stands there or is on its way, the dash reserves nothing, and
`MakeRest` then rests where it stands. Likely fix [guess ~80%]: land on a free standable cell of the same shade patch near
the nearest one.

Recommended class: Polish for Pyrelands 0.1.0 (it changes which cell, not what the animals do; no bar names it); a fix of
CreatureBehaviors in its own right. The Conductor decides.

## Acceptance test

`python3 infrastructure/state/acceptance/RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL.py "<save>"` exits 0 on a save
made on the fixed build: a hot, sunny Pyrelands map, six ullai spawned in the open, 600 ticks later. Watched red on the visit
8 walk save, 2026-11-24: two cells named, exit 1. The build run also writes the offline test of the landing choice.
