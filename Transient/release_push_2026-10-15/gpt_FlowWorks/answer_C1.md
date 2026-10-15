I found 16 issues worth checking before release. This is a source-only review; the suggested checks have **not** been run. Paths below are relative to `src/RimMandrake/FlowWorks/Source/`. Locations use exact code quotes instead of guessed line numbers.

**F1 — HIGH — Pending products and adapter escrow have no destruction settlement**

- **Where:** `Machinery/CompLiquidConverter.cs`, fields `public int pendingCount;` and `public ThingDef pendingThing;`; `Machinery/CompLiquidPipeAdapter.cs`, `public float carry;`.
- **What happens:** These balances survive saves, but neither shown comp handles parent destruction. Destroying/deconstructing a converter with blocked item output discards its pending products. Destroying an adapter with positive carry discards resource already withdrawn from the foreign store; negative carry also loses its outstanding debt.
- **Repro:** Block a converter’s output placement until its pending count rises, then deconstruct it. Separately, obtain a fractional adapter carry through a short foreign-store transfer and destroy the adapter.
- **Suggested check — cheap live:** Record pending products, carry, tank stock and foreign resource stock immediately before and after destruction. Check for an equivalent recovered item/resource balance.
- **Confidence:** **Medium** — no settlement exists in the shown comps; an omitted external destruction patch could change this conclusion.

**F2 — MEDIUM — Static dictionaries retain removed maps until a different map is first queried**

- **Where:** `Machinery/RM_LiquidNet.cs`, `StateOf`, `Rotation`, and `RM_HoseLinks.For`:
  `if (!states.TryGetValue(map, out NetState s))`
  and equivalent guards around cleanup of `rotations` and `byMap`.
- **What happens:** Removed-map cleanup runs only on a dictionary miss. Continuing on an already cached home map never cleans a removed quest map. These static dictionaries retain its Map, topology, graph and referenced things, including after returning to the menu.
- **Repro:** Use machinery on home and quest maps. Remove the quest map, then keep querying machinery on the existing home map.
- **Suggested check — cheap live:** Inspect the three dictionary key sets after map removal and after several home-map queries. Assert every retained key belongs to `Find.Maps`.
- **Confidence:** **High**.

**F3 — MEDIUM — A topology bump cannot refresh hose ports within the same tick**

- **Where:** `Machinery/RM_LiquidNet.cs`, `RM_HoseLinks.Refresh`:
  `if (built && checkedTick == now)`
  followed by `return;`. `RM_LiquidNet.Bump` only increments `revision`.
- **What happens:** After the link index has been queried, changing an end’s role or coupling during that tick leaves its old link and `RM_NetPort` available. Rebuilding components after a bump still reads that stale index. `Live` checks eligibility and spawned endpoints, but does not compare the current role, position or coupling against the cached link.
- **Repro:** While paused, warm an Outflow network query, cap that end, then query ports again without advancing a tick. A transfer occurring at that tick can still see Outflow.
- **Suggested check — cheap live:** Read `PortsOf` before and after the gizmo change at the same tick, then after advancing one tick. Repeat for moving/coupling the end.
- **Confidence:** **High**.

**F4 — HIGH — An undersupplied machine can indefinitely stall a disconnected network**

- **Where:** `Machinery/RM_LiquidNet.cs`:
  `r = rotations[map] = new RM_ConsumerRotation();`.
  `Machinery/RM_LiquidNetKernel.cs`, `MayDraw`:
  `if (kv.Key != machine && kv.Value >= s.Value && now - kv.Value <= Window) return false;`.
- **What happens:** Consumer rotation is shared by every machine using a LiquidDef on the map, regardless of network. Machine B can repeatedly mark itself starved while its isolated tank contains less than one recipe batch. If A was last served, B’s continuing starvation makes A yield forever, despite A having ample independent supply.
- **Repro:** Give converter A abundant water. On a disconnected network, give B one water unit for a two-unit recipe. Let A run once, then let B request work continuously.
- **Suggested check — offline SelfTest:** Use the production rotation with one served machine and another repeatedly starved machine representing a separate component. Assert the latter cannot veto the former.
- **Confidence:** **High**.

**F5 — HIGH — Shared tanks defeat settle budgets and the start-of-cycle stock rule**

