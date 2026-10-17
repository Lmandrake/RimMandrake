SUBJECT: FlowWorks (RimWorld 1.6 mod, C# + XML defs).

Slice: **FlowWorks_3pits**. Static review of the supplied text; locations below use method names.

1. **Saving between a forced move and detector execution erases the fall**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `RM_SuperdeepTrapState.Tick`, `ExposeData`

   ```csharp
   if (lastCell.TryGetValue(p, out IntVec3 prev) && prev != pos
   ```
   ```csharp
   Scribe_Collections.Look(ref jumpers, "jumpers", LookMode.Reference);
   ```

   Fall detection requires an old position, but that history is not serialized. After loading, the first detector pass merely establishes the pawn’s current position. `TryJumpInto` resolves its own arrival immediately; arbitrary forced movement does not receive that protection here.

   **Repro:**
   1. Let the detector observe a pawn on surface ground.
   2. Pause and use a script to change its position into an uncovered D4 cell.
   3. Save before another detector pass, then reload and advance time.
   4. Compare with an otherwise identical run that executes the detector before saving: only that run registers the fall.

   **Confidence:** high. The required history and the complete serialization method are visible. The same guard also ignores a pawn first introduced directly onto a pit floor.

2. **An enemy can collapse the deck while friendly occupants receive no fall**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Pits/Trigger/CompPitCoverTrigger.cs` — `RunScan`

   ```csharp
   && (p.Faction != parent.Faction || RimMandrakeFlowWorksSettings.superdeepCapturesOwnFaction))
   ```
   ```csharp
   Pit.Spring(onCover);
   ```

   The faction exemption filters both the triggering mass and the eventual faller list. `Spring` destroys the entire deck but processes only that filtered list. Friendly occupants remain stationary, so the position-change detector cannot subsequently supply their missing fall. This also disagrees with the explosion route, which supplies all occupants.

   **Repro:**
   1. Disable capturing the cover owner’s faction.
   2. Put a colonist and an enemy on connected covers; use an enemy heavy enough to trigger the weakest tier alone.
   3. Run the lead cover’s scan.
   4. Observe that both covers disappear but only the enemy receives the forced descent.

   **Confidence:** high. The filtered list is passed directly through to destruction and damage handling.

3. **Destroying a cover outside `Spring` removes the floor without causing a descent**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs` — `DeSpawn`; `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `RM_SuperdeepTrapState.Tick`

   ```csharp
   base.DeSpawn(mode);
   RM_SuperdeepTrap.EngineOf(map)?.BumpClimbGeneration();
   ```
   ```csharp
   if (lastCell.TryGetValue(p, out IntVec3 prev) && prev != pos
   ```

   Ordinary removal only invalidates climb geometry. It never processes occupants. The detector cannot recognize the floor disappearing beneath a stationary pawn.

   **Repro:**
   1. Disable the automatic mass trigger.
   2. Put a pawn on an intact cover and let the detector observe it.
   3. Destroy the cover directly with a dev action or script calling `Destroy`.
   4. Advance several detector passes without moving the pawn.
   5. Check for fall injuries and spike hits: neither occurs.

   **Confidence:** high. Both the removal path and the detector’s movement requirement are explicit.

4. **Absolute-mode forced movement from covered D4 to open D4 is never a fall**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `RM_SuperdeepTrapState.IsFallingArrival`

   ```csharp
   return RM_PitTrapMath.IsPitDescent(eng.ExcavatedDepthAt(prev), eng.ExcavatedDepthAt(pos));
   ```

   This branch reads raw excavation depth at the departure cell. A cover therefore contributes depth four instead of ground depth zero. The resulting `4 → 4` transition fails `IsPitDescent`.

   **Repro:**
   1. Disable relative climbing.
   2. Prepare adjacent covered and uncovered D4 cells.
   3. Let the detector observe a pawn standing on the cover.
   4. Script a forced position change onto the uncovered cell, then execute the detector.
   5. Repeat starting from ordinary surface ground: that arrival produces a fall.

   **Confidence:** high. The relative branch correctly uses `StepDepthAt`; the absolute branch visibly does not.

5. **A working ladder route off a surface island still fails map-edge reachability**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `RM_Patch_Reachability_SuperdeepMapEdge.Postfix`

   ```csharp
   if (g.TrappedIn(k, comp, p) || (!g.ComponentIsPocket(k, comp) && !g.TouchesEdge(k, comp)))
   {
       __result = false;
   ```

   Ladders deliberately do not join pocket-grid components. Consequently, a surface component without a border cell is rejected even when lowered ladders provide a complete route through the surrounding trench.

   **Repro:**
   1. With relative climbing enabled, surround a surface island with a D4 trench.
   2. Install one ladder facing the island and another facing the exterior, connected by walkable trench floor.
   3. Use a pawn permitted to climb both.
   4. Verify that ordinary movement can traverse the ladder route.
   5. Query `CanReachMapEdge` from the island: this postfix rejects its surface component.

   **Confidence:** high. The surface-island rejection has no ladder-route exception, while the grid explicitly excludes ladders.

6. **Turning relative climbing off also turns ladder orientation enforcement off**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `IsHeldAt`; `src/RimMandrake/FlowWorks/Source/RM_PitTrapMath.cs` — `PlanRoute`, `BestLip`

   ```csharp
   return RM_PitTrapMath.Held(true, true, Captures(p), p.Flying,
       RM_LadderRules.LadderLetsOut(p.Map, c, p), wide);
   ```

   The absolute branch exempts a pawn merely because its cell contains a usable ladder. Neither this predicate nor the fallback planner checks the wall it faces. `BestLip` can select any of eight neighbouring cells.

   **Repro:**
   1. Disable relative climbing.
   2. Build a ladder facing north in a D4 cell with accessible northern and southern rims.
   3. Put a captured colonist on that ladder cell.
   4. Order it onto the southern rim.
   5. It can leave over the opposite wall.

   **Confidence:** high. Directional ladder APIs exist in this slice but are bypassed throughout this branch.

7. **A ladder hanging on nothing still cancels “held” status**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `IsHeldAtRelative`, `IsTrapped`

   ```csharp
   return RM_PitTrapMath.HeldRelative(true, inPocket, Captures(p), RM_PocketGrid.CanFly(p),
       RM_LadderRules.LadderLetsOut(p.Map, c, p), g.WideAt(k, comp, c, RequiredWidth(p)));
   ```

   `LadderLetsOut` checks permission and raised state, but no exit edge. Conversely, `UsableLadderIn` requires `LadderLeadsOut`. Standing on a now-useless ladder therefore makes `IsHeld` false, and `IsTrapped` returns early without checking whether the pocket has an exit.

   **Repro:**
   1. Build a lowered ladder facing a shallower rim.
   2. Deepen that rim until the ladder faces equal-depth floor.
   3. Put a pawn allowed to use the ladder on its cell; enable own-faction capture if necessary.
   4. Compare `IsHeld`/`IsTrapped` with the ladder’s “hangs on nothing” inspection and its absence of a structural exit.

   **Confidence:** high. Permission and actual exit validation demonstrably differ.

8. **The 4,000-cell safety cap falsely declares large sealed pits escapable**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `TryGetTrapRegion`

   ```csharp
   if (e.cells.Count >= MaxRegionCells)
   {
       e.trapped = false;
   ```

   Exhausting the search budget is treated as proof of an escape. In absolute mode, this disables the reachability veto even though the hard movement floor still prevents departure. The reroute branch also interprets the pawn as untrapped.

   **Repro:**
   1. Disable relative climbing.
   2. Script a 64×64 D4 excavation without ladders or covers.
   3. Place a captured human inside.
   4. Compare `IsHeld(p)` with `IsTrapped(p)`: the former is true and the latter false.
   5. Request an outside destination and observe the disagreement between route admission and actual movement.

   **Confidence:** high. The cap explicitly changes the answer to “not trapped,” without discovering an exit.

9. **Capture Down works through blocked diagonal corners**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitRooms.cs` — `TryFindLipCell`, `JobDriver_CaptureDown.MakeNewToils`

   ```csharp
   if (kind == RM_PitRoomMath.LipKind.Interact && !SocialInteractionUtility.IsGoodPositionForInteraction(c, target, map))
   ```
   ```csharp
   hold.FailOn(() => !pawn.Position.AdjacentTo8WayOrInside(Victim.Position)
   ```

   Touch jobs receive no obstruction check. Capture then requires only coordinate adjacency and a non-superdeep worker cell.

   **Repro:**
   1. Create an eligible pit prison with the victim at `(10,10)`.
   2. Put solid walls at `(9,10)` and `(10,9)`.
   3. Put the warden at the reachable surface cell `(9,9)`.
   4. Issue Capture Down.
   5. That diagonal cell qualifies as the nearest lip, and capture completes through the closed corner.

   **Confidence:** high. Both lip selection and the capture toil omit any corner or line-of-sight validation.

10. **The jump command accepts covered destinations and rejects covered departure cells**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `TryJumpInto`, `JumpTargetFor`

   ```csharp
   if (eng == null || !eng.IsSuperdeepExcavation(cell) || eng.IsSuperdeepExcavation(p.Position)
       || !cell.Standable(p.Map) || !p.Position.AdjacentTo8WayOrInside(cell))
   ```

   Both eligibility checks use raw D4 status. They do not distinguish a concealed hole from walkable covered ground.

   **Repro:**
   1. Stand a colonist beside an intact covered D4 cell.
   2. Invoke the jump command, or call `TryJumpInto`.
   3. It teleports onto the cover, adds the jumper flag, and receives no descent because arrival resolution recognizes the cover.
   4. From that cover, try jumping into an adjacent open D4 cell: the departure-depth check refuses it.

   **Confidence:** high. The eligibility and arrival predicates visibly disagree.

11. **Queued falls can damage a pawn after another fall teleports it to safety**

   **Severity:** wrong behaviour  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs` — `RM_SuperdeepTrapState.Tick`, descent-processing loop

   ```csharp
   if (p.Spawned)
   ```
   ```csharp
   RM_SuperdeepTrap.OnForcedDescent(p, p.Position, this, drop);
   ```

   Candidates are collected before damage and `PitDescent` callbacks run. Processing subsequently checks only `Spawned`; it does not verify the original map or landing cell. A callback can move a later candidate, which then receives the queued fall at its new position using the old map’s trap state.

   **Repro:**
   1. Establish detector history for pawns A and B, then force both into holes before one detector pass.
   2. Register a `PitDescent` handler that, when A falls, despawns B and respawns it on safe ground on another map.
   3. Ensure A precedes B in the scan.
   4. Execute the detector: B still receives its queued fall, and the original state records it.

   **Confidence:** high for this scripted callback case. The event and deferred processing are both supplied code.

12. **Construction order restores quadratic cover scanning**

   **Severity:** perf  
   **Location:** `src/RimMandrake/FlowWorks/Source/Pits/Trigger/CompPitCoverTrigger.cs` — `RunScan`

   ```csharp
   if (n != null && n.thingIDNumber < self.thingIDNumber) return;
   ```
   ```csharp
   List<Building_PitCover> deck = RM_PitCoverUtility.Deck(self);
   ```

   The cheap test eliminates covers with a smaller *adjacent* ID, not every cover except the global lead. A deck can contain linearly many local ID minima. Each performs a complete flood before discovering the actual lead.

   **Repro:**
   1. Build a long covered trench by placing every other cover first.
   2. Fill the intervening gaps afterward.
   3. Run every cover’s scan with no pawns present.
   4. Profile `Deck`: approximately half the covers flood the entire connected deck per scan cycle.
   5. Double the length and compare work: the adverse construction order produces quadratic growth.

   **Confidence:** high. The full flood completes before the global ID test.

13. **Crowded pit rendering performs quadratic pawn comparisons even while paused**

   **Severity:** perf  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs` — `MapComponentUpdate`, `HitsShallowerPawn`

   ```csharp
   for (int i = 0; i < frameRects.Count; i++)
   ```
   ```csharp
   if (HitsShallowerPawn(p, d, left, right, a, b))
   ```

   Every candidate occluder piece scans every nearby pawn. With occupants at the same depth, none qualifies as shallower, so each scan runs to completion. Caching rectangles reduces repeated geometry calculation but leaves the quadratic comparison count.

   **Repro:**
   1. Enable lip occlusion.
   2. Dev-spawn a dense group along the southern rows of a visible D4 pit.
   3. Pause and profile `MapComponentUpdate`.
   4. Double the visible population while retaining the same geometry; count `CoverPieceHitsShallowerPawn` calls.

   **Confidence:** high. The nested population scans are explicit and run per rendered frame.

14. **The drawing cache retains an unloaded map**

   **Severity:** perf  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs` — `RM_Patch_PitDepthDrawOffset.ExcavationOf`

   ```csharp
   private static Map cachedMap;
   private static RM_MapComponent_Excavation cachedComp;
   ```

   These strong references have no clearing path in the supplied class. Unlike `RM_SuperdeepShooting`’s cache, this cache has no `Forget` method. It retains the previous map until another non-null map reaches `ExcavationOf`; disabling the drawing feature can prevent that replacement indefinitely.

   **Repro:**
   1. Draw a pawn with depth drawing enabled on a populated map.
   2. Keep a weak reference to that map in a test harness.
   3. Unload the game and disable depth drawing.
   4. Force collection and inspect retention: the static drawing cache still references the old map and component.

   **Confidence:** high for the retention path. It pins one cached map, rather than accumulating an unlimited number.

15. **Pawns sink through intact covers**

   **Severity:** cosmetic  
   **Location:** `src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitDepthDraw.cs` — `SinkOf`

   ```csharp
   int dFrom = ex.HollowDepthAt(from);
   ```
   ```csharp
   int dTo = to.IsValid ? ex.HollowDepthAt(to) : dFrom;
   ```

   Movement, shooting, and immersion treat intact covers as ground. Pawn depth drawing reads the excavation underneath without checking covers. Lip occlusion likewise classifies occupants using raw hollow depth.

   **Repro:**
   1. Enable depth drawing and disable automatic cover triggering.
   2. Build an intact cover over D4.
   3. Stand a non-flying pawn on it.
   4. Compare its draw position with an adjacent surface pawn: the covered pawn is visibly sunk despite standing on the deck.

   **Confidence:** high. The drawing calculation never applies the cover-as-ground rule used elsewhere.

## Outside this slice

- **Explosion ordering:** the postfix searches for the cover after `ExplosionAffectCell`. Whether the original method has already destroyed that cover requires the vanilla method body.
- **Native-array retirement:** the 2,500-tick disposal delay cannot be validated without the pathfinder’s customizer-cache and job lifetimes.
- **Settings and load orchestration:** excavation-component lifecycle code, settings handlers, and `RM_PocketGridMath`/`RM_CliffMaskMath` are absent. Their invalidation, initialization, and connectivity implementations remain unverified.
- **Removal and liquid systems:** XML defs, migration/removal handling, flow kernels, tanks, hoses, bottles, rivers, and River Colors settings migration are not supplied. The design documents do not establish their implementation safety.