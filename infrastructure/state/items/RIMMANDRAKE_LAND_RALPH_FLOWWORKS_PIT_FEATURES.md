---
state: proposed
needs: offline
---

# RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES

Filed 2026-11-13 by the Ralph clone cleanup (the retired Ralph loops, `design/RimMandrake/retired_loops_2026-11-13.md`).
Graffiti, GSS and Pyrelands were fully on main and their clones were removed. FlowWorks is not on main.

## spec

The Ralph FlowWorks loop built pit features that never reached main. Land the parts the locked FlowWorks
Design Version 0.1.0 asks for, rebuilt onto today's FlowWorks, and leave the rest to the owner.

## where it lives

- Remote branch `origin/ralph/flowworks`, commits `ec381202c5..69c6028177` (36 commits, 2026-11-07 to 11-08; merge-base ec381202c5).
- Bundle (verified): `D:\ClaudeWork\backups\rimmandrake\ralph_cleanup_20261113\ralph_flowworks\ralph_flowworks.bundle`.
- Clone kept: `/home/mandrake/rm/scratch/BENCH/ralph_flowworks` (HEAD = the remote tip; only `ralph/` loop files dirty).
- File-by-file comparison with origin/main: `D:\ClaudeWork\rimmandrake\conductor\ralph_cleanup_20261113\flowworks_branch.tsv`
  (171 files; non-generated ABSENT 79 = 56 `ralph/` scaffolding + 23 mod source, DIFFERS 63, IDENTICAL 1).

## what is unlanded, per feature

| feature | branch files (main lacks or differs) | 0.1.0 asks for it? | branch selftest |
|---|---|---|---|
| Raiders rescue their fallen | `RM_RaiderRescue.cs` (745 lines) | yes: leaf `raiders_fetch_their_fallen`, inventory `inv_raider_fetch_fallen` (impl absent on main). Same work as FLOWWORKS_RAIDERS_BUILD_LADDER_FOR_FALLEN | `RaiderRescueChecks` |
| Bedless pit prison | `RM_BedlessPitPrison.cs` (672) | yes: leaf `drained_hole_is_a_prison`, inventory `inv_prison_no_bed` (impl absent on main) | `BedlessPitPrisonChecks` |
| Hung bridge redraw | `Pits/Suspension/RM_SuspensionHang.cs` (984), `RM_SuspensionHangMath.cs` | yes: leaf `hung_bridge_spans` (main already has suspension bridges; this is the hung deck look) | `Hang_*` checks |
| Ladder rigs | `RM_LadderRigMath.cs`, `RM_LadderDraw.cs`, `art_source/LadderRig/slice.py` | yes: `portable_ladder_leans_on_its_wall` | `LadderRigChecks` |
| One depth drawing | (branch tag PIT_DEPTH_ONE_DRAWING) large diffs in `RM_PitDepthDraw.cs`, `RM_PitDrawMath.cs`, `RM_ExcavationWalls.cs` | yes: `pawn_height_follows_depth`, `pit_reads_as_hole`. BUT its sink numbers (0.37..1.50 at 0.5..4 m, knee curve, pitSinkPerLevel 0.3) contradict the owner-confirmed sink of 0.05 per half metre on main (23151d18be): take the drawing, never the numbers | `PitDepthDrawingChecks` |
| Sod on pit covers | `RM_PitCoverSod.cs` + Math, diff in `Building_PitCover.cs` | yes: `covered_pit_springs` | `PitCoverSodChecks` |
| Three pit looks, oblique default | `RM_PitLook.cs` + Math | `pit_reads_as_hole` yes; WHICH look is an owner call | `PitLookChecks` |
| Raid-stall fixes | `RM_MeleeTargetReach.cs`, `RM_CliffMelee.cs`, `RM_RaidLeavesTrapped.cs`, never trash a concealed cover (isTrap) | supports the judged raid (vision point 4) and the fetch leaf | none named |
| Rain fill rate (~0.24 m per rain day) | diff in `RM_PitFillEffects.cs` | bug fix; overlaps RIMMANDRAKE_SLOW_RAIN_FILL_PIT_BRIMS_IN_ONE_NIGHT | none named |
| Starting water bottles | `Patches/Scenarios_StartingWaterBottles.xml` | no (not in the vision; `inv_bottles_thirst` does not name starting bottles): OWNER CALL / next version | none |
| Dig progress | branch version | superseded by main d23e9b6a83: drop | — |
| Climbing gear placement | `ClimbingGear/place.py` | art tooling for the ladder/climb leaves | none |

## what landing would take

The branch predates today's FlowWorks changes: water is now one number per square, the pawn sink default changed
(23151d18be), and dig progress landed separately (d23e9b6a83). This is no merge; it is a port feature by feature onto
current main, rereading each branch file against main's water and sink model. Settings in
`RimMandrakeFlowWorksMod.cs`, `RM_PitRoomMath.cs` and `RM_RaiderTrenchMath.cs` differ heavily and need a line-by-line
reconcile. The branch's own last progress note recorded the full selftest at 1282/1285 (three reds it called
pre-existing).

Owner calls before landing: which pit look is default; whether starting water bottles belong at all (next version?).

## verify

Acceptance test: per feature, the branch's named SelfTest checks (`RaiderRescueChecks`, `BedlessPitPrisonChecks`,
`Hang_*`, `LadderRigChecks`, `PitDepthDrawingChecks` rewritten to main's sink numbers, `PitCoverSodChecks`,
`PitLookChecks`) pass on main in `RimMandrakeFlowWorks.SelfTest`; the raid-stall fixes and rain rate have no branch
selftest, so `Acceptance test: none, needs a live raid` for those until one is written. Then `rimflow verify
RIMMANDRAKE_LAND_RALPH_FLOWWORKS_PIT_FEATURES --sha <sha> --level L0 --result pass ...` and close.
Delete the clone `/home/mandrake/rm/scratch/BENCH/ralph_flowworks` once landed or dropped (the bundle and the remote
branch keep the work).
