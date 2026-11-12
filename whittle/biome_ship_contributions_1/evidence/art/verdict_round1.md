# Art judge verdicts, round 1 (naive judge, brief design/RimMandrake/art_judge_brief.md)

Inputs judged: judge1/ images listed in the brief. Not given (B3/D1): true-scale panel beside a vanilla human and
sibling keeps, so B3 and D1 are judged only from the in-game-size strips and wall sims. Alpha measured: every
building/wall PNG is RGBA with real transparency (Hide bank 34% transparent, Fossil case 20%, both atlases 28%).

## RM_FurnaceHideBank
RM_FurnaceHideBank: KEEP
- Material matches the hide reference (B4): the panel is the furnace beast's grey-brown rock plates with the same
  ember-orange seams, in bands, laced with wire to a dark bolted steel frame on two feet. Reads as cut hide, not paint.
- Painterly, no drawn keyline (B1, B1a); the dark frame is steel, not an outline.
- Play zoom (B2): at 48 px it still reads as a framed panel of warm plates; body value well apart from the ground.
- Footprint (D3): fills the 1x1 square without overflow; feet sit at the bottom edge. Real alpha, no ground shadow (D4).
- Note, not a REDO: the glow is subtle at 48 px; that suits "gives the warmth back, slowly".

## RM_FossilCase
RM_FossilCase: KEEP
- Shows what the description asks: a small curled animal skeleton, joints in place, in banded orange canyon stone,
  behind glass (diagonal glare streaks) in a bolted steel case.
- Painterly, no keyline (B1a); stone colour reads as stone, steel as steel (B4).
- Play zoom (B2): orange slab in a dark frame is a bold, distinct shape at 48 px; the skeleton becomes texture
  there, which is acceptable for a 1x1 decoration.
- Square case fills the cell, real alpha (D3, D4).
- Note, not a REDO: the skeleton is carved in relief rather than lying as bone; reads as fossil, which is the intent.

## RM_PatternHull (Atlas + MenuIcon, judged on wallsim)
RM_PatternHull: KEEP
- Linking renders right in all four layouts: the south face strip appears only where no wall is south (ring top
  middle, ring bottom, L foot, lone block, run); corners and vertical runs show top only. No sliced or misplaced cells.
- Material (B4): dark oxidised steel plate with rust bloom, bolted plate seams per cell, and faint cyan circuit-like
  lines; reads as dead smartsteel with live pattern metal in it. Blue-grey is on the dark/charcoal side but present.
- Strong value contrast against the warm ground (B2). No heavy keyline (B1a); the 1 px light bevel is a highlight.
- Menu icon matches the atlas.
- Note, not a REDO: the cyan lines are faint; if the owner wants the "live" metal to read at play zoom, brighten them.

## RM_SpunstoneHull (judged on wallsim, vs OLD style reference)
RM_SpunstoneHull: KEEP
- Fixes the defect it replaces: it is now a real linked atlas and renders correctly in ring, L, lone block and run;
  face strip only where open to the south.
- Keeps the old picture's look: pearl-white wound strands, fibrous grain, soft grey shading; reads as spun stone
  material, not paint (B4). High contrast against the ground (B2). No keyline (B1a).
- Note, not a REDO (no brief line covers it): each cell repeats the same braid and the strands stop at the cell
  join (thin dark seam every cell), so a long run reads as a row of identical woven blocks rather than continuous
  threads. Proposal below.

## RM_TelluroxHexplate
RM_TelluroxHexplate: KEEP
- Tiles seamlessly: the 2x2 shows no seam at the joins; measured left/right edge columns differ by 0.31 mean
  (adjacent columns 1.85) and top/bottom rows are identical, so the hex grid continues across tile edges.
- Shows the description: hexagonal plates edge to edge with dark grout, each banded (growth rings) and pitted,
  with scratch scars; varied light-to-dark plates break up repetition. Reads as shell/stone, not paint (B4).
- Note, not a REDO: plate bands all run the same direction and scars are light; fine for a floor.

## Proposals (not verdicts)
- Linked wall atlases whose material is a continuous fibre or grain (Spunstone) should carry the grain across
  cell joins in a straight run, or vary per cell; evidence: RM_SpunstoneHull_wallsim.png straight run, strands cut
  at every join.
