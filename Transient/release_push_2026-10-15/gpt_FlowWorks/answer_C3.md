I found **12 findings**. Locations below use exact code anchors rather than guessed line numbers. The proposed checks have not been run.

1. **F1 — HIGH — Saving before the descent detector runs erases fall and spike damage**

   **Where:** `RM_SuperdeepTrap.cs`, `TryJumpInto`: `p.Position = cell;`; detector: `lastCell.TryGetValue(p, out IntVec3 prev) && prev != pos`; serialization: `Scribe_Collections.Look(ref jumpers, "jumpers", LookMode.Reference);`.

   **What happens:** Jumping teleports immediately but defers damage to the next detector pass. Only `jumpers` is saved; the previous position and pending descent are not. After loading, the detector initializes its baseline at the destination and never recognizes that fall. Ordinary forced position changes awaiting detection have the same vulnerability.

   **Repro:** Pause beside a spiked D4 pit, use “jump into pit,” save before advancing a tick, then reload. The jumper flag survives, but the pending damage does not.

   **Suggested check:** **Cheap live:** compare injuries and `DescentCount` after one tick with and without the intervening save/load.

   **Confidence:** High.

2. **F2 — MEDIUM — Removed maps retain persistent path grids indefinitely**

   **Where:** `RM_PitPathing.cs`: `private static readonly Dictionary<Map, MapGrids> grids`; `private static readonly Dictionary<Map, LadderGrids> ladderGrids`; cleanup occurs inside the respective `if (!...TryGetValue(map, ...))` branches.

   **What happens:** Both static tables strongly retain maps and persistent `NativeArray` allocations. Cleanup runs only when a qualifying request creates an entry for another map. Removing a map, returning to the menu, disabling the feature, or loading another game does not itself release these grids. Retired grids also require further qualifying requests before their disposal timer is checked.

   **Repro:** Generate grids on a temporary map, remove it, and continue on an already-cached map—or start a game whose pawns never request closed-ladder grids.

   **Suggested check:** **Cheap live:** inspect both private tables and their arrays’ `IsCreated` values immediately after map removal and after loading another game.

   **Confidence:** High.

3. **F3 — HIGH — Multi-cell covers become ground only at their anchor**

   **Where:** `RM_PocketGrid.cs`, `EffectiveDepth`: `depth[map.cellIndices.CellToIndex(c.Position)] = 0;`.

   **What happens:** The supplied cover specification supports multiple occupied cells, but this derivation clears exactly one cell per cover. The remaining covered squares retain their excavation depth in the pocket grid and full cliff-mask derivation. They can therefore partition rooms or block paths through an intact deck. Incremental masks additionally use `StepDepthAt`, creating a potential disagreement between full and incremental derivations.

   **Repro:** Place an intact multi-cell cover over a D4 area; compare its anchor and other occupied cells.

   **Suggested check:** **Cheap live:** enumerate `cover.OccupiedRect()`, comparing `EffectiveDepth[index]` with `StepDepthAt` for every cell, including after reload.

   **Confidence:** High for the multi-cell design mismatch; the cover utility implementation is outside this input.

4. **F4 — HIGH — Pawnless reachability still blocks valid large-pawn and flyer paths**

   **Where:** `RM_SuperdeepTrap.cs`, `RelativeVeto`: `int k = p == null ? RM_PocketGrid.PersonBand : RM_PocketGrid.ClimbLimitOf(p);`; the flying exemption requires `p != null`.

   **What happens:** Pawnless queries always use K2 and receive no flight exemption. As documented in the brief, vanilla 1.6 `Pawn_PathFollower.StartPath` performs a pawnless `CanReach` before walking. Consequently, it can reject a route that the actual pawn’s K3/K4 cliff mask—or flight exemption—would permit.

   **Repro:** Use a pawn whose measured climb limit is at least three. Order movement across a sheer three-level step without a ladder. Repeat with a flight-capable pawn.

   **Suggested check:** **Cheap live:** compare pawnless `CanReach`, pawn-specific `CanReach`, and the resulting `StartPath` outcome on the same endpoints.

   **Confidence:** High, using the `StartPath` behavior established in the brief.

