**The leading explanation is vanilla’s collision recovery.** It can move a held pawn onto the bank without calling FlowWorks’ step veto. That bypass exists at `f4971d58fa` and in today’s checkout. The failing run proves the overlap and the escape, but it did not record the position writer.

[572] reads held at 67,62 at tick 844, with 2.98 m of water. [683] and [689] place Human21212 at 67,60 and 67,62 in 0.96 m. At tick 2164, [694–695] both read **Human21222**, because `ProofSwim` returns the first pawn on the square. [692] independently places **both** raiders at 67,63. [697/699] put Human21212 on dry 67,64 at tick 2224. [708] still has him there. The wardens spawn at 2584, and the cut lands at 2599. The other raiders’ movement within the ring is compatible with continued confinement. [Failing receipt](design/concepts/FlowWorks/version/in_game/visit_9/evidence/sc_moat_raid_20261123T161018.json)

### Ranked mechanisms and deciding readings

Percentages are my estimates for this incident. FlowWorks line numbers apply to both revisions unless marked otherwise.

1. **Collision recovery — 90%.** Each pawn tick, `Pawn_PathFollower.PatherTick` tests overlap before normal movement. For these same-faction pawns, both need collision-enabled jobs, nearby-hostile flags and eligible bodies. The blocker must pass the standing and ID/stance checks. Human21212’s lower ID still permits the branch if Human21222’s `FullBodyBusyRecently` property is true. `CellFinder` searches cardinal walkable cells, checks doors and occupancy, and can pick 67,64. It does not price the cliff or use the 300-versus-2 terrain costs. `PatherTick` writes `Position` directly. FlowWorks’ descent detector ignores arrivals at depth zero (`RM_SuperdeepTrap.cs:817`). [692] supplies the required overlap. The jobs, flags and chosen cell are missing, and the bait had already vanished. Vanilla refreshes the flags per pawn every 100 ticks by scanning regions. [PatherTick](/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/Verse.AI/Pawn_PathFollower.cs:217) · [Collision gates](/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/RimWorld/PawnUtility.cs:482) · [Cell selection](/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/Verse/CellFinder.cs:575)

   **One reading.** Stage two standing, gearless humanlikes on 67,63 in a 4 m cut with 0.963 m of water. Give both collision-enabled jobs, set both nearby-hostile flags, stop the blocker’s pather, and use the higher-ID pawn as mover. Leave 67,64 as the only open cardinal neighbour. Tick the mover’s pather once. **True** if the direct overlap write moves it to 67,64 while the FlowWorks step check refuses that edge. **False** if the overlap predicate is true and the write does not occur. This is the red regression case.

2. **Emergency relocation from an unoccupiable square — 5%.** `StartPath` checks occupancy before reachability. A cached path cost of at least 10,000 or a closed door the pawn cannot open invokes a radial search and direct teleport. Spawning an impassable thing over a pawn also invokes recovery. Both routes still exist. [686] shows shallow terrain at the edge and [694–695] show cost 300 there. The records leave a gap, but draining chest-deep water to shallow water supplies two passable terrains. The opened sluice was at 76,67. [Occupancy and recovery](/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/Verse.AI/Pawn_PathFollower.cs:537) · [Spawn recovery](/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/Verse/GenSpawn.cs:180)

   **One reading.** Put one gearless pawn at 67,63 with no building on it and order an in-cut `Goto` each tick across a staged 1.531→0.963 m drain. Record `TryRecoverFromUnwalkablePosition` and its destination. **True** if recovery writes 67,64. **False** if occupancy stays valid throughout publication.

3. **Ordinary path step — 3%.** `RM_PitPathing.cs:480` submits the route, but `RM_SuperdeepTrap.cs:918,997` checks the actual edge when the pawn enters it. A normal human’s climb limit is two half-metre notches. At 3.00 m the edge is two notches, at 2.98 m it is three, at 1.53 m it is five, and at 0.963 m it is eight. A committed path or a stale pocket label alone cannot authorize the exit. An actual pass requires a missing veto, a usable oriented ladder or ramp, sufficient climb ability or gear, free travel, a too-narrow pocket, titan stride, or walkable support on the source square (`RM_CliffMask.cs:428`, `RM_PocketGrid.cs:712`, `RM_TrenchStride.cs:193`). With the absolute rule, a held pawn can only step to another superdeep square. [572] weighs against persistent exemptions. None was recorded at the exit.

   **One reading.** Stage one gearless human, the same cut and bare bank, relative capture enabled, and a bank step queued at 3.00 m. Hold its execution until 2.984 m has published. Submit that same `nextCell` to the patched entry check through the remaining drain, including both sides of the 0.963 m publication. **True** if any entry is allowed. **False** if every entry is vetoed, even with the old path.

