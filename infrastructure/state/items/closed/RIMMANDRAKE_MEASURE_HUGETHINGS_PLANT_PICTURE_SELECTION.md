# RIMMANDRAKE_MEASURE_HUGETHINGS_PLANT_PICTURE_SELECTION

## spec
The giant-plant promise's must-show line `plant_click_selects_picture` (design/validation_walks/RimMandrake/HugeThings.md
north star) has no instrument: `src/RimMandrake/HugeThings/northstar/showcase_plants_live.py` reports its SELECTION row
UNMEASURED because no bridge or static hook reads `Thing.CustomRectForSelector` / the selection rect for a placed plant.
Add a read (a `TitanValidationHooks`-style static hook in HugeThings returning the selector rect for a thing id, or a
bridge endpoint) and wire it into the showcase so the row compares that rect with the drawn picture's rect it already
records. Found by the fresh judge of RIMMANDRAKE_SPLIT_HUGETHINGS_PLANT_AND_TITAN_PROMISES, 2026-11-11.

## verify
L0: hook compiles and a selftest drives the row with a fake bridge; L2: live plant showcase row PASS on a restored site.
