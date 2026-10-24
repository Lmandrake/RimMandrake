## spec
found-by: BENCH bridge run (2026-10-23, run 1, build fed77f423a, 14-mod fw_gss_sitting tier).
Class: HARNESS presumed. `python.exe src/RimMandrake/FlowWorks/northstar/ladder_wall_proof.py <out> --fresh-map`
(`Transient/bridge_run_1_20261023/ladder_wall.json`): LADDER_PARITY_OVER_WALL FAIL with
`order: ORDERED taken=True from=(127,0,125) landing=(129,0,125) byLadder=True`, `after: null`, then ONE_WAY UNMEASURED
"never got over". `after` is pos(pid) (ladder_wall_proof.py:107): pid comes from HoseProbe "colonists" (presumed the
numeric thingIDNumber) and is compared with jawa/list_pawns `id` (e.g. "Human123") -> never equal -> None -> scored FAIL.
A null read must be UNMEASURED/HARNESS, never FAIL; match on thingIDNumber or strip the def prefix. Rerun owed for
LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A4 (WALL_LADDER_PLACED and DOUBLE_WALL_REFUSED PASS this run; A7 census verified).
