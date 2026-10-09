# Belt helper 2026-10-08: LIQUID_HEAT_PUSH_1 + HARMONY_PATCH_RESILIENCE_1

Offline only. Progress appended per stage.

## Stage 0: claim + read
Both items claimed (FOUNDRY leases). Read: LiquidDef.cs, RM_LiquidFire.cs PushHeat, RM_MapComponent_Excavation tick/pulse,
RM_PitExposure coupling, FlowWorks north-star script plan + extensions.py chain pattern, BOILING_WATER_BURNS_1 §3.
MEASURED (RimSage): GenTemperature.PushHeat -> Room.PushHeat returns false when UsesOutdoorTemperature. So vanilla heat
can only warm an ENCLOSED room; an open Scald shore stays at outdoor temperature. Not a bug: that is "one kind of heat".
MEASURED: no hot/cold FluidDef exists (boiling/icy LiquidDefs have canalFluid null), so no canal or pit can hold boiling
water today; a boiling pond's channel fills as RM_Fluid_Water.

## Stage 1: LIQUID_HEAT_PUSH_1 design
- Flags: LiquidDef.cold beside hot (icy row, via the generator); FluidDef.hot/cold (a future boiling canal fluid heats
  with no code); RM_LiquidHeatExtension (terrain mod-extension) for terrains no LiquidDef claims (the Scald's RUT_ScaldWater*).
- Every 250 ticks (own timer, not frozen by the depth engine): wet hot/cold cells (excavated fill + natural terrain,
  natural list rescanned every 15000 ticks) push vanilla heat per fill level into their ROOM (vanilla neighbour split for
  impassable deep water). Per room: summed, clamped so the room never passes the liquid's target (hot 50 C, icy 0 C),
  capped at 8 heaters' worth. Outdoor rooms skipped (vanilla does nothing there anyway). Cell budget per interval with
  energy scaled up so cost is bounded and average power exact. All numbers PROVISIONAL.
- Settings: on/off + strength slider. Math Verse-free in RM_LiquidHeatMath (C# selftest).
- Follow-up (not built): a boiling/icy canal FluidDef so a pit can be FLOODED with boiling water.

## Stage 2: LIQUID_HEAT_PUSH_1 build + tests
Built (winbuild OK). New: RM_LiquidHeatMath.cs (Verse-free), RM_LiquidHeat.cs (runner + identity + RM_LiquidHeatExtension +
RM_LiquidHeatProof). LiquidDef.cold, FluidDef.hot/cold. Icy row cold via generator (registry regenerated: 1-line diff).
Settings: liquidHeatPushEnabled / liquidHeatStrength. TerminalBiomes patch marks 6 RUT_ScaldWater* hot (validate_patch: 6 matches, OK).
C# selftest 129/129 (5 new LiquidHeat cases; mutating the target clamp turns one red). v2 --offline all PASS.
Extension chain liquid_heat (DRAFT, never run live): kinds / warms-and-chills / off-is-inert. selftest_extensions PASS.
run_selftests: only FAIL besides mine was Utils/art/selftest_placeholder_lint.py (stale art allowlist; not this work).

## Stage 3: HARMONY_PATCH_RESILIENCE_1 helper + FlowWorks adoption
LIQUID_HEAT_PUSH_1 published f90610cd5, `rimflow implemented` -> built (owes A1 L1, A2/A3 L2). Follow-up filed:
BOILING_ICY_CANAL_FLUIDS_1.
Shared applier src/RimMandrake/_Shared/HarmonyResilience/PatchApplier.cs (per-class try/catch, [PatchFeature] names the
feature + setting, forced off for the session but saved with the player's value, red notice in settings, census line).
FlowWorks adopted: PatchAll gone, 30/30 classes carry [PatchFeature] (28 with a setting). winbuild OK.

## Stage 4: patch-target lint + selftest
Utils/lint_harmony_targets.py (dnfile over game + our DLLs; cached) + selftest (every verdict both ways, real-index sanity
probe, NO_FEATURE mutation). All of src/: 408 targets, 402 OK, 0 missing, 4 unresolved (Vehicle Framework), 2 dynamic.
run_selftests GREEN 344/346 (2 skipped).

## Stage 5: publish + rimflow implemented
(pending)
