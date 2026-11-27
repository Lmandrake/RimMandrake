# Judge 2: Scrapper heavy bridge deck pieces, check of the repair (offline), 2026-11-27

Judge: claude-opus-5-5, a blind judge. I did not make the work, and I am not judge 1.
Brief: design/RimMandrake/art_judge_brief.md (clone RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS.det, HEAD 7ebbccc7d0).
Item: the owner's ticket of 2026-11-26, "FlowWorks, default look Scrapper: the heavy bridge and both jetties still draw the OLD
art ... Generate Scrapper versions in the manner of his picks, art judge first, install through art install; the art judge also
rules cables drawn over a colonist and posts on old anchor frames."
Subject: src/RimMandrake/FlowWorks/art_source/JettyBridgeRedesign/generated/tiles/heavy_bridge_Scrapper_B_{root,mid,tip,solo}.png
(256x256, run east). sha1 prefixes (sha1sum order mid, root, solo, tip): b71ab8a8973c, 378354d8ec6d, 58f4835bce0d, 571ee0e021d7.
This is the second look: the check of the repair. It checks judge 1's REDO lines (E4, B3) and changes that the regen made.

## Verdict: KEEP (all four pieces)

| piece | verdict | notes |
|---|---|---|
| root | KEEP | E4 and B3 repaired. Pick B's 6-bolt end plate on the left, riveted girders on both long edges |
| mid  | KEEP | E4 and B3 repaired. Olive and brick-red riveted plates between the girders, rope lashing on the top girder |
| tip  | KEEP | E4 and B3 repaired. The mirror of root: the bolted end plate is on the right |
| solo | KEEP | E4 and B3 repaired. Bolted end plates at both ends, one olive panel between them |

### (a) In the manner of his picks, reads as Scrapper beside C, heavier than C: YES
- Pick B's structure is kept part for part (j2/pieces.png, rows NEW against pick B):
  - the same end-plate width and the same 2x3 big bolts with corner gussets;
  - the same two riveted girders top and bottom, at the same rows;
  - the same panel division in mid;
  - the same opaque rows, 20..234.
- The material comes from his Scrapper C:
  - chipped olive panels, with one brick-red panel in mid;
  - rust orange and oxide brown girders;
  - a rope lashing on the girder.

  This matches the Scrapper brief: "riveted steel plates of different ages ... rope or wire lashing ... rust orange, oxide brown,
  faded olive and brick-red panels". The deck reads as rusted, never as "abandoned". It reads as the same hand as C (j2/row1.png
  against j2/row3.png).
- It reads as heavier than C at 64 and at 32 px/cell (j2/play32_x2.png, top = NEW, middle = C). The deck is wider, the end plates
  are big and dark, and the girders are thick, where C has a slim deck with rope rails. The rusty post and chain now match the
  deck. The "one bridge, two art styles" fault from judge 1 is gone.

### (b) Seams and square-boundary rhythm: PASS
- Measured on the four PNGs:
  - At each joint (root|mid, mid|mid, mid|tip, root|tip), the mean |dRGB| across the joint is 5.04 to 5.06. Between the last two
    columns inside a piece it is 5.61 to 5.68. So a joint is no rougher than the texture.
  - The alpha rows are identical in all four pieces.
- By eye at 2x (j2/ew4_joints_x2.png, joints at x=768 and x=960 of closeup_new_ew4_192.png): the girder rivet rows, the rail
  lines and the panel joints run straight through every joint. In the turned N-S run there is no seam either (j2/ns_pair.png).
- Rhythm (polish only): mid carries one red panel and one rope lashing. So a long span repeats them once per square. At 32 px
  this shows as a faint red patch per square. His picks B and C also repeat their mid detail per square. Blocks nothing.

### (c) Defects that the brief names: none
Passed:
- B1a: no keyline; the dark edges are the girder rims, as in pick B.
- B2: at 32 px/cell the deck has the following clear shapes, which stay clearly apart from the water and the grey anchors:
  - dark bolted ends;
  - an olive and red body;
  - rust rails.
- B3: matches sibling C.
- B4: it reads as rusted steel plate, not paint.
- C3: top-down, as pick B is.
- D1: judged at 192, 64 and 32 px/cell.
- D2: 256 px per cell.
- D3: rows 20..234, the same as the picks.
- D4: no baked shadow or halo.
- E1 and E2: generated art, not donor art and not a script stand-in.
- E3: not owner-kept (new art).
- E4: the note is met. The pieces are new Scrapper art in the manner of pick B, not the old atlas.

