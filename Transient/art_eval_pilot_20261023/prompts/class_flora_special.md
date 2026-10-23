# Class prompt — flora: SPECIAL growth (hanging curtains, wall growth, vent growth)

Read `00_preamble.md` first. Some plants grow on overhangs, walls or vents but are still drawn as one picture on
a ground cell.

Look for:
1. **Shows the described growth habit** (`DESC_MISS`): hanging fingers hang, a curtain reads as a curtain. Since
   the game draws it on a flat cell, the picture must still make sense standing on the ground (it may imply the
   overhang it hangs from, but not paint a whole rock face — `ALPHA_HALO`).
2. Everything in `class_flora_bush.md` items 2–10 applies.
