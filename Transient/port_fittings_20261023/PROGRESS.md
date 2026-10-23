# Port fittings drain — 2026-10-23 (BENCH offline helper)

Gate: src/RimMandrake/FlowWorks/selftest_hose_fittings.py
- known-red BEFORE: 43
- known-red AFTER: 41 (pump entries pruned; tank candidates not installed)

| item | state | sha | comparison PNGs |
|---|---|---|---|
| TANK_LANE_FITTINGS_REDRAW_MODERN_ONLY | candidates drawn, NOT installed (owner-KEPT); needs owner | 42678b8eff (script) | cmp_<Look>_<Tank>.png |
| TANK_SOUTH_PORT_REDRAW_STUB_PEEKS_OUT | candidates drawn, NOT installed (owner-KEPT); needs owner | 42678b8eff (script) | cmp_<Look>_<Tank>.png |
| TANK_NS_PORTS_REDRAW_COUPLE_THIN_AIR | candidates drawn, NOT installed (owner-KEPT); needs owner | 42678b8eff (script) | cmp_<Look>_RM_LiquidTank / _UniversalCargoTank.png |
| PUMPSTATION_SOUTH_PORT_REDRAW_ALMOST_THERE | built (owes A2 L1 live look) | 42678b8eff + ledger 2ed58b8340 | cmp_RM_PumpingStation_{Kludged,Repaired}.png |

## Log
- started: reading items, gate, prior fitting approach (6199b2ed13)
- known-red BEFORE = 43 (selftest_hose_fittings.py --table, HEAD 2de91f64bb)
- plan: one general compositor art_source/TankPorts/port_fittings.py (per-look material, W/E/N/S, pumps) on base art read from git
  (Modern trio: modern_port_fittings.build output; rest: pre-change HEAD); selftest_tank_art_edges measures the body on that base,
  so TankArtEdges.cs should not change.
- art.py install refused all 16 tank pictures: owner-KEPT (delegation_policy 2.3) -> only the pumps installed
- pump install with --why alone was refused at pre-push by art_guard; re-recorded with --reason script:port_fittings.py (2ed58b8340); lesson filed
- selftests: hose_fittings PASS (41 known), tank_art_edges PASS (TankArtEdges.cs unchanged, no C# rebuild)
- DONE
