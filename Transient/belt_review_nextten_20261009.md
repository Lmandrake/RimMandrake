# Next-ten + design-rows C# review, 2026-10-09 (FOUNDRY helper)

Scope: WIRE_DOWN_ALERT_1, DECOY_SHADE_TARP_1, SPECIMEN_CABINET_DISPLAY_1, SHIP_TOW_LINE_1, DUST_SETTLED_LETTER_1,
SCREEN_STOPS_SPORES_1, VERMIN_EAT_BREEDING_FOOD_1, TAKEN_BY_LAND_SERVICE_1, THICK_LIQUID_CREEP_1, CB-1, CB-4, TB-2, TB-3,
GS-5, EH-5, DI-4, FV-2, Cauldron PatchApplier move. All new files reachable (csproj Compile Include verified or reflection-found).

## Fixed
- RM_TakenByLand.cs SafeReturn catch (was line ~225): Return() pulls the pawn out of the world's keeping BEFORE spawning it
  (RemovePawn), so any throw between (PickReturnCell, GenSpawn, policy hooks) left the pawn held by nothing and the record
  dropped (`return true`): a pawn vanishing with only a Log.Error. Now: pawn put back with PassToWorld(KeepForever), record
  kept, retried in an hour.

## Findings, not fixed (low)
- RM_BroodRansom.cs Grant (FV-2): a multi-roll gift that places SOME items loses the unplaced rolls; only a fully failed
  grant is requeued. Table-missing grants requeue hourly forever (harmless, one entry).
- RM_ShadeHop.cs AddLureCandidates: allocates `new Pawn[0]` per call when ambush is off (trivial).
- RM_HorizonWarning.cs Notify_Arrived matches def + exact spawnCenter; a worker that rewrote parms.spawnCenter would leave
  the plume up and then send a false "dust settled" letter. No worker found that does (presets honoured); not changed.
- RM_TakenByLand.cs gale Remove pins via ForcefullyKeptPawns and Return only RemovePawn()s: pre-existing pattern, left.

## Checked, no defect
- Alert_WireDown.cs: null comp guarded, fallen/links initialised, label reads list GetReport filled.
- RM_SpecimenCabinet.cs: Building_Storage cast guarded, null slot group yields nothing, XML class names exist.
- RM_CompSalvageWinch.cs: target lost/dead/unspawned/obstacle all release; pawn move via Position+Notify_Teleported; items
  DeSpawn+Spawn on a walkable checked cell; Scribe_References symmetric; ticks only past a null-target early return.
- RM_FalseShade.cs / RM_ShadeHop.cs decoy: registry rebuilt on spawn (not saved, correct), unspawned decoys skipped.
- RM_CompVerminBreeder.cs + RM_VerminFoodMath.cs: reach test capped at 8, food consumed only after a successful spawn,
  SplitOff(full stack) is safe, famine gate still every 250 ticks (that comp is a Pawn comp, not a Plant: CompTick correct).
- THICK_LIQUID_CREEP (RM_FlowKernel): stamp keyed on pulseCount+1 so stale stamps never match; kernel recreated on resize.
- RM_TakenByLand*.cs: records Scribed Deep with null removal; legacy SweptAway/GaleCarried books still tick and drain old saves;
  Count/PendingCount include the service; unregistered policy keeps the record; Decide covers missing/dead/map-gone.
- RM_GasScreenBridge.cs: resolved by name once, signature matches Scarlands RM_CompAerosolScreen.IsPositionScreened.
- RM_HorizonWarning.cs plume lists: save/load padded for old saves with no def names.
- CB-1 RM_CompReactionSource, CB-4 RM_CompDungSeeder, TB-3 WellLedger, TB-2 GreyHullCrust (HashSet Scribe, two-strike),
  GS-5 OwnerMismatchSweep (copies before Unlink), EH-5 SumpLivingMap (hard FlowWorks dep is declared in About + csproj;
  RM_Liquid_Tar exists), DI-4 RM_Alerts_DangerClock (division constant non-zero), Cauldron PatchApplier (BeforeExpose first,
  AfterExpose last, ReforceOff after draw, [PatchFeature] field is a public static bool).

## Verification
- winbuild FlowWorks: 0 errors. selftest_flowworks_kernel_oracle.py PASS 1/1.
- NOTE: the shared clone has a peer's uncommitted FlowWorks edit (SettingsKit csproj + RimMandrakeFlowWorksMod.cs); the DLL
  rebuilt here therefore includes it and is NOT committed. FlowWorks DLL needs a rebuild after that peer lands.
