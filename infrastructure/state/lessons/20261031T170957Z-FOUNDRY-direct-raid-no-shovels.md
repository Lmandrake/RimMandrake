A raid spawned through jawa/spawn_pawn (raid_trench_proof --direct) skips IncidentWorker_Raid.PostProcessSpawnedPawns, so every postfix there (RM_Patch_Raid_Shovels) never runs: the direct raid held no shovel and could not fill by construction. Hand the gear the real incident would have, and read it back (CAUSEWAY_DIAGNOSE_WAITS_AT_THE_LIP, 2026-10-31).
home: skills/live-debugging-proof-harness
