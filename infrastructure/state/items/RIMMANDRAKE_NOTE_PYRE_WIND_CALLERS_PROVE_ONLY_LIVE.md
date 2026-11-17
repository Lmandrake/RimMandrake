# RIMMANDRAKE_NOTE_PYRE_WIND_CALLERS_PROVE_ONLY_LIVE

Wind-carry callers' planted faults survive every offline test (Polish, stage 6)

## spec
Seven planted faults in the wind carry's game-side callers (FireEcologyHook Carry lighting every probe, the spread prefix always vanilla, carried fires forgotten, MarkCarried a no-op, the front line along the wind, the scar wind unset) and one kernel fault (Downwind cone widened) stayed green in T_FUZZ, T_BURN_ECOLOGY (the Python model) and lane 1. Bar burn_line_walks proves at stage 6 (sc_burn_line_walks), so the live scene is the decider; an offline caller check (a static read like entry_gated, or the model driven from the C# caller) would catch them earlier. Polish: not part of passing.

## verify
Acceptance test: none, the decider is the live scene sc_burn_line_walks at stage 6; an offline guard is optional Polish

## criteria
The named command passes at the fix sha; the planted fault (lane2/planted_faults.json) is caught.

## refs
file: src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs
file: src/RimMandrake/Pyrelands/Source/MapComponent_BurnLine.cs
