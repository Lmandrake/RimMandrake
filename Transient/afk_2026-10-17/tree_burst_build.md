# TREE_BURST_BUILD_LITRES_BUY_YEARS — progress (BENCH AFK, 2026-10-17)

Design: design/RimMandrake/tree_burst_design_2026-10-17.md (§8 rulings, §9 build delta)

## Status
- [x] read design §8/§9
- [x] survey ExplosiveGrowth as built
- [x] C# changes
- [x] def/roster changes (RM + RUT twins)
- [x] plant defs: 16 small plants no wood; Kneeling Ollim size 3.0; Sweetline 480 days, 12x life
- [x] Mod Settings
- [x] build + review + selftests
- [x] validation script row
- [x] commit/publish

## Notes
- 13:xx C# written (kernel tree fns, registry isTree/fungus, RM_TreeLife drink+burst prefix, TopResolver.TreeBurst, settings group, ProofTreeLife); DLL builds clean.
- Census finding: six plants are trees by the size-only rule but missing from design §7 table: RM_DulcisPlant (a mushroom -> marked fungus), RM_GlowGlobe, RM_KeeningCordax, RM_Maddrick, RM_Phorrik, RM_Thulvane (follow the rule; FLAG for owner).
- XML: T6 15 small plants stripped of wood (Brelloch keeps salt, loses the Wood tag); T7 Pyrelands grass bursts; T8 Rot -> wetNativeBiomes (both rosters), 32 None rows -> Churn, PaleTree/Skulltop None+DryNative; fungi list + treeRulesExempt RM_Greatbole; T9 Sweetline 480/x12, Kneeling Ollim 1.6~3.0.
- Selftests: kernel fuzz (new `tree` family, mutation-checked), archetype seed selftest updated (Q7, tree/fungus columns), validation.py static PASS (also fixed pre-existing sprinklersEnabled DEFAULTS miss).
- Committed c698bbe683. Marked clean: 9 C# files + archetype_seed.py (ExplosiveGrowthFuzz.cs, validation.py, northstar_site.py left DIRTY: not fully re-read).
- FloodedCanyon/validation.py pinned RM_Harrovaq -> WoodLog (passed before, failed after Q3); updated to the ruling, cited.
- OWED deploys (game RUNNING / FOUNDRY holds bridge): Baroque Biomes (ExplosiveGrowth DLL + roster), Contagion, FeverWood, FloodedCanyon, GelatinousSlime, Greentide, LanternDeeps, LeaningScrub, Miasma, Stillsand, TerminalBiomes, TheForge, TheSump flora defs, UtinniPatches roster.
- OWED live rows: probe_tree_life, probe_tree_burst_off, probe_rules (tree arm now wants x0.1 / x1).
