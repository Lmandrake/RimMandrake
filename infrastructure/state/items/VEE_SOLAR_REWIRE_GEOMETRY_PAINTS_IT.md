# VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting (LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST).
The defs must resolve first: a log silent about a def the load never had is not a pass.
A1: both mutators are TileMutatorDefs of mandrake.rm.solarmirrors; a patch failure carries the mod name "Solar Mirrors", a config error the defName.

live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has TileMutatorDef/RM_StrongInsolation --has TileMutatorDef/RM_Sunless && python3 src/RimMandrake/Utils/live_log_check.py --absent SolarMirrors --absent 'Solar Mirrors' --absent RM_StrongInsolation --absent RM_Sunless
