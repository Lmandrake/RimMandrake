# SEABED_DESCENT_ASCENT_1 — the gravship flies down to the sea floor and back up

Split from `SEA_DIVE_HATCH_RETIRE_1`. Owner, 2026-10-01: *"Now the ship just flies to a new
planetary layer called sea floor."* Phase 2 of the seabed plan
(`/home/mandrake/.claude/plans/glistening-tumbling-moore.md`); the layer itself is built
(`SEABED_PLANET_LAYER_1`, `src/RimMandrake/DivingInteraction/Source/RM_SeabedLayer.cs`).

## spec

1. The pilot console's destination step offers the `RM_SeabedLayer` tile under a sea tile (and the sea
   tile above a floor tile) as a launch destination; fuel cost per depth both ways.
2. Arrival on a floor tile generates the floor map (`RM_SeabedSite`) and lands the ship; take-off from
   the floor returns it to the beach (land-layer) tile above. No pawn walks or caravans between the two
   (`canFormCaravans false` already holds).
3. Read GravTide (`gravtide.mod`, installed, inactive) for technique before writing anything: it has
   already solved most of this (CLAUDE.md, the 2026-09-26 "is there a mod" lesson).

## criteria

- From a sea tile, the ship's launch dialog offers the floor below; landing there builds a floor map;
  launching from it returns to the beach (land-layer) tile above.
- Proven live with a bridge state read (`Find.CurrentMap.Tile.Layer`), not a screenshot hunt.

## reshaped 2026-11-01 after a code read (owner card: "Read code, then reshape")

The idea stands (owner 2026-10-01: the ship flies to a new planetary layer called sea floor). The BUILD
mostly exists and is vanilla-driven, not ours: `RM_SeabedLayer.xml` registers the layer with
`defaultMapWorldObject RM_SeabedSite`; `RM_SeabedSiteParent` (91 lines) picks the floor generator from the
tile's biome (`RM_SeabedGenerators.xml`); a gravship landing on a layer tile makes that world object
through vanilla `GravshipUtility` (RimSage-read 2026-10-03). So spec steps 1-2 are the stock Odyssey
launch dialog plus our site object. What is still UNMEASURED, and is this item's real work:
1. does the launch dialog list a floor tile when launching from an impassable sea tile (and the beach tile
   from the floor)? (`SEA_FLOOR_AND_CATCH_PASS_1` line 23 flags the same unknown)
2. does the return trip from the floor reach the beach (land-layer) tile above, with fuel cost per depth?
3. leftovers: `RM_SeaDiveHatch` is retired by `SEA_DIVE_HATCH_REMOVE_1`; nothing here depends on it.
NEXT: one bridge state read of `Find.CurrentMap.Tile.Layer` before/after a descent (see criteria); then
either close with that evidence or fix only the failing step. Do not rebuild the layer or site object.
