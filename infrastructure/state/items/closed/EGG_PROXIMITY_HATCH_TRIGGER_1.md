# EGG_PROXIMITY_HATCH_TRIGGER_1

## Spec
Owner, 2026-09-08 (verbatim): "Still need to dev a trigger for eggs that
hatch at you on proximity." Eggs (JawaIkee/SWBestiary fauna) hatch when a
pawn approaches — an ambush/horror beat, not a timer.

BirthHatchDemo (src/RimUtinni/BirthHatchDemo) is the existing dev demo
for birth/hatch machinery — start there; its retirement (consolidation
map R14) is GATED on this item extracting whatever it still teaches.

## Verify
Quicktest: pawn walks near a proximity egg → hatch fires with the
creature aggroed; distant eggs stay dormant.

## Criteria
Trigger radius/def-configurable; works for at least one shipping egg
def; BirthHatchDemo either retired or explicitly kept with reason.
