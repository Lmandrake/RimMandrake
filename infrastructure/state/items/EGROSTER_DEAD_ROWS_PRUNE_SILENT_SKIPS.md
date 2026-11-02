# EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting and records the
verdict with `rimflow verify` on the built sha. The roster def must resolve first: a log silent about a def the load
never had is not a pass. The pruned rows are RSW_Scrubgrass, RUT_RustPuff, RUT_PaleTree, RUT_PaleMoss,
RUT_Placeholder_GreentideGiantTree and RSW_Plant_MujaFruit_Wild.

A1: the registry skips a row whose `plant` string resolves to no ThingDef (GetNamedSilentFail), so every
RM_/RUT_/RSW_ row of RUT_ExplosiveGrowthRoster_Campaign (UtinniPatches Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml,
15 rows on 2026-11-02) must resolve as a ThingDef in the live game.
live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef/RUT_ExplosiveGrowthRoster_Campaign --has ThingDef/RM_BloomCrop --has ThingDef/RM_CrackedThornwood --has ThingDef/RM_DyingCreep --has ThingDef/RM_GiantLeaf --has ThingDef/RM_HeatsinkFungus --has ThingDef/RM_LightPipeNub --has ThingDef/RM_Ollim --has ThingDef/RM_ScorchedStars --has ThingDef/RM_SweetlineTree --has ThingDef/RM_TwistingThorngrass --has ThingDef/RM_TwistingThornweed --has ThingDef/RSW_Plant_Chakroot_Wild --has ThingDef/RSW_Plant_HubbaGourd_Wild --has ThingDef/RSW_Plant_HydenockTree_Wild --has ThingDef/RSW_Plant_JoganTree_Wild
live-proof A2: python3 src/RimMandrake/Utils/live_def_check.py --has RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRosterDef/RUT_ExplosiveGrowthRoster_Campaign && python3 src/RimMandrake/Utils/live_log_check.py --warnings --absent RUT_ExplosiveGrowthRoster --absent RSW_Scrubgrass --absent RUT_RustPuff --absent RUT_PaleTree --absent RUT_PaleMoss --absent RUT_Placeholder_GreentideGiantTree --absent RSW_Plant_MujaFruit_Wild
