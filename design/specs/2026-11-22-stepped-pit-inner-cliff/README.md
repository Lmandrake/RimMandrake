# A stepped pit: the inner cliff stops part way down the side walls

Item: `RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM`. Mod: FlowWorks (pits). Status: option B is built in the
mod behind the Mod Setting "Pit relief: shadows and depth shading" (`pitSteppedReliefEnabled`, default on; off: the earlier look).
The shadow's sun is the game's own (section Light), so "sun A or B" is no longer a choice. Seen in game on ArchSmall, 2026-11-22:
`D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM\BEFORE_AFTER_stepped_pit_in_game.png`.

His words (2026-11-22, about 6:20 PM PST, on the comparison sheet of
`RIMMANDRAKE_ASK_GPT_HOW_TO_DRAW_STEPPED_PIT_FLOOR_HE_COULD_NOT_READ_IT`): *"I see comparison.png now. Oh boy. These all
have issues I'm afraid. Today, A, B look like very thin pale walls standing on in a pit, not that either side is higher or
lower. Though some of A's work making the floor darker is helpful. I think the lips do need to have a differently colored
"edge" marked in black as today. But one thing in these pictures that's wrong is that it can't go all the way up to the
original pit outside... that's what's making it look like a standing wall. The inner "cliff" should only go part way up
the side walls. It's all about the side wall interactions. They need to extend deeper into the pit where it is deeper, and
the cliff edge within the pit needs to only come up as far as it should to make it clear what it is. Make sense? This
might work better in the game than in the mock-up. But I agree that each level needs a pretty clear differential in
coloration to help demark it. That will be tricky when we add floor terrain later, but so it goes. I'm not sure I can
make out the shadow, but yes, I think realistic shadowing is crucial here."*

## Where to look

- The pick image: `D:\ClaudeWork\rimmandrake\showings\RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM\PICK_stepped_pit.png`
  (in game today, the build before the shelf fix, the build now; his L and the 2 m / 6 m step, close; both at default zoom,
  shown 2x). The first version, with options A and B, is `PICK_stepped_pit_v1_A_B.png` beside it.
