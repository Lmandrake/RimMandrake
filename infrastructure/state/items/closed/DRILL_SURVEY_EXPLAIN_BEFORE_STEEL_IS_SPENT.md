# DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT

From the BENCH player's-eye FlowWorks UX review, 2026-10-22, read offline from source (owner's night order: "Keep testing and getting Flow Works absolutely logical, looking great and sensible, and the UI/UX workable for the player."). Behaviour must not change unless the item says so; text-only fixes need a winbuild with DLL + .srchash committed together.

## spec

1. **Drill/tap survey is a dead-end until built** (`Building_LiquidDrill.GetInspectString`): the
   subsurface result ("nothing drillable found under this map") is readable only on a BUILT drill.
   A player spends steel, components and 400 W to learn there was nothing to drill. Show the survey
   while placing (PlaceWorker readout / ghost text) or on the map's info. **Filed `DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT`.**

## criteria

- A new player can read the changed UI and know what to do next; the old confusing text is gone (grep).
- FlowWorks selftests stay as green as before.

## NEXT

Pick it up offline; no game needed for the text part.
