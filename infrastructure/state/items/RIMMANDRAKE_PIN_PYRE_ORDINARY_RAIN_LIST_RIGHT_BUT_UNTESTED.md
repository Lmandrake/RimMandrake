## spec
Polish (Pyrelands, bar no_ordinary_rain, stage 6; blind challenge cycle 2). RM_FireEcoKernel.OrdinaryRainDefNames (Rain,
FoggyRain, RainyThunderstorm, TorrentialRain) is complete today: RimSage shows exactly those four rainRate-1 ordinary rains
across Core and Odyssey (BloodRain, ToxRain and the snows aside). But no builder test reads the list: planted fault
K_RAIN_LIST_DROPS_FOGGYRAIN survived every offline test, and sc_no_rain forces only Rain, so a dropped entry would ship. Pin
it: an offline check that the list equals the def dump's non-snow, non-blood, non-tox weathers with rainRate above 0.

## verify
The new check goes red on K_RAIN_LIST_DROPS_FOGGYRAIN (design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/planted_faults.json) and green on the shipped kernel.

## criteria
Acceptance test: python3 design/concepts/Pyrelands/version/blind_challenge/cycle_2/lane2/catch_check.py K_RAIN_LIST_DROPS_FOGGYRAIN <the new test> exits 0, 1 pass; today it has no test
to run (blind lane 1 row forced_ordinary_rain_becomes_black_rain is the only catcher).

## refs
file: src/RimMandrake/Pyrelands/Source/Kernel/RM_FireEcoKernel.cs
