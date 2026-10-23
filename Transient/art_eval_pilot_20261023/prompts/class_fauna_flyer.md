# Class prompt — fauna: FLYERS

Read `00_preamble.md` first. A flyer has a **grounded** body set (south, east, north) and, when it really flies, a
**flight flip-book**: whole-body frames `<frame>_<direction>` (direction north/east/south). Never a separate wing
layer. — owner 2026-09-19 (*"we make flyers flyers when we can"*; flip-book, not a wing render-tree).

Look for:
1. Everything in `class_fauna_walker.md` for the grounded set (facings, alien, canon, scale, style, donor).
2. **Grounded wings** (`FLYER_WINGS_GROUNDED`): standing/walking, the wings are folded and symmetric; a raised or
   spread wing pose belongs to flight frames only. A wingless or truncated body is a defect (owner 2026-10-15,
   Firehawk: *"north-facing image is just its wingless form, grotesquely"*).
3. **Flight frames** (`FLYER_BODY_MOVES`): head, neck and body hold the same place and size across the frames of
   one direction; only the wings change pose. — owner 2026-10-20: *"Their bodies should be kept static while the
   wings flap."* Judge from the stills; never ask for a live capture.
4. **Flight frames agree with the grounded art** (`F_INCONSISTENT`): same species, palette, proportions; an old
   flip-book that matches none of the grounded candidates is a mismatch.
5. **North/south in flight** follow the same rule as on the ground (rear vs front, no overhead view).
6. Small flyers (insects): still need readable silhouettes at 32 px/cell (`LEGIB_32`).
