# WASTELAND_MECHANICS_BUILD_1 — tranche 1 report

## Status
In progress — design read, engine seams checked on RimSage (connected).

## Plan (tranche 1)
1. §4 storms: three WeatherDefs + a WeatherDef dose extension + a biome-gated
   MapComponent (ash storm deposits Biotech pollution + seeds Cinderfelt on its
   fresh fall when it ends). Exhumation = bind RM_Wasteland into MovingDunes
   (ash material + DuneWeatherExtension on the ash storm), PatchOperationFindMod-guarded.
2. §3 dose layer: RM_CompAmbientDose (ToxicBuildup via vanilla ToxicUtility) +
   settings-gated heat pusher on the Smolderback.
3. §2 processor comps: CompMilkable subclass, pollution/ash-depth gated fill,
   occasional un-pollute.
4. §1 Middenshell — only if time remains.

## Engine seams (RimSage, decompiled 1.6)
- CompHasGatherableBodyResource.CompTick fills 1/(intervalDays*60000)/tick when Active;
  WorkGiver_Milk resolves TryGetComp<CompMilkable>() -> `is T` so a subclass is milked.
- ToxicUtility.DoAirbornePawnToxicDamage(p, extraFactor) = the vanilla fallout dose
  (ToxicBuildup, scaled by ToxicResistance and ToxicEnvironmentResistance).
- PollutionGrid.SetPolluted / CanPollute / EverPollutable / IsPolluted.
- WeatherDef.sandRate (core field); WeatherManager.SandRate lerps it; MovingDunes
  StormFactors keys off SandRate or DuneWeatherExtension.forceStormTransport.
- Pawn.Tick -> ThingWithComps.Tick -> CompTick every tick (CompHeatPusher works on a pawn).

## Built (pre-rebase shas; landed shas in the final reply)
- 779ff3dd0 — C#: RM_MapComponent_WastelandStorms (biome-gated via
  RM_WastelandStormBiomeExtension), RM_WeatherDoseExtension, RM_CompAmbientDose,
  RM_CompRadiothermalHeat, RM_CompProcessorGatherable (CompMilkable subclass); 9 new
  Mod Settings toggles/sliders; DLL + .srchash.
- bad5a1831 — §4: RM_WastelandAshStorm (sandRate 1.2, dose 1.0, 900 fall cells/day,
  seeds RM_Cinderfelt at 35% of fresh fall on storm end), RM_WastelandRadiationHalo
  (dose 0.6), RM_WastelandPlasmaStorm (def only, UNWIRED). Ash + halo added to
  RM_Wasteland weather (3 / 2). Patches/RM_Wasteland_MovingDunesBinding.xml:
  PatchOperationFindMod "Moving Dunes" -> adds RM_Dunes_WastelandAsh material, binds
  the biome, DuneWeatherExtension on ash/plasma storms = the exhumation reuse.
- 229ebf6e1 — §2/§3 wiring: Sloghog -> RM_ContaminantBezoar every 5 d (full rate on
  polluted/toxic ground, 35% off, un-pollutes 0.25/day); Sootgrazer -> 5 RM_SootBrick
  every 3 d (also feeds on ash drift >= 0.1); Smolderback heat 12/s + ambient dose
  (room when indoors, 6-cell radius outdoors).

## Remaining
- §1 Middenshell — NOT BUILT. 🔴 Verification bar FAILS: the TitanicCreatures engine's
  max footprint is 4x4 (LargePawnsBridge.FootprintSizeFor T3 = 4, "Large Pawns' hard
  ceiling"), so a 20-cell body is not supported. Width is an owner ruling -> escalate,
  not shrink. Art (512) also pending.
- Plasma storm gate: "terminator families only" has no tile/map signal on a single
  RM_Wasteland BiomeDef — design call owed (how a map knows it is a terminator pocket).
- Halo/plasma player-facing names still owed to the owner (working labels shipped).
- Storm OCCURRENCE is not settings-gated (weather commonality in XML); only effects are.
- Processor collection uses the vanilla milking job, so the job text reads "milking".
- Finding, not fixed: RM_Wasteland still lists ToxRain at 4, against sheet §6 ban 5
  (no rain) — belongs to the roster owner (WASTELAND_RULED_CONTENT_1 content).
- Live verify (quicktest state reads) per the item's verify block — not done (no game).

## Verification
- XML parse: all Wasteland XML parses. validate_patch.py UNMEASURABLE here (no load set).
- dotnet build Release: 0 errors, 0 warnings.
- run_selftests.py: 76/78, only failure the known selftest_deployed_biome_refs.
- Engine seams read on RimSage (connected): see above.
