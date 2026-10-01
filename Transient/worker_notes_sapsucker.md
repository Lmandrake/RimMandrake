# FEVERWOOD_SAP_SUCKER_MISHANDLE_HOOK_1 — worker notes

- No item prose file exists; spec = ledger file event + closed FEVERWOOD_SAP_SUCKER_TUNING_1.md item 2.
- [x] Signature (RimSage): `internal bool Pawn_MindState.CheckStartMentalStateBecauseRecruitAttempted(Pawn tamer)`; sole caller InteractionWorker_RecruitAttempt.Interacted, failed-tame branch only. `Pawn_MindState.pawn` is a public field.
- [x] Harmony ref in csproj ($(HarmonyDll), same as CreatureBehaviors) + brrainz.harmony modDependency/loadAfter; duplicate CreatureBehaviors reference removed.
- [x] RM_Patch_SapSuckerMishandle postfix -> RM_CompSapSuckerRefusal.NotifyMishandled (hediff + sibling RM_CompPlantAlarm.TriggerAlarm). Ollareth given a hediff-less SapSuckerRefusal comp so its alarm rings on a failed tame.
- [x] Mod Settings toggle `sapSuckerMishandleRefusalEnabled` (default on).
- [x] Built clean (0 warnings, 0 errors). UNTESTED LIVE.
- Not covered: failed training of a tame animal (different seam).
