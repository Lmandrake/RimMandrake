# EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting and records the
verdict with `rimflow verify` on the built sha. The roster def must resolve first: a log silent about a def the load
never had is not a pass. The pruned rows are RSW_Scrubgrass, RUT_RustPuff, RUT_PaleTree, RUT_PaleMoss,
RUT_Placeholder_GreentideGiantTree and RSW_Plant_MujaFruit_Wild.

live-proof A2: python3 src/RimMandrake/Utils/live_def_check.py --has RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef/RUT_ExplosiveGrowthRoster_Campaign && python3 src/RimMandrake/Utils/live_log_check.py --warnings --absent RUT_ExplosiveGrowthRoster --absent RSW_Scrubgrass --absent RUT_RustPuff --absent RUT_PaleTree --absent RUT_PaleMoss --absent RUT_Placeholder_GreentideGiantTree --absent RSW_Plant_MujaFruit_Wild
