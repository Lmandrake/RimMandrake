# STASIS_LOCKER_BUILD_ANCIENT_COMPLEX_LOOT

## verify

The supervisor's live round (relentless_live_round.py) runs each line below on a game-up sitting (LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST).
The defs must resolve first: a log silent about a def the load never had is not a pass.
A1: the two found-grade PrefabDefs must resolve; a failed patch names Patches/ColdStorage_AncientComplexLoot.xml on its file: line (live_log_check joins it to the record).

live-proof A1: python3 src/RimMandrake/Utils/live_def_check.py --has PrefabDef/RM_AncientStasisLocker_Wrecked_Edge --has PrefabDef/RM_AncientStasisLocker_Kludged_Edge && python3 src/RimMandrake/Utils/live_log_check.py --absent ColdStorage_AncientComplexLoot --absent RM_AncientStasisLocker_