5. **F5 — HIGH — “Too big for the pit” pawns remain physically trapped**

   **Where:** `RM_SuperdeepTrap.cs`, `RelativeStepAllowed`: `return RM_PitTrapMath.StepAllowed(fromD, toD, k, join);`; `IsHeldAtRelative` separately supplies `g.WideAt(...)` to `HeldRelative`. `RM_CliffMask.cs` selects masks only by climb band.

   **What happens:** Width can exempt a pawn from being held and grant a reachability escape, but neither the cliff masks nor the universal step floor implements that exemption. A pawn with K below the wall height and insufficient pit width can display “too big,” report untrapped, and still have every exit rejected.

   **Repro:** Force a pawn with K3 and required width two into a one-cell D4 hole without hardware.

   **Suggested check:** **Cheap live:** read `RequiredWidth`, `IsHeld`, `IsTrapped`, exit mask bits, and `RelativeStepAllowed` together. The hold/reachability and movement answers should agree.

   **Confidence:** High.

6. **F6 — HIGH — Ramp changes and settings changes do not explicitly wake cliff-mask derivation**

   **Where:** `RM_PitRamp.cs`, `SpawnSetup`/`DeSpawn`: calls to `BumpClimbGeneration()` without `Notify_CellDelta`; `RM_PocketGrid.cs`, `SettingsChanged`: increments salts and calls `RM_PitRooms.RebuildAllMaps()`.

   **What happens:** Mask keys are checked only inside connectivity computation/update callbacks. The ladder implementation explicitly documents that a generation bump alone does not schedule that update, and explicitly pushes a cell delta. Ramps omit that step; the settings invalidator also schedules no connectivity update. Existing masks can therefore retain the previous topology while the step floor reads the new state.

   **Repro:** Build/remove a ramp on otherwise unchanged terrain, or change ramp span after masks exist. Request a route before another terrain change occurs.

   **Suggested check:** **Cheap live:** compare `ProofMask` before/after the operation, then push one cell delta and compare again.

   **Confidence:** Medium. Confirm against the omitted `BumpClimbGeneration` implementation; the shown ladder code documents this exact scheduling requirement.

7. **F7 — MEDIUM — Pocket reachability and rooms lag current cliff topology by up to 60 ticks**

   **Where:** `RM_PocketGrid.cs`: `public const int RebuildMinTicks = 60;`; `if (!paused && now - g.builtTick < RebuildMinTicks) { return; }`; `SettingsChanged` rebuilds rooms before rebuilding existing pocket bands.

   **What happens:** Queries deliberately retain stale component labels after generation changes. Cliff masks can meanwhile derive from current depths. Reachability may reject an available route or approve a newly blocked one. Settings-triggered room rebuilding initially reads those stale bands too.

   **Repro:** Immediately after a pocket build, excavate or fill its only gradual exit while the game runs. Query before the 60-tick throttle expires.

   **Suggested check:** **Cheap live:** read `ProofPocket`’s `gen` and `built`, reachability, and room identity immediately after mutation and after the throttle expires.

   **Confidence:** High.

8. **F8 — HIGH — Cross-pocket reachability discards the destination’s ladder state**

   **Where:** `RM_SuperdeepTrap.cs`, `RelativeVeto`: `bool destWayIn = !startWayOut && destPocket ...`; final call: `RM_PocketGridMath.ReachVetoed(false, startPocket, startWayOut, destPocket, destWayIn)`.

   **What happens:** Once the starting pocket has an exit, `destWayIn` is always false. Consider two separate sheer pockets A and B: A has a usable ladder; B’s ladder is alternately lowered and raised. Both layouts produce identical arguments to `ReachVetoed`, although only the lowered-B layout permits A→surface→B. At least one layout must receive the wrong reachability verdict.

   **Repro:** Put a friendly pawn in laddered pocket A and request B’s floor; toggle only B’s ladder.

   **Suggested check:** **Offline SelfTest:** construct those two decision-input fixtures and require different verdicts. **Cheap live:** compare `CanReach` with actual path availability.

   **Confidence:** High for the information loss. The omitted helper determines which layout is misclassified.