4. **Bridge placement — 1%.** `RM_SpanUtility.DeckAt` checks the exact cell and excludes raised leaves (`Building_SpanDeck.cs:27,183`). The anchor at 68,64 cannot lend height to 67,63. A fresh raise can tip a rider **on** 68,63 to a free hinge-bank square (`RM_Drawbridges.cs` old `284,431,528`, today `295,447,544`). An actual lowering formerly could treat someone beneath the leaf as a rider. Today it marks occupants beneath on lowering (`:340`). The instant raise set `holdRaised` before these raiders spawned. The bridge gate only restricts opening, and collapse only relocates protected player pawns to anchors.

5. **Other forced placement — 1% combined.** A carrier would need a downed casualty, access and a bank drop (`RM_RaiderFetchFallen.cs:329`). A jump needs usable gear or an ability and a landing (`RM_RaiderTrench.cs:325,387`). Wall climbing needs an actual wall and gear or ladder (`RM_WallClimb.cs:247,284`). River shove needs an active current lane (`RM_MapComponent_RiverCurrent.cs:522`). None has a matching trigger in the calls. Slime slip resets movement progress, and deck stumble drops riders **into** a cut (`RM_SlimeSlip.cs:100`, `RM_MapComponent_SuspensionBridges.cs` old `1412`, today `1419`). Shore rescue adds no placement route. It issues a `Goto` through the same veto, defaults to 0.70 exhaustion, and has no check between ticks 2164 and 2224 (`RM_Swim.cs:544,690`).

### Depth timing

Raw water follows the flow pulse, normally 250 ticks. Exhaustion reads raw depth for each pawn every 250 ticks. Its 60-tick pawn profile cache holds swimming traits, not depth. The separate climb cache publishes every 60 ticks at phase 11, up to 256 cells per tick, with the generation bump after the last batch. Pocket and wall reach rebuild on generation with a 60-tick throttle. The step veto reads published cell depth directly. Vanilla placement reads cached terrain walkability. Terrain writes and recosting have their own schedule. These reads can disagree, but stale 1.53 m climb depth still leaves five notches, above the human limit. The climb lift ends at **1.5 m**, and the deep-swim flag at **2 m**. [Publication and tick order](src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs:467) · [Thresholds](src/RimMandrake/FlowWorks/Source/RM_SwimMath.cs:299)

### Minimal containment for the proven bypass

In `Superdeep/RM_SuperdeepTrap.cs`, add this guard for the relative rule. The red case above should stay in the cut. This minimal version defers unstacking to vanilla’s retry if it picks an illegal cell, even when another floor square is free.

```diff
+[HarmonyPatch(typeof(CellFinder), nameof(CellFinder.TryFindBestPawnStandCell))]
+internal static class RM_Patch_PitUnstack
+{
+    [HarmonyPostfix]
+    static void Postfix(Pawn forPawn, IntVec3 cell, bool cellByCell, ref bool __result)
+    {
+        if (!__result || !cellByCell || !RM_CliffMask.On || cell == forPawn.Position
+            || !RM_SuperdeepTrap.IsHeld(forPawn))
+            return;
+
+        var eng = RM_SuperdeepTrap.EngineOf(forPawn.Map);
+        __result = forPawn.Position.AdjacentToCardinal(cell)
+            && RM_Patch_PathFollower_SuperdeepFloor.RelativeStepAllowed(forPawn, eng, cell);
+    }
+}
```

**Unread or unverified.** The failing save, full runtime logs and live Harmony patch list, and the full source of the other active mods. The receipt has no escape-tick jobs, stance flags or position writer. The proposed test and diff were neither run nor applied.