# RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN

Found by the FlowWorks 0.1.0 walk-brief reader (item RIMMANDRAKE_STEWARD_FLOWWORKS_PRE_HUMAN_STAGE, 2026-11-21 ~6:15 PM PST).

## spec

None of FlowWorks's 31 in-game checks in `design/concepts/FlowWorks/version/test_table.json` declares a C# file. Each one
declares only its Python script and the concept folder (`reads`, `file`); no check has `exercises`. Measured 2026-11-21.
So the change relation (`src/RimMandrake/rimflow/rerun_relation.py`, page
`design/specs/2026-11-21-rerun-only-related/boundary.md`) relates no C# change of the mod to any check except `sc_walk`
(kind `live_full`, a whole-mod check). Every other check keeps a row made before any C# change.

The concrete case (measured with `build_match.carried_rows` and `git merge-base --is-ancestor`):
- `sc_pit_reads` (bar `pit_reads_as_hole`) and `sc_covered_pit` (bar `covered_pit_springs`) count from visit 2, build
  65926ef481 (2026-11-19 7:37 PM PST).
- The pit draw was rebuilt after that build: e2288f4c84 (2026-11-20 5:58 PM PST, "pits drawn as relative terrain"; it
  changes `Source/Superdeep/RM_ExcavationWalls.cs` by +274/-14 and adds the concealed-cover lids). The water look was
  rebuilt by b80104f7a7.
- `sc_sluice`, `sc_one_network`, `sc_slime`, `sc_river`, `sc_fill_tiers` and `sc_dig_and_read` also count from
  65926ef481. 34 files under `Source/` changed between that build and the walk build bdd56c6ff6.
- `build_match.py check --mod FlowWorks` reads "31 count, 0 to run" and lists 65 UNDECLARED files, among them
  `RM_ExcavationWalls.cs`, `RM_UnderLiquid.cs` and `RM_MapComponent_Excavation.cs`.

The boundary page accepts "a C# file the check exercises but does not declare" as not survived, with the owner's walk
as a guard. With no C# declared on any check, that case is the normal case for every C# change. So the walk is the only
reader of those bars after a C# change.

The fix: each FlowWorks in-game check declares the C# files (or folders) that its scene exercises, in `exercises`.
Then the relation reruns exactly the touched checks. The same gap can exist for every other mod's test table [guess
~70%]; check those too.

Why the reader did not fix it in the sitting: the fix changes which in-game verdicts count at the walk door. For
FlowWorks now, it would send checks back to Stage 6 after the mod reached Stage 7. The walk-brief reader has no veto,
and only the Conductor decides that.

## verify

Run the acceptance test below. Also, after the declarations, `build_match.py check --mod FlowWorks` names
`sc_pit_reads` and `sc_covered_pit` as RERUN, or they carry rows made on a build that holds e2288f4c84.

## criteria

Acceptance test: `bash infrastructure/state/items/RIMMANDRAKE_DECLARE_FLOWWORKS_SCENE_CSHARP_PIT_REDRAW_UNSEEN.acceptance.sh`
(from the repo root). Exit 0 means pass: no UNDECLARED line names `Superdeep/RM_ExcavationWalls.cs`,
`Superdeep/RM_UnderLiquid.cs` or `RM_MapComponent_Excavation.cs`. Expected result: 3 of 3 ok. Seen red on the base
(origin/main at the time of filing): 0 of 3, exit 1.

## refs

file: design/concepts/FlowWorks/version/test_table.json
file: src/RimMandrake/rimflow/rerun_relation.py
