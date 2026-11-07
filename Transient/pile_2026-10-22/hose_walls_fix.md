# Hose walls fix (BENCH helper, 2026-10-22)

## Status
- [ ] ledger notes/claims
- [ ] GSS-era code found
- [ ] regressing sha(s)
- [ ] fix
- [ ] selftest
- [ ] proof row
- [ ] build/review/commit/publish
- [ ] findings filed

## Notes
- ledger: owner words noted on HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS; both items claimed by BENCH.
- GSS-era code: HoseMath.Clear/WallDepth identical in GSS (7cf08bf64e^) and today. WallDepth per-cell edge rule born 9e9f153d4e
  (2026-10-04, GSS round 4); before it Clear refused any sample whose floor cell is blocked (seam z=40.0 floors into a wall -> refused).
- GSS cords use CordWorld.Clearance (exact distance to nearest WALKABLE cell box) - seam-safe. The hose reinvented a per-cell metric.
- Offline tests: GSS C# SelfTest (HoseSelfTest, GssFuzz hose half) DID move to FlowWorks (HoseChecks.cs runner, HoseFuzz.cs);
  but every wall assertion (Clear, WallHits) uses the same WallDepth, so the test inherited the blind spot.
- Live evidence: census_mapC_relay.json reel 41679 pose points 49-52 in walls (22,40),(22,39).
- Fix 849b1674ea (DLL cf6d33f7b6 by ./publish): WallDepth = -CordWorld.Clearance; HoseMath.WallCrossings + HoseProbe census wallCross/wallCrossAt;
  proof_hose.py block `walls` row HW1_no_laid_hose_crosses_a_wall (+ selftest_proof_hose verdict checks).
- Tests: HoseWallSeamChecks S1 seam, S2 grazes still pass, S3 metric vs independent ruler, S4 C3-north re-lay (seeds 7/8 crossed (22,39)/(22,40)
  at z~40.04 before) + 160-wall sweep. Red on old (S1,S3,S4), green after. FlowWorks SelfTest 838/838, hose 380/380.
- st34 owner maze: old taut 30.9 cut wall seams (44 samples in walls); now 35.0 -> needs 37-cell hose (assertion updated).
- Items -> built (implemented cf6d33f7b6); owed L2: HW1 on save b maps C and R; reel o1 through gap (22,42)-(22,43).
- Status: DONE, ready for a live check.
