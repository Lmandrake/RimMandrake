# A pit with steps in its floor: how to draw it so a player can read it

Item: `RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT`. Status: options for the owner to pick from. Nothing
in the mod is changed.

His words (FlowWorks walk, 2026-11-22, about 2:35 PM PST): *"Station 34 to 39 look good and indicate their depth well. There
are no "steps" in height within a single pit though. I'm inducing some now in station 39. Result is not favorable. That is
NOT clear what I'm looking at. If the more southern pits are deeper, that would show on the eastern and western walls too,
and it does not."*

## Where to look

- Comparison sheet (full size): `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT\comparison.png`
  (half size in this folder: `img/comparison.png`). A row for each style. The columns are case (a) close, case (a) at
  default zoom, case (b) close, case (b) at default zoom. The default-zoom shots are shown at 2x so that you can see them.
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

Pick **P** (A + B with the floor tint fixed). The one change with the most gain for the least cost is **A's side strip
sized by each square's own floor, with no cap at 2.5 m**: it answers his words directly. Make the tint fix in any case:
the code already promises it, and today it does not draw.

Then build the pick and judge it live on stations 34 to 39 and on the six stepped pits of this page. Do not judge it by
these mockups only.

## GPT's answer: not obtained

The brief said to ask GPT (gpt-6.1-sol, high), and that was not possible. On 2026-11-22, at about 3 PM PST, every Codex
login on Archmagi was revoked: `gpt_consult.py` exited 20 (AUTH, "refresh token was revoked") on the Linux login, on the
Windows login and on `.codex_arena_judge`. The Chrome route was also down, because Chrome was not running. That is filed as
`RIMMANDRAKE_RELOGIN_CODEX_CONSULT_EVERY_HOME_REVOKED`. The question is ready in `gpt_prompt.md`, with the eight captures.
To send it after a login:

    python3 src/RimMandrake/Utils/gpt_consult.py --prompt-file design/specs/2026-11-22-stepped-pit-floor-look/gpt_prompt.md \
      -i <each of the 8 captures named in the prompt> -m gpt-6.1-sol --effort high --out <answer.md>

This page has no GPT ideas in it. The options above are this run's own.

## How it was made

- Staged on ArchSmall, the quicktest tier, game paused, area cleared of everything, no pawns in it, by
  `stage_stepped_pits.py`. Each pit's depths were read back and agree with the request.
- Captured with `capture_stepped_pits.py`. Close shots were at rootSize 8, the floor of this install, about 73 px a cell.
  Default-zoom shots were at rootSize 24, about 23 px a cell.
- The mockups were drawn with `mock_stepped_pits.py tex <out>`.
- ArchBig was not touched (he was walking on it under his hold).
