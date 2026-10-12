# PUMP_POUR_TUNE_NO_FASTER_THAN_GRAVITY

Found live by BENCH 2026-10-11 (flowworks tier, 11 mods, export of c4bd7af75a, FlowWorks DLL addf7fd7). Class: MOD (tuning).

## finding
Owner ruling Q3 (liquid_network_semantics_design_2026-10-11.md): *"Keep it as faster draining"* -- a pump on Pour drains a
Dump tank FAST, against the Dump tank's slow gravity rate. Live, the basic `RM_LiquidPump` pours a Dump tank no faster
than gravity:

| scene | drained per 1000 ticks |
|---|---|
| L2a Dump tank, Outflow hose end, no pump | 25 units |
| L2b Dump tank on the pump's pipe net, pump on Pour, no Outflow end | 20 units |

Mechanism: `Building_LiquidPump.levelsPerCycle` defaults to 1 (RM_LiquidPump has no RM_PumpExtension) and a level is
`RM_PumpMath.TankUnitsPerLevel` = 5 units, so Pour moves 5 units per 250-tick cycle -- exactly `dumpUnitsPerCycle` (5).
The pumping stations (levelsPerCycle 2 and 4) would be faster; the basic pump is not.

Evidence: Transient/bench_live_20261011/fw_live_checks.log rows L2_dump_tank_drains_without_pump (PASS) and
L2_pump_pour_drains_dump_fast (FAIL); result JSON fw_live_checks_result.json.

NEXT: decide the basic pump's Pour rate (e.g. levelsPerCycle 2+ when pouring a Dump tank, or a lower gravity rate) and re-run fw_live_checks L2.

## fix (built ed20705bd5, FlowWorks DLL md5 e8860a76)
On Pour the cycle budget is `RM_PumpMath.PourLevels(levelsPerCycle, dumpUnitsPerCycle)` = max(levelsPerCycle,
dumpUnitsPerCycle/5 + 1): always at least one level more than the gravity rate at any slider value. Basic pump: 2 levels =
10 units/cycle vs gravity 5; stations (2, 4) unchanged. A failed later level no longer overwrites the inspect status.
L0: selftest `Pump_pour_is_faster_than_gravity` (PumpChecks.cs). Design doc §3.3 pour-rate line updated.
NEXT: BENCH pilot rerun — fw_live_checks L2_pump_pour_drains_dump_fast must PASS (expect ~40 per 1000 ticks vs L2a ~25), then
`rimflow verify --criterion A2`.
