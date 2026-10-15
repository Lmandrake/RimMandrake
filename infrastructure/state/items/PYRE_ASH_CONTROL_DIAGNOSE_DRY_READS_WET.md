# PYRE_ASH_CONTROL_DIAGNOSE_DRY_READS_WET

## cause — ROW/SITE, not the mod (MEASURED offline from the fixture)
Site r3 (`NS_Pyrelands_site_1_417df172fdb5_r3.rws`, terrain grid decoded) has a pond (hash 42032, 501 cells, ringed by
hash 25036) at x 67-72, z 180-189. The row's fixed strip at PAD_ASH (60,190) put its "far" dry control at (69,191):
the pond row z=189 is 2 cells away = `ashNaturalWaterRadius` 2, so `Sweep` marked it watered. The mod read is correct.
Pond identity is from the hash geometry, not a hash table (no same-mod-set dump): INFERRED it is water/mud.

## fix (68049f4519)
`pick_ash_strip`: the row reads the live terrain of the strip's halo (strip + radius) and moves the strip inside the pad
until no water/mud/riverbank lies within the radius; UNMEASURED if none is clear. Also probes the far cell before the
water. Selftest replays the r3 pond geometry.
