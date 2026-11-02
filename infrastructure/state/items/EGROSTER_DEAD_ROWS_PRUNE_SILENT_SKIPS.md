# EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting and records the
verdict with `rimflow verify` on the built sha. The roster def must resolve first: a log silent about a def the load
never had is not a pass. The pruned rows are RSW_Scrubgrass, RUT_RustPuff, RUT_PaleTree, RUT_PaleMoss,
RUT_Placeholder_GreentideGiantTree and RSW_Plant_MujaFruit_Wild.

A1: the registry skips a row whose `plant` string resolves to no ThingDef (GetNamedSilentFail), so every
RM_/RUT_/RSW_ row of RUT_ExplosiveGrowthRoster_Campaign (UtinniPatches Defs/ExplosiveGrowth/RUT_ExplosiveGrowthRoster.xml,
15 rows on 2026-11-02) must resolve as a ThingDef in the live game.
Live proofs (one line per criterion, read by relentless_live_round.py): infrastructure/state/live_proofs/EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS.txt
