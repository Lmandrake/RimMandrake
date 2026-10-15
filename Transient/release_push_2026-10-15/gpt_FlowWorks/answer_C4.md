I found **10 MOD findings**. Checks below are proposed, not executed. Paths are relative to `src/RimMandrake/FlowWorks/Source/`; citations quote exact code lines.

**F1 — MEDIUM — Save/load loses moving fire’s burn progress and liquid identity**

- **Where:** `RM_LiquidFire.cs`, `ExposeData`, `Maintain`, `TakeCarried`:
  ```csharp
  private readonly Dictionary<int, int> carriedAcc = new Dictionary<int, int>();
  private readonly Dictionary<int, FluidDef> burningFluid = new Dictionary<int, FluidDef>();   // not saved
  ```
- **What happens:** `ExposeData` saves neither carried progress nor its tick/liquid provenance. Saving between a burning level moving and its queued destination igniting resets that progress. Additionally, restored burning cells lack `burningFluid`: when subsequently drained, `Maintain` records a null carried liquid, which `TakeCarried` accepts as matching **any** fluid:
  ```csharp
  bool same = !carriedFluid.TryGetValue(i, out FluidDef cf) || cf == null || cf == fluid;
  ```
  Reload can therefore delay consumption, or allow progress from one liquid to accelerate another.
- **Repro:** Have burning liquid flow between cells beside an ongoing fire. Save while carried progress awaits a pending ignition; reload and compare against uninterrupted play. For the identity case, reload a burning cell, drain it, then ignite another burnable fluid beside its former position.
- **Suggested check:** **Offline serialization harness:** round-trip a fire with carried progress and a pending destination. Assert identical accumulator and fluid after ignition. Also round-trip an actively burning cell, then test cross-fluid carry rejection.
- **Confidence:** High for the omitted state and wildcard; medium for the precise player timing window.

**F2 — HIGH — An escapable endpoint exempts a sealed endpoint from reachability veto**

- **Where:** `RM_PocketGridMath.cs`, `ReachVetoed`:
  ```csharp
  return !sameComponent && !(startPocket && startWayOut) && !(destPocket && destWayIn);
  ```
- **What happens:** Either endpoint having a way suffices to return “not vetoed.” A pawn in a sealed starting pocket passes this gate when the destination pocket has a ladder. Conversely, an escapable starting pocket passes it when the destination pocket has no entrance. The two endpoint requirements are independent; satisfying one cannot release the other.
- **Repro:** Construct two separate pockets: one sealed, one laddered. Query travel in both directions. This helper accepts both.
- **Suggested check:** **SelfTest:** assert `ReachVetoed(false, true, false, true, true)` and `ReachVetoed(false, true, true, true, false)` are both true. Both currently return false. Then cheaply compare pawn-aware `CanReach` with actual path acceptance.
- **Confidence:** High for the erroneous helper result; its exact downstream job symptoms require the omitted caller.

**F3 — MEDIUM — Every cover performs the entire deck census**

- **Where:** `Pits/Trigger/CompPitCoverTrigger.cs`, `RunScan`:
  ```csharp
  List<Building_PitCover> deck = RM_PitCoverUtility.Deck(self);
  ```
  The lower-ID rejection occurs **after** this flood-fill.
- **What happens:** Only the lead sums pawn mass, but every cover first allocates and traverses its whole deck. For an N-cell deck up to the 400-cell cap, this is O(N²) traversal every 30 ticks. A 400-cell deck performs approximately 160,000 cover visits per scan cycle, before neighbour probes and collection allocation. New covers also begin with synchronized scan counters.
- **Repro:** Build a large connected covered moat with triggering enabled; it need not contain any pawns.
- **Suggested check:** **Cheap live profiling:** measure one synchronized scan cycle for connected decks of 50, 100 and 200 cells. Count `Deck` calls and visited cells; the current implementation should show quadratic growth.
- **Confidence:** High.

**F4 — HIGH — Disabling heat preserves a cache that misses terrain changes**

