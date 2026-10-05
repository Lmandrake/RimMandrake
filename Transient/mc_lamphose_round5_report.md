# MessyConduit lamp-mast + hose round 5

## 1 Lamp mast head (station 6)
- The "frozen bright sparkle" was round 4's `RM_MapComponent_Aerial.DrawLitHead`: two additive SparkGlow quads (0.9 and 0.35
  cell, MoteGlow shader) drawn every frame at a hard-coded per-look head point while the glower glowed. Removed with its
  helpers (`AerialMaterials.LampHead`/`LampHeadFor`/`HeadGlow`) and the probe's `litHeads`.
- Now exactly the vanilla WallLamp shape (RimSage, Core WallLamp: CompPowerTrader + CompGlower, no overlay, no extra
  graphic): the look's art + `CompGlower` (radius 12, (217,217,208), colour picker, darklight, ColoredLights upgrade -- kept
  from round 4) + flick switch. The light is the glow grid's alone.
- Head art: each look's lamp mast draws its own art (ThingStyleDef per look, `AerialStyles.StyledDefs`) plus its own top
  overlay (`TopPathFor`, look dir first). Slots the art agent should write (256x512, drawSize 2x4, drawOffset z 1.5):
  - `src/RimMandrake/MessyConduit/Textures/RimMandrake/MessyConduit/Aerial/Styles/<Look>/AerialLampMast.png` (pole + head)
  - `.../Aerial/Styles/<Look>/AerialLampMastTop.png` (head part drawn above pawns, topOffsetZ 2.15)
  - Look folders: Scrapper (junker: bare bulb in crude reflector dish), Industrial (angular), Modern (streetlight),
    Futuristic (cybertek). Def-less fallback: `.../Aerial/AerialLampMast.png` / `AerialLampMastTop.png`.
  - Bulbs should be painted unlit-neutral (no baked glow halo): the head is the same drawing day and night, like WallLamp.


## 2 Hose at reel centre (station 11)
- Round 4's mouth was just above the drum's UNDERSIDE (art u 168, v 165 of 256 at drawSize 2.8 = centre +0.44, -0.41), and
  the reel-end brass coupling + wrap reached ~0.6 cell back down the hose -- out past the drum into the see-through gap
  above the base rail. That was the peeking end.
- Now `HoseReelRect.Mouth` = the drum's AXIS, read off all four looks' `Reel_Deployed.png` (axle bolt v 124, drum between
  flanges u 118-245 -> u 180): centre +0.57, +0.04 cells. The hose (Conduits altitude) runs under the opaque drum.
- On the 2x2 reel the reel-end fitting is no longer drawn (`HoseReelRect.HidesHoseEnd`; probe `reelEndsHidden`): the hose
  simply disappears under the drum. A 1x1 reel keeps its centre mouth and coupling.
- Selftests: r5 st11 (mouth at axis, inside the footprint, 0.45 cell above the drum underside; a hose laid south starts at
  the axis); round-3 "2x2 route counts from the mouth" re-based on the new mouth (8.943 = straight mouth->target).


## 3 Hose path search (station 34)
- **The search did not give up. The route really is longer than the hose.** The owner's station-34 walls, read cell for
  cell off `20261004210108_1.jpg`: (12,8) + (11,9) shut the north-east gap (a pinched diagonal), (3,2) shuts the west
  corridor's south end, column 2 z3-8 and (10,1..3) force the long way: out the chamber's west door, north, round the far
  west side, along the bottom, up and over (10,1..3), out the south-east gap. Offline, production `HoseMath`: taut
  **32.3 cells x 1.05 margin = 33.9 -> "needs about 34"**, exactly the in-game message. 30-cell hose -> "route too long".
  A 36-cell hose (Mod Settings) takes it. The length rule is unchanged.
- The old search was not the limit there either (73 cells expanded, cap 20000), but its cap was a flat expansion count
  that had no relation to the hose. Replaced by `HoseMath.RouteCells`: the same 8-way A* bounded by LENGTH --
  any node whose path + straight remainder exceeds `SearchLengthBound` = 1.5 x maxLength/1.05 + 4 (46.9 for a 30-cell
  hose; zig-zag cell paths run up to ~1.3x taut) is never opened, so every route that fits is found and the search stays
  inside a (2 x bound + 3)^2 square. Only when nothing is within reach does an unbounded search (cap 90000 = a 300x300 map)
  tell "route too long" from "no route".
- Numbers (selftest r5): boxed-in free end on a 250x250 map: bounded 1389 cells 0 ms, unbounded no-route check 62491 cells
  23 ms (only on a click / the 250-tick corridor check). Spiral mazes: 7x7 route 19.0 (hose 21), 9x9 33.0 (36), 11x11 51.0
  (55), 13x13 73.0 (78): each found by a hose just long enough, refused "route too long" by one 3 cells shorter.
- Not changed: the lay itself (`HoseMath.Lay` -> `CordPlanner.Plan`, a cord file, cap 40000) -- a route the check passed is
  laid by the same corridor; a failed lay still retracts with its reason.


## Build / selftests / commits
- MessyConduit C# selftest 572/573: every hose check passes (new r5: st11 axis x2, st34 owner maze x2, spiral, 250x250
  bound); the 1 failure is `nodal: junction art does not fit its cords`, from the cord agent's uncommitted CordBuilder work.
- run_selftests.py 172/177; failures unrelated (northstar_matrix C2 pre-existing, MandrakePatches, ledger_lint,
  StarWarsPatches semantics, UtinniPatches dump).
- winbuild: 0 errors, built from a `git archive` of the committed source (the shared tree carries the cord agent's dirty
  Core files); DLL + .srchash committed. Not deployed.
- Commits: d7fb73e3a (source, selftests, this report), 8c8c5fe76 (DLL). Both on origin/main.
- Unproven live: the lamp head with the new per-look art at night/noon, the hose vanishing under the drum on all four reel
  looks (the axis is measured off the art, not seen in game), and the in-game retract message at station 34.

