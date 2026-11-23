## spec
Child 4 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. Walk-under (R8 amended 2026-10-18: *"only for these new bridges
uniquely, NOT actual tunnels."*), sunken bridges, and the hit below on collapse. Design: `design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §1.4, §4, Q6/Q7;
`design/RimMandrake/flowworks_bridges_design_2026-10-17.md` §5.1, §5.2.
- **Floor band** under a suspension deck when the floor is **≥ 2 m** below the deck; shallower stays a wall from below.
  Keyed to the suspension deck class only (never "is the cell covered"); no roof, dug passage or other building grants it.
- Pocket grid / cliff masks (`RM_PocketGrid.cs`, `RM_CliffMask.cs`) give the decked cell two bands; a pawn's band is
  the pocket it is in.
- Drawing: deck above floor-band pawns, deck-band pawns raised over the deck (flying-pawn draw-height pattern);
  fallback if 1.6 batching refuses per-pawn altitude: deck semi-transparent over floor-band pawns.
- Nothing rests under a deck: items and corpses dropped there slide to the nearest open floor cell; no building there.
- Shots: a solid deck blocks shots between deck band and floor band; a grate does not; within a band, ignored.
- Click cycling: deck band first, second click the floor band.
- Pawns under a deck are exposed as in the open (a deck is not a roof, Q9): `RM_PitExposure` must not skip them.
- Collapse: pawns under the falling deck are hit like a roof collapse (vanilla scale); debris blocks the floor cells
  until cleared.
- **Sunken bridges** (deck height H > 0): anchors on a ledge at H; reached from a ledge, ramp or ladder (Q7); the
  pawn sink and a ledge shadow so it reads as down in the hole. Setting "Sunken bridges".
- Setting "People can walk under suspension bridges" (off: every deck a wall from below).
Dependencies: `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS`; **`PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH` (P2) must pass
before this ships** (it proves the per-request mask swap the two bands ride on); P5 `PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT`
for holes deep enough to test. Code may be written before P2 passes. Art: sunken-deck ledge shadow, debris (art item).
ESTIMATE 3 to 4.5 agent-days + 1 day live.

## verify
- L2: 4 m trench with a steel bridge over it: a colonist ordered along the trench floor walks the cells under the deck
  (path read) while another crosses on the deck at the same tick; both arrive.
- L2: 1.5 m trench: the floor path does not pass under the deck (routes around or reports no path).
- L2: an item dropped on a floor-band cell under a deck ends on an open floor cell (position read).
- L2: a solid deck: `CanHitTargetFrom` deck→floor-band pawn false; grated: true.
- L2: overload the bridge with a pawn underneath: the pawn under it takes roof-collapse damage (hediff read) and the
  floor cells hold debris until a clear job runs.
- L2: 4/7/7/4 square, sunken bridge at 4 m across the core: a pawn on the 4 m ring crosses it (path read).
- L2: raiders in a 4 m moat walk under a bridge (record with modcheck; behaviour is the ruling, not a bug).
- L4 joint look: one screenshot of a pawn passing under a deck (the picture that proves the idea).
