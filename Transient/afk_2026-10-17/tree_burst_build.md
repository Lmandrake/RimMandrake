# TREE_BURST_BUILD_LITRES_BUY_YEARS — progress (BENCH AFK, 2026-10-17)

Design: design/RimMandrake/tree_burst_design_2026-10-17.md (§8 rulings, §9 build delta)

## Status
- [ ] read design §8/§9
- [ ] survey ExplosiveGrowth as built
- [ ] C# changes
- [ ] def/roster changes (RM + RUT twins)
- [ ] plant defs: 16 small plants no wood; Kneeling Ollim size 3.0; Sweetline 480 days, 12x life
- [ ] Mod Settings
- [ ] build + review + selftests
- [ ] validation script row
- [ ] commit/publish

## Notes
- 13:xx C# written (kernel tree fns, registry isTree/fungus, RM_TreeLife drink+burst prefix, TopResolver.TreeBurst, settings group, ProofTreeLife); DLL builds clean.
- Census finding: six plants are trees by the size-only rule but missing from design §7 table: RM_DulcisPlant (a mushroom -> marked fungus), RM_GlowGlobe, RM_KeeningCordax, RM_Maddrick, RM_Phorrik, RM_Thulvane (follow the rule; FLAG for owner).
- XML: T6 15 small plants stripped of wood (Brelloch keeps salt, loses the Wood tag); T7 Pyrelands grass bursts; T8 Rot -> wetNativeBiomes (both rosters), 32 None rows -> Churn, PaleTree/Skulltop None+DryNative; fungi list + treeRulesExempt RM_Greatbole; T9 Sweetline 480/x12, Kneeling Ollim 1.6~3.0.
- Selftests: kernel fuzz (new `tree` family, mutation-checked), archetype seed selftest updated (Q7, tree/fungus columns), validation.py static PASS (also fixed pre-existing sprinklersEnabled DEFAULTS miss).
