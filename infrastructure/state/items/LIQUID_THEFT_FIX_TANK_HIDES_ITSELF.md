# LIQUID_THEFT_FIX_TANK_HIDES_ITSELF

Found live by BENCH 2026-10-11 (flowworks tier, 11 mods, export of c4bd7af75a, FlowWorks DLL addf7fd7 deployed). Class: MOD.

## finding
`RM_LiquidTheft.Witness` (src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTheft.cs) asks
`GenSight.LineOfSight(p.Position, tank.Position, map)`. That 3-arg overload ends only at the single `Position` cell
(`CellRect.SingleCell(end)`), and `RM_LiquidTank` is 2x2 with `fillPercent` 1.0, so its other three cells block sight.
A witness whose line enters the tank through any cell but `Position` never sees it.

## evidence
- fw_live_checks L6: our Fill tank drew a Naora (OutlanderCivil) tank 100 -> 60 units over a hose with two Naora villagers
  5 cells NE; `RM_LiquidTheft.caught` stayed 0 for a whole in-game day (Transient/bench_live_20261011/fw_live_checks.log).
- Discriminating probe (Transient/bench_live_20261011/fw_theft_los_probe.py / .json): same tank, refilled and drawn.
  Witness at (81,185), NE, line crosses tank cell (78,182): caught 0 -> 0 over 3 cycles. Witness at (73,177), SW, line
  reaches (77,181) = Position first: caught 0 -> 1.
- GSS's power-tap twin is unaffected (the clamp is 1x1): POWER_THEFT A2 caught on the first cycle.

## fix (suggested)
Use the rect overload: `GenSight.LineOfSight(p.Position, tank.Position, map, CellRect.SingleCell(p.Position), tank.OccupiedRect())`
(or test sight to any occupied cell). Add a SelfTest/live row with a witness on each side of a 2x2 tank.

NEXT: fix Witness to aim at the tank's OccupiedRect, then re-run fw_live_checks L6 (letter + one-day goodwill).

## fix (built ed20705bd5, FlowWorks DLL md5 e8860a76)
`Witness` now calls `GenSight.LineOfSight(p.Position, tank.Position, map, CellRect.SingleCell(p.Position), tank.OccupiedRect())`.
L0: selftest `Theft_witness_sees_a_2x2_tank_from_every_side` (LiquidTheftChecks.cs) replays vanilla's walk on the probe's
geometry (NE hidden by the Position-only aim, seen by the footprint aim) and pins the production call.
NEXT: BENCH pilot rerun — fw_live_checks L6_theft_spotted_letter must PASS (caught 0 -> 1 with the NE witnesses), then
`rimflow verify --criterion A2`.
