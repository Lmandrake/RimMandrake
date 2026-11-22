## spec
Pyrelands 0.1.0, in-game visit 5 (ArchBig, tier pyrelands, 2026-11-22, build e63595716c). Check `sc_firefoam_sprayer`
(bar `firefoam_sprayer_reaches_the_fruit`, `inv_firefoam_sprayer`). Class SITE (the staged scene), repair not known.

What was measured (design/concepts/Pyrelands/version/in_game/visit_5/evidence/run_firefoam_repaired2.log, timelines every
250 ticks):
- The sprayer row PASSes (13 Filth_FireFoam cells, fruit taken, no burn): the 3acf1ad82b fix lays foam live.
- The control row (no sprayer) FAILs in every visit: visits 3, 4 and 5 (2-cell ring), and visit 5 again with a 3-cell ring
  and the sprayer row's foam cleared first (ab3a14c6f5). One `map_fire start` over each ring edge lights only 41 to 54 of
  the 72 ring cells (ChanceToStartFireIn refuses the rest), so the ring has gaps from the first tick.
- Both colonists, with and without the sprayer, walk through the gaps in under 250 ticks to (227,32)/(227,33), a ring cell
  beside the fruit that is not burning, and then stand there with job Harvest for about 1500 ticks, unburned, until the
  ring's fires fall from about 45 to under 10; the fruit is taken only then (control at tick 1750 with 4 fires left; the
  sprayer colonist at tick 2000 with 0). So the sprayer row's PASS does not show that the sprayer was needed, and the
  control cannot show that fire stops a bare colonist.
- The planted run (PYRE_PLANT_RING_GAP=1, west edge unlit, evidence/run_firefoam_planted_ring_gap2.log) read the
  control PASS: the colonist stood at (227,34) for 1250 ticks, then the fire spread into its cell and burned it (3 burns).
  So the control reads chance, not the ring: it passed with the gap and failed without it.
- The `inside` box of `_harvest_through_fire` (x+2..x+6) counts the ring's inner column once the ring is 3 cells thick.

Why the fix is not known: a solid ring needs every ring cell burning at once (relight the refused cells until all burn, or
lay a fuel that always lights), and the fruit's own fires make every colonist wait whatever it carries; which scene shows
"the sprayer gets you through fire a bare colonist cannot cross" is a scene-design call (Designer, scenes.json).

## verify
Stage 6, tier pyrelands: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains firefoam_sprayer`
on a reloaded site; then with PYRE_PLANT_RING_GAP=1 (through WSLENV).

## criteria
- The control row PASSes on the real build (the bare colonist is stopped by fire or burned) and FAILs with
  PYRE_PLANT_RING_GAP=1, in one sitting.
- The sprayer row shows the sprayer colonist taking fruit while the ring still burns, where the bare colonist could not.

## Acceptance test
The command above: component without_sprayer_fire_stops_or_burns PASS, and FAIL under PYRE_PLANT_RING_GAP=1. Red now
(visit 5: FAIL on the real build, design/concepts/Pyrelands/version/in_game/visit_5/evidence/pv5_firefoam_repaired2.json).

## refs
file: src/RimMandrake/Pyrelands/validation.py
