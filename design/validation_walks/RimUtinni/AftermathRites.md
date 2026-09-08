# AftermathRites — validation walk
subject: src/RimUtinni/AftermathRites  (packageId `mandrake.rut.aftermath`)
deps: mandrake.rm.aftermath (hard modDependency — the RM_AftermathRuleDef/RM_AlliancePairDef defTypes and the AftermathRuleRunner engine live there); loadAfter also names mandrake.rm.ninefold (soft, godTie is a plain string field, no hard dep)
list: minimal+mandrake.rm.aftermath
status-hint: defs-only companion supplying 8 RM_AftermathRuleDefs (campaign-specific aftermath-raid rules, each naming a real Ash'karr faction, a vanilla IncidentDef payload and a Ninefold god tie) and 5 RM_AlliancePairDefs, as DATA for mandrake.rm.aftermath's engine — carries no C#.

## must be true
- Both def files load without XML/type errors — RM_AftermathRuleDef and RM_AlliancePairDef are types defined in mandrake.rm.aftermath's C#, so a missing/inactive engine mod makes every def in this mod fail to resolve, not just warn.
- Exactly 8 RM_AftermathRuleDef defs exist: RM_AftermathRule_RegroupAndReturn, RM_AftermathRule_AlliesArrive, RM_AftermathRule_ScavengersOnTheField, RM_AftermathRule_TheyComeForTheirOwn, RM_AftermathRule_ShkaarsEscalation, RM_AftermathRule_ZizziksAftermath, RM_AftermathRule_TheRootedReceipt, RM_AftermathRule_TheReckoning.
- Only rules 1-3 (`triggerKind=BattleOutcome`) are evaluated live this build (per the file's own header, citing AftermathTriggerKind.cs); rules 4-8 carry real telegraph/letter/godTie data but their triggerKind isn't wired yet — this is documented status, not a bug to "fix" in this walk.
- Every `payloadIncidentDefName` is a real vanilla IncidentDef (RaidEnemy or ShortCircuit) — the header explicitly records that no third-party IncidentDef defName is used because none was verified to exact-defName precision.
- Exactly 5 RM_AlliancePairDef defs exist, 2 reachable by the current engine (the Geonosian Hive / Free Droid Enclaves pair, both directions) via rule 2's BattleRecord-close path; 3 "Blackstar-hire" pairs (HuttCartel/Pirate, Empire/Pirate, Helix/Pirate) are shipped as data ahead of rule 8's real trigger, not reachable by anything in this build yet.
- Every FactionDef named in the alliance pairs is real: Jawa_GeonosianFoundryHive, Jawa_FreeDroidEnclaves, Jawa_Junkers, Jawa_HuttCartel, Jawa_AscendantHelix (this tier's own FactionDefs), plus vanilla Core `Pirate` and `Empire` (the campaign's Blackstar Company / Galactic Empire are reskins of these, not new defNames).

## the walk
1. [L] Player.log after load (minimal+mandrake.rm.aftermath list) contains no "Config error in mandrake.rut.aftermath" and no XML error naming RM_AftermathRuleDefs.xml or RM_AlliancePairDefs.xml
2. [D] def read-back: RM_AftermathRuleDef RM_AftermathRule_RegroupAndReturn exists; triggerKind=BattleOutcome, triggerOutcomes=[Routed], minSurvivors=3, payloadIncidentDefName=RaidEnemy, payloadFactionMode=SameAsTrigger, godTie=Shkaar, godDelta=8
3. [D] def read-back: RM_AftermathRuleDef RM_AftermathRule_TheReckoning exists; triggerKind=TakingEventWitnessed, payloadFactionMode=HuttClaimant, godTie=MobUnloo, godDelta=-5
4. [B] jawa/get_def {defType: "RM_AftermathRuleDef", defName: "RM_AftermathRule_ScavengersOnTheField"} → expect resolved triggerOutcomes contains "Repelled", payloadFactionMode=SameAsTrigger, godTie=Rekko, godDelta=-6
5. [B] jawa/get_def {defType: "RM_AlliancePairDef", defName: "RM_AlliancePair_GeonosianHive_FreeDroidEnclaves"} → expect resolved a=Jawa_GeonosianFoundryHive, b=Jawa_FreeDroidEnclaves, weight=1
6. [D] def read-back: RM_AlliancePairDef RM_AlliancePair_HuttCartel_Blackstar exists; a=Jawa_HuttCartel, b=Pirate
7. [B] jawa/get_defs {defs: "RM_AftermathRuleDef/RM_AftermathRule_RegroupAndReturn;RM_AftermathRuleDef/RM_AftermathRule_AlliesArrive;RM_AftermathRuleDef/RM_AftermathRule_ScavengersOnTheField;RM_AftermathRuleDef/RM_AftermathRule_TheyComeForTheirOwn;RM_AftermathRuleDef/RM_AftermathRule_ShkaarsEscalation;RM_AftermathRuleDef/RM_AftermathRule_ZizziksAftermath;RM_AftermathRuleDef/RM_AftermathRule_TheRootedReceipt;RM_AftermathRuleDef/RM_AftermathRule_TheReckoning"} → all 8 resolve, none missing
X. [S] none — pure data defs, nothing to look at visually; behavioural proof of rules 1-3 actually firing a raid belongs to mandrake.rm.aftermath's own walk (this mod only supplies the data they read).
