# PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS

Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.5 steps 2-3, 5 (build item 2 of three in §8.7).
Builds on `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` (ae8d38f27c) and the pond-bed hollow (acfae20df4): the masks read the
same depth as the pocket grid (`RM_PocketGrid.EffectiveDepth` = `ClimbDepthAt`, so a dry bed's 2/4 counts; covers read 0).

## state (BENCH, 2026-10-14) — built OFFLINE, live checks owed

Nothing deployed; the bridge was not touched.

**Built (FlowWorks), active when `RM_CliffMask.On` = capture on + relative rule on + "a ladder is needed to get out" on:**
- `RM_CliffMaskMath` (pure, selftested): `AllowedBits` (StepAllowed for cardinals with ramp/ladder joins, DiagonalAllowed for
  diagonals), `LadderJoins` (any SHALLOWER cardinal neighbour), `RampJoins` (1..span up), CellConnection bit order.
- `Superdeep/RM_CliffMask.cs`: one `NativeArray<CellConnection>` per band K = 1..3 per map (allocated with vanilla's
  ConnectivitySource, freed with PathFinderMapData). Derived inside GatherData only (postfixes on `ComputeAll` /
  `UpdateIncrementally`): 3×3 per vanilla cell delta, full re-derive (cells within 1 of a hole) when the climb generation,
  a climb setting or the rule's switches move. Vanilla's array is never written.
- Per-request swap: prefix on private `PathFinder.ParameterizePathJob(…, request)` notes the pawn; postfix on
  `PathFinderMapData.ParameterizePathJob` sets `job.connectivity` to its band. Flyers and K ≥ 4 keep vanilla; pawnless = K 2.
- Ladders: a LOWERED ladder is a structural edge (raise/lower bumps the climb generation); the prison-door rule is per
  pawn: `RM_PitPathing` now only hands such a pawn an offset grid closing lowered ladder cells (`PitLeg.ClosedLadders`).
- Retired under the masks: AvoidPits / StayInPit / PlanRoute legs and the entry veto `OutsiderBarredFromFloor`. They remain
  ONLY as the fallback branch when the relative rule is switched off (design §8.5 Mod Settings: "off = today's absolute D 4
  rule, kept as a fallback branch"); selftests of the fallback stay.
- Step floor (§8.5 step 4): every non-flyer is checked (not only held pawns), ramps and usable ladders join.
- Reachability: `RelativeVeto` and `CanReachMapEdge` apply to every non-flyer (physics for everyone, §8.1), not only captured.
- Pocket grid: a ladder counts as a way out only where it joins a shallower cardinal neighbour of another component, so the
  pocket and the pathfinder agree. **Behaviour change:** a ladder standing in the middle of a flat pit floor no longer frees
  anyone (it must stand at a wall). climb_proof's ladder moved to pit D's west wall cell.
- Walking speed (§8.5 step 5): `RM_Patch_PitStepCost` prices a walked step with `StepCost` for the pawn's K (pawn noted by a
  prefix on `CostToMoveIntoCell(Pawn, IntVec3)`): slow climb × "Slow climb factor" (new setting `pitSlowClimbFactor`, 1-4,
  default 2) at s = K ≥ 2, ramp 0, ladder 2 × climb cost per level (setting comes with the ramp item).
- Bridge read: `ProofClimb("mask:x,z;K")` → `CLIFF k= bits= vanilla= derived= derives=` + the pocket line.

Selftests: FlowWorks C# 315/315 (6 new, `SelfTest/CliffMaskChecks.cs`, incl. mask-flood == pocket-label on 40 random
grids × 3 bands); `northstar/selftest_climb_proof.py` (mask row verdicts); settings registry + northstar.

## risks to watch live
- Colonists are now bound by the step rule too (design §8.1): a colonist who digs the cell under itself into a pocket, or
  is inside a sheer pit without a wall ladder or ramp, cannot walk out. Haulers no longer path down into sheer pits.
- Diagonals along a pit's lip are refused where a corner is a cliff (no corner-cutting), so routes hug pits cardinally.
- A pawn the prison-door rule refuses loses the ladder's floor cell (accepted by design); a job targeting that exact cell
  from inside the pit can loop on PatherFailed.
- Masks re-derive on every climb-generation move (each dig step): watch frame time while several colonists dig.

## live checks owed (also in Transient/experiment_2026-10-14/live_worklist.md)
- `climb_proof.py` all rows incl. new `CLIMB_mask_seals_cliff_edge` (person band has no east bit on pit B's west lip,
  muffalo band has); `CLIMB_ladder_prison_door` with the wall ladder.
- Raider/colonist ordered across a sheer D 3 trench walks around it (never through); a colonist ordered into a sheer D 4 pit
  with a lowered wall ladder goes down the ladder and back up; with the ladder raised the order is refused (no path, no loop).
- No `Notify_PatherFailed` loop in Player.log during the above; no NativeArray/Harmony errors at load.

## criteria
- O1 L0: mask math + mask-equals-pocket selftests pass — done (315/315)
- O2 L0: masks swapped per request, planner retired, floor/cost/reachability for everyone, pinned — done
- A1 L2: live rows above PASS — OWED