- **Where:** `Machinery/RM_LiquidNet.cs`, `SettleTick`:
  `var view = tanks.Select(t => new RM_SettleTank(t.thingIDNumber, t.storedUnits, t.Capacity, t.storedLiquid, t.EffectiveMode)).ToList();`.
- **What happens:** Each component snapshots current stock immediately before its own settle. A tank attached to two separate components therefore receives two independent budgets. Liquid received through the first component can be forwarded through the second during the same settle call, contrary to the design’s epoch-stock guarantee.
- **Repro:** Connect Empty tank E to Store tank S on one run, and S to Fill tank F on another. Arrange E’s component to settle first. Water can travel E → S → F in one cycle. A shared Fill tank can likewise receive more than `tankUnitsPerCycle`.
- **Suggested check — offline SelfTest:** Compose two production `SettlePlan` calls over shared mutable tank stock. Assert map-wide per-tank budgets and that initially empty S sends nothing that cycle.
- **Confidence:** **High**.

**F6 — MEDIUM — Quiet topology still requires a map-wide hose scan on every queried tick**

- **Where:** `Machinery/RM_LiquidNet.cs`, `RM_HoseLinks.Refresh`:
  `new List<CompHoseReel>(comp.OrderedReels())`;
  `Ends` also constructs `new RM_NetPort { Reel = r, Cell = r.far, Role = role }`.
- **What happens:** The signature backstop copies and scans every reel once per queried tick, allocating replacement port objects even when topology is unchanged. The bath job’s fail callback repeatedly calls `PayNow`, which reaches network queries through `Available`; those calls also allocate tank/view lists. An active bath can therefore expose a map-wide hot path unrelated to its own network size.
- **Repro:** Keep a bath bill working on a map containing many unrelated laid hoses.
- **Suggested check — offline performance fixture:** Count signature visits and allocations for repeated unchanged-topology queries across successive ticks, including the bath payment path. Measure the complete adapter path, rather than only the pure kernel.
- **Confidence:** **High**.

**F7 — HIGH — Adapter failure rollback can duplicate or erase foreign resources**

- **Where:** `Machinery/CompLiquidPipeAdapter.cs`:
  `catch (Exception) { broken = true; return 0; }`
  and `return Mathf.Max(0, u);` after `SettleSend`/`SettleTake`.
- **What happens:** A foreign operation can mutate storage and then throw, or succeed before its read-back becomes non-finite. The adapter reports zero, so `Move` reverses the tank leg while leaving the foreign mutation intact. Sending duplicates resource; taking loses resource. Shutting the adapter afterward does not repair that transaction.
- **Repro:** Encounter a compatibility failure where `AddResource`/`DrawResource` changes stock before throwing, or where the subsequent `AmountStored` getter fails.
- **Suggested check — offline SelfTest:** Inject foreign stores that mutate then throw, and stores whose post-operation getter returns NaN. Assert conservation across tank stock, foreign stock and carry.
- **Confidence:** **High**.

**F8 — HIGH — Repeated short sends export resources without debiting tank stock**

- **Where:** `Machinery/RM_LiquidTransfer.cs`, `SettleSend`:
  `carry -= delta - u * perUnit;`.
  `Machinery/CompLiquidPipeAdapter.cs`, Send mode:
  `addResource.Invoke(storage, new object[] { k * per });`.
- **What happens:** Fractional acceptance becomes negative carry, but Send mode never uses that debt to charge later transfers. With `per = 1`, offering one unit and accepting 0.5 returns zero whole units: the tank is restored, foreign storage gains 0.5, and carry becomes −0.5. Repetition exports arbitrary usable resource while the tank remains unchanged.
- **Repro:** Use an adapter against a foreign store that repeatedly accepts fractional amounts.
- **Suggested check — offline SelfTest:** Perform twenty one-unit sends with acceptance fixed at 0.5. The current path leaves the source unchanged while exporting ten resources. Require eventual whole-unit debit or retained positive escrow backed by actual withdrawn stock.
- **Confidence:** **High**.

**F9 — HIGH — Taking a charged hose off-map explicitly deletes its liquid**

