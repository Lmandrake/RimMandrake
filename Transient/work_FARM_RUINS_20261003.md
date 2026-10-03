# GELATINOUSSLIME_FARM_RUINS_1 work log 2026-10-03
- Searched src/ for farmruin/slimeruin: none. Mechanic exists only as MapComponent_SlimeFieldConversion (not a genstep).
- Plan: GenStep_SlimeFarmRuins (order 752) in new Source/FarmRuins.cs + Defs/GenStepDefs/RM_SlimeFarmRuins.xml + toggle farmRuinsEnabled (worldgen-affecting, labelled).
- Built: Source/FarmRuins.cs (GenStep_SlimeFarmRuins order 752 + MapComponent_SlimeFarmRuins recording sites), Defs/GenStepDefs/RM_SlimeFarmRuins.xml, Patches/RM_SlimeFarmRuins_MapGenPatch.xml, csproj Compile, SlimeSettings.farmRuinsEnabled (labelled worldgen-affecting).
- Choices: vanilla Fence/Wall (WoodLog) at 15-50% hp, no new art/defs; footprint must be wholly slime terrain; loot Silver/Steel/WoodLog + a lost MeleeWeapon_Knife (SilentFail). The "last ledger" has no vanilla thing: not built. Artpipe: nothing needed (no new art).
- Validation: component farm_ruins_genstep_registered + setting flip + mock fault nofarmstep; selftest 57 clean/27 faults/0 problems. winbuild OK. Live criterion (list_things + review shot) NOT run (no bridge).
