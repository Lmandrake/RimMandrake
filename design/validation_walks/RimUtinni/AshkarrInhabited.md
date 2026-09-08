# AshkarrInhabited — validation walk
subject: src/RimUtinni/AshkarrInhabited  (packageId: mandrake.rut.inhabited)
deps: mandrake.rm.inhabited (modDependencies + loadAfter)
list: minimal+mandrake.rm.inhabited
status-hint: Data-only SettlementManifestDef/SecurityProfileDef instances (districts, cast slots, gate posture) for four named Ash'karr settlements, one per faction — schema owned by mandrake.rm.inhabited, no art/verb/claim logic of its own.

## must be true

- Four SecurityProfileDefs exist: `Inhabited_SecurityProfile_Junkers`, `Inhabited_SecurityProfile_HuttCartel`, `Inhabited_SecurityProfile_FreeDroids`, `Inhabited_SecurityProfile_Deepwater`, each with the spec'd `searchesLeavers`/`searchChance` pair (false/0, true/0.6, false/0, true/1).
- Four SettlementManifestDefs exist: `Inhabited_Manifest_TheClaimJump`, `Inhabited_Manifest_DeepwaterHold`, `Inhabited_Manifest_GorgaPalace`, `Inhabited_Manifest_TheCrackingYard`.
- Each manifest's `securityProfile` field names one of the four SecurityProfileDefs above — no dangling reference.
- Each manifest's `factionDefName` names a real, loaded FactionDef (`Jawa_Junkers`, `Jawa_DeepwaterCompact`, `Jawa_HuttCartel`, `Jawa_FreeDroidEnclaves`).
- Each manifest's `place` field names an `InhabitedPlaceDef` from the `mandrake.rm.inhabited` tier (`RM_InhabitedPlace_Scrapyard`, `RM_InhabitedPlace_WaterHold`, `RM_InhabitedPlace_Palace`, `RM_InhabitedPlace_MachineHold`).
- Each manifest's first district (`districts[0]`) is the one the v1 compose step actually reads — scrapyard / cistern hall / palace hall / charging hall respectively — and `castSlots` is non-empty.

## the walk

1. [L] Player.log after load contains no `Config error in mandrake.rut.inhabited` and no XML error naming `SecurityProfileDefs_District2.xml`, `SecurityProfileDefs_Junkers.xml`, or any of the four `SettlementManifestDefs_*.xml` files.
2. [D] def read-back: SecurityProfileDef `Inhabited_SecurityProfile_Junkers` exists; searchesLeavers=false; searchChance=0
3. [D] def read-back: SecurityProfileDef `Inhabited_SecurityProfile_HuttCartel` exists; searchesLeavers=true; searchChance=0.6
4. [D] def read-back: SecurityProfileDef `Inhabited_SecurityProfile_FreeDroids` exists; searchesLeavers=false; searchChance=0
5. [D] def read-back: SecurityProfileDef `Inhabited_SecurityProfile_Deepwater` exists; searchesLeavers=true; searchChance=1
6. [D] def read-back: SettlementManifestDef `Inhabited_Manifest_TheClaimJump` exists; factionDefName=Jawa_Junkers; securityProfile=Inhabited_SecurityProfile_Junkers; place=RM_InhabitedPlace_Scrapyard; districts[0].label="scrapyard"
7. [D] def read-back: SettlementManifestDef `Inhabited_Manifest_DeepwaterHold` exists; factionDefName=Jawa_DeepwaterCompact; securityProfile=Inhabited_SecurityProfile_Deepwater; place=RM_InhabitedPlace_WaterHold; districts[0].label="cistern hall"
8. [D] def read-back: SettlementManifestDef `Inhabited_Manifest_GorgaPalace` exists; factionDefName=Jawa_HuttCartel; securityProfile=Inhabited_SecurityProfile_HuttCartel; place=RM_InhabitedPlace_Palace; districts[0].label="palace hall"
9. [D] def read-back: SettlementManifestDef `Inhabited_Manifest_TheCrackingYard` exists; factionDefName=Jawa_FreeDroidEnclaves; securityProfile=Inhabited_SecurityProfile_FreeDroids; place=RM_InhabitedPlace_MachineHold; districts[0].label="charging hall"
10. [B] jawa/get_defs {defType: "RimMandrake.Inhabited.SettlementManifestDef", fields: ["districts", "castSlots", "securityProfile", "factionDefName", "place"]} → all four manifests resolve with non-empty `castSlots` and a first district matching step 6-9's labels; confirms the RESOLVED def (post-inheritance), not just the raw XML
11. [B] jawa/list_factions → `Jawa_Junkers`, `Jawa_DeepwaterCompact`, `Jawa_HuttCartel`, `Jawa_FreeDroidEnclaves` all appear as real, loaded factions on the live world — confirms every manifest's `factionDefName` resolves to something that actually exists in this campaign
12. [S] (human pass) walk each of the four settlements in-game and confirm district shapes/adjacency and cast NPC placement read correctly against the manifest's authored intent