- **Where:** `Machinery/RM_LiquidSpill.cs`, `DrainHeld`:
  `RM_HoseHold.Drain(ref hl0, ref r.heldUnits, null);`.
- **What happens:** When no map or valid drain cell is available, the code clears the held ledger with no destination. The warning says the liquid “went with it,” but the reel retains zero units.
- **Repro:** Remove a charged reel from its map through a lifecycle path that invokes `DrainHeld` after its map/drain location becomes unavailable.
- **Suggested check — offline SelfTest or cheap live:** Charge a reel, call `DrainHeld` with a null map, and compare held units plus placed output. Also exercise the actual caravan/map-transfer removal path.
- **Confidence:** **High** for the deletion; the ordinary gameplay path into this branch needs the omitted reel lifecycle.

**F10 — HIGH — Stopped hoses cannot return held liquid to natural ponds**

- **Where:** `Machinery/RM_LiquidSpill.cs`, `PlaceHeld`:
  `Outlet(map, ex, cell, liquid, liquid?.canalFluid, out IntVec3 c) == RM_OutletKind.Channel`.
- **What happens:** `Outlet` supports the new `Body` destination, but `PlaceHeld` accepts only `Channel`. A hose draining over a compatible pond or dry lakebed converts all its held liquid to filth instead of crediting the pond, even when whole levels fit. This bypasses the pond-return fix.
- **Repro:** Charge a hose with at least five units, place its drain end over a compatible depleted pond bed with no nearby dug channel, then stop its flow.
- **Suggested check — cheap live:** Record pond stock, hose stock and spill counters before and after draining. Expect one returned level per five units, with only the remainder spilled.
- **Confidence:** **High**.

**F11 — HIGH — Failed spill placement still commits the entire debit**

- **Where:** `Machinery/RM_LiquidSpill.cs`, `OutletLeg`:
  `return RM_TransferLeg.Sink(k => Spill(map, cell, liquid, k));`.
  `Spill` warns and executes `break;` when both filth attempts fail.
- **What happens:** `Sink` reports complete acceptance regardless of placement success. If the liquid’s filth and generic filth both fail, all unrepresented units have already left their source. Logging a warning does not make this the sanctioned fill-in overflow, and no stock or pending spill remains.
- **Repro:** Drain a tank or hose where surrounding cells reject both spill filth types.
- **Suggested check — offline SelfTest:** Inject a filth placer returning false, including failure after some successful patches. Assert refused volume remains in its source or a saved pending ledger.
- **Confidence:** **High**.

**F12 — HIGH — A wall at an Outflow end is checked after adjacent destinations**

- **Where:** `Machinery/RM_LiquidSpill.cs`, `Outlet`: the adjacent-channel/body searches precede
  `if ((ex != null && ex.IsExcavated(end)) || !end.Standable(map) || end.GetTerrain(map).IsWater)`.
- **What happens:** An adjacent channel or pond can be selected before the code discovers that the nozzle cell itself is blocked by a wall. Thus a nominally blocked end can discharge into neighbouring liquid cells, contrary to the specified wall-blocked behavior.
- **Repro:** Put an Outflow end beside a receptive channel, then build a wall over the end while leaving the neighbouring channel receptive.
- **Suggested check — cheap live:** Query `Outlet` for that end and inspect the resulting port binding. Assert a wall-blocked end returns `Blocked` before selecting neighbouring destinations.
- **Confidence:** **High** for the helper’s ordering; **medium** for whether the omitted hose binding permits every placement variant.

**F13 — HIGH — Reaction item outputs retain the placement-loss bug fixed in converters**

- **Where:** `Machinery/Kits/RM_LiquidReaction.cs`, `Drop`:
  `count -= t.stackCount;`
  followed by the unchecked
  `GenPlace.TryPlaceThing(t, at, parent.Map, ThingPlaceMode.Near);`.
- **What happens:** Reactants are consumed through an always-successful sink. `Drop` decrements its output count before attempting placement and ignores placement failure. Failed or partially placed output has no saved pending ledger. The converter’s pending-output fix has not been applied to this analogous producer.
- **Repro:** Run an item-producing reaction with no room to place its product.
- **Suggested check — offline SelfTest:** Inject false and partial placement results. Assert consumed reactants correspond to placed products plus saved pending products.
- **Confidence:** **High**.

