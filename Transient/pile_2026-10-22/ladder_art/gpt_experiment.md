# GPT perspective experiment — portable ladder on four pit walls
Owner (2026-10-22, by card): "Please show GPT an image of a ladder on the North wall of a 2x2 pit. Then ask it to produce images of similar ladders along the west, east, and south walls in correct perspective. See how it does. Tell it the perspective you're using for the pit art. "the camera is..." Then see if that informs you."

## The camera paragraph (given to GPT verbatim)
The camera is orthographic and looks almost straight down at the ground, tilted slightly so that it looks from the south: north is up the screen, there is no vanishing point and no foreshortening with distance (parallel edges stay parallel), and height is drawn as a shift UP the screen (toward north), so the south-facing sides of tall things are what you see (a vanilla wall shows a lit south face about 0.35 of a cell tall below its dark top). A pit is the same thing inside out. The inner face of the NORTH bank faces the camera and is drawn as a lit band hanging down from the far rim, half a cell tall for this 4 m deep pit and darkening toward its foot. The WEST and EAST banks are seen almost edge-on, as narrow strips about a quarter of a cell wide running the whole length of the pit, the west strip in shadow and the east strip lit, meeting the north face at 45-degree mitred corners. The SOUTH bank faces away from the camera and is not seen at all: only a thick black lining marks the near rim, and whatever stands deep in the pit has its lower part hidden behind that near lip. The ladder in the picture stands on the pit floor at the foot of the north face, leans back against that face, and its top pokes up past the far rim; because height runs up the screen, its rails run straight up the screen. One cell is 128 pixels; the pit is 2 x 2 cells.

Source: `src/RimMandrake/FlowWorks/Source/RM_WallFaceMath.cs` (D4 north face 0.50 cell, side strips 0.23, rim line 0.04,
south lining 0.08; vanilla wall face 0.35 MEASURED) and `Superdeep/RM_ExcavationWalls.cs` ("EAST / WEST faces: narrow
strips of the same ground, west in shadow, east lit"; south face not drawn). Pawn depth = a shift SOUTH,
`RM_PitDrawMath.cs` (0.3 cell per level, 1.2 at D4). Correction to the brief I was handed: the game DOES draw east/west
faces, as narrow strips (0.23 cell at D4), not nothing; and sprites show the SOUTH-facing sides of tall things, not north.

## Reference image
`gpt/ref_north_2x2.png` (512 px = 4 cells at 128 px/cell; 2x2 D4 pit in the owner-shot dirt, A7 north ladder at
drawSize 1.5, offset +0.25 north). `gpt/ref_empty_2x2.png` is the same pit without the ladder. Generator (provenance):
`src/RimMandrake/FlowWorks/art_source/LadderPortable/gpt_reference.py`. Overview of every result: `gpt/sheet_all.png`.

## Prompt variants and results
All are Codex $imagegen edits with the reference attached; prompts in `gpt/p*.txt`, each carrying the camera paragraph verbatim.
- v1 `gpt/v1_all_four.png` — all four walls in one image, camera paragraph only (`p1.txt`).
- v2 `gpt/v2_west.png`, `v2_east.png`, `v2_south.png` — one wall per image, plus "Think about which faces of the pit and of the ladder the camera can see from where it is before drawing" (`p2_*.txt`).
- v3 `gpt/v3_all_four_depthrule.png` — all four, plus the depth rule in numbers (floor drawn 1.2 cells further down the screen) (`p3.txt`).
- v4 `gpt/v4_all_four_thinkfaces.png` — all four, with v2's "which faces" sentence (`p4.txt`).

## What GPT did per wall
- **North**: copied ours unchanged in every variant.
- **West / East**:
  - v1 and v3: the ladder turned to lie EAST-WEST across the side strip, short (~0.6 cell), slanting downward into the pit, its outer end
    hanging over the rim onto the ground. It reads as a bracket or ramp lying flat, i.e. our A7 west problem. The numeric depth
    rule (v3) did not fix it, only steepened the slant.
  - v2 and v4: the ladder stands UPRIGHT, its rails running up the screen (north-south) along the side strip. Its top leans
    toward the wall and touches the rim line, its foot sits ~1-1.2 cells further down the screen. It is turned three-quarter:
    the rails are offset so the near rail sits lower and the rungs show as short diagonals, nearly edge-on in v2 west and
    showing more rung in v2 east. v4 draws all four consistently, the side ladders ~0.9 cell long against the north's ~1.0.
  - In every variant GPT invented no wall face on the sides: it kept our narrow strips and laid the ladder over strip and floor.
    No cast shadow beyond the ladder's own thin dark edge. No perspective taper.
- **South**: the same answer in all four variants: an upright stub with the foot hidden behind the near lip's black lining and
  ~0.5-0.8 cell showing above it, inside the pit opening. This is what the camera implies (the part above rim height is drawn
  north of the lip) and it matches RM_Ladder_south's "top pokes over the near rim".
- Collateral: v1 dropped the pit's black outline on three sides. The others kept the pit.
- **Reads as propped?** (my read, maker = judge, advisory) v4 sides: yes, mostly. They read as ladders stood against the side walls,
  clearly more than our A7 horizontal west. v2 west (edge-on) is weaker, a thin pole. v1/v3 sides: no, they look laid flat.

## What it implies for our side-wall drawing
1. Under our camera, height is "up the screen" on EVERY wall, so a west/east ladder should run north-south, upright, not lie
   east-west. Our A7 west lies east-west and so reads as fallen. GPT reached the upright answer only when told to reason about
   which faces the camera sees (v2, v4); given geometry alone (v1, v3) it repeated our mistake.
2. Recipe for our own redraw: the west sprite is the north ladder turned three-quarter, about 0.9-1.2 cells long up the screen.
   Its top touches the rim line, leaning a few degrees toward its wall. Its rails are offset (near rail lower) so it has
   thickness, and its rungs show as short diagonals. East mirrors it. No invented wall face, and no shadow baked in (D4).
   It needs rails thick enough to stay a ladder, not a pole, at 32 px/cell (v2 west's failure).
3. South: keep the current convention, the top portion above the near lip, foot hidden.
4. Prompt lesson: for a camera question, the "which faces can the camera see, think first" sentence moved GPT more than exact numbers.
5. Nothing installed. v4 is a sketch for direction, not shippable art (painted on a pit, not a cut-out sprite).
