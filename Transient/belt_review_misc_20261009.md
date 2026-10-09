# Belt review misc 2026-10-09

(skeleton; findings below)

## Findings so far (diff-scoped read of every in-scope commit)
- RM_MapComponent_ChillGardenDefense.cs ExposeData: old saves lack escalationScore (defaults 0, losing tier-2 progress). FIXED: PostLoadInit raises it to offenseScore.
- WasteRunProof.cs ProofPress: Enum.TryParse accepts numeric strings -> undefined enum. FIXED: Enum.IsDefined guard.
- RM_ElderTradeUtility.Offer: OK (deliveryCell/map validated before; rollback correct). DI-5 RemapRenamedKeys OK (Resolve returns null when unmapped; single overload).
- AxisKernel/GradientAxis surge grid OK (missing key tolerated by ExposeUshort; old save requested=0 -> fraction 1).
- WarblingGlow OK. HeatedSuit OK (null room guarded). Zuurrik SS-2 OK. LP-7 cache OK. LP-6 OK.
- EH venom inspect line (CompContactVenom.cs): lists every colonist in contact on the map, not only those in THIS stand; low severity, in a peer-adjacent mod, not changed.
- Stillsand dune hook: old Harmony target gone, now event listener (RM_DuneEvents) OK.

## Landed / marked
- cb93dae7a: Garden old-save floor + WasteRunProof enum guard (DivingInteraction and WasteRun DLL+srchash rebuilt; diving fuzz + lint pass).
- mark-clean (full read, zero findings): RM_LastOutcomeLog, RM_ExcavationSanityMath, TapLedger, RM_HazardClockInspect, RM_DuneEvents, RM_PatchApplierProbe, RM_FeverWoodProof, MovingDunesTintProof, RM_HazardNativeExtension, RM_Alert_VenomContactClock, LuminousSettingsReadouts, DeepfireHealthDebugActions, MapComponent_DeepfireLights.Health.
- NOT marked: edited files (ChillGardenDefense, WasteRunProof need second full pass after commit) and large pre-existing files read diff-only (not full-file).
- Peer-dirty files (FlowWorks RimMandrakeFlowWorksMod.cs, TakenByLand) reviewed read-only: FL-5 reset (static dictionary snapshot) OK, no finding.
