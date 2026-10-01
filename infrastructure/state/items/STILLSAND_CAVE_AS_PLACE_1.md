# STILLSAND_CAVE_AS_PLACE_1 — the cave's preservation, its drip, its glass walls and its mark

Split from `STILLSAND_PRECIOUS_CAVES_1` (spec 2, "the cavern as a place", and two table rows).
The chamber itself is built: a thick-roofed, permanently shaded floor of the rock's own rough stone,
and the brine seep, which reuses FlowWorks' shipped `RM_WaterBrineShallow`. These parts are still owed:

## spec

1. **The mummified preservation register:** nothing rots inside the cave, and desiccated remains stay.
   This needs C#. Read `CompRottable` first, then gate rotting on a roofed `RM_Stillsand` cave cell.
2. **The drip:** the cave's drip is the one water sound in the biome. It needs a SoundDef and an
   audio file, played as an ambient sustainer near the seep.
3. **The lens grotto's grown-biosilica walls:** a mineable natural-rock ThingDef that yields
   `RM_Biosilica`, with its own art (do a dedup check, then `fill_queue.py`). Then replace the
   floor stacks in `RM_PreciousCave_LensGrotto` with a ring of this wall.
4. **The taken cave's tribal mark:** a proper tribal glyph. Today the row soft-references the
   Graffiti mod's `RM_Graffiti_Vandal` scrawl.

## criteria

- A corpse left in a Stillsand cave does not rot.
- A lens grotto shows biosilica walls that can be mined for `RM_Biosilica`.
