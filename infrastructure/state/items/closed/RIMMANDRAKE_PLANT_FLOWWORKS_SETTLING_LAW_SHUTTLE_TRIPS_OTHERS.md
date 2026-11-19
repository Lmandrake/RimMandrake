# RIMMANDRAKE_PLANT_FLOWWORKS_SETTLING_LAW_SHUTTLE_TRIPS_OTHERS

## spec
Child of `RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS`. FlowWorks' law family `settling` (law `settled_scene_reaches_fixed_point`, check "no fixed point after"
in FlowKernelFuzz.cs) is the one family not yet seen to go red. Its planted break, ShippedMatrixProbe `--plant shuttle`
(one level moved back and forth between two cells each pulse), turned kernel_fuzz red 20/300, but every red came from
`fluids_never_turn_into_each_other` or `sink_drain_accounted_cell_by_cell`: the per-pulse checks return first, and the
probe hook cannot see a cell's fluid or the sinks (they live in the test's ArrayWorld, not the kernel) [measured:
`D:\ClaudeWork\rimmandrake\evidence\vv_laws_first_slice\p_settling.log`]. Fix: plant from the world side (a hook in the staged ArrayWorld that knows cellFluid and
sink), shuttling only between two same-fluid non-sink cells in a no-sink scene; or a staged-source plant in the
kernel that makes a settled pool oscillate.

Codex review (2026-11-18, finding 3): the shuttle as written need not reverse or continue: both endpoints must hold a
level AND have room for another, so with depths [2,2] and water [U,U] the first move leaves [2U,0] and neither cell is
eligible again; the pair is not kept between calls and need not be adjacent. A world-side plant should keep one pair,
check the donor's stock and the receiver's room each call, and confirm the post-pulse state really alternates.

## criteria
- Acceptance test: `python3 src/RimMandrake/Utils/vv_laws.py prove FlowWorks --family settling` prints
  `settling/kernel_fuzz PROVEN ... by settled_scene_reaches_fixed_point`; NOT_PROVEN today (watched, 2026-11-18).

## verify
- The same command, plus the unplanted baseline green.

## refs
file: src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs
file: src/RimMandrake/Utils/vv_laws.py
