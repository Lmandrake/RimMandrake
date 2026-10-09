# Rites census 2026-10-09 (FOUNDRY helper)

Script: `Transient/belt_rites_census_20261009.py` run on origin/main af96461c0. Sanity probe: it finds the two fixed Rites behaviors by name and all 2666 src xml files parse-scanned.

Rule checked: every RitualBehaviorDef declares `<roles />` (vanilla Dialog_BeginRitual.CreateRitualRoleAssignments foreach-es it; null NREs).

| def type | count | notes |
|---|---|---|
| RitualBehaviorDef | 3 | RUT_JoiningWaterBehavior, RUT_NineFaultsBehavior, RUT_TheReturnBehavior: all PASS (the three fixed at af95c91e6) |
| RitualPatternDef | 3 | each names a local behavior, outcome and target filter that exist |
| PreceptDef (ritual) | 3 | ritualPatternBase resolves to the local pattern in all three |
| RitualOutcomeEffectDef | 4 | 3 RUT_ plus RM_Ishko_RitualOutcome_PlaceSacredMark (SacredGraffiti, referenced by no rite by design) |
| RitualObligationTargetFilterDef | 3 | RUT_SlimeHandRing, RUT_FreshFind, RUT_DebtStoneWithWater |
| RitualObligationTrigger / Stage / Role defs | 0 | none authored |

Other shapes checked: the Greentide patch only retargets vanilla TreeConnection / GauranlenTree workers (no new behavior). The `.rid` ideoligion files reference no RUT_ rite. No broken rite found; nothing to fix.

Live proof: JoiningWater proven in sitting 3. Re-check items filed for the other two: NINEFAULTS_RITE_START_RECHECK_1, THERETURN_RITE_START_RECHECK_1.
