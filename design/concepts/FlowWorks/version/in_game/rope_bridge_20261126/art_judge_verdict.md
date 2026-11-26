# Rope suspension bridge redraw - blind judge verdict (2026-11-26)

*Judged on the run before the polish pass (captures judged_ew_rails_on.png and Transient/rope_bridge_look_judged); the polish after it: backstays tied to the bollard heads, hand rope 0.045 -> 0.055 and netting 0.45 -> 0.55 thick (its polish lines 2, 3 and 1). The other crops here are the final run.*

Judge: claude-opus-5-5, blind (did not make the art). Brief: design/RimMandrake/art_judge_brief.md@1b8e220252, standing_rulings.md
§The judge refuses flaws, not polish. Look 1 of at most 2.

## Verdict: KEEP

Promise judged (E4, owner walk 2026-11-25, verbatim): "Rope bridge should look like Ropes along the sides with planks laid
upon the ropes. The rails should also be of ropes and cast shadows. The ropes coming from the ground should be aligned with
the sides of the bridge, not sit in the middle of the walkway and connect to nothing. Rope bridge "rails" should look like
rope netting, and Rope bridge "no rails" should still have hand-guide rails as part of its construction. There should be
sparse wood slats on a rope bridge, that's it."

Evidence: crops/ew_rails_on.png, crops/ew_rails_off.png, crops/ns_off_left_on_right.png, crops/pawn_on_ew.png; native parts
src/RimMandrake/FlowWorks/art_source/RopeBridge/out/*.png; judge zooms in D:\ClaudeWork\rimmandrake\judge_rope_bridge\
(off_zoom.png, on_zoom.png, playzoom_x2.png, parts.png).

1. Side ropes with sparse slats, nothing more on the walkway: YES. Two twisted side ropes run the full span (EW and NS);
   plank slats are lashed across them with open pit showing between each slat (about one slat per 0.35 cell). The old
   solid boardwalk and the mid-walkway ground ropes are gone. The only things crossing the deck are the south hand rope
   and netting, drawn there by the top-down height shift (geometry).
2. Railings OFF still show hand-guide ropes: YES. EW off: a sagging hand rope on each side from post top to post top, with
   thin vertical hangers down to the side rope. NS off (left): hand ropes as thin lines along both sides.
3. Railings ON read as rope netting: YES. EW on: a diamond/X rope lattice between hand rope and side rope on both sides,
   clearly netting, also at 32 px/cell. NS on (right): the netting is near edge-on and reads as a hatched double line
   (geometry per the brief note).
4. Hand ropes / netting cast shadows: YES. EW on: a clear dark lattice shadow falls south-east below the deck on the pit
   floor. EW off: fainter diagonal hanger and hand-rope shadow lines below the deck. NS: diagonal shadow lines fall east
   of each bridge.
5. Ground ropes and bollards in line with the sides, connected: YES. EW: one bollard at each end of each side rope (north
   and south rows), the side rope running straight from bollard into the deck; a stay runs from each bollard up to the post
   top. NS: bollards at north and south ends in line with the two side ropes. None sits mid-walkway; none ends in nothing.
6. Style (B1 painterly, B1a no outlines, B2 play zoom): YES. Native parts: grained, weathered planks and twisted hemp rope
   with soft shading, no black keyline. At 32 px/cell the slats and two side ropes read as bold shapes, warm wood clearly
   apart from the dark pit and the soil.

No refusals.

## Polish (blocks nothing, files nothing)
- polish: NS railings ON vs OFF are hard to tell apart at play zoom (netting edge-on); a slightly heavier netting line would help.
- polish: the hand-rope shadow with railings OFF is faint compared with the netting shadow.
- polish: the EW end stays run on past the bollards to the ground beyond them, with no stake at their foot.
- polish: in game the rope reads orange-brown rather than the pale hemp of the reference photo and of the native parts.
- polish: EW railings ON, the south netting drawn over the slats makes the deck busy at close zoom (height projection).