9. **F9 — MEDIUM — Map-edge reachability misses pawnless queries and isolated surface islands**

   **Where:** `RM_SuperdeepTrap.cs`, map-edge postfix: `if (p == null || !p.Spawned || c != p.Position) { return; }`; its relative check uses only `g.TrappedIn(...)`. `RM_PocketGrid.cs`, `TrappedIn`: surface components immediately return false.

   **What happens:** Pawnless and hypothetical-start queries retain vanilla’s cliff-blind answer. Even a matching pawn query approves a depth-zero island surrounded by an unclimbable trench: it is a surface component rather than a pocket, so `TrappedIn` cannot reject it.

   **Repro:** Surround ordinary ground with a closed D3/D4 trench. Place a K2 pawn on the island and query map-edge reachability with and without a pawn.

   **Suggested check:** **Cheap live:** compare those answers with an actual path request to an edge cell.

   **Confidence:** High.

10. **F10 — HIGH — Relative D3 prisons lack capture-down and lip service**

    **Where:** `RM_PitRooms.cs`, `IsPitCell`: `return eng.IsDugRaw(c) && RM_PocketGrid.IsPersonPocketCell(map, c);`; capture menu rejects `!eng.IsSuperdeepExcavation(clickedPawn.Position)`; `ShouldServeFromLipFor` requires `eng.SuperdeepCellCount != 0` and a superdeep destination.

    **What happens:** Room formation recognizes a sheer D3 person-band pocket as a pit prison, but capture-down and ordinary lip-service routing still require absolute D4. Such a prison can hold an enemy and contain a prisoner bed while offering no capture-down order. Its warden interactions also miss the lip-service gate.

    **Repro:** Build a ladderless, sheer D3 prison with a prisoner bed and force a K2 humanlike enemy into it.

    **Suggested check:** **Cheap live:** compare `IsPitRoom`, `CaptureDownVerdict`, menu availability, and `ShouldServeFromLipFor` for otherwise identical D3 and D4 cells.

    **Confidence:** High.

11. **F11 — HIGH — Wet destinations bypass ladder and relative climb pricing**

    **Where:** `RM_PitStepCost.cs`: `if ((to == 0 && from == 0) || (to > 0 && eng.FillAt(c) > 0)) { return; }`.

    **What happens:** Any liquid in the destination skips `MaskedStepCost`. Ladder slowness, per-level ladder charges, and the slow-climb factor therefore disappear for that step. The reverse climb onto dry ground still receives them. Keeping wading cost does not implement the documented symmetric ladder/climb cost.

    **Repro:** Measure descent down a ladder into a dry cell, add one liquid level, and repeat. Change “Ladder slowness” between measurements.

    **Suggested check:** **Cheap live:** read `Pawn_PathFollower.CostToMoveIntoCell(Pawn, IntVec3)` for both directions and both fill states. Verify that wet movement retains both its wading charge and the applicable edge charge.

    **Confidence:** High.

12. **F12 — MEDIUM — Absolute-mode trap discovery credits exits through solid walls**

    **Where:** `RM_SuperdeepTrap.cs`, `TryGetTrapRegion`: neighbours are enqueued using only `eng.IsSuperdeepExcavation(n)` and cover checks.

    **What happens:** This BFS traverses every eight-connected D4 cell without checking buildings, doors, walkability, or diagonal obstruction. An inaccessible usable ladder—or width exemption—behind a wall makes the whole component report untrapped. Reachability then promises an escape that the actual path cannot execute.

    **Repro:** Disable relative climbing. Divide a D4 excavation completely with walls, put the only lowered ladder on one side, and force a friendly jumper into the other.

    **Suggested check:** **Cheap live:** compare `TryGetTrapRegion`/`IsTrapped` with an actual route to the ladder and surface.

    **Confidence:** High.

## Outside this slice

The following implementations are needed to finish the audit:

- `RM_MapComponent_Excavation`: owning Scribe fields, load initialization, generation writes, and tick/update scheduling.
- `RM_SuperdeepShooting.EngineFor`: the component cache used throughout this slice.
- `RM_PocketGridMath`, `RM_CliffMaskMath`, `RM_PitTrapMath`, and `RM_PitRoomMath`.
- Cover buildings, triggers, occupied-cell lookup, and cover path-cost patches.
- Settings callbacks, Harmony bootstrap/PatchApplier behavior, and the actual XML defs.
- Liquid stock, flow kernel, and `RM_LiquidFire`: this slice cannot establish liquid conservation.
- Vanilla 1.6 path-grid job caching/eviction: necessary to determine whether disposing retired customizer arrays after 2,500 ticks is safe. The shown code alone does **not** prove a use-after-free.

No inlined C# file appears truncated. `known_behaviours.md` explicitly contains truncated ledger heads.