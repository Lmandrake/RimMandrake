# FOUNDRY bridge belt 2026-10-10

## milestones
- 06:45 tier acc_20261009d applied (68 mods), deploy 138 files in sync, launched via steam
- 06:49 game UP (3 min load, 68 mods). Coordinator/owner: continue into L2 after L1.
- 06:55 L1 sweep (src/RimMandrake/Utils/scenes/l1_sweep_20261010.py + Transient/l1_log_20261010.py): 
  - PASS KINETIC_BLAST_WEAPONS_1 EK.load (log: ExplosiveKnockback Harmony patched 4 missing 0; 0 error lines naming mod), KA.load (KineticArms patched 2 missing 0; FleckDef RM_Fleck_KineticRing found; RM_ThingSetMaker_KineticRuins type resolves; probes absent->0/False).
  - NOT RECORDED: SUMP_NOOTHELM_B_PLANT_1 A1 (defs found, but recipe 'ingredients' field read does not show RM_RawLanneth - UNMEASURED, reader blind); ZERSIUM L4 (RSW_Zersium notFound: Armoury not in this 68-mod tier, config gap not a fail); LASSO A2 (config Mod_2944488802_Core.xml has no LassoSpawnChance element -> FAIL per rule, owed fix at game-down); EXCAVATION_WALL_ART A2 half (PNGs no magenta; TrapSpikeArmed still referenced in FlowWorks human_review.py/validation_v2/review html - not a def, undecided); LINKED_GRAPHIC A2 (68-mod not 15-mod config, menu-time log only).
  - Log noise: donor-missing cross-refs (OuterRim_*, ZBiome_*, CypreJungleMud) expected on minimal list; QuestNode_End rejects RUT_HistoryEvent_EggAssassination success/failedOrExpiredHistoryEvent fields (real? EggReckoning).
- 07:05 quicktest started (start_debug_game_ready -> Playing). HAZARD_CLOCK_INSPECT_LINES_1 A1 PASS (src/RimMandrake/Utils/scenes/l1_hazard_clock_20261010.py, Grey Sea surface map, tile 114502): player-owned lit SunLamp after ProofBurn 1h inspects 'Burning steadily for 1 hour' (0 seconds before burn); unlit lamp shows only vanilla power lines. TRAP: lamps spawned with spawn_batch have no faction so IsWorklightClass is false (lamps=0) - use build_batch faction=player. RM_Skylight with no well-ledger entry inspects empty (A2 well half needs a ledger-registered well; not done).
