# RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES

Owner, live sitting 2026-11-08 ~10:30 PST: *"Animals need some drawlayer help: big animals should has southern ones over
northern ones. Dalgo mare currently violating this. Can we somehow fix this once and for all, for ALL large pawns and
objects in the game? I have had to say this many times in the past."* Earlier, 2026-10-16
(GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT): *"The rule seems simple: if you are more south, you go in front."*

## Cause (decompiled 1.6, `D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse`)
- `Pawn_DrawTracker.cs:43` a pawn draws at `def.Altitude + FlightYOffset() + SeededYOffset`; `:60` SeededYOffset is
  `Rand.RangeSeeded(-AltInc, +AltInc, thingIDNumber)`. Which of two overlapping pawns is in front is a coin flip fixed by
  their thing ids: the Dalgo mare.
- `Printer_Plane.cs:67` printed quads tilt 0.01 toward the camera at their north edge, so two buildings of different
  heights on one layer order by size, not by position.

## Fix (built 2026-11-08, `src/RimMandrake/MandrakePatches/Source/SouthDrawsFront/`)
- Pawns: DrawPos's SeededYOffset read routed to a z-ordered offset (band -0.037..+0.26 above the Pawn layer, +0.30 more
  in full flight). Buildings (Building..BuildingOnTop): each print lifted by its footprint's south edge, flat. Plants:
  BiomesShell's RM_PlantDrawOrder moved here and made game-wide (was our biomes only). Setting "Southern things draw in
  front", default on, off = vanilla.

## Watch out (measured limits)
- A pawn still draws over every building and tree (Pawn layer is above them): a pawn north of a tree is not hidden.
- A pawn's own render stack spans layer -10..100 x 0.000366: a northern pawn's node on render layer L still draws over a
  southern pawn's body closer than about 0.31 x L cells on a 250 map (an animal overlay, L~10: 3 cells; a human head,
  L~50: 15 cells). Animal bodies (the reported case) are strict. Compressing the stack would close it; untested depth
  precision, not done.
- Realtime-drawn buildings (DrawAt, not the map mesh) are not ordered.
- Proof: `selftest_south_draws_front.py`, `selftest_south_draws_front_scenarios.py` (offline, pass);
  `prove_draw_order_live.py` written, NOT run (the owner was playing).
