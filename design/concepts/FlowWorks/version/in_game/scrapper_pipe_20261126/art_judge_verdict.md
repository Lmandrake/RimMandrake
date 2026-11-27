VERDICT: KEEP

Subject: the "Scrapper" look of the universal pipe, as a straight run (26 cells, live game, about 109 px per cell, 2026-11-26).
Judge: a fresh blind art judge (claude-opus-5-5). Brief: design/RimMandrake/art_judge_brief.md.
Question: does it now read crisp at close zoom, with no repeating spot, at a quality that sits beside the Industrial pipe?
Owner's note (E4, 2026-10-23), the requirement: "scavver pipe is VERY low res, please use higher resolution graphics." / "Another example of the ugly as heck scavenger-style pipe low res".

## Baseline: the old screenshot (20261023223056_1.jpg)
I cropped the straight run between the tank and the 4-way junction. The pipe is a soft copper band. It has one teal-green spot at the same place in every cell, so it reads as a stamped repeat. This is the fault that the owner named.

## Per image
- **scrapper_west.png**: KEEP. The edges are sharp: the ground steps to the dark cylinder edge in one pixel (luma 70 to 26, the same step as Industrial, 75 to 29). The body has rounded shading, with a lit centre and dark flanks. Orange rust carries irregular grey-green patina. The fittings break the run at uneven spacing: wrapped collars, a bolted two-hole clamp and a plain seam. The west end cap is a small domed cap, not an open bore (C6 passes). No single spot repeats cell by cell.
- **scrapper_mid.png**: KEEP. Same reading. At 3x nearest-neighbour zoom (scratch zoom_cmp.png) the pipe is 13 to 14 px thick, the same as Industrial. The texture holds up as painted rust, not upscale blur. The dark edge is the cylinder's shading, not a drawn keyline (B1a passes).
- **scrapper_east.png**: KEEP. Same reading. Collars and clamps vary along the run, and the east cap is domed and closed.
- **industrial_mid.png** (reference): plain steel, with a twin highlight stripe and a dark edge, 13 to 14 px thick. The Scrapper pipe matches it in thickness, edge sharpness and shading depth. Scrapper carries more surface detail, as a scavenger style should, so it sits beside Industrial at the same resolution tier.
- **both_runs.png** (wider view): Scrapper reads as a clear orange line, with dark fitting marks well apart from the brown ground (B2 passes). Industrial reads as a thin dark double line. Both read as the same scale of object, and neither looks blurrier than the other.

## Constraints applied
B1 (high resolution where the player sees it): passes. B1a (no outlines): passes. B2 (legible against the ground): passes. B4 (the colour reads as material): passes; it reads as rusted iron or copper, not paint. C6 (true perspective plane, no bore on the run): passes. E4 (his note "use higher resolution graphics"): met.

Not given: the 32 px/cell copy and a true-scale panel beside a human (D1). The question named this live capture set as the level that is enough, so D1 is noted here, not judged. The pipe is not owner-kept, so E3 does not apply.

## Polish (blocks nothing, files no ticket)
- The rust and patina base texture still shows a faint one-cell periodicity when measured: the autocorrelation of the green-minus-red signal at a one-cell lag is about 0.45 on the west and east captures, and 0.06 on mid. By eye I see no landmark that repeats; the fittings and the soft mottle hide it. A second base variant would remove the remaining sameness.
- The fitting variants sometimes cluster. On east, two clamps sit in adjacent cells, then three collars come close together. A spread-out random pick would read more hand-built.
- The bolted clamp's light grey reads a little pale against the rust. A slightly darker or rustier grey would sit in better.
