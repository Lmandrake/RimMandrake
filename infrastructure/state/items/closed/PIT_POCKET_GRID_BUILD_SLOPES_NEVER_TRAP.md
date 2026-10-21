# PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP

Spec: `design/RimMandrake/relative_depth_climb_design_2026-10-12.md` §8.1-8.3, §8.5 steps 1, 4, 6-9, §8.6 (build item 1 of
three in §8.7). Owner rulings: §10 there, 2026-10-12. Unblocks `POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE` step 2.

## state (BENCH, 2026-10-13) — built OFFLINE, live climb proof owed

Nothing was deployed and the bridge was not touched (a live driver held the game).

**Built (FlowWorks, behind the new Mod Setting `pitRelativeClimbEnabled`, default ON; OFF = the old absolute D 4 rule,
whose code paths are kept verbatim):**
- Math, selftested (`RM_PitTrapMath`): `ClimbLimit` (band edges on body size 0.75 / 1.65 / 3.0 → K 1/2/3/4, scaled by
  `pitClimbAbilityMultiplier`, + `RM_ClimbAbility` extra levels), `StepAllowed`, `DiagonalAllowed`, `StepCost` (slow climb
  at s = K ≥ 2, ramp 0, ladder per level; NOT yet wired into `RM_Patch_PitStepCost`, that is item 2), `ArrivalDropsTooFar`,
  `FallDropScale`, `HeldRelative`.
- Pocket grid: `RM_PocketGridMath` (pure labeller, no cell cap) + `Superdeep/RM_PocketGrid.cs` (per map, bands 1..3; K ≥ 4
  needs no grid). Depth-only (walls never stale it; vanilla reachability is ANDed). Covers read as ground. Generation
  `RM_MapComponent_Excavation.ClimbGeneration` moves on Deepen, FillIn, cover spawn/despawn, load, settings; rebuilt from
  the map tick at most once per 60 ticks, never mid-query; person-band flips re-region rooms.
- One climb-depth seam: `RM_MapComponent_Excavation.ClimbDepthAt` (dug depth today). POND_BED step 2 (2026-10-14) now feeds
  the dry bed's depth through it (`HollowDepthAt`), so a drained pond is a hollow to the climb rule.
- Hold / trapped: `IsHeldAt` reads the pocket of the pawn's band (W×W over pocket cells); `IsTrapped` = no usable ladder in
  the pocket and wide enough everywhere. `TryGetTrapRegion` (BFS, 4000 cap) is now the absolute branch only.
- Step floor (§8.5 step 4): `StepAllowed`/`DiagonalAllowed` for HELD pawns only (see gaps).
- Reachability (§8.5 step 6): `RelativeVeto` = same band component, any start, pawnless at K 2; ladder or too-narrow pocket
  is a way in/out. Captured pawns and pawnless queries only (see gaps).
- Rooms (§8.5 step 7): a pit room is a person-band pocket (`RM_PitRooms.IsPitCell`).
- Falls (§8.5 step 8): detector falls on drop > K into any dug cell, damage × drop ÷ 4; flyer landings likewise.
  Jump (step 9): jumper stays captured while in any dug cell.
- Interim pathing: `RM_PitPathing`'s planner/avoid grids key on person-band pocket cells instead of open D 4 cells.
- Player text: settings tooltip prints the size table (`RM_PocketGrid.BandText`).
- Bridge read: `RM_NorthstarProofs.ProofClimb` ("x,z;K" or "pawn:<id>").

Selftests: FlowWorks 306/306 (14 new, `SelfTest/PocketGridChecks.cs`); `northstar/selftest_climb_proof.py`; toggle
registry 115.

## gaps this item leaves (by design, closed by items 2-3 of §8.7)
- No connectivity masks: vanilla A* still walks cliffs, so the step floor and the reachability veto apply only to pawns the
  hole captures (colonists the pit ignores are untouched; the capture policy is unchanged). An unheld captured pawn can
  still climb a cliff out of a non-pocket.
- A held pawn in a mixed D3/D4 pocket whose ladder sits on a D3 cell can loop re-planning (the staged planner only knows
  pocket cells as "pit"); retired by item 2.
- No ramps, no ladder span/speed change, no `RM_ClimbAbility` race patches, step cost not wired, warden lip service still
  reads D 4. Conservative reachability false negatives are not logged.

## live proof owed (§8.6) — `src/RimMandrake/FlowWorks/northstar/climb_proof.py`, never run yet
Deploy FlowWorks, then `python.exe src/RimMandrake/FlowWorks/northstar/climb_proof.py --origin X,Z` with the bridge held.
Measured rows: `CLIMB_pond_person_free`, `CLIMB_pond_person_walks_out` (D 2 ring / D 4 core), `CLIMB_D3_person_trapped`,
`CLIMB_D3_person_cannot_walk_out`, `CLIMB_D3_muffalo_free`, `CLIMB_D2_rat_trapped`, `CLIMB_ladder_prison_door`,
`CLIMB_rebuild_follows_fill`. Owed rows (UNMEASURED until ramps/masks): ramp frees and re-traps, raider vs ramped moat,
hauler from ramped floor, save/reload pockets identical.

## criteria
- O1 L0: math + pocket grid selftests pass (FlowWorks 306/306) — done
- O2 L0: every trap seam reads the relative rule behind `pitRelativeClimbEnabled`, pinned by `Pocket_wiring_pinned_at_call_sites` — done
- A1 L2: `climb_proof.py` measured rows all PASS on a live map — OWED
- A2 L2: save/reload keeps pockets identical — OWED
