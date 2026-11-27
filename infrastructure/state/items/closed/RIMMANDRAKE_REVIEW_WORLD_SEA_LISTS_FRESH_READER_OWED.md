## spec
One fresh reader (a run that did not make the change) reads the change of fcb00481dc..7716e0853e once, by
`src/RimMandrake/rimflow/roles/code_review.md`: `src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs` (BuildSea film
scale, BuildSwirls list/water/per-biome scale), `src/RimMandrake/BiomesShell/Source/RM_WorldLookLists.cs`,
`src/RimMandrake/BiomesShell/Source/RM_BiomesMod.cs` (two toggles). Page:
`design/specs/2026-11-26-world-sea-lists/boundary.md`.

## verify
`python3 src/RimMandrake/BiomesShell/selftest_world_sea_lists.py` stays PASS after any fix; a significant finding is
fixed test first.

## criteria
The reader's verdict is recorded (`code_review_status.py mark-clean` or a fix with its test). There is no second read.

## refs
file: src/RimMandrake/BiomesShell/Source/RM_WorldLook.cs
file: src/RimMandrake/BiomesShell/Source/RM_WorldLookLists.cs
