## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks checks that are wrong: six old tickets (fuzz float tolerance, lake floor skips height, idle-pulse settle, pond arms split, pit shot passes on another target, plot grid off the map).

## merged tickets

- `RIMMANDRAKE_FIX_FLOWWORKS_FUZZ_FOUR_FLAWS_SINK_STILL_FLOAT` (proposed): Four older FlowWorks fuzz flaws Codex found reviewing the exact volume law: per-fluid and sink laws still float, probe counts and JSON
  - sweep reading: Wrong test, still present: FlowKernelFuzz.cs:336 (sink) and :340 (per-fluid) still compare at 1e-3 (ten dL) after dbf76d554c made only the total-volume law exact; ShippedMatrixProbe findings 4-6 unreviewed; mod ledger open problem
  - its check: Per finding a case red on dbf76d554c and green after (finding 1: hook plant moving 1 dL between fluids or into the sink, vv_laws.py prove FlowWorks --family conservation); vv_laws.py lint clean; selftest_vv_laws.py green; unplanted kernel_fuzz stays 0 failures
  - files: `src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs`, `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs`
- `LAKE_FLOOR_SELFTEST_FIX_WET_SKIPS_HEIGHT` (proposed): [MINOR] Lake-access ruler accepts wet neighbours without checking the final height difference
  - sweep reading: Still present: LakeFloorChecks.cs:85 and :97 'if (Wet(s/m)) return true' before any height compare (file unchanged since ee7c219b70), so the drained-lake stranding check can pass a sunken lake; wrong test; mod ledger v0.1.0 open problem
  - its check: EdgeReachable rejects a one-cell lake with floor depth 10, surface -9U and climb 1 (planted case goes red), and the existing lake-floor checks stay green
  - files: `src/RimMandrake/FlowWorks/Source/SelfTest/LakeFloorChecks.cs`
- `LEVEL_SET_SELFTEST_FIX_IDLE_PULSE_SETTLES` (proposed): [MINOR] Integer-water tests accept a single idle final pulse as settling
  - sweep reading: still unfixed: LevelSetChecks.Run (LevelSetChecks.cs:27-41) sets settled on the last changed pulse, so a move/idle oscillation returns pulses-1 and passes as settled (GPT FE_cs_selftests_2.5, verified); a wrong test under the water-levelling bars
  - its check: LevelSetChecks.Run requires N consecutive unchanged pulses; a red-first alternating-stub selftest fails before and passes after
  - files: `src/RimMandrake/FlowWorks/Source/SelfTest/LevelSetChecks.cs`
- `LEVEL_WATER_FIX_POND_SPLITS_ARMS` (proposed): [MINOR] Surface-gap reference does not connect canal arms through their pond
  - sweep reading: HEAD level_water.surface_gaps still only records touched pond surface (no traversal to other mouths); oracle parity-tested vs RM_SurfaceGap.Measure in selftest_flowworks_kernel_oracle.py, so game shares it; owner-seat 'Done when' note 2026-10-29
  - its check: unit case: two arms joined by a pond score one body; C# parity holds
  - files: `src/RimMandrake/FlowWorks/northstar/level_water.py`, `src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py`
- `PIT_SHOT_PROOF_FIX_OTHER_TARGET_PASSES` (proposed): [MINOR] Choosing another attack target is treated as proof that the intended target is unhittable
  - sweep reading: still true on HEAD: northstar/depth_rebuild_proofs.py:420 PASS when picked(at2) != eb, so the AI choosing any other hostile passes the 'unhittable' row; a wrong test
  - its check: the row PASSes only when eb is refused as a legal target (not merely unpicked); a planted second hostile no longer turns a regression green
  - files: `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py`
- `EXT_PLOTS_HARDEN_GRID_OFF_THE_MAP` (proposed): FlowWorks extensions plot grid runs off a 100-wide map: plot C digs x=100 and FAILs as MOD instead of UNMEASURED/SITE
  - sweep reading: wrong test: a live run FAILed plot C as MOD when the grid ran off a 100-wide map (spawned from FLOWWORKS_CANAL_DIGS_FROM_SOURCE_FAILS_64F4CE); northstar/extension_proof.py still exists
  - its check: on a 100-wide map, a plot that does not fit reads UNMEASURED/SITE, not MOD FAIL
  - files: `src/RimMandrake/FlowWorks/northstar/extension_proof.py`

## his words (as recorded on the merged tickets)

- on `LEVEL_SET_SELFTEST_FIX_IDLE_PULSE_SETTLES`: "It should slosh around until it levels, pond or canal or otherwise." (owner, quoted on POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD)
- on `LEVEL_WATER_FIX_POND_SPLITS_ARMS`: Done when: level_water.surface_gaps continues the walk through a touched pond to its other wet mouths; a unit case with two arms joined by a pond scores one body.

## verify

Acceptance test: none as one command, each repaired check must be seen to FAIL on a planted fault and PASS on the build, per check (each merged ticket above names its check).

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: RIMMANDRAKE_FIX_FLOWWORKS_FUZZ_FOUR_FLAWS_SINK_STILL_FLOAT
item: LAKE_FLOOR_SELFTEST_FIX_WET_SKIPS_HEIGHT
item: LEVEL_SET_SELFTEST_FIX_IDLE_PULSE_SETTLES
item: LEVEL_WATER_FIX_POND_SPLITS_ARMS
item: PIT_SHOT_PROOF_FIX_OTHER_TARGET_PASSES
item: EXT_PLOTS_HARDEN_GRID_OFF_THE_MAP