- Half size in this folder: `img/PICK_stepped_pit_half.png`.
- The sweep (12 cases, each option, close and default zoom): the `sweep\` folder beside it.

## The rule (`pitrule.py`, a pure function of a square's depth and its 8 neighbours' depths)

1. Two offset functions of depth, `H(z)` (north face) and `W(z)` (side strip), keep rising to 20 m (today they stop at
   2.5 m, which is why his 4 m and 8 m floors had the same side walls). `W` is today's table up to 2.5 m; `H` is today's
   table at 0.7 (`NORTH_SCALE`) and rises only to 0.62 at 20 m, so a one-square shelf along a north wall keeps at least
   0.4 of a square in view to 8 m (see "The narrow north shelf").
2. A wall between a shallow floor `a` and a deep floor `b` is drawn in the deeper square and shows only the part between
   them: a face `H(b) - H(a)` tall, a strip `W(b) - W(a)` wide. Down any column the faces add up to `H(deepest)`.
3. An inner riser's top edge meets each side wall at that wall's depth-`a` line (`W(a)` in from the edge), never at the
   ground rim; the upper part of the side wall runs on unbroken past the riser, and the strip widens below it.
4. Every lip keeps its black line (now only between the side walls), with a pale band on the upper floor's edge. Faces take
   the depth value of their top; every surface is darkened to `K(z)` of its terrain by its depth (about 30 % per doubling,
   at every depth), a multiplier, so it holds over any floor terrain laid later.
5. A fixed sun lights the faces by their facing and casts shadows past each face's foot, longer for a bigger drop
   (`0.12 x (b^0.7 - a^0.7)` squares: a 2 m rim 0.19, a 4 m to 8 m riser 0.20, an 8 m rim 0.51).

Promises and their test: `selftest_pitrule.py` (P1 riser stops at the side wall, P2 side wall wider when deeper, P3 faces
add up, P4 every depth apart, P5 single-depth pits to 2.5 m keep today's side strips and a 0.7 north face, P6 3x3 locality, P7 a one-square north
shelf keeps 0.4 of a square in view to 8 m). Today's draw, twinned in
the test, is red on P1 to P4.

## The narrow north shelf (his fault on the pick, 2026-11-22)

His words, on the pick image: *"YOU SOLVED IT! The new pit renderings with shadows CLEARLY indicate the height relationships
(though the lower-right northern inner shelf is incredibly narrow, that's a bit weird and incorrect)."*

- Cause: his L's 4 m north arm showed `1 - H(4)` = 0.26 of a square (the outer north face took 0.74), and the rim's cast
  shadow (0.40) covered all of it, so the arm read as a lip.
- Fix: the north face is today's table at 0.7, rising only to 0.62 at 20 m (`H(4)` 0.50, `H(8)` 0.57), and the cast shadow is
  `0.12 x` instead of `0.15 x`. Four settings were rendered (the original, two milder ones, this one); a fresh Opus judge
  picked this one: the north arm is as wide as the west arm, and no step, shadow or riser is lost.
- What changes for a plain pit: its north face is 0.7 of today's (a 2 m pit's face 0.35 of a square, not 0.50). Its side
  strips are today's.
- Test: `selftest_pitrule.py` P7 (red on the old rule: 0.38 at 2.5 m), the C# case `PitStepped_north_shelf_stays_in_view`, and the
  golden tables (`gen_golden.py`).

## Light: the sun's direction, the moon, lamps, roofs (vanilla read in the 1.6 decompile; the build seen in game 2026-11-22)

His question (2026-11-22): *"how do shadows render when a player brings a strong light in the game today? If they light a pit
with a strong lamp, do the shadows throw correctly? What about if the light is "below?" This is pretty important actually."*

What vanilla does (read in RimSage):
- Sun shadows of buildings (`SectionLayer_SunShadows`) are baked with each wall's height in the vertex alpha; the shader pushes
  them along one global vector, `_CastVect`, which `SkyManager` sets every frame (x, z the shadow's direction and length; w the
  strength, `GenCelestial.CurShadowStrength`). By day the vector swings from west (morning) to east (evening) and always
  points south; by night it is the moon's, and the strength fades to 0 around dusk and dawn.
- On a pinned-sun map (Utinni, `RM_MapComponent_PinnedSun`), a never-ending weather event overrides the vector, and a patch
  rewrites its strength. So `_CastVect` is already the one sun every shadow in the estate follows: the Direct Sun ruling's
  "fixed sun = location" on Utinni, and the clock elsewhere.
- Lamps cast no shadows in vanilla. Light is a per-cell glow grid drawn as one darkening overlay over everything
  (`SectionLayer_LightingOverlay`), so a lamp brightens cells in its radius and never moves a shadow.

What the pit draws, as built (2026-11-22, `RM_PitReliefMath.PitSun`, `Superdeep/RM_PitSunDraw.cs`):
- The cast shadow and the face light take their direction, length and strength from `_CastVect`: `RM_PitSunDraw` reads it on
  the current map every 20 frames, snaps it (compass 15 degrees, slope 0.25, strength and sky glow 0.1: `SunKey`), and re-meshes
  the walls layer (its own mesh flag `RM_PitSun`) when the snapped value moves. Noon's vector (length 1.5) is slope 1; a longer
  vector casts longer, up to slope 2 (the march then reads a 7x7 window; a depth change re-meshes the 7x7). By day the sun, by
  night the moon, nothing at dusk and dawn; on a pinned-sun map the pinned sun.
- A square's share of that light (`SkyShare`): none under a roof (Direct Sun: a roof covers at every angle); none where lamp glow
  outshines the sky (full while the lamp gives at most half the sky's glow, so a lamp by day changes nothing). The layer also
  re-meshes on `GroundGlow` and `Roofs`. So no pit shadow points toward a lamp, and a lamp on a pit floor is not left in a sun
  shadow. With no directional light every face draws as a face in shade.
- Lamps throw no shadows (vanilla's do not either). A lamp-thrown shadow is a new feature for the owner (a Divergent change).
- The fixed north-west sun (`FixedSun`, azimuth 315, elevation 55) stays only as the offline twin's sun: the golden tables and
  the pick images use it.
- Tests: `PitStepped_shadow_follows_the_games_sun`, `PitStepped_shadow_strength_follows_the_sky_and_lamps` (red on stubs that
  answered the fixed sun, green on the build), `PitStepped_long_shadow_stays_inside_its_window` (red: the IndexOutOfRange
  that blanked every pit at 17 h in game; green on the 7x7 window).
- Seen in game (ArchSmall, `northstar/stepped_pit_light_stage.py`): at 17 h the east wall, facing west, reads 70 of 255 against
  43 for the west wall; at 08 h the west wall brightens (58 against 46 at noon); at dusk and at night the two are within 2.
  Torch glow on the lit floor 0.5 against sky 0 at 23 h.

## What the sweep found

- Reads right: the 2 m / 6 m step both ways, a north-south step, three levels, a deep corner, a hole in a shallow pit,
  1-wide trenches at 3 m and 8 m, a 1-square pit.
- His L's north arm was narrow (fixed: see "The narrow north shelf").
- Odd but not wrong: a deep floor north of a shallow one ends its wider side strip in a small notch at the step; the face
  under a raised 1 m island in a 6 m pit, with its corner pieces, reads as a bowl.
- Changes he may notice: a single-depth pit loses today's cream-lit north face (the faces now take the sun), and every
  floor is darker by depth.

## The build (as built)

- `RM_PitReliefMath`: `StepH`, `StepW`, `StepK` (notches), `PlanStep` (the plan of `pitrule.plan_cell`, with liquid), `PointTop`
  and `Lit` (the cast shadow at a point, a march over a window of depths, 5x5 in the twin `pitrule.lit_at` and 7x7 in the layer), `FaceLight`, `ShadowDark`,
  `StepFloorShade` (StepK anchored so the 2 m floor keeps its look), `StepLipAlpha`.
- `RM_UnderLiquid.NorthFaceAt` / `SideFaceAt(d, n, lv)`: H(d - lv) - H(n) under the rule (`Relief`, pushed from the setting), today's
  face by the drop when off. The water layers, `RM_LiquidSurface`, the ladder waterline proof read, the stakes' floor
  (`RM_SpikeDrawMath`) and `CornerPiece` read these, so every layer agrees on the face sizes.
- `SectionLayer_RMExcavationWalls`: the dry relief path (`ReliefCell`): faces as polygons of the plan, toned by StepK of
  their top x their light, lines by the plan, lip bands, the floor shade, the cast-shadow grid (8 a cell). `RedrawStep` dirties
  the 7x7 (a low sun reaches 2 squares).
- Test: `SelfTest/PitSteppedReliefChecks.cs`, golden tables written by `gen_golden.py --write` from `pitrule.py` (plain
  `gen_golden.py` fails when they drift). Red on the parent (the rule's functions absent), green on the build.
- Live stage: `FlowWorks/northstar/stepped_pit_stage.py` digs the 12 cases (`--set water`: 4 wet cases with ladders),
  captures each, saves the map (`RM_STEPPED_PIT_12_CASES`). `stepped_pit_light_stage.py` captures six lights and, with
  `--compare`, the relief switch off and on beside a colonist (`ProofPitRelief on|off`).
- Seen in game (2026-11-22): all 12 dry cases read as steps; side walls in water show down to the waterline; a ladder on a
  part-wet inner cliff hangs from the cliff's lip into the water. A ladder on a fully drowned cliff draws as a faint short
  stub about 0.3 of a square south of the drowned edge (on the polish list).

## The build plan (as planned before the build)

The walls layer is `Source/Superdeep/RM_ExcavationWalls.cs` (`SectionLayer_RMExcavationWalls`); its pure decisions are in
`Source/RM_PitReliefMath.cs` and the face tables in `Source/RM_WallFaceMath.cs`; the offline twin is `model/pitdraw.py`.

1. `RM_PitReliefMath`: `H(notches)`, `W(notches)`, `K(notches)` and the plan of `pitrule.plan_cell` (t, l, r, lt, rt, hv_l,
   hv_r, corner pieces, lip spans, lip bands), Verse-free; `pitrule.py` becomes the twin and writes the golden table
   (`SelfTest/PitReliefParityChecks.cs`). `selftest_pitrule.py` moves beside it as the offline promise test.
2. `NorthFace`, `SideFace`, `CornerFace`: the polygons of the plan (the face's west end is the polyline (lt, top) ->
   (lt, top - hv) -> (l, top - t)); the white "wall light" blend is replaced by a black tint of 1 - K(top) x light.
3. `Outline`: the north lip line spans [lt, 1 - rt]; a side lip line starts at hv. A pale lip band on a dug floor whose
   4-neighbour is deeper.
4. `FloorShade`: K(d) as the multiplier (it fixes `RIMMANDRAKE_FIX_PIT_FLOOR_TINT_PAST_TWO_M_DRAWS_ONE_COLOUR` on the way).
5. Cast shadow: a vertex-coloured grid over each dry floor (the layer's `Grid` helper), each vertex's alpha from the ray
   march of `render.cast_shadow` over the plan's heights; the sun is one constant (A: azimuth 0, B: 315). The march reads up
   to 2 squares away, so `RedrawStep` dirties the 5x5, not the 3x3 (P6 then reads "5x5").
6. Water and fittings: `RM_UnderLiquid.NorthFace/SideFace` (read by `RM_LiquidSurface` and `RM_SubmergeDraw`) take the
   same rule, the visible face from the neighbour's floor to the waterline: H(d - level) - H(n).
7. A Mod Setting, on by default: "Pit relief: shadows and depth shading" (off: today's look).
8. Test first: the promise test and a C# parity case, red on today's code; then the in-game stage: a savegame on ArchSmall
   with the sweep's 12 cases in a labelled grid.

## Not done

- Water: wet pits are not drawn by these mockups. The water layers (`SeeThrough`, `WetEdges`, `SideUnder`,
  `RM_LiquidSurface`) and the pit fittings (`RM_SubmergeDraw`) read the same face sizes and must change with them.
