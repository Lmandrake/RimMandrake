# belt_forge_20261009n — SHIP_ALLOY_FORGE_1

- [ ] claim
- [ ] read item + design
- [ ] search src
- [ ] build
- [ ] script
- [ ] publish
- [ ] implemented
- [x] claim (lease FOUNDRY.pid39844.d29862b7)
- [x] read item, design §0 §3.2-3.4 §6; VFE ProcessDef supports researchPrerequisites; forge processes list on CompProperties_AdvancedResourceProcessor
- WreckedMachines owns the ship smelter ladder (RM_WM_AutomatedSmelter_*), hides donor smelter
- PLAN: WM (RM tier) gets RM_WM_AlloyForgeRestoration (early, after smelter restoration) gating the VFE forge + RM_WM_PlasteelAlloying (late) gating VFEFactory_AlloyPlasteel, settings-gated patches; Armoury (RSW) adds RSW_AlloyDurasteel ProcessDef by patch, conditional on RSW_Durasteel existing (CANON_MATERIALS_BUILD_1 not built yet)
- toggles via runtime reflection (ProcessDef.researchPrerequisites, CompProperties_AdvancedResourceProcessor.processes), WM pattern; writing files now
- WM: research defs, AlloyForgeGates patch, settings+patcher C# written
- Armoury: durasteel patch (conditional on RSW_Durasteel), settings toggle, toggle C# written; building
- NOTE 21:19 a peer pull --autostash briefly swept my tracked edits; restored on reapply
- building validation now
- validation: WM static PASS (+2 drives, alloy_forge_gated chain); Armoury durasteel_static PASS; walks updated
- item prose updated; publishing
