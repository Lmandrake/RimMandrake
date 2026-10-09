# Next-ten pass 2, 2026-10-09 (FOUNDRY helper)
## Low-finding fixes
(pending)
## Full-file reviews
(pending)
- FV-2 fixed: RM_MapComponent_TentacleWatch.cs TickPendingGifts requeues `rolls - placed.Count` (partial grants keep the remainder).
- Related fix same file: SpawnEncounterAt seed cell and Great Emergence Bloom cell now fall back to a free pool cell if an edifice (limb/bridge) already stands on the seed (GenSpawn would wipe it).
- DUST_SETTLED fixed: RM_HorizonWarning.cs TryFirePrefix captures spawnCenter into __state; postfix passes it to Notify_Arrived.
- ShadeHop: static EmptyPawns replaces per-call new Pawn[0] (RM_ShadeHop.cs AddLureCandidates).
- Aerial RM_MapComponent_Aerial.cs: QueueAutoLink/ProcessAutoLinks — a factionless pole (map-gen ruin) stayed queued forever, keeping a per-tick ToList + ConduitRuns pass alive; now gives up after 600 ticks (pendingSince).
- BrineEncasementUtility.cs: edifice was destroyed before jacket.TryEncase(p); a failed encase lost the building. Now destroyed only after the pawn is held.
## Full-file reviews (no findings = clean)
- RM_FlowKernel.cs, RM_ExcavationDepth.cs, RM_ExcavationSanityMath.cs, RM_MapComponent_Excavation.cs, RM_ExcavationWalls.cs: clean. Low, not fixed: ExcavationWalls.cs ScorchHalo (~line 400) allocates two 25-element arrays per undug cell on every section regen while the scorch comp exists (regen-only cost).
- RM_ShadeHop.cs, RM_CompReactionSource(+Properties), RM_CompDungSeeder(+Properties), RM_MapComponent_WellLedger.cs, RM_CompHeatedSuitBattery.cs, RM_BrineEncasement.cs, RM_MapComponent_SumpLivingMap.cs, RM_BroodRansom.cs, RM_HorizonWarning.cs, RM_MapComponent_TentacleWatch.cs: no further defects.
- Low, not fixed: Aerial DrawLocalDrops/LocalConnections allocate lists per in-view pole per frame.
- Selftests: run_selftests 254 PASS, 1 FAIL (selftest_ledger_lint.py, ledger shard, unrelated to C#).