- **Where:** `RM_LiquidHeat.cs`, terrain-change postfix:
  ```csharp
  if (___map == null || !RimMandrakeFlowWorksSettings.liquidHeatPushEnabled)
  ```
  `Tick` also returns while disabled without invalidating `naturalCells`, `naturalKinds` or `nextRescanTick`.
- **What happens:** Terrain changes made while heat is off generate no stale notice. Re-enabling before the old rescan deadline resumes the cached cells and their old kinds. Drained hot water can continue heating; newly introduced hot water can contribute nothing. The stale state can last nearly **15,000 ticks—six game hours**.
- **Repro:** Let an enclosed hot pond populate the cache. Disable liquid heat, pump it dry, then re-enable promptly.
- **Suggested check:** **Cheap live read:** use `ProofHeat` on the drained cell. Confirm terrain kind is zero while its isolated room still receives liquid heat. Repeat after `ProofRescan`; the phantom contribution should disappear.
- **Confidence:** High within the shown cache lifecycle; an external settings invalidator is not included.

**F5 — HIGH — Mixed cover tiers use construction order as their strength**

- **Where:** `Pits/Trigger/CompPitCoverTrigger.cs`:
  ```csharp
  if (c.thingIDNumber < self.thingIDNumber) return;
  ```
  ```csharp
  float threshold = Pit.CoverTier.TriggerMassKg() * RimMandrakeFlowWorksSettings.trapSensitivityMultiplier;
  ```
  `Building_PitCover.cs`, `Deck`, joins adjacent covers without checking tier.
- **What happens:** The lowest-ID cover supplies the threshold for the entire mixed deck. A reinforced cover can fail at the woven rating, or a woven cover can withstand the reinforced rating, solely because of build order. Individual inspect strings still advertise each cover’s own rating.
- **Repro:** With own-faction capture enabled, connect woven and reinforced covers. Put one ordinary human on the woven section. Repeat with reversed construction order.
- **Suggested check:** **Offline deck/trigger case:** use the same positions, tiers and pawn masses; swap only cover IDs. Spring behaviour must remain identical.
- **Confidence:** High.

**F6 — MEDIUM — Connected decks larger than 400 cells collapse only partially**

- **Where:** `Pits/Building_PitCover.cs`, `Deck`:
  ```csharp
  while (open.Count > 0 && deck.Count < 400)
  ```
- **What happens:** The cap affects mechanics, not just computation. Both leadership and `Spring` operate on the truncated census. A connected deck can have multiple local leaders, sum only part of its occupants, and leave intact covers after its advertised “whole cover” gives way.
- **Repro:** Build a connected 401+ cell deck and overload one end. Inspect surviving covers and pawns at the other end.
- **Suggested check:** **Offline Python graph case:** use a 1×401 chain. Assert one leader, 401 counted cells and 401 removed covers after springing. The shown traversal cannot satisfy these.
- **Confidence:** High.

**F7 — HIGH — Burning liquid beneath an intact cover treats its occupants as immersed and trapped**

- **Where:** `RM_LiquidFire.cs`, `ApplyEffects`:
  ```csharp
  bool heldInPit = ex.IsSuperdeepExcavation(c);
  ```
  ```csharp
  if (things[t] is Pawn p && !p.Dead && Rand.Chance(RM_FireMath.AttachChance(heldInPit)))
  ```
- **What happens:** Unlike drowning and poison, fire never checks whether the cell is covered. A pawn crossing an intact deck over burning liquid receives the D=4 **1.0 attach chance**. The same shortcut classifies flying pawns and creatures that can escape by size or ladder as trapped. It contradicts both “cover is ground” and the stated bonus applying to a **trapped** occupant.
- **Repro:** Ignite liquid below a cover, disable mass triggering, and move a pawn onto it. Separately test a flying pawn over uncovered burning D=4 liquid.
- **Suggested check:** **Cheap live state read:** confirm the cover remains intact, drowning/poison are absent, and attached fire appears. An offline eligibility test should distinguish covered, flying, genuinely held and freely escaping occupants.
- **Confidence:** High.

**F8 — MEDIUM — Newly ignited cells receive burn time from before ignition**

