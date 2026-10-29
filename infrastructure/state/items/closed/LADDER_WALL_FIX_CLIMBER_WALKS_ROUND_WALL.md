## spec
found-by: BENCH bridge run (2026-10-23, run 1 driver 4, HEAD 39ec8aac5e deployed, 14-mod fw_gss_sitting).
Class: HARNESS suspected (not proven MOD).

Repro: `python.exe src/RimMandrake/FlowWorks/northstar/ladder_wall_proof.py <out> --fresh-map` (run from a D: git-archive export).
Evidence: `Transient/bridge_run_1_20261023/ladder_wall3.log`, `Transient/bridge_run_1_20261023/ladder_wall3.json`.

LADDER_WALL_FIX_LOSES_CLIMBER_BY_ID worked: the climber is now found and read, so OVER_WALL gives a real verdict.
That verdict is FAIL: `order: ORDERED taken=True from=(127,0,125) landing=(129,0,125) byLadder=True`, then after 900
ticks the colonist is at (117,110), wallX=128. That is 10 squares west and 15 south of the ladder foot. It is not
next to the wall on either side. ONE_WAY is therefore UNMEASURED. WALL_LADDER_PLACED, DOUBLE_WALL_REFUSED and
CLIMBER_CENSUS PASS.

Why harness: the colonist is undrafted and the wall is only 7 squares long (z c-3..c+3), so it can walk round the
wall. The row reads one position 900 ticks after the order. A colonist that climbed over and then walked off to
another job reads the same as one that never climbed.
Fix: draft the colonist (or lock its job queue), make the wall run the full rect, and poll the position each ~30
ticks for x > wallX (the first crossing is the verdict). Also record the job and its end condition. If it still
never crosses while drafted, refile as MOD against the climb job. Owed: LADDER_PARITY_BUILD_NO_KEYS_REQUIRED A4
(OVER_WALL/ONE_WAY).
