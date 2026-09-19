# GizkaStowaway NRE — root cause 2026-09-19

Item: GIZKA_TRIBBLE_ADAPTATION_1. Crash record: FULL_LIST_CANNOT_LOAD_GAME_1.
Verdict up front: **gizka is exonerated. There is nothing to fix in the gizka mod.**
The `new Game()` NRE was FlowWorks' stale DLL, and the same restart that deactivated
gizka also redeployed FlowWorks — two variables changed at once, and the crash was
attributed to the wrong one.

## Hypothesis

Vanilla `ReadingPolicyDatabase.GenerateStartingPolicies` walks every ThingDef and calls
`item.thingClass.SameOrSubclassOf<Book>()`. A ThingDef whose `<thingClass>` names a type
that did not resolve is kept in `DefDatabase` with `thingClass == null` (ConfigErrors
logs "has null thingClass" but does not discard the def), and the walk NREs on it.
Test: which ThingDef in the crash session had a null thingClass, and did gizka put it there?

## Evidence

1. Vanilla body confirmed via RimSage (`Source/RimWorld/ReadingPolicyDatabase.cs`):
   `foreach (ThingDef item in DefDatabase<ThingDef>.AllDefsListForReading) if (item.thingClass.SameOrSubclassOf<Book>()) ...`
   Stack in the crash log (`Transient/Player.log.closedsession_20260918_0129.txt` line 40020-40027)
   is exactly `GenTypes.SameOrSubclassOf(Type,Type)` <- `SameOrSubclassOf<T>` <- `GenerateStartingPolicies`
   <- `ReadingPolicyDatabase..ctor` <- `Game..ctor`. Null `baseType.IsSubclassOf` is the NRE.
2. Literal-string scan of that log (`MEASURE_ALLOW_SCAN=1 grep`), the ONLY null-thingClass def:
   - line 29950/29955: `Config error in RM_LiquidTank: has null thingClass.`
   - line 29960/29965: `Config error in RM_LiquidTank: has components but it's thingClass is not a ThingWithComps`
   - line 3864: `Could not find a type named RimMandrake.FlowWorks.LiquidTypes.Building_LiquidTank`
   - lines 1293-5897: the same missing namespace for `JobDriver_FillBottle/WashBottle/EmptyBottleIntoTank/FillBottleFromTank`,
     `WorkGiver_*` (4) and `RM_BottledLiquidExtension` (the 82 defdiscards BENCH already found).
   `RM_LiquidTank` is `src/RimMandrake/FlowWorks/Defs/.../RM_LiquidTank` with
   `<thingClass>RimMandrake.FlowWorks.LiquidTypes.Building_LiquidTank</thingClass>`. The whole
   `LiquidTypes` namespace was absent from the deployed FlowWorks DLL in that session.
3. Gizka in that log: zero `Could not find type` lines, zero config errors, zero exceptions.
   The only "Gizka" hits are the def-file source-trace lines and two healthy LoadTracer
   static-ctor lines (`RSW_GizkaDonorTuning`, `RSW_GizkaHarmony`, 1484-1485/1563).
4. Gizka audit, XML vs C# vs DLL: every class the XML names exists in
   `Source/*.cs`, is in the csproj `<Compile>` list (all 6 .cs files), and is present by
   name in `Assemblies/RimMandrakeGizkaStowaway.dll` (HediffCompProperties_GizkaFecundity,
   HediffComp_GizkaFecundity, MapComponent_GizkaInfestation, GameComponent_GizkaStowaway,
   RSW_GizkaStowawayMod, RSW_GizkaDonorTuning, RSW_GizkaHarmony). The one ThingDef gizka
   ships (`RSW_GizkaBait`) has `<thingClass>ThingWithComps</thingClass>`; the hediffs use
   `HediffWithComps`; the thought uses `Thought_Memory`. Patches touch only numeric fields
   on the donor/RSW gizka (MarketValue, egg-layer, hatcher, minAge, mateMtbHours) — never a
   class. Its C# never touches `thingClass` either. Deployed gizka DLL md5 == repo DLL md5
   (`296d9fa95fd152efd8c25851b79f231e`).
5. The confound: BENCH's 08:30 note on FULL_LIST_CANNOT_LOAD_GAME_1 records ONE restart
   that both deactivated gizka AND redeployed FlowWorks. The retest (`Transient/loadB_retest_20260918.md`)
   then credited gizka. The post-restart harvest (`Transient/harvest_loadB_postgizka_20260918.txt`)
   shows defdiscards 82 -> 49, i.e. the FlowWorks bottle discards were gone in the same run
   the NRE was gone. The game's FlowWorks DLL now contains `Building_LiquidTank` (byte-string
   check of `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\FlowWorks\Assemblies\RimMandrakeFlowWorks.dll`),
   and the live `Player.log` (Sep 18 20:41 session) has 0 `has null thingClass` and 0
   `Could not find a type named` lines.

## Root cause

Stale FlowWorks DLL in the game folder (LiquidTypes namespace not compiled/deployed) left
`RM_LiquidTank` in `DefDatabase<ThingDef>` with `thingClass == null`; vanilla
`ReadingPolicyDatabase.GenerateStartingPolicies` dereferences every ThingDef's
`thingClass` and NREs inside `Game..ctor`, so no game can be constructed. Fixed by the
FlowWorks redeploy at ~01:29 on 2026-09-18 — not by deactivating gizka.

General lesson (already in the CLAUDE.md "DLL behind XML" family): a ThingDef whose
`thingClass` fails to resolve is NOT discarded — it stays in the database as a landmine
that vanilla trips in `new Game()`. `Could not find a type named X` on a `<thingClass>`
is a load-blocking error, not a cosmetic one.

## Fix

No code change in gizka. Nothing to rebuild, nothing to deploy (deployed DLL is
byte-identical to the repo's). The remedy is administrative: reactivate
`mandrake.rsw.gizkastowaway` on the full list and prove it on a cold load (BENCH).

## Build+deploy

Not performed — no defect to build. Deploy check: `Mods/GizkaStowaway/Assemblies/RimMandrakeGizkaStowaway.dll`
md5 matches `src/RimStarWars/GizkaStowaway/Assemblies/RimMandrakeGizkaStowaway.dll`.

## Owed

- BENCH: reactivate gizka on live + FULL.LATEST, cold-load, confirm `new Game()` and the
  campaign save load with gizka ON. That is the falsification test of this attribution.
- FULL_LIST_CANNOT_LOAD_GAME_1's 09:25 "RESOLVED by deactivating gizkastowaway" note is
  wrong on cause; fix the record when the cold load proves it.
- Observation only (not this task): the repo FlowWorks DLL (`7680d6ab4`, 142848 B, Sep 18 19:56)
  is newer than the game's copy (140800 B). Both contain the LiquidTypes names, so the
  crash cannot recur from that delta, but FlowWorks' latest build is not yet deployed.
- Consider a load-time guard: a harvest check that greps `has null thingClass` as RED —
  it is the one config error that guarantees `new Game()` fails.
