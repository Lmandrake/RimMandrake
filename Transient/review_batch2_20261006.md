# Review batch 2 — 2026-10-06 (FOUNDRY helper, offline)

Full-file review, real bugs only. Engine facts read from RimSage (decompiled 1.6): CompPowerTrader,
GenDraw.DrawRadiusRing, JobDriver_Deconstruct, ThingWithComps.Destroy, StunHandler.StunFor,
Pawn_HealthTracker.HealthTick, Pawn.Tick, CompGlower, GlowGrid.RegisterGlower.

Not committed. Uncommitted: RM_CompTetherPull.cs plus the rebuilt CreatureBehaviors DLL and .srchash,
and infrastructure/state/code_review/FOUNDRY.jsonl (11 clean marks).

## CreatureBehaviors
- RM_CompTetherPull.cs: FIXED. `PostDrawExtraSelectionOverlays` passed the raw tuned range to
  `GenDraw.DrawRadiusRing`. Lance range can legally reach 30 (slider) x 1.3 (Hyperweave) x 3 (multiplier)
  = 117 cells. Anything above `GenRadial.MaxRadialPatternRadius` logs a red error ("Cannot draw radius
  ring") and draws no ring. The ring is now clamped. The pull logic itself is unchanged: target targeting,
  reeling, snap/release, the Scribe keys and the tick choice (both hosts are tickerType Normal) all
  reviewed fine. Rebuilt with winbuild. NOT marked clean (uncommitted edit).
- RM_Building_TractionLance.cs: CLEAN. ResetPower is unconditional and the boost resets on release.
  powerOutputInt is not scribed, and SetUpPowerVars restores it on load. The fuel→RanOutOfFuel signal
  does not turn a consumer off. The proof helpers are debug-only.

## Wreckage (C# only; defs not touched)
- RM_CompSalvageLoot.cs: CLEAN. PostDestroy runs after base.Destroy with mapHeld captured first. Its
  only gate is DestroyMode.Deconstruct.
- RM_Patch_DeconstructSalvager.cs: CLEAN. Target is `protected override void FinishedRemoving()` on
  JobDriver_Deconstruct, which exists. The prefix+finalizer pair brackets the Destroy call.
- RM_WreckageMod.cs: CLEAN.

## WeepingStones
- RM_JobDriver_StockPoolPen.cs: CLEAN. The job-level fail is Destroyed (not Despawned), the spawn check
  sits on the goto only, and the count guard is in place.
- RM_JobDriver_FeedPoolPen.cs: CLEAN. The WorkGiver sets count=1.
- RM_JobDriver_NetPoolBreeder.cs: CLEAN. StunFor with addBattleLog false has no side effects.
- RM_JobDriver_CullVhorrin.cs: CLEAN.
- RM_PoolBreederUtility.cs: CLEAN.
- Design note, not a defect: the hold is 900 ticks plus the wait. If the walk takes longer than 900
  ticks, the target can move off again.

## TerminalBiomes
- RM_CompGlowerMobile.cs: CLEAN. Pawn.Tick → ThingWithComps.Tick → CompTick.
  - Note: Pawn.Tick also calls TickRare every 250 ticks, so the old CompTickRare override probably DID
    fire. The current CompTick is correct either way.
  - Minor: ForceRegister registers even when the glower is unlit. That is harmless for pawn glowers.
  - No def carries this comp yet.
- RM_HediffComp_Sunk.cs: CLEAN. HealthTick iterates a copy of the hediff list, so AddHediff mid-tick is
  safe. The scar fires at a severity of 0.05 or below, before ShouldRemove at 0.
