# VaultDungeons — validation walk
subject: src/RimUtinni/VaultDungeons  (packageId mandrake.rut.vaultdungeons)
deps: OskarPotocki.VanillaFactionsExpanded.Core (KCSG framework, modDependencies + loadAfter)
list: minimal+OskarPotocki.VanillaFactionsExpanded.Core
status-hint: six Forsaken-vault dungeons (three KCSG StructureLayoutDef templates x concentric rings) plus the VAULT_THAW_QUEST_FAMILY_1 quest layer that places each as a fixed-tile Site.

## must be true
- Three StructureLayoutDefs exist (RUT_VaultType1_MechanoidGarrison, RUT_VaultType2_FleshWeaponLoose, RUT_VaultType3_FrozenRakata), each a KCSG-consumable template.
- Six RUT_VaultThaw_V*_ QuestScriptDefs exist plus RUT_VaultClaimConflict and RUT_Reclamation, each placing its vault on a FIXED PlanetTile (no worldgen).
- Three SitePartDef/GenStepDef pairs exist (Type1/2/3), each GenStepDef's genStep is KCSG.GenStep_CustomStructureGen citing the matching StructureLayoutDef by defName.
- RUT_VaultHeart (ThingDef) exists as the core-ring interactable that gates V3's thaw.
- HistoryEventDefs_Vaults declares the 8 outcome events (visited/garrison broken/sleepers woken or killed/left sleeping/claim refused/Helix sided/reclamation survived) that the quest family's signal listeners depend on.
- SymbolDefs_Vaults declares the 12 KCSG symbols (guardians, hazards, RUT_Symbol_VaultHeart, RUT_Symbol_RakataCasket) the three layout templates place.
- Per the mod's own About.xml: "Not yet quicktest-proven" and V6's wake/loot branches listen on signals no vanilla part sends yet — this walk cannot assert those branches fire; it can only assert the defs load.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.vaultdungeons" and no XML error naming StructureLayoutDefs_Vaults.xml, SitePartDefs_Vaults.xml, QuestScriptDefs/RUT_VaultThaw.xml, or ThingDefs_Buildings/RUT_VaultHeart.xml
2. [D] def read-back: StructureLayoutDef RUT_VaultType1_MechanoidGarrison exists; StructureLayoutDef RUT_VaultType2_FleshWeaponLoose exists; StructureLayoutDef RUT_VaultType3_FrozenRakata exists
3. [D] def read-back: ThingDef RUT_VaultHeart exists
4. [D] def read-back: SitePartDef RUT_VaultSite_Type1 exists; minMapSize = (325,1,325); wantsThreatPoints = false
5. [D] def read-back: GenStepDef RUT_GenStep_VaultSite_Type1 exists; linkWithSite = RUT_VaultSite_Type1; genStep Class = KCSG.GenStep_CustomStructureGen; structureLayoutDefs contains RUT_VaultType1_MechanoidGarrison
6. [D] def read-back: SitePartDef RUT_VaultSite_Type2 exists; GenStepDef RUT_GenStep_VaultSite_Type2 cites RUT_VaultType2_FleshWeaponLoose
7. [D] def read-back: SitePartDef RUT_VaultSite_Type3 exists; GenStepDef RUT_GenStep_VaultSite_Type3 cites RUT_VaultType3_FrozenRakata
8. [D] def read-back: QuestScriptDef RUT_VaultThaw_V1_RustCathedral exists; RUT_VaultThaw_V6_Umbra exists; RUT_VaultClaimConflict exists; RUT_Reclamation exists
9. [D] def read-back: IncidentDef RUT_GiveQuest_VaultThaw_V1_RustCathedral exists (the quest's firing route) through RUT_GiveQuest_Reclamation
10. [D] def read-back: HistoryEventDef RUT_VaultSleepersWoken exists; RUT_HelixSidedWithTheWoken exists (the 8 outcome-event vocabulary the quest signals depend on)
11. [D] def read-back: SymbolDef RUT_Symbol_VaultHeart exists; RUT_Symbol_RakataCasket exists
12. [B] jawa/fire_quest {questDef: "RUT_VaultThaw_V1_RustCathedral"} → quest generates without error and becomes available (confirms the QuestScriptDef's root parses and its slate vars resolve — does not confirm V6's unfired wake/loot signal branches, which the mod's own About.xml flags as not yet proven)
13. [B] jawa/kcsg_place with structureLayoutDefs: ["RUT_VaultType1_MechanoidGarrison"] on a cleared rect → placement succeeds, no KCSG error, RUT_VaultHeart and at least one RUT_Symbol_* guardian spawn on the map
14. [S] (human pass) walk the three placed vault rings in person — ring reachability (outer/garrison/core, never skippable) is a spatial claim no automated check here proves
