# Proof hooks 2026-10-09 (FOUNDRY helper)

(append per item)
- PATCHAPPLIER_FORCED_MISS_PROBE_1: built d2bd41b0a, landed d99ab07c5. ExplosiveKnockback RM_PatchApplierProbe.Probe (static_call type RimMandrake.ExplosiveKnockback.RM_PatchApplierProbe method Probe). Expect patched=0 missing=1 feature=Forced-miss probe settingOff=True isBroken=True.
- ELDER_TREASURE_PROOF_HOOK_1: f0a40050e. static_call type=RimMandrake.DivingInteraction.RM_ElderTradeUtility method=ProofTreasures -> count=N names=...
- FEVERWOOD_LIMB_PROOF_HOOK_1: 57e7044af (landed 56d71f272). type=RimMandrake.FeverWood.RM_FeverWoodProof method=ProofLimbs -> limbs cap pressure chorusSilenced sentinels blockedUntil cooldownLeft. selftest_feverwood passed.
- SWIM_HOOD_CANDRAW_PROOF_1: 8e97e6803. type=RimMandrake.StarWars.JawaRules.JawaHoodProof method=ProofHood -> hooded swimmingHooded pawn swimming canDraw flags toggle. Needs a swimming hooded pawn on the map or reports swimming=false.
- WASTE_RUN_SIGNAL_DEBUG_HOOK_1: 061bda171. RimMandrake.Utinni.WasteRun.WasteRunProof ProofGizmo/ProofPress. DUNES d15df5865 RM_DunesProof.ProofTint. SETTINGS+map_comp_read: 1b7fbe441 companion source only, NOT deployed. All 7 implemented in ledger.
