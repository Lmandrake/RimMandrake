## spec
Plan P4 of `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG` (`design/RimMandrake/flowworks_one_rebuild_plan_2026-10-17.md`):
`design/RimMandrake/flowworks_unified_depth_2026-10-17.md` §7.2, done in the same pass as
`WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`.

Absorbed 2026-10-17 (`design/RimMandrake/flowworks_ticket_consolidation_2026-10-17.md`):
`LAKE_FLOOR_TUNE_TEN_TO_FIFTY_METRES` (same bed code and settings) and `LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS` (the
litres/dL base built at `cf4f24213` + `0d6167af4`; its live checks were never run and are carried below).

**The title is partly wrong (titles cannot be edited):** "pit stays 2 m (D5)" was reversed by the owner's card later
on 2026-10-17 (colonists dig to 8 m by default, setting 2-20 m: `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT`). Water no longer
moves in whole notches (exactly level). Build neither. Everything else in the title stands.

## verify
- L1: no "five" anywhere in FlowWorks code, defs, settings or strings; `sourceBudgetMultiplier` deleted (D4 default,
  veto on `DEPTH_DEFAULTS_ASK_ELEVEN_VETOES`); one burn rate (D3 default).
- L1: `FillTier` by metres of water; every whole-notch reader (pumps, burn, heat, drowning, mouseover, Level Holder,
  drilling reserves) reads metres/litres; the Python oracle reads the C# constants; changed in the same commit.
- L1: lake floors: natural lake/pond floor default 20 m, setting to 125 m; very large lakes and oceans may reach 50 m
  (propose the size class for "very large" and show it to him); oceans/edge rivers stay limitless; settings in metres.
- L1: containers in litres: bottle 1.5 L, bucket 15 L, barrel 208 L; a save from before the litres base migrates with
  every container's contents unchanged.
- L2 (P10 walk): mouseover and settings show metres and litres in game; a pre-litres save loads with the same liquid.
