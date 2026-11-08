# FlowWorks pits: what to look at (Artisan pass 8, 2026-11-08: offline pass, nothing new seen in game yet)

Pass 8 built the look changes below and committed the DLL; none is deployed or seen yet (the Conductor gave game A to GSS
for its landing). The next sitting shoots them in `ralph/live/GALLERY8.md`'s batches A and B.

## Pass 8 changes he will see (my calls, not his)
- **Depth drawing, one scale for pawn and wall.** A pawn sinks 0.37 / 0.67 / 0.94 / 1.20 / 1.50 cells at 0.5 / 1 / 1.5 / 2 /
  4 m (was 0.3 per 0.5 m, 2.4 at 4 m) and no lower past 4 m; the pit's far wall is drawn with the same numbers, so a pawn on
  the far side of a pit stands on the floor at the wall's foot. 8 m still draws a taller wall than 4 m (1.72 vs 1.50 in a
  3-row pit). A pawn walking down a graded trench now keeps lowering (each step's lip is the step's own drawn edge).
  Least sure: the 20 % wall-over-head assumed a colonist 1.0 cell feet to crown; vanilla's head offset suggests ~1.25. The
  sitting measures it and tries the scale at 0.3 and 0.375 (and the near-lip hold at 0 and 0.4) side by side.
- **Climbing gear on the ground:** NOT changed in game. Your kept sprite reads as a brown blob at 64 px; a candidate (E2:
  pale rope coil in a belt, two grapnels, claws, drawSize 0.9) waits for your ruling: QUESTIONS 6, contrast sheet
  `shots\climbgear_ground_contrast_pass8.png` (A = yours).
- **Ladders on rails:** two rails on every wall (north down the face, east/west beside the wall, south hooks over the lip),
  drawn raised or lowered; side-wall ladders get posts and rungs wide enough to read at 64 px. Portables lean on every wall
  (11-39 degrees) and lie flat on the floor when the wall is too tall, giving no way out.
- **Suspension bridge hung:** posts on both end squares, a main cable dipping between them, hangers to a sagging deck
  (treatment 0, default); 1 = rope walk, 2 = cable-stayed, switchable for a side-by-side sheet. The deck is drawn over a
  pawn walking on the hole floor beneath it.

## Changes to approved things
None. Drawbridges untouched (their pinned checks stay green).

## Earlier (pass 4), kept for reference

Shots: `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\pass4\` (older passes in `shots\old\`). Quick-test maps on game A,
root 20 (play zoom, ~23 px a cell) and root 11 (the closest a player can zoom).

## First look (ordinary-play frames)
- `first_look_ladders_lowered_r20.png`: a 5x5 pit 2 m deep, a wooden ladder on the middle of each wall, all lowered, a
  colonist on the floor. The north ladder hangs on the far face on its iron rails, rim to floor; east and west are thin strips
  down the side walls; the south one shows only above the near lip.
- `first_look_ladders_raised_r20.png`: the same four ladders raised: each lies out on the ground beyond its rim, pointing
  away from the hole; the rails stay bare in the hole.
- `first_look_climbing_gear_worn_r8.png`: four colonists wearing climbing gear, facing south, east, north, west, and the
  kit on the ground (your kept sprite).
- `first_look_story_raider_in_pit_r20.png`: your covered-pit story, replayed: a raider who fell through the cover, in the
  pit, in evening light, with archers just north of him.
- `sheet_ladders_r11.png`: lowered, raised, a 4 m steel pit (north and east lowered, south and west raised), and portable
  ladders in 2 m and 4 m pits.

## My calls, not his
- **Ladders: lowered = in the hole, raised = out of it.** A lowered ladder is printed down its own wall at the hole's drawn
  depth (the oblique cut's far face, so its foot is where a colonist's feet are). A raised one is drawn slid up and lying
  on the ground beyond its rim. On the north wall that is the truth of the camera (a ladder standing up out of the hole). On
  the other three walls it bends the truth: a ladder slid up a side or near wall would stand over the hole, where it reads
  as "lowered". Your bar says "a raised ladder beside the rim ... the same ladder lowered into the excavation", and this is
  that reading.
- **The near (south) wall's ladder shows only its top**, three rungs and the rail hooks over the lip, for the same reason a
  colonist's legs are hidden there. First built as a sliver nobody could find; made taller (built, not yet seen).
- **Climbing gear:** your kept ground sprite stays (pass 3 had swapped it; I put it back). The worn pack facings are new:
  a belt with the rope coil and a grapnel from the front, the coil on the back from behind and the sides.

## What I'm least sure about
- The story's opened pit read as a flat grey box in evening light (`first_look_story_raider_in_pit_r20`), where every
  daylight staged shot shows a dark hole with a lit far face. Not yet explained.
- At play zoom the side-wall ladders are dotted lines.
- The portable ladder on a north wall stands straight on the face; only side-wall portables visibly lean.

## Changes to approved things
None. Drawbridges untouched.
