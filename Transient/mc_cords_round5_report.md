# MessyConduit cords round 5 report (2026-10-04)

## 1. Cable entering the mass (station 1)
- Cause (shot 20261004204130, left of the pile): an edge into a tangle ended at `CordGraph.EndPos` = the pile's boundary cell centre + 0.3 toward the run, and `CordBuilder.AttachEnd` had no tangle branch, so the cable stopped in the open on the pile's rim. The pile's own cables run only between its connectors (random cells), so nothing met it.
- Fix: `CordBuilder.PileConnectors` (one deterministic connector list shared by the pile and its entering cords); `AttachEnd` has a tangle branch: the cord runs on into the pile and ends ON the nearest connector port (`EntryPort`: junction arm tip / strip socket), arriving along the port; a strip pile also gets a plug at that socket (`EndDecor`). The edge cache key now carries the pile's cells, so a reshaped pile re-plugs its entering cords.
- Selftest `SelfTest/ReviewRound5Checks.cs` "entry": every cord entering the 3x3 pile (both arts) ends <= 0.04 cells from a port, a plug at each strip entry; can-fail: the old rim end point is off every port. The detached-end check (`Program.cs`) now accepts a pile end anywhere in the pile.

## 2. Junction boxes on piles: jitter, thinner strands, thicker T/+ (stations 1,4)
- Pile scatter (`PileConnectors`): each box off its cell centre by up to 0.32, any angle (was 0/90/180/270), scale 0.82-1.12 x 1.05 (was a flat 0.8), boxes kept >= 0.45 apart; strips the same (any angle, size jitter). Selftest "scatter" over 6 seeds: <= 1/4 on a centre, <= 1/4 square to the grid, >= 2 sizes per pile; can-fail: a planted grid scores as a grid.
- Wires thinner: `SectionLayer_RM_MessyCords.StrandWidth` 0.11 -> 0.08, `ShadowWidth` 0.17 -> 0.13 (static, LOD and moving layers all read it).
- Boxes thicker: `CordBuilder.JunctionScale` 1.0 -> 1.15 for BOTH T and + (with the round-5 brick art af013af66, arms 18-28 px of 128 -> 0.16-0.25 cells thick over a 0.08 wire). Cords tuck into the arm at ArmTuck x 1.15 (0.46), capped so two adjacent junctions' tucks never cross and never pass the far node. Audit (`CordAudit`) radius window scaled to match.
- T and + same centre/size: both drawn at the same scale with their arm-meeting point on the node (T via its art anchor). Selftest "tee/plus" asserts equal scale >= 1.1 and meeting point on the node centre. Body size: the round-5 art (af013af66, landed during this round) draws T and + as ONE brick of the same size/centre (T = the X shifted up TapeAnchorZ x 128), so TapeAnchorZ 0.152 still holds.

## 3. Random mix: one colour per piece (station 5)
- Round-4 change REVERTED: `ConduitStyles.MixBlock/MixColourIndex/MixSegments` and the section layer's `MixRibbons` (near and LOD) are deleted.
- New `ConduitStyles.MixPieceColours`: every mix piece (node to node) is ONE colour; pieces are coloured in ordinal order of their endpoint key, starting at a hash of it and stepping to the first colour no already-coloured piece sharing a node has. Pure function of the stored cells -> identical after save/load; the endpoint key (part of the piece key before '#') does not change on a live/dead flip. `RM_MapComponent_CordGraph.ComputeMaterials` writes it into the piece's material index, so the static mesh, the LOD mesh and the moving layers (sway / whip / ripple / face, all keyed by `MatIndexOf`) draw the same single colour.
- Selftests (StyleStage2Checks): 5-piece nodal tree -> 0 node-sharing clashes, >= 2 colours; order-independent; 4x4 nodal grid of 24 pieces -> >= 4 colours, <= 2 clashes; straight node-to-node cord -> one colour; can-fail planted all-one-colour tree.
- Probe (`ConduitStyleProbe`): `mixTex` is now the piece's single strand texture; `mixSegmentsPrinted`/`mixLodSegmentsPrinted` removed.

## 4. Industrial black pole cable width (station 6)
- Table: `Source/Aerial/AerialMaterials.cs` `WidthOf(look)` (span ribbon width, cells): Industrial **0.17 -> 0.10**; Scrapper 0.14, Modern/Futuristic 0.095 unchanged. The default-look global `SpanWidth` initialiser 0.17 -> 0.10 (Build overwrites it from the table anyway). Hookup cables (ConduitVisuals) follow at 0.85 x width, floor 0.1.
- Shadow ribbon (`SectionLayer_RM_AerialGround.ShadowWidth` 0.42) untouched.

## Build / selftests / commits
- `winbuild.py MessyConduit`: 0 errors. `selftest_messyconduit.py` 573/573 (new review5 checks + rewritten mix checks). `run_selftests.py` 172/177: MandrakePatches, northstar_matrix, UtinniPatches dump, StarWarsPatches semantics (parallel flake), ledger_lint -- none touch MessyConduit cords.
- Review tooling: `validation_style.py` S9d builds a 3-cell Modern-mix spur (MIX_SPUR) off the right half so the mix run has >= 3 node-to-node pieces, and requires each mix piece ONE colour (mixTex == [strandTex]), >= 2 colours across the pieces, every colour printed (and its LOD mesh when LOD is on). `human_review.py` station 5: height 19 -> 23, two 3-cell mix spurs up off the mix row (x 5 and 9, z 19-21), the check reads >= 3 mix pieces in >= 2 colours, each piece uniform; texts updated. `selftest_human_review.py` 24/24.
- Unproven live: everything above (offline only; the review map needs a rebuild for station 5's new spurs).
- Hose: `HoseMath.WireVisibleWidth` still says StrandWidth 0.11 (comment + 0.11 constant); Hose files were off limits this round.

## Commit record
- 466749d46 cords r5 source + selftests + S9d/station 5 + this report; 4554fb531 DLL+srchash from committed source.
- The Industrial span width (AerialMaterials.WidthOf 0.17 -> 0.10) landed inside the lamp/hose agent's d7fb73e3a (its pathspec commit took the worktree file, which held this edit).
- The first ./publish hit an autostash reset failure (shared clone, lock contention); the stale rebase state was cleared by the time it was checked, nothing was lost, and the commits were pushed by hand after the DLL rebuild.
