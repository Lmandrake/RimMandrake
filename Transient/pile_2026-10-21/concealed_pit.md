# concealed pit (PIT_COVER_FIX_PLANKS_DRAWN_AS_DIRT + PIT_COVER_FIX_OCCUPANT_STAYS_BELOW)

- [x] claim both (BENCH leases)
- [x] part 1 XML/Python rename, published 9a82ae98f4: RM_PitCovers.xml labels+descs (3 kinds, all disguise), review_map.py, human_review.py, c12/c02 scenarios, owner_review_stage.py, both KEYSHEETs. defNames unchanged.
  - selftest_review_map FAIL pre-existing: uncovered Spikes/Drawbridge textures (not this change)
- [x] part 1 C# strings (built with part 2; was blocked (another helper's drawbridge .cs uncommitted: RM_DrawbridgeArt/Control, Building_SuspensionDeck, RM_DrawbridgeMath, SelfTest/DrawbridgeChecks)
  - Building_PitCover.cs l.184 "A pit cover was taken apart/broke under", l.238 "A pit cover gave way under", l.296 placeworker refusal
  - RimMandrakeFlowWorksMod.cs l.798/1697 "Pit covers give way under enough weight", l.1321-1322 "Blasts break pit covers", l.1553
  - RM_MachinerySettings.cs l.211-223, RM_LineCrossingMath.cs l.138/143 ("a pit cover carries no lines")
- [x] part 2 diagnosed
- [x] part 2 built: RM_PitCoverBeneath(+Math), seams in RM_SuperdeepTrap/Building_PitCover/SpanDeck, draw+label hidden, inspect 'Below, hidden:'; SelfTest 773/773 (4 new Beneath_* cases); live row X8b_cover_occupant_stays_below + ProofBeneath + mock fault cover_lifts_occupant (validation_v2 offline O-LIVE-NEG green); NOT run live, NOT deployed

## Part 2 diagnosis (read, not run)
A cover has NO "below" for anyone: every reader treats an intact cover cell as ground for whoever stands on it.
- RM_SuperdeepTrap.IsHeldAt / IsHeldAtRelative return false on a covered cell -> she is not held.
- StepDepthAt reads a covered cell as WalkingDepth 0 (pocket grid, cliff masks, step prefix) -> her cell is part of the
  SURFACE component, so reachability and A* walk her straight off onto ground.
- The floor band (RM_SuspensionUnderpass.InFloorBand) that does model "under a deck" exists only for
  Building_SuspensionDeck with FloorBandPassesUnder; R8 says no cover grants it.
- Draw: DrawDepth gives covers "their old read" (hollow depth), but the pawn draws at Pawn altitude over the
  FloorEmplacement mimic -> visible on the cover.
- Side bug same cause: SpanUtility.LoadOn counts her mass on the deck (a raider sealed under a cover would spring it at once);
  Building_PitCover.DeSpawn riders / explosion fallers would give her a second fall (OnForcedDescent) from the floor she is on.

## Fix plan (ready to build when Source is clean)
1. RM_SuperdeepTrapState: saved HashSet<Pawn> `beneath` (Scribe_Collections LookMode.Reference, prune nulls), static
   BeneathTotal early-out. IsBeneath(p) = in set && intact cover at p.Position.
2. Building_PitCover.SpawnSetup (!respawningAfterLoad): each living, non-flying pawn on a dug cell -> beneath; StopDead +
   end current job.
3. Pure math (new RM_PitCoverBeneathMath, linked into SelfTest csproj): TakesBeneath(dug,dead,flying,load);
   StepFromBeneath(toDug,toCovered,fromFloor,toFloor,k) -> Refused | StaysBeneath | Emerges; Trapped(neighbour verdicts).
4. Seams: IsHeldAt -> true when beneath at c; IsTrapped -> math.Trapped; step prefix (RM_Patch_PathFollower_SuperdeepFloor)
   -> math verdict first (Emerges clears the flag); Reachability veto + CanReachMapEdge -> own cell only when trapped.
5. Exclude beneath pawns from LoadOn, Building_PitCover.DeSpawn riders, RM_Patch_ExplosionBreaksPitCover fallers.
6. Hidden: prefix Pawn.DynamicDrawPhaseAt (1.6 Pawn.cs l.2746) and DrawGUIOverlay -> skip when beneath.
7. Inspect: Building_PitCover.GetInspectString adds "Below: <names>" across the deck.
8. Known gap: a PARTLY covered pit — A* still plans in the deck view, so a beneath pawn with an open neighbour gets
   re-plans until the step prefix stops it; full floor-view walking under covers would extend R8 (owner question).
9. Tests: SelfTest checks for the math; live row in northstar/validation_v2.py X8/X9 covers: dig 3x3 2 m, colonist in
   the middle, spawn RM_PitCover_PlankLattice over all 9, read held/beneath/position after 300 ticks, inspect line, draw
   skipped, deck not sprung. Not run live.
