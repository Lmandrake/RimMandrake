# LongShade review 2026-10-09

Scope: tonight's new C# in src/RimMandrake/LongShade/Source. All files are in RM_LongShade.csproj. Referenced defNames (RM_Vrekka, RM_Mirrak, RM_Gulloth, RM_TollokInfestation, RM_LongShadeCleanPatch, vanilla yields) exist.

## Fixed (commit 6d8ff244c, landed 4022228212)
1. Defs/ThingDefs_Buildings/RM_LureAwning.xml: no `<tickerType>`, so `RM_CompLureAwning.CompTickRare` (RM_ShadeExtras.cs:138) never ran and the Mod Settings "off" toggle did nothing. Added `<tickerType>Rare</tickerType>`.
2. RM_ShadeExtras.cs:134 RM_CompLureAwning: `registeredOff` was not reset on respawn, while RM_CompShadeGear re-registers on every spawn. Added PostSpawnSetup reset.
3. RM_ShadeExtras.cs IncidentWorker_RM_HullTow.TryExecuteWorker: pawns were generated before the entry-cell find, so a failed find leaked unspawned pawns into world pawns. Entry-cell find moved first.
4. RM_ShadeExtras.cs Harrok Scan: `prey.pather.MovingNow` had no null guard. Added one.

## Noted, not changed
- RM_LongShadeMiddens.cs:263 ShouldBuildHeap counts spent heaps toward maxHeapsPerMap. Searched heaps never despawn, so vrekka stop building once the cap fills with spent ones. The comment at :223 says this is intended; a design call.
- RM_ShadeExtras.cs Stampede.Issue restarts every runner's Goto when any one lacks it. Harmless.

## Clean marks
Clean: RM_LongShadeMiddenMapgen.cs, RM_LongShadeMiddens.cs, RM_LongShadeMod.cs, Kernel/RM_ShadeExtrasKernel.cs.
NOT marked: RM_ShadeExtras.cs (edited, needs a second full pass), plus RM_LongShadeMapgen.cs, RM_Patch_DewfringeWildSpawnGate.cs, RM_ShipfallCommons.cs, Kernel/RM_LongShadeKernel.cs and SelfTest/* (not read in this pass).

## Checks
winbuild OK. LongShade/validation.py STATIC PASS. run_selftests: 3 FAIL + 1 CRASH, none LongShade (FlowWorks northstar, placeholder_lint, ledger_lint, GimmeSomeSlack proof_all). No dotnet in WSL, so the SelfTest fuzz project did not run; the kernel is unchanged.
