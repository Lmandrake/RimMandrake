# FlowWorks liquid networks: what flows where, and who decides (2026-10-11)

status: DESIGN, for the owner's cards in §9. No mod source is changed by this pass. The FlowWorks build agent waits on it.
Owner order, typed 2026-10-11:
> *"Have you already given thought to how to select whether a hose is filling a tank or emptying a tank? Or setting direction
> at all? Or multiple tanks connected to each other, and multiple pumps? I think we need a thorough design pass on all of this
> to limit the complexity. We don't want to get into full circuit flow simulation if we can help it. Perhaps there's a way we
> can just set flexible hoses to be sources or sinks, and let everything else on the pipe network simply be "connected" and
> add/drain as they need? Seems like a good idea. ... this is worth a deep design pass, adversarial review, and GPT
> consultation."*

Binding inputs: `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md` (rulings #1, #2, #3, #9 bind here);
`design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md` (FINAL); the code at bench `4bd915dde5`:
`src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs`, `RM_LiquidNetKernel.cs`, `CompLiquidPipeAdapter.cs`,
`LiquidTypes/Building_LiquidPump.cs`, `LiquidTypes/Building_LiquidTank.cs`; `design/RimMandrake/liquids_framework_design.md`
("conservation of mass holds everywhere").

## 1. The player's model (the whole thing, in five sentences)

1. **Pipes and hoses only connect.** Everything joined by rigid pipe or by a hose left on **Connected** is one network, and
   every tank on it is one shared store that machines on it fill and drain as they need; nothing moves between tanks by
   itself, and pipes hold no liquid, so liquids never mix in a pipe.
2. **A pump is the only thing that puts liquid INTO storage from the world** (ruling #3). It needs no setting: it fills the
   store of the network it sits on, and stops when that store is full.
3. **A hose is where you choose a direction.** Its reel gizmo reads **Connected / Send to nozzle / Take from nozzle / Shut**.
   The *nozzle* is the free end you carried out, so the direction is always relative to something you can see.
4. **Filling vs emptying a tank is that one choice.** Hose from your base to the ship's tank: *Send to nozzle* fills the
   ship; *Take from nozzle* empties it into your base. No pump either way: storage passes to storage freely (ruling #9).
5. **A nozzle left on the ground is an outlet.** *Send to nozzle* pours the network's stored liquid out onto the ground or
   into a channel (draining needs no pump, ruling #3); *Take from nozzle* in a pond works only through a pump on that hose's
   network (intake needs a pump, ruling #3); *Connected* or *Shut* caps it.

That is the owner's candidate ("set flexible hoses to be sources or sinks, and let everything else on the pipe network
simply be connected"), made exact: **direction lives only on hoses (and on the foreign-pipe adapter, which already has the
same two-way gizmo); everything else is connected.**

## 2. How the established mods do it (read from their files, not recalled)

Read 2026-10-11 from the installed workshop copies (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`).
All three ship DLLs only and no IL decompiler is installed, so **structure is read from DLL metadata (type, field and
method names via `dnfile`), Defs and language files; per-tick algorithm bodies are INFERRED from names, not read.**

| | VE Framework PipeSystem (`2023507013/1.6/Assemblies/PipeSystem.dll`) | Dubs Bad Hygiene Lite (`2570319432`) | Rimefeller (`1321849735`) |
|---|---|---|---|
| net = | one per `PipeNetDef`, i.e. one per resource; cardinal flood fill; `PipeNet.Merge`/`Destroy` on topology change | one per `PipeType` (`Sewage, Air, Heating, Water`) | one pipeline net carrying oil AND fuel, kept as separate totals (`OilStorage`, `FuelStorage`, `TotalOil`, `TotalFuel`) |
| roles | `PipeNet` lists `producers, receivers, storages, thingConverters, resourceConverters, refillables, processors, extractors` | `WaterUsers, WaterPumps, WaterTowers, Sewers, …`; `WaterPumpedPerTick`, `PumpingCapacitySum` | wells/derricks/siphons push; refineries, crackers, powerplants pull |
| distribution | pooled: aggregates `Production, Consumption, Stored, AvailableCapacityLastTick`, then `DistributeAmongStorage` / `DrawAmongStorage` (INFERRED: surplus to storage, shortfall from storage) | demand-pull: consumers `PullWater`, pumps add; `shuffledWaterStorage` (INFERRED random order) | per-resource `PullOil/PullFuel/PushCrude/PushFuel` (INFERRED pooled) |
| player's per-tank control | `CompResourceStorage.markedForExtract` (to items), `markedForTransfer` ("transfer" to other tanks; semantics INFERRED); no priorities | a contamination "Drain tank" only | **`CompStorageTank`: `AllowInlet`, `AllowOutlet`, `DrainTank`** ("Drain the contents of this tank to other available tanks") |
| perf | event-driven topology, dirty flags, cached on/off lists, `PipeNet.NextTick` | `dirty` flag | `cycleIndex` round-robin (INFERRED) |
| cross-mod | none; each mod defines its own `PipeNetDef` on the shared engine | DBH-only | Rimefeller-only |

What we take: **(1)** every one of them is a pooled ledger, not a pressure solver; the owner's "not circuit flow" is the
genre norm. **(2)** All of them are one resource per net; we avoid needing that only because our pipes hold nothing (§3.8).
**(3)** Where the player chooses fill vs empty, it is a **per-tank** toggle (Rimefeller inlet/outlet/drain, VE transfer),
which is model B in §5; nobody puts direction on a hose, because none of them has a portable hose. **(4)** No mod joins
another mod's pipes; "plugs in cleanly" is done with an adapter building (§3.10), which matches the genre.

## 3. Rules

### 3.1 Network membership
- A **network** is what `RM_LiquidNetKernel.Walk` reaches from a member: rigid universal-pipe cells (cardinal), machines
  touching or standing on them, tanks touching them, and hose links whose mode is **Connected**. Directed (Send/Take) and
  Shut hoses are NOT crossed by the walk: a directed hose is a one-way transfer between two networks (§3.4), not a join.
- **A tank is an endpoint, never a conductor** (FINAL §3.1, `RM_LiquidNet.cs:14-17` invariant, kept). A tank touching two
  pipe runs is a member of both networks; the runs do not merge. Consequence the player sees: such a tank is a shared buffer
  (run 1's pump can fill it, run 2's machine can drain it), but run 1's pump never reaches run 2's other tanks.
- **Machines are origins, never conductors** (kept). A pump, converter, reactor, bath bench or pipe adapter between two runs
  does not join them.
- Relay reels conduct as today (FINAL §3.1); every hose in a relay chain has its own mode; a chain of Connected hoses is one
  network.

### 3.2 Several tanks on one network
- No equalising and no priorities. Tanks on one network are one store; liquid moves into or out of a tank only when a
  machine, a directed hose or an outlet moves it.
- **Fill order:** the fullest tank already holding that liquid with room, then an empty tank (ties: first reached). This
  generalises `TankToFill`'s existing "prefer a tank already holding it" and consolidates, so a mixed-liquid network keeps
  free tanks free.
- **Draw order:** the emptiest tank holding that liquid (ties: first reached), so tanks empty one at a time and come free
  for another liquid.
- Both orders are origin-independent, so every machine on a network sees the same choice (today's "first reached" is
  origin-dependent; §6 step N2).

### 3.3 Several pumps
- Pumps only ever move world → store. Two pumps cannot fight: there is no reverse pump. Two pumps on one network share its
  room; each 250-tick cycle each pump fills until the store is full, then reads "store full". Pumps on different networks
  joined only by a directed hose do not interact except through that hose's transfer.
- A pump with no tank on its network but an outlet (§3.5) on it pumps straight through to the outlet (irrigation: pump at
  the river → hose → nozzle in the field). The outlet is treated as a sink with its own room (the cell's room), so the
  pump's code path stays "find room for the units".

### 3.4 Directed hoses (the only direction setting)
- Each reel has a `mode`: **Connected** (default; joins), **Send to nozzle**, **Take from nozzle**, **Shut** (carries
  nothing; the walk does not cross it; ruling #2's drain applies, §3.7).
- A directed hose has a *from* side and a *to* side. The from side's store is: the tank itself, if that end is a tank
  (ruling #9: a tank passes liquid to a hose screwed into it, no pump); else every tank on the network walked from that end.
  The to side is the same, or an **outlet** if the to end is the nozzle lying free (§3.5).
- Each cycle (250 ticks) each directed hose moves at most `hoseUnitsPerCycle` (PROVISIONAL 10 = two pump levels) from the
  from side's draw order to the to side's fill order, one liquid per move, picking the first (source tank, destination)
  pair that is compatible (same liquid, or an empty destination). Tanks present on both sides are removed from the from
  side (no self-transfer).
- A full destination → nothing moves, the hose stays flat, inspect reads "destination full". An empty source → the same,
  "nothing to send".
- No pump is needed for any storage → storage move (ruling #9). A pump is needed only for world → storage (§3.6).

### 3.5 Outlets: draining to the world
- A nozzle lying free on a directed hose set to **Send to nozzle** is an outlet. Each cycle it pours up to
  `hoseUnitsPerCycle` of the from side's store into the nozzle cell: into an excavated channel cell through the excavation
  engine's pour (`TryPourLevel`, the path the pump's pour uses today), or onto open ground as a FlowWorks spill (surface
  flood). A cell that cannot take the liquid (full channel, a channel of another fluid, a wall) backs up: nothing moves,
  "outlet blocked" (and `NoteDriverBackedUp`, as the pump's pour does).
- Outlets need no pump and no power (ruling #3: "Taking liquid out of storage to the outside world does not [take work]").
- A free nozzle on Connected or Shut is capped: nothing leaves.

### 3.6 Filling from the world: pump only
- No nozzle intake by itself (ruling #3). A free nozzle on **Take from nozzle** lying in liquid is an **intake** only while
  a powered pump is on the network at the hose's reel end: the nozzle cell joins that pump's reach cells. Without such a
  pump it reads "intake needs a pump". (Card Q2 asks whether the pump must be coupled to the reel itself instead.)
- **Pump pour mode is retired** (card Q4): pouring out is an outlet's job and needs no pump. A pump is "draw" only.

### 3.7 A switched-off hose drains out of its open ends (ruling #2)
- A hose holds liquid while it is flowing: `heldUnits = ceil(hoseCells × hoseUnitsPerCell)` (PROVISIONAL 0.2/cell, so a
  30-cell hose holds 6), debited from the transfer that first fills it, so conservation holds (liquids framework: "conservation
  of mass holds everywhere").
- When a hose stops carrying (mod switch off, Shut, wound in, picked up, dropped, an end decoupled), its held liquid spills
  at its open end(s) as a FlowWorks spill; with no open end it returns to the tank it came from, else to the reel's cell.
  Card Q3 offers the cheaper reading (a cosmetic puddle, no units).

### 3.8 Mixed liquids
- Any number of liquids per network. Pipes and Connected hoses hold nothing; each tank holds one liquid (unchanged,
  `Building_LiquidTank.cs` "one stored LiquidDef"); every move pairs a liquid with a compatible destination. So the classic
  pooled-net failure (two fluids in one pipe) cannot occur. Only directed hoses and outlets hold liquid in transit (§3.7),
  and they carry one liquid at a time.
- An outlet or directed hose moves whatever its from side holds, draw order first. A per-hose liquid filter is NOT in v1
  (card Q5 asks).

### 3.9 Joins: pipe ↔ hose ↔ tank ↔ machine
| join | result |
|---|---|
| pipe — pipe (cardinal) | one network |
| pipe — tank (cardinal or under) | the tank is a member; it never joins two runs |
| pipe — machine (8-way or under) | the machine is a member (origin) |
| tank — machine (8-way) | member |
| hose (Connected) between any two members | one network across it (relay reels conduct) |
| hose (Send/Take) between two members | two networks, one-way transfer |
| hose with a free nozzle | outlet (Send), pump-driven intake (Take), capped (Connected/Shut) |
| our pipe — VE/DBH pipe | drawn as a coupling, never joins (FINAL §3.1 G1.7); liquid crosses only at an adapter (§3.10) |

### 3.10 Foreign pipe networks (ruling #1: "plugs into other pipe networks cleanly")
- The clean plug is the existing `CompLiquidPipeAdapter` (a VE `CompResourceStorage` on the VE side, a FlowWorks machine on
  ours, `CompLiquidPipeAdapter.cs:10-19`). Its gizmo is renamed into the hose vocabulary: **Send into <VE net> / Take from
  <VE net> / Shut**, PROVISIONAL rate unchanged (`unitsPerRareTick` 10).
- One adapter def per foreign resource (VE nets are one resource each); the adapter is a 1×1 fitting placed where the two
  pipe kinds meet, and the rigid pipe's art (ruling #8) draws a matching flange.
- DBH (water only) and Rimefeller: seams only; no adapter in v1 (their nets are not VE PipeSystem; §2).

### 3.11 Save compatibility
- Reels: new `rmHoseMode` (default Connected) and `rmHoseHeld`/`rmHoseHeldLiquid` (default 0). An old save loads with every
  hose Connected and empty.
- **Behaviour change at load:** today a hose with a tank at an end equalises toward the emptier tank across it
  (`RM_LiquidNet.TankFeedTick`). Under this design a Connected tank–tank hose joins the two into one store and moves nothing;
  the player sets Send/Take to move liquid. One-line load message when a map holds such a hose.
- Pumps saved with `RM_pumpPourMode=true` load as draw pumps; one message per map names them ("pumps no longer pour; lay a
  hose and set it to Send to nozzle").
- Adapters: `RM_adapterFeedNet` true → Send, false → Take (no new key needed; a Shut state adds `RM_adapterShut`).

## 4. The simulation: a ledger, not a circuit

- **No pressure, no flow rates through pipes, no pipe contents, no solving.** Connectivity is a BFS (the existing kernel);
  each mover (pump, converter, reactor, bath, adapter, directed hose, outlet) does one bounded transfer per cycle against the
  store of the network(s) it touches. This is the per-network pooled budget of VE PipeSystem (§2) reduced further: we have no
  continuous producers/consumers per tick, only discrete transfers every 250 ticks (pump, hoses) or rare tick (machines).
- **Order within a cycle** is the game's tick order (hash-interval ticks spread movers across the 250 ticks). Every rule is
  first-come, bounded, and conservative (remove, then add, put back on refusal: `RM_LiquidNetKernel.TankFeedTransfer`), so
  order changes who gets room first, never totals.
- **Cost.** Walk cost O(network cells + links), capped at `MaxVisits` 1500 (kernel). Walks per cycle = movers + 2 per
  directed hose; within a tick a walk is cached per origin (`RM_NetCache`). Budget kept from FINAL §3.5: 20 reels, 4 pumps,
  10 tanks ≤ 0.05 ms/tick mean, now with 5 directed hoses and 2 outlets added to the fixture.
- **Edge cases that break naive pooling, and the rule for each:**
  - *Loops (pipe rings, hose rings):* the BFS visited set (kernel `seen`/`crossed`). Directed-hose cycles (A sends to B, B
    sends to A) are legal but churn; each hose moves once per cycle; the inspect string names the hose that closes the
    circle (cycle found by a DFS over the directed-hose graph, built with the hose index once per tick).
  - *Two pumps fighting:* impossible by construction (§3.3).
  - *A tank both source and sink:* allowed. It is a buffer (pump fills, directed hose drains). A tank on both sides of the
    same directed hose is removed from the from side.
  - *A full sink:* nothing moves, no credit, the hose reads full and stays flat; a pump reads "store full".
  - *Truncated walk (> 1500):* the network is "too large", existing kernel flag; inspect says so.
  - *A tank shared by two networks:* each network's movers see it; liquid can cross through it only by those movers'
    own rules (a buffer, not a merge).
  - *Directed hose with both ends on the same network:* the from side minus the to side is empty, so it moves nothing and
    reads "both ends on one network".

## 5. Candidate models compared (option portfolio)

The decision can be interrogated on four different questions: *where does the player put intent* (hose, tank, pump, or
nowhere), *does the engine move liquid by itself* (equalise vs only on command), *how much physics* (ledger vs pressure),
*how does it meet other mods*. One best candidate per question:

| | A. Directed hoses (recommended) | B. Tank modes (VE-style) | C. Level equalisation (communicating vessels) | D. Directed pumps (circuit-lite) |
|---|---|---|---|---|
| intent lives on | the hose reel: Connected / Send / Take / Shut | each tank: Store / Empty out / Fill up | nowhere: tanks seek a common level | each pump has an in-side and out-side |
| tank → ship tank | hose Send to nozzle | set the base tank Empty out (also empties into every other base tank) or the ship tank Fill up | moves only half (to equal level) | needs a pump on the line |
| drain to the ground | nozzle on Send | needs an outlet building + mode anyway | needs an outlet anyway | pump pours |
| fits ruling #3 (storage → world free) | yes | yes | yes | no (the pump does it) |
| fits ruling #9 (tank → hose, no pump) | yes | yes | yes (that is today's `TankFeedTick`) | no |
| player confusion risk | must know which end is the nozzle (the one he carried) | one knob per tank, but "Empty out" sends everywhere on the net | "why did my full tank half-empty into the new one?" | rotation-dependent direction, invisible without a flow display (ruled out for now, #5) |
| engine cost | walk per directed hose per cycle | settle per net per cycle | equalise pairs per cycle, never quiet | real direction graph, loops, priority |
| code delta | small: link mode in the kernel; replace `TankFeedTick` | medium: per-tank state, net settle | none (exists) but no fill-vs-empty choice | large |

**Recommendation: A.** It is the owner's own candidate, it puts the one decision (fill vs empty) on the one object the
player handles to do it (the hose he just carried), it is the smallest code change from what exists, and it is the only
model where every scenario (tanker load, tanker unload, irrigation, drain, refuel, tank-to-tank) is one click on one gizmo.
B is the runner-up and is what VE PipeSystem does for its tanks (§2); its weakness is that an "Empty out" tank empties into
everything on its network, so moving liquid between two specific tanks needs separate networks anyway, which means a hose,
which means A. C is today's behaviour and cannot express "fill the ship". D is the circuit simulation the owner wants to
avoid.

## 6. Delta against the code and the FINAL design (build steps)

| # | step | files | change | gate |
|---|---|---|---|---|
| N1 | Link modes in the kernel | `RM_LiquidNetKernel.cs`, `RM_LiquidNet.cs` (`RM_HoseLinks`), `CompHoseReel.cs` | `RM_NetLink.Mode`; `Cross` skips non-Connected links; reel `mode` field + gizmo + Scribe key `rmHoseMode` | kernel selftests: Connected joins, Send/Take/Shut do not; save default Connected |
| N2 | Origin-independent fill/draw order | `RM_LiquidNet.TankToFill`, new `TankToDraw`; callers in pump, converter, reactor, bath, adapter | fullest-with-room fill, emptiest draw | selftests: two tanks, two origins pick the same tank |
| N3 | Directed hose transfer | replace `RM_LiquidNet.TankFeedTick` with `HoseTransferTick`; reuse `TankFeedTransfer`, `Across` | §3.4 | selftests: tank→tank Send/Take, pipe-net→tank, both-ends-same-net, full sink, empty source, loop pair |
| N4 | Outlets | `HoseTransferTick`, `HoseEnds.cs` (free end kind), excavation pour / spill | §3.5 | selftests on the pour picker; live bar `NS_outlet_drains_without_pump` |
| N5 | Pump-driven intake through a nozzle | `Building_LiquidPump.ReachCells` + hose index | §3.6, per card Q2 | live bar `NS_intake_needs_pump` (no pump: nothing moves) |
| N6 | Retire pump pour | `Building_LiquidPump.cs` (`TryPour`, `pourMode`, gizmo), `RM_PumpMath.PickPour` moves to the outlet | per card Q4; load message | selftest: a pour-mode save loads as draw |
| N7 | Held volume and off-drain | `CompHoseReel.cs`, map component | §3.7 per card Q3 | conservation selftest: units before = after a fill + switch-off |
| N8 | Adapter vocabulary | `CompLiquidPipeAdapter.cs` gizmo + Shut | §3.10 | save key mapping test |
| N9 | Settings | `RM_HoseSettings.cs`, `RM_MachinerySettings.cs` | `tanksFeedHoses` → `directedHosesEnabled`; new `outletsEnabled`, `nozzleIntakeEnabled`, `hoseUnitsPerCycle`, `hoseUnitsPerCell` | typed settings registry rows (FINAL §3.10) |

**Deleted:** `RM_LiquidNet.TankFeedTick`'s equalisation (`RM_LiquidNetKernel.FeedTarget`, the fill-fraction formula in
`TankFeedUnits`); the pump's pour mode; FINAL step 9 ("open nozzle extends the coupled pump's reach") is replaced by N5.
**Kept unchanged:** the kernel walk, the tank-endpoint invariant, routes and crediting (a directed hose credits its own reel
plus the route links on each side), the lease and tint rules, the per-tick cache, the VE/DBH visual-only rule.

## 7. Adversarial review

PENDING.

## 8. GPT consultation

PENDING.

## 9. Owner questions (card-ready, recommended first)

PENDING final wording after the reviews.
