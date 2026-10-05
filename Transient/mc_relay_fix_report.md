# MessyConduit relay hookup fix (station 42)

Status: built offline, selftests green, NOT deployed, NOT run live

## Diagnosis (shot 20261004223832_1.jpg, crop of the relay reel)
- The feeding hose ends at `HoseRelay.IntakePoint` = the MIDPOINT of the intake cell's shared edge. For a west approach
  that is the lower west cell, so the end sits at footprint-centre z - 0.5 and x = footprint edge.
- The reel art (all 4 looks, both stored and deployed, drawSize 2.8) has ONE brass inlet, on the pump's west side:
  rows v ~119-147 of 256 (centre v ~133 = centre z -0.05), face at u 8-11 = 0.29 cell OUTSIDE the footprint edge.
- So the coupling was drawn ~0.45 cell below the inlet and 0.29 cell inside the inlet face: it floats under the pump base,
  beside the inlet, pointing at the base rail -- exactly the shot. The last leg was also not straight, so the coupling
  axis followed the hose's last bend, not the inlet's.
- Other sides: the side-view art leaves bare ground between parts of the N and S footprint edges and the outline
  (drum top 0.3 inside the N edge, base rail ~0.2 inside the S edge), so a coupling on the edge midpoint stops short /
  floats there too.

## Fix
- Measured the art: src/RimMandrake/Utils/mockups/messy_conduit/reel_intake_geometry.py -> Source/Hose/ReelIntakeGeometry.cs (per look x stored/laid art: west inlet dz/face, E/N/S outline point per edge cell; every depth within +-0.31 cell of the edge).
- HoseRelay.DrawnEnd / EdgeOffset / EndTolerance 0.35 / EndStraight 0.6; HoseMath.Lay(endInward) plans to a point 0.6 out and lays the last 0.6 cell straight into the end (StraightenEnd on flat, centre, plump); EndPoint/EnsureLay use it (lay key carries relay look + stored/laid); DrawEnds points the relay coupling along the intake axis.
- WireVisibleWidth 0.11 -> 0.08 basis (no clearance use: only width-ratio checks + probe); HoseSelfTest width bound 4-5x -> 4-7x.
- Probe: relayEnd {drawnEnd, inward, edgeOffset, withinEdge, tailAngleDeg, relayLook, relayArt}.

## Tests
- selftest_messyconduit 613/613 (review7: 64 end cases on edge within 0.35, 16 lays W/E/N/S x 4 looks straight into the end < 3 deg, station 42 west inlet, wire width, 2 can-fails). run_selftests 177/178 (northstar_matrix C2 live shots, pre-existing). winbuild 0 errors.
- validation_hose.py --relay RL3/RL4 now also require: lay end == endPoint, |edgeOffset| <= 0.35 on the intake side, within the edge, tail < 3 deg, west end on the inlet (centre z +-0.15, face outside the edge). Written, not run (main window holds the bridge).
- fakegame.py WIRE_VISIBLE follows 0.08.

## Unproven live
- Everything on screen: coupling face-to-face with the brass inlet at station 42, the straight last stretch, the E/N/S outline ends (N meets the valve wheel / near flange top, S the base foot, E the far flange). Needs deploy at next shutdown + a human_review rebuild of station 42.
- Note: a stored (not laid) relay offers its coiled hose's dangling nozzle as the S-side outline in 3 looks; reads as plugging into it.


## Commits
- 742e0700e source, selftests, RL3/RL4, generator, this report; e267df858 DLL + .srchash from committed source. Not deployed: deploy_custom_mods.py --mod MessyConduit --apply owed at the next shutdown.
