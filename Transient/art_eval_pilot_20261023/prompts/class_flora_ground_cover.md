# Class prompt — flora: GROUND COVER (grass, moss, mats, low carpets)

Read `00_preamble.md` first. Ground cover is drawn many times per area — often several small copies per cell —
so it is judged as a *texture of the land*, not as a single specimen.

Look for:
1. **Reads as what the description says** (`DESC_MISS`): moss must look like moss, a mat like a mat hugging the
   ground, grass-analog blades like blades. — owner 2026-09-19 (Pale Moss): *"make look really like moss"*.
2. **Low and flat in silhouette**: ground cover sits ON the ground; a tall upright bush-shape or a single big
   object is wrong (`DESC_MISS`/`FOOTPRINT`).
3. **Repeats without a seam or a stamp**: imagine 20 copies scattered at random sizes — does one striking
   feature repeat obviously? Edges must fade naturally, no hard rectangle or circle edge (`ALPHA_HALO`).
4. **No baked ground**: no soil patch, rock or puddle under it unless the description makes the substrate part
   of the plant (`ALPHA_HALO`).
5. **Legible at 32 px/cell** in the scale panel's normal-play view: a coherent tuft with value contrast against
   the brown ground, not grey mud (`LEGIB_32`).
6. **Scale**: a tuft/cushion small beside the human (well under a cell) unless the card says otherwise
   (`SCALE_WRONG`). Check `cells` and `visualMax` on the card.
7. **Realism** over illustration (`STYLE_CARTOON`) — owner 2026-10-10 on kept flora: *"two more improved
   variants that are more realistic"*.
8. Donor or vanilla texture standing in (`DONOR`), and duplicates across candidates (`DUPLICATE`).

KEEP when one candidate passes 1–6; list other good ones in `keep_also` (ground cover benefits from a random
pool).
