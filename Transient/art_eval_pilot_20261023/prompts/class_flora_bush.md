# Class prompt — flora: BUSHES, SMALL PLANTS, FUNGI, REEDS (one-cell plants)

Read `00_preamble.md` first. A one-cell plant is one picture (no facings), drawn on the bottom edge of its cell at
a random size within its range, often in a random pool of variants.

Look for:
1. **Shows the description's defining feature** (`DESC_MISS`): the fruit it yields, the quills, the glow, the
   frond shape. If the plant is harvested for an item, the item should be visible on the mature plant.
2. **Alien where invented, faithful where vanilla**: an invented plant must not read as a plain Earth plant
   (`STYLE_EARTHLY`); a vanilla plant's art is a reinterpretation of the vanilla one (check the label).
3. **Natural, not constructed** (`CONSTRUCTED`) — owner 2026-10-18: *"Do not make it look constructed by people as
   an arch: it needs to be a natural plant"*.
4. **Stands on its base** (`ANCHOR`): stem/base at the bottom of the canvas, centred; nothing cut off at the
   bottom, not floating.
5. **No baked scenery** (`ALPHA_HALO`): rocks, soil mound, water or a ground disc under the plant are a defect
   unless the description says the plant grows on/around that thing.
6. **Scale** (`SCALE_WRONG`): compare with the human in the scale panel and the description's own words
   ("knee-high", "waist-high", "shin-high", "melon-sized"). A knee-high plant is about a third of the human.
7. **Fills its canvas** (`FOOTPRINT`): a tiny subject floating in a big empty canvas is drawn tiny in game
   (look at the 32 px/cell view; owner 2026-09-19 on the Rot: *"wrong size, 6 wide"*).
8. **Legibility at 32 px/cell** (`LEGIB_32`) and **resolution at max zoom** (`RES_LOW`).
9. **Realistic painterly** (`STYLE_CARTOON`, `STYLE_OFF`) — owner 2026-10-15 (Nysyllin): *"ask for a much more
   realistic version to be generated"*.
10. Donor art (`DONOR`) is never the final keep, even if it looks good.

A good primary plus good alternates → KEEP with `keep_also` (random pool). Keep-worthy but improvable → KEEP
with the improvement in `note`.
