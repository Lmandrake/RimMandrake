# SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED — naive judge on the over-pit scenes, 2026-11-05

Judge: a fresh Opus that did not make the art (rm-judge), shown the owner's two reference photos, the Timber deck, and offline renders of the redrawn art over 4 m pits at 83 px/cell (art_source/SuspensionRedesign/scenes.py; images beside this file: suspension_redesign_2026-11-05/scenes_over_pits_r4.png and _crop.png).

History: round 1 (0e40ad009a, 2026-10-24) Steel WEAK / Heavy WEAK; round 3 Steel WEAK / Heavy OK; round 4 below.

After round 4, changes not re-judged (a code review's findings): translucent strokes now blend instead of punching alpha into the picture, the anchors' cables end on the deck band's cable line (no 4 px jog), antialias dust (alpha 1-3) cleared; scenes_over_pits_installed_crop.png is the same view rendered from the installed Textures; the four looks are the same drawings in other finishes (looks_contact.png: rows base, Scrapper, Industrial, Modern, Futuristic).

## Verdict (round 4, verbatim)

- **Steel: OK.**
- **Heavy: STRONG.**

## Judge's text

> # Judge r4: SUSPENSION_BRIDGE_REDRAW_HEAVY_JUST_PAINTED (naive judge; judged on crop_r4.png against the owner photos and Timber)
> 
> (a) Broken: nothing serious. No holes, no misaligned joins, no red. The one risk is the Steel E-W anchors: the tower's X-brace is drawn flat across the full walkway, so from above it reads a little like a crossed-out gate (a barrier) rather than a portal. The one-per-cell slab joints on Heavy read as expansion joints, which is fine.
> 
> (b) Steel reads as a light steel footbridge: cement anchors, braced I-beam portals (the N-S face-on portals are good), a wooden crosswalk and steel rails. Along the span there is no main cable, no hangers and no stays, so it reads as a railed boardwalk, not clearly a suspension bridge. Heavy clearly reads as a heavy steel truss bridge: a dark lattice truss on both sides, heavy end portals, a paved concrete road and a cement base. It is rugged and close to the owner's photo. The two kinds are clearly different from each other. Heavy is far from Timber. Steel's planks are lighter and more even than Timber's, and it has rails, so the two can be told apart, but they share the plank look.
> 
> (c) Verdicts:
> - Steel: OK (towers and materials right; cables under-stated)
> - Heavy: STRONG
> 
> (d) Fixes (all for Steel):
> 1. Deck tile: a thin dark cable just outside each rail, with hanger ticks every 1/4 cell.
> 2. Anchor tile: 2-3 diagonal stay cables from the tower top down to the deck edge.
> 3. Thin the E-W anchor X-brace or keep it to the outer posts, so it reads as overhead, not as a barrier.
