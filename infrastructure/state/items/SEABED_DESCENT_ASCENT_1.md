# SEABED_DESCENT_ASCENT_1 — the gravship flies down to the sea floor and back up

Split from `SEA_DIVE_HATCH_RETIRE_1`. Owner, 2026-10-01: *"Now the ship just flies to a new
planetary layer called sea floor."* Phase 2 of the seabed plan
(`/home/mandrake/.claude/plans/glistening-tumbling-moore.md`); the layer itself is built
(`SEABED_PLANET_LAYER_1`, `src/RimMandrake/DivingInteraction/Source/RM_SeabedLayer.cs`).

## spec

1. The pilot console's destination step offers the `RM_SeabedLayer` tile under a sea tile (and the sea
   tile above a floor tile) as a launch destination; fuel cost per depth both ways.
2. Arrival on a floor tile generates the floor map (`RM_SeabedSite`) and lands the ship; take-off from
   the floor returns it to the surface tile above. No pawn walks or caravans between the two
   (`canFormCaravans false` already holds).
3. Read GravTide (`gravtide.mod`, installed, inactive) for technique before writing anything: it has
   already solved most of this (CLAUDE.md, the 2026-09-26 "is there a mod" lesson).

## criteria

- From a sea tile, the ship's launch dialog offers the floor below; landing there builds a floor map;
  launching from it returns to the surface tile above.
- Proven live with a bridge state read (`Find.CurrentMap.Tile.Layer`), not a screenshot hunt.
