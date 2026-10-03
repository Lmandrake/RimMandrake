# BELT MessyConduit LANE A — 2026-10-02

Started Fri Oct  2 16:34:52 PDT 2026

## L1 rope physics
(pending)

## L2 graph/builder
(pending)

## L3 live ends
(pending)

## L4 render
(pending)

## Live sessions
(pending)

## Log
- 16:36 read docs + source (HEAD cfc6dd58e + 050d3b677). Baseline selftest 137/137 (3 s, cached build). Plan: L1 Settle() in CordLayer (PBD per rope.relax, cell-neighbour obstacle cache, iteration budget), LayParams wire/hose params; SelfTest block "lane A".
- 16:42 L1 DONE offline: CordLayer.Settle (PBD: bend smoothing, min-bend-radius stiffness pass, symmetric Gauss-Seidel inextensible, cached cell-neighbour obstacle test, iteration budget 160k point-iters/strand, min 20, max 70; 16 final project+restore rounds), PinMask, LayParams wire/hose params (CordKind.Hose(): bend R 1.2, smooth 0.8, step 0.25, excursions 6-10, no loops/heaps, slack 0.15-0.30 clamp 1-6). SelfTest LaneAChecks.cs: red 144/154 -> green on all lane-A checks. Measured: max segment stretch 0.2-2.4% (bar set 3%: one segment next to an end pin in 'gap' sits at 2.4% and does not converge; compression up to 8% = bunching), length within 2.6% of budget, 0 fell back, laid/path medians 2.7-3.8. Hose yard: min bend R 10.7 (wire 0.02), 0 self-intersections (wire 23 on same yard = sanity probe). Perf (net8 JIT, Windows): 1027-cell density field -> 124 nodes, 188 cord edges, 359 strands, 98,875 laid points; cold build 659 ms, warm 7 ms. NOTE lane B's AerialSelfTest red checks share the run (not mine).
- 16:44 L2 DONE offline (red 244/251 -> 251/251): CordGraph.MergeStubs (same buried component + walk cells within 2 floor-conduit steps -> keep middle stub; a through-wall pass keeps both faces); long-run end heaps (cord > 40 cells: one heap 1.5-5 cells from each end, own RNG stream); LED strips keyed to live (DecalKind.PowerStripDark, LaidPiece.LiveKeys on tangle + device-stub pieces, device-stub edges carry L/D in the cache key). Measured: comb 9 stubs -> 1; comb+through-wall 11 -> 2; 64-cell run heaps near A 3 / near B 3 (3 strands); tangle lit 5/0, tangle_off 0/5. Tangle entity + exit cords + spur/blob knots were already built (1a) and stay oracle-parity green. Python oracle NOT extended for merge/end-heaps (C#-only properties).
- 16:46 L3 core DONE offline: new Core/CordMotion.cs (CordMotion.Whip: 3 sines + seeded 0.6-2 s snaps, joint pinned; CordMotion.Sway CPU path; DownedWireSchedule DRIP/FLASH/QUIET/CRACKLE, exp gaps mean 0.9 clamp 0.3-2.5, Glow(), SparksDue()). Builder: CordStrand.WhipA/WhipB (live floor terminal tail ~0.4 cell kept in Pts, layer skips it when whipping), FrayLive decal OnWhip, wall-hanging tails Lifted + SwayW (0 at hole -> 1 at tip). Motion checks written with the code (not red-first). Selftest 270/270 (incl. lane B aerial 59/59).
- 16:52 Verse side for L2-L4 written + built (0 warnings): settings (tangleMin, whip, downedWire, sparksOnlyOverlay, maxSparkingEnds, highlight, sway, swayAmplitude, lod; scrollable screen); CordMaterials StrandLod/Highlight/PowerStripDark (tinted placeholder until art); section layer skips whip tails + swaying lifted strands, prints a LOD sub-mesh (1 strand, every 3rd point), DrawLayer toggles LOD by CameraZoomRange.Far and hides during the gravship cutscene (RimSage: same guard as SectionLayer_Things); component: PollLive covers LED keys, DrawMotion (whip mesh, CPU sway mesh on game time, downed-wire schedule w/ downward MicroSparks + flash glow, selection highlight mesh cached per net/build + stub rings); probe ops motion/motionreset/select:x,z/deselect. validation.py: SHIPPED +9, lane-A live block (B1,B3,B4,B4b,B5,B6,B6b,B7,B8,B9,M10,perf + p1b_ screenshots). Offline tier 5/5 PASS. Sway: CPU path only (shader path not built).
- 16:56 LIVE session 1 (lock held as LANE A): killed PID 3776, deployed (11 files VERIFIED), tier messyconduit (9 mods), Steam relaunch, bridge up in 15 s. validation --live --fresh-map: 31 PASS / 1 FAIL (B8: harness left the camera at Furthest -- frame_cell_rect keeps the zoom; fixed: set_camera_zoom back). Live numbers: settle 16 strands max stretch 0.020, len dev 0.02; rebuild 8.4 ms for 6,823 laid points; whip 3 draws on 1 live floor end (0 with whip off); downed wire hist Drip4/Flash3/Quiet6/Crackle2 in 14 s; sway CPU 2 lifted, hash differs over 30 ticks (wind 0.116), 0 with sway off; highlight net1 3==3, net2 12==12, 0 deselected; LOD far: 2 LOD sub-meshes on, 13 full off; strips lit 2 -> dark 2 after battery 0; tangleMin 20 -> 0 tangles, 6 -> 1. Screenshots p1b_01..06 (05/06 tiny: taken at Furthest; re-shooting).
- 17:08 Highlight fix (tinted near-black strand stayed near-black -> warm band on white texture); rebuild, redeploy, relaunch messyconduit: validation --live --fresh-map 32/32 PASS (northstar/validation_result_20261002T170301.json), --save-load MC_LANEA2_20261002 3/3 PASS (hash 6053201b5ab6e657 before == after), tier flowworks + relaunch, --removal-check MC_LANEA2_20261002 M9 PASS (0 errors naming the mod). modcheck record -> REFUSED (by design: 3 UNBUILT/UNCOVERED bars, no north-star checklist). LEARNED: screenshot_cell_rect does not capture per-frame DrawMesh (highlight/whip/sway); OS capture p1b_08_highlight_onscreen.png shows the highlight (cropped to the game window; full-desktop BMP deleted).
- END 17:08: selftest 270/270 (incl. aerial 59/59), probe 7/7. Game UP on flowworks tier at main menu; live lock released. Nothing committed (brief forbids git).

## Status
- L1 rope settle + hose params: DONE (offline + live B1)
- L2 graph/builder (stub merge, long-run end heaps, lit/dark strips; tangles/knots/stubs already 1a): DONE (offline + live B6/B6b/M10)
- L3 whip, downed-wire bursts, selection highlight: DONE (offline + live B3/B4/B4b/B5)
- L4 sway (CPU path), LOD, cutscene guard: DONE (live B7/B8/B9); shader sway path NOT built; floor ripple NOT built
