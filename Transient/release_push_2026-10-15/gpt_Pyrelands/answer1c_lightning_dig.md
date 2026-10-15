1. **A second short before the grid rebuild can discharge the protected batteries**
   - **Where:** `src/RimMandrake/Pyrelands/Source/RM_LightningBreaker.cs:59–68,91–96,167–181,273–290`
   - **Mechanism:** `Trip()` immediately makes the breaker unarmed, then requests a power-grid update (65–68, 95). Until that queued update rebuilds the net, another short can still see the original `net.transmitters` and batteries. The traversal stops only at **armed** breakers (167–170), so it now crosses the tripped breaker. With no armed boundary, `Plan()` returns null (171–173), and the prefix permits vanilla’s whole-net discharge (285–287). The existing proof explicitly rebuilds the grid after its single short (388–389), hiding this window.
   - **Repro:** On a battery–conduit–breaker–conduit–battery grid, force two fault-side shorts without advancing a tick or rebuilding power nets between them.
   - **Severity:** gameplay-visible
   - **Check:** Extend `ProofTrip` to call `DoShortCircuit(culprit)` twice before line 389; record the protected battery’s charge after each call. Repeat with an intervening rebuild as the control.
   - **Confidence:** medium — depends on the power manager’s deferred-update timing.

2. **The sprayer lacks targeting permissions for open-ground firefighting**
   - **Where:** `src/RimMandrake/Pyrelands/Defs/ThingDefs_Sprayer/FirefoamSprayer.xml:125–135`
   - **Mechanism:** The weapon supplies an ordinary `Verb_Shoot` without a `targetParams` override. Ordinary shooting defaults do not enable location or fire targeting. Consequently, the foam projectile can work when fired at an accepted pawn/building target, while the player cannot directly select an otherwise empty burning cell—the tool’s central use case.
   - **Repro:** Equip and draft a colonist; ignite grass away from buildings and pawns; try to aim the sprayer at that fire and at adjacent empty ground.
   - **Severity:** gameplay-visible
   - **Check:** Read the merged verb’s `targetParams.canTargetLocations` and `canTargetFires`, then test target acceptance on a cell and a free-standing `Fire`. Check acceptance without advancing a prolonged burn.
   - **Confidence:** medium — confirm the inherited targeting values.

3. **A failed yield placement permanently consumes the sand deposit**
   - **Where:** `src/RimMandrake/Pyrelands/Source/RM_TerrainDig.cs:49–58`
   - **Mechanism:** Completion removes the designation (52) and replaces the sand with gravel (54) before attempting item placement. It ignores `TryPlaceThing`’s success result (57), then returns the unspawned item on failure (58). A crowded placement area therefore loses both the finite deposit and its yield. `ProofShovel` can conceal this: its result reports the returned item’s definition/count without requiring it to be spawned (199–204).
   - **Repro:** Surround designated sand with enough nonmergeable item stacks that nearby placement fails, then let a miner finish shovelling.
   - **Severity:** gameplay-visible
   - **Check:** Add a blocked-placement case to the shovel chain. Confirm placement failure, then read terrain, designation, and spawned glass-sand count; a non-null returned `Thing` is insufficient evidence.
   - **Confidence:** high

4. **Queued shovel orders can excavate beneath newly constructed walls**
   - **Where:** `src/RimMandrake/Pyrelands/Source/RM_TerrainDig.cs:80–87,116–121,135–154`
   - **Mechanism:** The designator requires open ground (86), but neither job eligibility nor the running driver repeats that requirement. `HasJobOnCell` checks designation, terrain extension, forbidden status, reservation and reachability only (118–121). The driver fails only when disabled or the designation disappears (137–138). A wall constructed after designation leaves the sand eligible, and `PathEndMode.Touch` allows excavation from beside it.
   - **Repro:** Designate sand while miners are unavailable, construct a wall on that cell, then enable mining. A miner can shovel the terrain underneath the completed wall.
   - **Severity:** gameplay-visible
   - **Check:** In the shovel chain, designate sand, spawn a wall over it, and query `HasJobOnCell` using a miner standing beside it. Also check interruption when the wall appears during the dig.
   - **Confidence:** high

No additional findings for hunts 1–3, 5, 7, 9 or 11 in the supplied implementation. The actual fulgurite hook, plant/fire ticks, burn-line state, ash grids/washing, scorchfruit ID tracking and mapgen code were not supplied, so those requested behaviours remain unassessed.