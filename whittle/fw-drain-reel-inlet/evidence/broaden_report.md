I reviewed the version on disk now. While I was reading, `HosePorts.cs` changed to the design you described: `RawFind` builds `rawReachable` using a clamped body cell, `Pick` takes an optional `ISet<Cell> reachableContacts`, and `HoseBodyInletChecks.cs` and `ProofBodyInlet` were added. So this is a review of that code plus the cases it doesn't cover. It is not a completion verdict.

## The design as built

It's sound, and I'd keep it. Simpler versions would be less safe:
- **The `Pick` filter is the part that does the work.** Filtering only the perimeter cells in `RawFind` would let `Pick` choose an unreachable contact on a reachable multi-cell candidate. The filter during collection is only a speed-up.
- **The clamp is correct.** Perimeter cells never include corners, so the clamped body cell always equals `contact - side`. This is the exact edge cell, not the origin or centre.
- **`HashSet<Cell>` is fine.** `Cell` is `IEquatable` with its own hash, the set is static scratch, and `Clear()` keeps its capacity, so it allocates nothing once warm. A bitmask by perimeter index would save little and is easier to get wrong.
- **What's preserved:** unfiltered `Pick` behaves as before for every other caller. `RawFindAt` (free ends) is unchanged. The pump gate now ignores lower-id reels on another band, which is the right outcome.
- **One gap in the tests:** the random oracle (`HoseTickAllocChecks` `PickByEdgeLists`) and the allocation test only run unfiltered `Pick`.

## Cases a player would try that the checks miss (by priority)

1. **Relay inlets have no band check. This is the likely real gap.** In `RM_LiquidNet.Ends`, `comp.IsFed(r)` sets `inlet = r` before `Port()` is even read. Relay intake cells (`HoseRelay.IntakeCells` / `RelayAt`) don't consult bands. A player chaining reels into a pit would end the lip reel's hose on the lip cell beside a pit-floor reel's intake. That hose never steps down, so routing allows it, and the floor reel is then fed across a sheer wall. The STATEMENT says "a reel body cannot hydraulically couple", which arguably covers this. Either filter intakes the same way (`BandAt(intake) == BandAt(intake - side)`) or record it as an explicit limit.

2. **The pump's port row can differ from `Pick`'s contact row.** The pump gate (`ReelSideOn`) uses `RM_PumpPortMath.PortCell`, which starts from `pump.Position`. `Pick` chooses the lowest-k contact. Example: a 3x2 pump on (13..15, 10..11) facing south has Position (14,11) in RimWorld, so its west port is (12,11). A 2x2 reel on (11..12, 10..11) gets the band check at (12,10)/(13,10), but the hose actually couples at (12,11)/(13,11).
   - This only matters if a reel or pump footprint can sit across two bands. I couldn't find a placement rule that answers that, so check it.
   - If it can happen, for pump candidates only add a perimeter cell to `reachable` when its body cell is that side's `PortCell`. Fallback to other candidates still works, since Machine ranks last.

3. **Water changes bands.** The real `ClimbDepthAt` counts water up to its surface, and a brim-full pit reads 0. A reel on the floor of a flooded pit, beside a pipe on the lip, couples while the pit is brim-full. Once it drains below the brim (or below the 2 m swim threshold) it uncouples and draining stops. That is the drain-a-pit job P5 exists for.
   - The same swim-threshold flicker that `FloorJoined` fixed for routing applies to endpoints.
   - My recommendation: endpoints accept "equal band OR `FloorJoined`". `FloorJoined` means "same floor", not a ramp/ladder route grant. If you don't adopt it, record it as a limit.

4. **Decks and covers.** A reel on a surface deck or cover reads band 0 and should couple to a pipe on the ground. A reel on a sunken deck reads the ledge depth and should not. A deck collapsing or a cover being removed changes the band while the reel is coupled. None of this can be represented by the doubles.

5. **Caches lag.** `Port()` is cached for 60 ticks (phased by id), and the `RM_HoseLinkCache` slot audit adds another 60. After digging, flooding or toggling the rules, the old link can last about 120 ticks.
   - `ProofBodyInlet` calls `Port(true)`. That forces a refresh (bumping `linkInputSerial`), so it both hides the lag and changes the state it's measuring.
   - It also proves geometry only. It doesn't show the net's link or any liquid moving.

6. **How it looks (GSS).** `RM_LiquidJoins.ReelCoupledTo` decides whether the pipe draws its arm or a dead-end cap, and `DropFeed` removes the reel's feed. After the coupling flips, the section mesh may not redraw.

7. **A remaining limit to record, not to fix here:** `RawFindAt`'s on-footprint shortcut (`on != null`) skips the band check entirely. P5's "same x/z cell" sentence describes exactly that case (a hose end on the pit floor under a pump standing on a deck).

## Limits of the engine doubles (`AdapterStubs.cs`)
- `StepDepthAt` and `HollowDepthAt` both just return `ClimbDepthAt`, and `IsCovered` / `DeckAt` are hard-coded to false/null. That rules out water, `FloorJoined`, covers and sunken decks.
- `Position` is set to the footprint origin, which is not RimWorld's Position for 3x2 or rotated buildings. The "proper side" pump tests therefore check the wrong port cells.
- The reel is 3x2 with no rotation or look; real reels are 2x2. That's fine for `Pick`, but not representative.
- `RM_LiquidNet.RoleOfThing`, `Ends` and `HoseRelayIndex` aren't stubbed, so nothing offline tests hydraulic coupling. Only `Find` is tested.
- `Joins` and `LadderAt` return true for every cell pair. That's fine as a witness, not as a model.
- There are no cases at the map edge (`InBounds`) and no tests of the rules toggling during play.

## Extra checks

**Offline (1–3):**
1. **Filtered random oracle plus allocation test.** Brute-force over (candidate, side, k) using a random reachable set and compare with filtered `Pick`. Also assert that 1000 filtered `Pick` calls allocate 0 bytes.
2. **Relay across bands.** Using production `HoseRelay` / `HoseRelayIndex` (stubbed as needed), put a free end on a lip intake beside a floor reel. Assert it doesn't feed, or keep a witness test that pins the documented limit.
3. **Pump with a real-style Position** (3x2 facing south, Position = (minX+1, minZ+1)), with the reel's two rows on different bands. The pump must couple only if the port row's two cells share a band, and the reported contact should be the port cell. If `StepDepthAt` can be stubbed separately, add a water case too.

**Disposable live (1–3), run without `Port(true)`:**
1. **Hydraulic, not just geometric.** Install a reel on a pit floor through normal placement, and record whether straddling was allowed. Put a filled tank on the lip beside it. Without forcing anything, wait at least 250 ticks. Then read the net link for that reel and the tank's volume change. Expect no link and no change. Repeat with a same-band neighbour on the floor or deck, and expect liquid to move. Screenshot the pipe cap and feed to show the GSS look is unchanged.
2. **Relay across the wall**, as in offline check 2: expect no feed, or record the limit.
3. **Flood and drain.** Fill the pit to the brim, then pump it down. Log coupling every 60 ticks to record exactly when it couples and uncouples (the decision in case 3).