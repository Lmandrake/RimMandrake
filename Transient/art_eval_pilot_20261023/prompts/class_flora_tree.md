# Class prompt — flora: TREES and large plants

Read `00_preamble.md` first. A tree is one picture drawn larger than its cell: the trunk base sits on the cell,
the canopy overhangs neighbours. Players walk beside and under trees, so scale against the human matters most.

Look for:
1. **Size beside the human** (`SCALE_WRONG`) — owner 2026-10-15 (Hydenock): *"That's a beautiful tree but it's
   tiny! It should be much much larger."* and *"Superb though that is just a moderate one. They can get much
   bigger."* A full-grown tree is several times human height unless the description says otherwise.
2. **Trunk anchoring** (`ANCHOR`): the trunk base at the bottom centre of the canvas, roots/base not cut off,
   the canopy not lopsided so far that the tree seems to float off its cell.
3. **Reads as a tree, not a lump** (`LUMP`) — owner 2026-10-18 (Mourvel): *"Reads like a green lump or hill. It
   was supposed to be a willow-like dome the player could step beneath."* Silhouette must show trunk and canopy.
4. **Shows the description** (`DESC_MISS`): bark colour, wind-stripped branches, where it grows, its shadow habit.
5. **Natural, not constructed** (`CONSTRUCTED`).
6. **No baked scenery** (`ALPHA_HALO`): no cliff, rock or ground under the roots unless the description makes the
   rock part of the plant (a tree "gripping rock" may show its roots in a crack, but not a whole cliff face).
7. **Realism** (`STYLE_CARTOON`) — owner 2026-10-18 (Vurmeloth): *"Much more realistic please."*
8. **Resolution** at max zoom (`RES_LOW`): a big tree needs a big canvas.