Polish lines (no ticket, block nothing):
- The deck alpha is about 252, not 255, over the whole deck (min 146 in mid; about 99% opaque). His installed picks
  heavy_bridge_B and bridge_Scrapper_C measure the same (p50 253 and 252). It is a property of the cutting tool, not of this
  regen. It is invisible at play zoom.
- The edges of the rust blobs on the olive panels have a lacy, slightly fractal look at 192 px/cell. At play zoom it is not
  visible.
- From judge 1, still true: in N-S the chain covers most of the slim post (j2/ns_pair.png, left).

## Q1. Cables drawn over a colonist: the finding of judge 1 STILL HOLDS. Settled offline as a code fact. How bad it looks needs the game
- Code, unchanged: RM_DeckArt.cs:456-459 prints every cable run at AltitudeLayer.PawnUnused, above pawns. The comment says
  "cables over pawns (design.md §3: PawnUnused, directly above Pawn)". There is no split between the near and the far side.
  git log on the file shows no later change of the draw order.
- Seen in closeup_new_ew4_192.png:
  - The near (south) main chain crosses the colonist's chest and legs. This is ACCEPTABLE: that chain is in front of him, and
    he stays readable.
  - A far-side hanger (x~670, y~235-290) still runs down into the colonist's hair. This is NOT ACCEPTABLE: that hanger is
    behind him.
  - His installed Industrial pick B does the same, with a rope hanger into the hair at the matching place
    (j2/anchors_and_ind_pawn.png, right panel).
- In N-S runs both chains run beside the pawn, and there is no overlap (j2/ns_pair.png).
- This is a draw-order fault in the code. The pieces do not cause it, and it does not block the KEEP of the pieces.
- The fix that judge 1 proposed stands:
  - print the far-side main cable, its hangers and its backstays of an E-W run below Pawn, for example at BuildingOnTop plus a
    few AltInc;
  - keep the near side at PawnUnused.
- I did not fix it. Test 2: no access; my launcher's brief is offline, with no commits and no ledger writes. It is owed as a
  code item, and the parent must file it if judge 1's run did not.
- What needs the game: how far real pawn draw offsets and headgear raise the head into the far hangers. Show a colonist, with
  and without a helmet, mid-span on a 2-square and on a 4-square E-W Scrapper heavy bridge, at about 128 px/cell. The ruling
  does not depend on that shot.

## Q2. Posts on the old anchor frames: believable as geometry (settled offline). The material match needs the game
- Seen in j2/anchors_and_ind_pawn.png. Left two panels: the NEW left and right ends of the 4-square E-W run. Third panel: his
  pick B's left end.
  - E-W: the near (south) post's foot plate lands on the anchor slab's south edge and overhangs it by about 0.05 cell. The far
    post's foot meets the slab's north edge. The backstays land on the slab's outer corners. Pick B places its posts and
    backstays exactly the same way on its own anchor.
  - N-S (j2/ns_pair.png): the posts stand just outside the 0.86-cell-wide slab, as they do in pick B.
  - So the placement is his picked geometry and is believable: posts at the abutment's edges.
- What offline cannot settle: the composite draws the old anchor raw, as clean light-grey concrete with no stuff tint.
  - Next to the rusty deck and the rusty posts, that raw slab now reads as another look.
  - The anchor has no footing or plate under the posts.
  - Whether the posts read as bolted to it or as standing beside it depends on the in-game tint (steel or another common stuff).
- What needs the game: both ends of an E-W and of an N-S Scrapper heavy bridge built of steel, at about 128 px/cell, framed on
  the post feet and the backstay landings. If the feet float, or the grey slab clashes, the fix is a Scrapper heavy anchor with
  post footings. That is new anchor art, outside this item. It is not a change of the post geometry.

## Evidence (D:\ClaudeWork\rimmandrake\heavy_bridge_scrapper\)
- j2\pieces.png: the raw pieces; rows are NEW, pick B and Scrapper C.
- j2\row1.png, j2\row2.png, j2\row3.png: the composite rows, at 64 px/cell.
- j2\play32_x2.png: 32 px/cell at 2x, NEW / C / pick B.
- j2\ew4_joints_x2.png: the deck joints at 2x.
- j2\ns_pair.png: N-S, NEW against pick B.
- j2\anchors_and_ind_pawn.png: the post feet on the anchors, and the Q1 hanger in pick B.
- Inputs: j2in\*.png.
