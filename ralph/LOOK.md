# FlowWorks pits: what to look at (Artisan pass 3, 2026-11-07)

Shots: `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\pass3\` (pass 2's are in `shots\old\pass2\`). Ordinary quick-test
maps on game A, 11:00 daylight, at root 20 (ordinary play, ~23 px a cell) and root 11 (the closest a player can zoom).

## The depth look: a contrast sheet, one view, every hole occupied

`contrast_depth_looks_r20.png` (shown at 2x) and `contrast_depth_looks_r11.png`. Left to right: undug, then dry holes 0.5,
1, 1.5, 2, 4 and 8 m, each 2x2 with a drafted colonist on its north-west square. Top of each block: occupied; below: the same
depths empty. Three treatments, all live in the build (Mod Setting "How a pit's depth is drawn"):
- **L0 wall bevel** (the look until now): a black-outlined box, a light band on the far edge that stops growing past 1 m,
  and colonists in 4 m and 8 m holes drawn on the ground SOUTH of the hole. 2, 4 and 8 m look the same.
- **L1 oblique cut**: the far wall's face hangs as far as the occupant sinks (one scale for both), lit at the rim and
  darkening to the foot, a line every metre, soft shade inside the side walls and the near lip; the near bank hides the
  occupant's legs. No outline. Each depth its own look, 4 m vs 8 m by a taller, darker face. Occupants read waist, chest,
  shoulders, then head only.
- **L2 shadow well**: the top-down reading: a short rim band, the whole floor in view and darker with depth, occupants
  barely shift but are drawn smaller and darker the deeper they stand. 4 m and 8 m both near-black.

**My call, not his: L1 is now the default.** It is the only one where the wall visibly rises over the occupant's head and the
hole reads as a hole rather than a mat or a box. "All three wrong" is a fine answer; L0 and L2 stay one setting away.

What I'm least sure about: at 8 m in a two-row hole the face fills almost the whole opening, so the occupant is a head at
the near lip. True to the camera, but small; the 8 m hole may want more floor to show.

## Other changes he will see
- A covered pit dug in grass now carries the grass of the ground around it (sod printed from its neighbours' plants), where it
  showed a bare square. My call, not his. NOT yet seen in game.
- Changes to approved things: none. Drawbridges untouched.
- My calls from pass 2 still stand: pit spikes are never trashed by raiders; a person the hole traps can be captured from the
  lip with no bed.
