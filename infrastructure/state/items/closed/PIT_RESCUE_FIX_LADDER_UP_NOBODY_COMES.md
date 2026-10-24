## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod fw_gss_sitting tier).
**PRIOR PASS NOW FAIL (STOP).** Class: MOD presumed, unproven.
`python.exe src/RimMandrake/FlowWorks/northstar/pit_rescue_live.py <out> --fresh-map` twice
(`Transient/bridge_run_1_20261023/pit_rescue.json`, `pit_rescue2.json`): RESCUE_LADDER_QUEUED PASS (250), RESCUE_LADDER_BUILT
PASS (RM_LadderPortable at 37,36, built at 1000 / 4250), RESCUE_COLONIST_OUT FAIL: at tick 8000 the victim is still downed on
the pit floor (37,35); both rescuers idle (LayDown/GotoWander, Wait_Wander/GotoWander). The non-pit control colonist WAS
rescued at 250, so vanilla rescue works.
2026-10-22 13:45 belt (`src/RimMandrake/FlowWorks/northstar/pit_rescue_result_20261022T1345_belt.json`): all 3 PASS, out at 4750.
Lead: ladder parity round 2 landed between (d5aa811b73 "lowered ladder = held-open prison door", b69a95a2d0, 8b21b0a217
"drop dead noKeys term in MayClimbLowered"): presumed the auto-built rescue ladder now stands RAISED (or the rescuer's
climb eligibility is refused), so no path down. First read: ProofLadderParity / HoseProbe "LADDER cell=37,36" raised= on the
rescue ladder, and MayClimb for the rescuer. Blocks LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A6 (first half).
