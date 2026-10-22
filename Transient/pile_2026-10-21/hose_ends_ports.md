# HOSE_ENDS_FIX_MISSES_THE_PORTS — progress (BENCH helper)
Owner 2026-10-21 23:56 PDT, C5 Fuel Depot: "Hose attached to tank and reel broken..."
## Status
- [x] claim (lease BENCH.pid13742)
- [x] diagnosis (a/b/c): (b)
- [x] tests (selftest_hose_ports.py; SelfTest PortEnds +25 checks; review7/GptA fixtures moved to the measured nozzle)
- [x] fix / build (bench, FlowWorks SelfTest + hose suites green; fuzz 4/4)
- [x] live proof row NS_hose_ends_on_ports in northstar/proof_hose.py (scene 0 = C5 geometry), NOT run
## Findings
- Classification: (b) port coordinates out of step with the art. Reel: HoseReelRect.Mouth/NozzleTip (u 9/256 @2.8) describe the
  10-05..10-15 art; 2e22f30e3c (10-17 provisional render install) replaced all 8 reel textures with small renders whose outlet is
  elsewhere -> coupling drawn ~1.3 cells W of centre in empty ground (matches screenshot px). 2c27b49569 (10-21) changed art again + drawSize 2.15.
- Tank: far end couples at the end CELL's shared edge (pts[n-1]+side*0.5, unchanged since GSS); tank art port is at the footprint
  centre-line on W/E edges -> coupling 0.5 cell off the drawn port; centre stub (PIPE_ENDS_BUILD_MEET_IN_THE_MIDDLE) shows through margin = the 'gap'.
- Loop: reel outlet faces W on every look (non-rotatable reel), so an E target needs a U-turn after the 1.6-cell lead-out: by design.
- C# BLOCKED: other helpers' uncommitted FlowWorks .cs (drawbridge) -> stop at ready-to-build.
## Girth fold-in (coordinator 00:00, owner: "Hoses need to be twice as thick ... Solid pipes appear unchanged in width")
- Pipes "unchanged": DEPLOY, not a draw path. Game DLL = b5e399067a build (md5 6fd717c9), game pipe atlases = pre-8d5b94b0e1 (all 4 looks md5 = old).
  Every pipe draw path (atlas linked graphic, centre stubs = atlas sub-material, pole span = SpanWidthCells 0.14) follows the halved values in repo.
- Hose: FlatVisible 0.09 -> 0.18, PlumpExtra 0.025 -> 0.05 (patch, blocked on C#).
- Reel generator: reel_intake_geometry.py now reads drawSize from defs, emits OutletTip table, --check -> STALE today (would have caught it).
- Building the C# patch in a scratch export of HEAD (bench worktree untouched).
- Patch written in scratch export (HoseMath TankPortGeometry + EndOnPort + per-look NozzleTip; CompHoseReel Look; MapComponent PortEnd; widths 0.18/0.05; slider 0.5-2; SelfTest PortEnds). Building it in the export next.
- fuzz: 2 new 'plump much longer than flat' [outlet] fails with patch; baseline 0. Bisecting width vs mouth.
- trying: lead-out pair whose plump > 1.25x flat +0.5 kept as last resort
- others' C# committed; patch APPLIED to bench, building

## Result
- Fix: reel nozzle per look from ReelIntakeGeometry.OutletTip (generated from the installed art at the defs' drawSize 2.15); tank end
  bends onto RM_LiquidTank's W/E flange (TankPortGeometry + HoseMath.EndOnPort, centre stub from the flange); lead-out join whose
  plump pose grows > 1.25x flat is a last resort (fuzz 144). Hose 0.18/0.23 cell, slider 0.5-2x. HoseRelay.EndTolerance 0.75 (new art inset).
- Pipes "unchanged" live = 8d5b94b0e1 atlas + DLL never deployed (game DLL = b5e399067a build). No pipe draw path uses an old width.
- Open: the reel outlet faces W on every look and the reel is not rotatable, so an EAST target still U-turns after the lead-out (by design;
  mirroring the reel art for east targets would be a cosmetic change -> owner's call). Tank N/S sides and the tall tank have no drawn port:
  edge midpoint kept.
- Deploy owed (FlowWorks DLL + pipe atlases + reel/tank art + defs), then run proof_hose NS_hose_ends_on_ports.
