modcheck composes a mod's hard dependencies only, so a live row that reads another mod's defs (UtinniPatches reading Armoury's RSW_Phrik) fails 'def did not load' on a list that never carried that mod. Before classing such a FAIL as MOD FAILURE, read the job's worker.log 'deploy: with ...' line; the repair is a modcheck_closure tier in modset_builder.py (guard: modcheck/selftest_live_defs_on_the_list.py).
item: ASTEROID_DESERT_ORES_1
home: skills/live-debugging-proof-harness