- **Where:** `RM_LiquidFire.cs`, `BurnPulse`:
  ```csharp
  int levels = RM_FireMath.CanalLevelsToBurn(lit != null, ref acc, pulseTicks, canalTicks);
  ```
- **What happens:** Ignition records an accumulator but no burn-start timestamp. The next pulse credits the complete `pulseTicks`, even if the cell ignited immediately beforehand. Source cells have the same issue through `LevelsDue`. Consumption can occur almost one pulse early, especially visibly with fast burn settings.
- **Repro:** Ignite immediately before a flow pulse, then compare with ignition immediately after the preceding pulse. Both receive the same first-pulse credit despite different elapsed burning time.
- **Suggested check:** **Offline timing case:** ignite at tick 599, process a 600-tick pulse at tick 600, and use a 600-tick burn threshold. The current arithmetic consumes a level after one actual burning tick.
- **Confidence:** High.

**F9 — MEDIUM — A later explosion inherits an unrelated earlier explosion’s origin**

- **Where:** `RM_LiquidFire.cs`, `NotifyExplosionAt`:
  ```csharp
  if (blastHops.TryGetValue(ci, out int bh) && ex.IsSourceCell(c))
  ```
- **What happens:** Front-generated explosions are remembered by centre cell for 300 ticks. Any subsequent explosion at that centre inherits their source-hop restriction, regardless of its actual origin or damage type. A fresh player grenade or shell can therefore fail to ignite source cells because an earlier liquid detonation used that location.
- **Repro:** Trigger a liquid-front detonation near its source-reach limit. Within 300 ticks, detonate an independent bomb at the same centre. Compare its ignition footprint with an otherwise identical bomb at a fresh centre.
- **Suggested check:** **Offline notification harness:** seed a remembered front blast, then submit an independent `Bomb` notification at its centre. Assert that the new thermal trigger starts with direct-ignition provenance.
- **Confidence:** High.

**F10 — MEDIUM — Heat sampling loses power after the per-room cap**

- **Where:** `RM_LiquidHeat.cs`, `Push`:
  ```csharp
  Credit(map, cells[e], energies[e] * exScale);
  ```
  followed by `Apply` calling `RM_LiquidHeatMath.RoomEnergy`, which caps each sampled room.
- **What happens:** Global sampling weights preserve uncapped sums, but they cannot preserve sums after per-room capping. Excess credited to a sampled room is discarded; unsampled rooms receive nothing. Consequently, adding unrelated liquid elsewhere can reduce an existing room’s average heating or cooling.
- **Repro:** Have 6,000 hot excavated sources, ordered as two groups of 3,000 in separate enclosed rooms. The 3,000-cell budget visits one room per interval. Each room receives its capped contribution only every other interval.
- **Suggested check:** **SelfTest:** compare two intervals of full room aggregation against alternating weighted samples. At strength 1, the cap is 700 energy per room per interval. Full aggregation supplies 1,400 per room over two intervals; this sampling arrangement supplies only 700.
- **Confidence:** High.

## Outside this slice

The following are needed to complete the integration audit:

- `RM_MapComponent_Excavation`: serialization, post-load repair, fire/pulse ordering, settings invalidation and actual `MapRemoved` cleanup.
- `RM_PocketGrid`, reachability consumers, cliff-mask ownership, ladder/ramp implementations and trap state: endpoint handling, cache generations, pawnless queries and cover-removal descent detection.
- `RM_LiquidStock`, `RM_LiquidBody`, `FluidDef`, `BurnOffLevel` and volume adapters: source burn units, debit semantics and conservation.
- Cover, flame, exposure, drowning and thought XML: ticking configuration, health stages, memory stacking and upgrade behaviour.
- `PatchApplier` and actual vanilla/mod override implementations: Harmony target resolution and compatibility coverage. In particular, explosion damage/destruction ordering and persistence need inspection before asserting further explosion/save bugs.

**No supplied C# file appears truncated.** `known_behaviours.md` explicitly contains truncated ledger heads, so their complete acceptance criteria were unavailable.