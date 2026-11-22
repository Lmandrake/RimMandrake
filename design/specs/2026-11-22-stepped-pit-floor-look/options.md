# A pit with steps in its floor: how to draw it so a player can read it

Item: `RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT`. Status: options for the owner to pick from. Nothing
in the mod is changed.

His words (FlowWorks walk, 2026-11-22, about 2:35 PM PST): *"Station 34 to 39 look good and indicate their depth well. There
are no "steps" in height within a single pit though. I'm inducing some now in station 39. Result is not favorable. That is
NOT clear what I'm looking at. If the more southern pits are deeper, that would show on the eastern and western walls too,
and it does not."*

## Where to look

- Comparison sheet (full size): `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT\comparison.png`
  (half size in this folder: `img/comparison.png`). A row for each style: Today, A, B, C, P, then GPT's G1, G2, G3 and
  the new pick (last row). The columns are case (a) close, case (a) at default zoom, case (b) close, case (b) at default
  zoom. The default-zoom shots are shown at 2x so that you can see them.
- Each mockup on its own: the `mockups\` folder beside the sheet, `<style>__<case>__close.png` and `__default_zoom.png`.
- The game captures: the `captures\` folder beside the sheet. This folder has `img/captures_close_six_pits.png` and
  `img/captures_default_zoom_six_pits.png`.

The cases:
- (a) his case: a 3x3 pit, 8 m deep, with an L of three 4 m squares in the north-west.
- (b) a straight step: a 4x4 pit, with the north two rows 2 m deep and the south two rows 6 m deep.
- The captures also show (c) a staircase of 1 m, 3 m and 6 m, (d) a 6 m hole in a 1 m pit, (d) a 1 m island in a 6 m pit,
  and (e) a 1 m / 3 m step under 2.5 m of water.

## What the draw does today, and why a step does not read

The code is `SectionLayer_RMExcavationWalls` and `RM_PitReliefMath`. Its offline twin is `model/pitdraw.py`.

- Each square has a floor height. The deeper square of two neighbours draws the edge between them, and the size of the
  edge comes from the drop between them:
  - When the shallower square is to the north, the deeper square draws a black rim line and a lit "north face" that hangs
    down. The face height comes from the drop: 0.12 cell at 0.5 m, then 0.23, 0.35 and 0.50 cell at 2 m. From 2.5 m it is
    always 0.62 cell.
  - When the shallower square is to the west or east, the deeper square draws a black line and a lit side strip the full
    height of the square. The strip is 0.06 cell wide at 0.5 m. From 2.5 m it is always 0.29 cell.
  - When the shallower square is to the south, the deeper square draws only a black lining, 0.045 to 0.08 cell.
- A floor gets darker with its own depth.

These are the five reasons a step does not read:

1. **The east and west walls do not change where the floor steps.** The outer side strip of a square comes from the drop
   from the ground outside to that square's floor. Every drop of 2.5 m or more draws the same 0.29 cell strip, so a 4 m
   floor and an 8 m floor have the same wall. In his case both depths are past the cap. This is exactly what he saw.
2. **An inner step looks like the pit's own north wall.** An inner step with the shallow floor to the north draws the same
   black line and lit face as the outer rim. So pit (b) looks like two pits side by side, and (c) looks like three.
3. **An inner step with the shallow floor to the south is a thin black line only.**
4. **The floor colour does not change past about 2 m [measured].** The mean floor colour (RGB) on ArchSmall was 33.1/23.7/15.4
   at 3 m, 33.4/23.9/15.9 at 4 m, 32.8/23.8/16.7 at 6 m and 33.6/24.6/17.6 at 8 m. The code promises 22 % darker for each
   doubling. His own capture agrees: his shallow squares read 24.7/18.5/13.2 and his deep squares 23.6/17.8/12.8. This is
   a defect, filed as `RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR`, with its acceptance test.
5. **A raised island reads as a hole.** The square south of the island draws a north face, and the squares beside it draw
   side strips. The result is a lit "U" around the island (capture d2).

A pit with one depth reads well today (stations 34 to 39), because there the face height and the wall agree. Every option
below keeps that look for a pit with one depth of 2.5 m or less.

## The options

Each option is shown on (a) and (b), close up and at default zoom (23 px a cell). The mockups are drawn offline by
`mock_stepped_pits.py`, with the ground, floor and face colours measured from the ArchSmall captures. The "Today" row was
checked against the real game frames before any option was judged: its shapes and tones match.

### A. The walls show the profile (mocked)

- **What it draws.** The outer walls keep growing past 2.5 m, at a rate per doubling of the depth: the north face becomes
  0.76 cell at 4 m, 0.87 at 6 m and 0.95 (the cap) at 8 m, and the side strip becomes 0.37, 0.44 and 0.48 (the cap). The
  side strip of a square is sized by that square's own floor, so where the floor steps down, the east and west walls widen.
  The black line stays only where the pit meets the undug ground. An inner step has no black line.
- **Why it reads.** It is what a camera above the pit shows: the deeper the floor, the more wall you see. This answers his
  words directly: a deeper south part shows on the east and west walls. Without the inner black lines, (b) reads as one
  pit with a ledge.
- **Cost.** Small. Two face tables, the line rule, and a re-check of everything that hangs on a face: ladders, fittings,
  the waterline cut (`RM_UnderLiquid.Waterline`) and the corner pieces. The art for each square still reads only its 3x3.
- **Where it fails.**
  - Past about 8 m the strips reach their cap, and then only the face foot and the floor tint tell depths apart.
  - A trench 1 square wide and 8 m deep has two strips of 0.48, so only 0.04 cell of floor shows.
  - At default zoom a difference of 0.1 cell is about 2 px. It reads, but only just.
  - Under liquid, the wall below the waterline is dimmed, so the step shows only above the waterline.

### B. Ledge lip and shadow (mocked)

- **What it draws.** Today's outer walls stay. Each inner step loses its black line and gets two things:
  - a pale lip along the top edge of the ledge;
  - a soft shadow on the lower floor at the foot of the step, wider for a bigger drop (0.18 cell at 1 m, at most 0.75).
- **Why it reads.** "Light edge above, dark band below" is the oldest 2D cue for height. It tells which side is lower
  from any direction, the south too, where today there is only a black line.
- **Cost.** Small. Per square, a lip quad and a gradient quad for each lower edge, from the 4 neighbours.
- **Where it fails.**
  - It does not fix the east and west walls, which was his complaint.
  - At default zoom the lip is about 1 px. The shadow carries the read there, not the lip.
  - Under water the lip is hidden. The shadow can still be drawn under the sheet.

### C. Depth colour bands (mocked)

- **What it draws.** Today's walls. Each floor gets a clear value step for each metre and a cool blue-grey shift with depth,
  like the sea bands on a map.
- **Why it reads.** The darker, colder floor is the deeper one, at any zoom and across the whole pit.
- **Cost.** The smallest of all: a floor colour table. It needs the tint defect (reason 4) fixed first.
- **Where it fails.**
  - It tells you which floor is deeper but not how much, unless you know the colour scale.
  - The cold colour looks wrong on a dirt pit.
  - Under liquid, the liquid's own colour hides it.
  - It does not fix the walls, and an inner step still looks like a pit wall.

### P. The pick: A + B, with the tint fixed (mocked)

- **What it draws.** The walls show the profile (A). Inner steps have no black line, and get a lip and a shadow (B). The
  floor tint works as the code already promises: 22 % darker for each doubling past 2 m.
- **Why.** A answers his words (the east and west walls). B makes the ledge read as a ledge from every direction. The tint
  separates the floors at default zoom, where the walls are thin.
- **Cost.** A + B + the tint fix. All of it is per square, and each square reads only its 3x3.

### G1. Drop marks (GPT's idea, mocked)

- **What it draws.** Solid pale triangles along each inner step. The base is on the step's visible foot, and the tip
  points into the deeper square. A charcoal copy sits 0.05 cell under each one. The count and the length grow with the
  drop: 1 triangle of 0.13 cell for 0.5 m, 2 of 0.18 for 1 m, 3 of 0.24 for 2 m, 4 of 0.30 for 4 m, 5 of 0.36 for 8 m.
  The base is 0.12 cell wide. Outer walls stay as today. Inner steps have no black line.
- **What the mockup shows.** Close up, each step reads as "down this way", from every direction. At default zoom the
  triangles are pale ticks: they show WHERE the steps are, but their direction is barely visible. A row of pale teeth
  can read as a spike trap, which RimWorld has. Where two inner steps meet at a corner, the marks crowd (case (a), the
  middle square). The mockup shortens a mark to the floor that is left in its cell.
- **Cost.** Up to 5 triangles on each inner edge, from the 4 neighbours.

### G2. Depth patterns (GPT's idea, mocked)

- **What it draws.** A coarse monochrome pattern on the floor, aligned to the world, with no cell borders. The pattern
  comes from the floor's absolute depth: sparse small squares at 0.5 m, larger squares at 1 m, diagonal strokes at 2 m,
  crossed strokes at 4 m, solid diamonds at 8 m. The backing is the floor's hue at 35 % value; the marks are at 15 %.
- **What the mockup shows.** It is the strongest read at default zoom of all the rows: each depth is a clearly
  different patch, in both cases, and the patch does not depend on colour. But it does not say which patch is deeper
  until the player learns the code. The floor reads as tiles or carpet, not as dug earth. The 35 % backing makes the
  floor brighter than today's floor, so a deep pit looks less deep.
- **Cost.** One more floor quad per square, from a 5-tile pattern atlas. It needs no neighbours.

### G3. GPT's own pick: G1 + G2 + value steps (mocked)

- The patterns of G2, the marks of G1, and a value step with depth on the pattern's backing (42 % value at 0.5 m to 27 %
  at 8 m). The patterns separate the floors, the value says which floor is deeper, and the marks show the step.

### The new pick: G3 + A's walls (mocked, last row)

- G3, with A's walls: the outer walls keep growing past 2.5 m, and each square's side strip comes from its own floor.
  This keeps his words (the east and west walls show the step) in the pick, which G1 to G3 alone do not.

### Ideas judged and not mocked

- **D. Depth numbers.** A toggle overlay, like the game's beauty overlay, writes the depth on each square. The mouse-over
  depth already exists (`RM_MouseoverDepth.cs`). This option is exact and cheap, but it is not a read at a glance. Keep it
  as a companion to P, not as the answer.
- **E. Inner step face in the floor's own material.** The face of an inner step is drawn darker and in the dug floor's
  material, not the bright ground face of the rim, so a ledge differs from the outer wall. Most of this gain comes free
  with B (no black line, a lip). Add it if P still reads as two pits.
- **F. A true perspective toward the pit's centre.** A vanishing point makes deeper floors smaller. It is the most real,
  but it breaks the grid: a floor no longer fills its square, and pawns, items and clicks no longer fit the cells. The
  cost is too high. Rejected.

## How each option treats liquid and covers

- **Liquid.** In A and P the wall above the waterline keeps its profile. The step under the liquid shows by the darker,
  deeper liquid (capture e). In B and P the shadow can be drawn under the sheet. In C the liquid's colour hides the bands.
- **Covers.** A concealed lid draws no pit art today, and that stays in every option. An open deck shows the pit beneath it
  with the same rules.

## Recommendation

Pick **the new pick: G3 + A's walls, with the floor tint fixed** (the last row of the sheet). It replaces P.

- The Conductor judged that A and B are too subtle at default zoom, and that only the colour option reads at a glance.
  The mockups agree. In the new rows, the depth patterns (G2) are the one cue that read at default zoom in both cases
  without colour. The value step (from C, in G3) says which floor is deeper. The drop marks (G1) say where the step is
  and, close up, which way is down. A's walls answer his words about the east and west walls.
- The one change with the most legibility for the least cost is now **the depth pattern (G2)**: one floor quad per
  square from a 5-tile atlas, with no neighbour reads.
- Risks to judge live: the patterns look like tiles, not earth; the pale teeth can read as a spike trap (a different
  mark shape or a darker mark may be needed); marks crowd at inner corners; A's 0.95 cell face leaves little floor in a
  narrow deep square.
- Not mocked: GPT's wall depth register (idea 3), its perimeter collar (idea 4) and its motion cue (idea 5). The hole
  and island cases (d1, d2), which GPT says the marks will separate, were not mocked [guess ~70% that the marks do
  separate them, from the geometry].

Make the tint fix in any case: the code already promises it, and today it does not draw. Then build the pick and judge
it live on stations 34 to 39 and on the six stepped pits of this page. Do not judge it by these mockups only.

## GPT's answer (gpt-6.1-sol, effort high, 2026-11-22, about 3:20 PM PST)

Sent with `gpt_consult.py` (Linux Codex): the prompt is `gpt_prompt_sent.md` (the saved `gpt_prompt.md` plus a section
on the four mockups), with the eight captures and `comparison.png` as it was before the G rows. The answer, word for
word:

**I would add a deliberate visual language for depth.** Your mockups show why lighting alone is struggling: at default zoom, players see dark compartments and pale dividers before they see height.

The two strongest new approaches are **directional drop marks** and **depth-patterned floors**. One explains the boundary; the other makes whole regions distinguishable.

1. **Directional drop marks: triangles that point onto the lower floor**

   Draw small, solid triangles along each internal height boundary. Their bases touch the boundary; their tips point into the deeper square. Use the same treatment on all four orientations, including the currently almost invisible north-facing step.

   For an artist’s first mockup:

   | Drop | Triangles per cell edge | Length into lower square |
   |---|---:|---:|
   | 0.5 m | 1 | 0.13 cell |
   | 1 m | 2 | 0.18 cell |
   | 2 m | 3 | 0.24 cell |
   | 4 m | 4 | 0.30 cell |
   | 8 m | 5 | 0.36 cell |

   Make each triangle’s base **0.12 cell wide**, evenly distributed along the edge. Use pale warm grey, approximately 75% value, with a charcoal copy offset about **0.05 cell** underneath. These are contrasting geometric marks, not outlined textures.

   At default zoom, their bases are roughly three pixels wide. Direction survives even when counting becomes difficult. More and longer teeth mean a greater drop; this is a compressed scale, not one tooth per metre. Add another grade around 16 m.

   Crucially, the central hole gets arrows pointing **inward**; the raised island gets arrows pointing **outward**. That breaks their current visual ambiguity.

   **Cost:** a small bounded set of triangles per unequal edge, owned by the deeper cell; immediate neighbours suffice. Shorten marks near corners to prevent overlap.

   **Failures:** conspicuously diagrammatic; numerous small steps can look busy. The scale needs learning. Colour blindness is immaterial because shape carries the information. Under opaque liquid, marks must become an explicit overlay rather than submerged decoration.

2. **Depth-patterned floors: give each depth range a recognisable surface signature**

   Keep the earth material, but superimpose a coarse, monochrome pattern. Unlike C, this remains distinguishable when colour and brightness are distorted by water, lighting, or displays.

   Use one world-aligned pattern across equal-depth cells, with **no cell borders**. For the initial mockup, use a medium-dark earth backing, around 35% value, and charcoal marks around 15%:

   | Absolute floor depth | Pattern |
   |---|---|
   | 0.5 m | Sparse squares, 0.10 cell across, spaced 1 cell apart |
   | 1 m | Squares enlarged to 0.20 cell, same spacing |
   | 2 m | Diagonal strokes, 0.10 cell thick, spaced 0.50 cell apart |
   | 4 m | The same strokes crossed in both directions |
   | 8 m | Solid diamonds, 0.32 cell across, on a 0.50-cell lattice |

   These are **absolute-depth samples, not edge-drop sizes**. Map intermediate depths into clearly defined ranges. Extend the vocabulary beyond 8 m rather than squeezing everything deeper into black.

   The L should become an unmistakable patch of one pattern beside another. The staircase becomes three bands of different surface structure. Once learned, the pattern identifies approximate depth even away from a wall.

   **Cost:** one additional floor quad using a small pattern atlas, with world-aligned coordinates; no connectivity search.

   **Failures:** the patterns are an information convention, not natural geology. Fine strokes alias, so judge them at actual 23-pixel scale. Ground clutter and pawns obscure small regions. Under clear water, reduce water-detail competition; under opaque liquids, use the pattern in a depth overlay. Colour blindness does not remove the distinction.

Your existing mockups support this direction:

- **A:** Removing interior black lines helps grouping. But wider strips are still bevels, not a convincing wall profile. The 0.48-cell side strips also consume almost half a boundary cell and can make narrow floors look obstructed.
- **B:** The lip helps locate a boundary close up. The shadow lands on an already dark floor, so it contributes little at default zoom. Neither reliably communicates magnitude.
- **C:** The strongest overview treatment. Its cue occupies the entire floor area. Preserve its value separation; the blue shift alone will compete with water and can suggest a different material.
- **P:** Better close-up construction, but the overview still depends heavily on narrow edges. It needs C’s conspicuous floor separation, or an equally strong area cue.

3. **Wall depth registers: show exposed depth without widening the wall**

   On each outer east/west wall cell, reserve a fixed strip about **0.24 cell wide**. Inside it, draw a vertical stack of alternating pale and charcoal blocks, each about **0.18 cell wide × 0.10 cell long**. Show one through five blocks for the doubling grades above.

   Register each stack to the same northward position within its cell. Where the floor deepens, the next cell’s stack visibly lengthens. A short connector at that boundary makes the change conspicuous.

   This is a **schematic depth register**, not a physical wall profile. It answers the owner’s specific expectation: the side wall visibly changes where the floor changes, without swallowing the floor.

   **Cost:** a few small quads per boundary cell; local height determines the stack.

   **Failures:** needs a learned scale, and wall-only information cannot explain an isolated interior feature. Thin stripes disappear at default zoom, so use broad blocks. Monochrome survives colour blindness; submerged registers need an overlay to remain reliable.

4. **A continuous perimeter collar: establish “one excavation”**

   Give the excavation’s outer boundary a continuous, distinctive ground-level collar: approximately **0.10–0.14 cell wide**, neutral stone, with the usual black outer outline. Keep this collar entirely absent from internal ledges.

   The collar establishes one enclosing shape. Internal divisions then sit inside that shape rather than repeating the complete visual signature of another pit.

   **Cost:** border strips and local corner joins. Distinguishing an undug neighbour from a dug neighbour requires no flood fill.

   **Failures:** this communicates grouping, not magnitude. It cannot fix the hole/island reversal alone. Decks can hide it; retain it around visible openings. It works in monochrome and is independent of deep-value saturation.

5. **A brief downhill motion cue**

   When digging changes a floor, or while the pit is selected, send a short sequence of contrasting dashes across each changed boundary **toward the lower square**, then fade them. Think of a surveying animation rather than continuously falling dirt.

   Motion supplies direction when static shading is ambiguous. It is particularly useful for the reversed central-hole/island pair and submerged steps.

   **Cost:** a narrow animated overlay strip per active unequal edge; shared animation can avoid individual particles.

   **Failures:** screenshots lose it, reduced-motion settings need a static substitute, and permanent motion becomes distracting. Speed is a poor magnitude scale. This is supplementary feedback, not the primary depth treatment.

**For the outer east/west walls**, keep the ground-level rim continuous. If retaining A, make the **inner foot boundary** jog where floor depths change, with a short transverse join. Call that a stylised stepped strip; widening alone will not produce a readable profile. I would favour fixed-width walls plus the depth registers over further expansion.

**For a south-facing internal step**, reserve the complete black-rim-and-wall treatment for the excavation perimeter. Give the ledge a modest material face, downhill marks, and a clearly different lower-floor pattern. Apply the directional marks equally to reverse-facing steps. That distinction matters more than another shadow.

**My ranking:** floor patterns plus directional marks first; C’s restrained value separation alongside them; wall registers next; perimeter collar for grouping; motion last.

**The cheapest high-impact experiment is the directional marks.** Mock them on every orientation, especially the hole and island, at actual default zoom.

For liquid and covers, visibility needs an explicit policy: show physical cues through clear water and deck openings; use an intentional depth overlay where opaque liquid or decking obscures them. Concealed lids show nothing. No physical floor treatment can remain legible through an opaque surface.

## How it was made

- Staged on ArchSmall, the quicktest tier, game paused, area cleared of everything, no pawns in it, by
  `stage_stepped_pits.py`. Each pit's depths were read back and agree with the request.
- Captured with `capture_stepped_pits.py`. Close shots were at rootSize 8, the floor of this install, about 73 px a cell.
  Default-zoom shots were at rootSize 24, about 23 px a cell.
- The mockups were drawn with `mock_stepped_pits.py tex <out>`. The G rows use GPT's own numbers, from its answer above.
- ArchBig was not touched (he was walking on it under his hold).
