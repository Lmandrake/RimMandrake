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

## 22:42 FIX helper: starting on 4 judge FIXes (UCT x3 upper W/E stubs, Futuristic LiquidTank NE collar)
- 22:47 cause: UCT upper W/E port row (128 px = z 1.5) is ABOVE the body's side silhouette (body top ~133; side reachable only rows >=180), nearest opaque at that row = strap top; E nozzle occupies rows 148-195 to 35 px from edge. LT-Fut NE port column x=384 lies over the kept elbow fixture (cols 351-411) + valve (to 467). Plan: coupler stays at the port; a thin bypass pipe routes around fixtures to a collar on the body (UCT: drop 23 px from edge to the end-cap side ~row 240; LT: jog right past the valve, down to the right shoulder). Before-snapshot of all 18 outputs in scratchpad.
- 22:50 port_fittings.py: ROUTES bypass for the 4 FIX ports; regenerated 18 outputs: 14 byte-identical to before (cmp), 4 differ; kept-fixture pixels untouched (UCT nozzle: 0 px touched; LT elbow/valve box: 0 px). 4 cmp PNGs re-rendered (AFTER half from new art, overlays kept; method verified exact on Modern UCT).
- 22:51 selftests hose_fittings + tank_art_edges PASS (installed art unchanged). Filed CARGO_PORT_DECIDE_PERCHED_ON_SHOULDERS (FOUNDRY): UCT upper W/E port row sits above the body's side silhouette. Lesson filed. Committing.
- 22:53 round 2: Futuristic RM_LiquidTank NW collar hides the cable strap's top loop -> let the loop draw over the collar
- 22:55 round 2 done: OCCLUDE restores the cable loop (cols 131-160) over the NW collar; 17 outputs byte-identical, 1 changed; cmp_Futuristic_RM_LiquidTank.png re-rendered; selftests GREEN