**F14 — HIGH — Stock snapshots both miss theft and falsely accuse the player**

- **Where:** `Machinery/RM_LiquidTheft.cs`:
  `RM_LiquidTheftMath.Touched(t.theftSeenUnits, t.theftSeenLiquid, t.storedUnits, t.storedLiquid)`.
  The loop examines every foreign artificial tank without checking who moved its liquid.
- **What happens:** Equal withdrawals and deposits between checks leave the same snapshot and escape theft accounting. Conversely, a foreign faction’s own machinery changing its own tank triggers player theft detection, even without a player connection. A nearby witness can initiate goodwill charges for autonomous NPC operation.
- **Repro:** First, withdraw and replace equal quantities between theft checks. Separately, operate a foreign-only pump/tank network near its owners with no player connection.
- **Suggested check — offline SelfTest plus cheap live:** Assert a balanced pair of committed player transfers is counted, while foreign-only transfers are excluded. Read caught/charge counters for both cases.
- **Confidence:** **High**.

**F15 — HIGH — Ground-fed bath recipes have unlimited unpaid liquid**

- **Where:** `Machinery/Kits/RM_LiquidBath.cs`, `TryFindSource`:
  `if (c.InBounds(map) && ext.terrains.Contains(c.GetTerrain(map)))`
  followed by `return true;`.
  Completion draws only when `bathed != null`.
- **What happens:** Matching terrain satisfies a craft without any stock debit. It also takes priority over connected tanks. A finite pond can consequently support unlimited recipes that would consume `unitsPerCraft` from tanks. The comments explicitly describe this behavior, but it conflicts with the brief’s higher-priority scarcity/conservation law.
- **Repro:** Place a liquid-bath bench beside qualifying finite liquid terrain and run repeated bills. Compare with the same bills supplied from a tank.
- **Suggested check — cheap live:** Complete several crafts and compare pond stock before/after against `crafts × unitsPerCraft`. Verify that nearby qualifying terrain does not bypass payment.
- **Confidence:** **High**.

**F16 — HIGH — Multi-input converters can permanently starve later liquids**

- **Where:** `Machinery/CompLiquidConverter.cs`:
  `int pick = RM_ConversionMath.FirstRunnable(batches);`.
  `Machinery/RM_ConversionMath.cs`:
  `if (batches[i] > 0) { return i; }`.
- **What happens:** Every cycle chooses the first runnable liquid in stable store order. If that input remains supplied, later compatible liquids never run. Consumer rotation cannot help: it rotates machines competing for one liquid, rather than liquids offered to one machine. This contradicts the design’s per-cycle liquid rotation rule.
- **Repro:** Supply a general distiller with two continuously replenished, distillable liquids. Keep the first tank nonempty and product capacity available.
- **Suggested check — offline SelfTest:** Present two runnable liquids across repeated cycles and assert both are selected within a bounded interval. The current selector always returns index zero.
- **Confidence:** **High**.

## Outside this slice

The following omitted implementations prevent completing the corresponding audits:

- **`Building_LiquidTank`**: stored-liquid migration, capacity changes, destroyed/despawned acceptance, tank-mode Scribe fields, and persistence of theft baselines/caught faction/debt.
- **`CompHoseReel`, hose settings, hose map component and port binding**: held-volume Scribe fields, load reconstruction, role-change invalidation, removal/drain ordering and setting-off behavior.
- **`Building_LiquidPump`, excavation component, body/stock implementation and flood engine**: actual source debit, pour rollback, pond migration, terrain/path/region invalidation and gate-state cache invalidation.
- **XML, LiquidDef/conversion definitions, shared patch application and `StylePickerCore`**: shipped recipe values, def wiring, Harmony target resolution and patch behavior when feature settings change.
- **Vanilla 1.6 method bodies** were not supplied, so Harmony overload compatibility and `JobDriver_DoBill.MakeNewToils` iterator timing remain unverified.

The residue component also leaves its pending cell/fluid queues unscribed, but its supplied header explicitly says no def carries the extension yet; I excluded that dormant issue from the release findings.

The code inputs appear complete and untruncated. `known_behaviours.md` explicitly contains truncated ledger heads.