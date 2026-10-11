# FlowWorks liquid networks: what flows where, and who decides (2026-10-11)

status: DESIGN, reviewed by an adversarial opus subagent (§7) and GPT (§8); the owner decides through the §9 cards. No mod source
is changed by this pass. The FlowWorks build agent waits on it. Draft `bb58eb122` used direction-on-hoses (model A). Both reviews
found the same structural defects in it, and the adversary argued that direction on tanks is simpler. This version recommends
model **E** (§5) and keeps A as the card's second option, because GPT preferred a corrected A.

Owner order, typed 2026-10-11:
> *"Have you already given thought to how to select whether a hose is filling a tank or emptying a tank? Or setting direction
> at all? Or multiple tanks connected to each other, and multiple pumps? I think we need a thorough design pass on all of this
> to limit the complexity. We don't want to get into full circuit flow simulation if we can help it. Perhaps there's a way we
> can just set flexible hoses to be sources or sinks, and let everything else on the pipe network simply be "connected" and
> add/drain as they need? Seems like a good idea. ... this is worth a deep design pass, adversarial review, and GPT
> consultation."*

Binding inputs:
- `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`; rulings #1, #2, #3, #5 and #9 bind here.
- `design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md` (FINAL).
- `design/RimMandrake/liquids_framework_design.md`: *"conservation of mass holds everywhere"*.
- The code at bench `4bd915dde5`. Paths below are relative to `src/RimMandrake/FlowWorks/Source/` unless they start with `design/`.

## 1. The player's model (five sentences)

1. **Pipes and hoses only connect.** Everything joined by rigid pipe or a laid hose is one network. Every tank on it is a
   shared store that pumps and machines fill and draw from as they need. Pipes and hoses hold nothing, so liquids never mix in
   transit, and nothing moves between tanks unless a tank is told to.
2. **A pump is the only way liquid gets INTO storage from the world** (ruling #3). It needs no setting: it fills the tanks on
   its network and stops when they are full.
3. **Fill-or-empty is set on the TANK.** Each tank has one gizmo:
   - **Store** (the default) holds liquid for pumps and machines.
   - **Empty** sends its liquid to the other tanks on the network.
   - **Fill** pulls the network's liquid into itself.
   - **Dump** pours its liquid out of any open nozzle on the network.
   No pump is needed for any of these, because storage passes to storage, and to the ground, freely (rulings #3 and #9).
4. **A hose has one switch: its nozzle is Capped or Open.** A capped hose just connects. An open nozzle lying free is where a
   Dump tank pours out, and where a pump on that network can draw liquid from, if it lies in liquid.
5. **The tanker raid is one click each way.** Ship tank on **Fill** loads it from your base. Ship tank on **Empty** unloads
   it into your base. At a tar lake, the portable pump fills the ship tank through the hose.

This keeps the owner's core idea: *"let everything else on the pipe network simply be "connected" and add/drain as they
need"*. It moves the source/sink choice from the hose to the tank:
- **Tanks do not move.** A hose's direction flips whenever its reel is carried to the other side.
- **Each tank holds one liquid.** So "which liquid drains" is simply "which tank you set".
- **Relay chains then need no direction rules.**

The hose keeps what is physically true of a hose: its free end is open or capped. §5 compares the models, and card Q1 lets the
owner keep direction on hoses instead.

## 2. How the established mods do it (read from their files, not recalled)

Read 2026-10-11 from the installed workshop copies (`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\`).
All three ship DLLs only, and no IL decompiler is installed. So **structure was read from DLL metadata (type, field and method
names via `dnfile`), Defs and language files. Per-tick algorithm bodies are INFERRED from names, not read.**

| | VE Framework PipeSystem (`2023507013/1.6/Assemblies/PipeSystem.dll`) | Dubs Bad Hygiene Lite (`2570319432`) | Rimefeller (`1321849735`) |
|---|---|---|---|
| net = | one per `PipeNetDef`, i.e. one per resource; cardinal flood fill; `PipeNet.Merge`/`Destroy` on topology change | one per `PipeType` (`Sewage, Air, Heating, Water`) | one pipeline net carrying oil AND fuel, kept as separate totals (`OilStorage`, `FuelStorage`, `TotalOil`, `TotalFuel`) |
| roles | `PipeNet` lists `producers, receivers, storages, thingConverters, resourceConverters, refillables, processors, extractors` | `WaterUsers, WaterPumps, WaterTowers, Sewers, …`; `WaterPumpedPerTick`, `PumpingCapacitySum` | wells, derricks and siphons push; refineries, crackers and powerplants pull |
| distribution | pooled: aggregates `Production, Consumption, Stored, AvailableCapacityLastTick`, then `DistributeAmongStorage` / `DrawAmongStorage` (INFERRED) | demand-pull: consumers `PullWater`, pumps add; `shuffledWaterStorage` (INFERRED random order) | per-resource `PullOil/PullFuel/PushCrude/PushFuel` (INFERRED pooled) |
| per-tank player control | `CompResourceStorage.markedForExtract` (to items), `markedForTransfer` (to other tanks; INFERRED); no priorities | a contamination "Drain tank" only | **`CompStorageTank`: `AllowInlet`, `AllowOutlet`, `DrainTank`** ("Drain the contents of this tank to other available tanks") |
| perf | event-driven topology, dirty flags, cached on/off lists, `PipeNet.NextTick` | `dirty` flag | `cycleIndex` round-robin (INFERRED) |
| cross-mod | none; each mod defines its own `PipeNetDef` on the shared engine | DBH-only | Rimefeller-only |

What we take from them:
1. **Every one is a pooled ledger, not a pressure solver.** The owner's "not circuit flow" is the genre norm.
2. **All of them run one resource per net.** We do not need that rule, only because our pipes hold nothing (§3.8).
3. **Where the player chooses fill vs empty, he chooses it per TANK.** That is Rimefeller's inlet/outlet/drain and VE's
   transfer, and model E follows it. Nobody puts direction on a hose, but none of them has a portable hose either.
4. **No mod joins another mod's pipes.** "Plugs in cleanly" is done with an adapter building (§3.10).

## 3. Rules

### 3.1 Networks (components), computed once per topology change
- **Conductors:** universal-pipe cells (they conduct cardinally), relay reels, and laid hoses that are live (FINAL §3.1
  eligibility: hoses enabled, `Laid`, non-null lay, both ends spawned). A **component** is a connected set of conductors,
  where each hose counts as one conductor.
- **Members attach; they do not conduct.** A tank or machine attaches to every component it touches:
  - a pipe cardinal to it or under it, for a tank;
  - a pipe 8-way around it or under it, for a machine;
  - a hose whose end is coupled to it.

  A tank between two pipe runs is a member of both, and the runs do not merge. This keeps FINAL's endpoint invariant
  (`Machinery/RM_LiquidNet.cs:14-17`) but states it on components, which makes it well-defined. The adversary (A7) and GPT
  (G1) both showed that it is not well-defined on per-origin walks. A tank–hose–tank pair is a component of one conductor
  (the hose) with two tanks attached, which honours ruling #9.
- **A member's store** is the set of tanks attached to any component it is attached to. A tank 8-way to a machine also
  counts, as it does today. The player sees "what this touches through pipe or hose".
- **Computed per topology revision, not per tick.** A map-level `revision` counter is bumped by:
  - spawn or despawn of a pipe, tank or machine;
  - a reel state change (laid, wound, dropped, carried) or a port change;
  - a nozzle Capped/Open change;
  - a settings change.

  Components, membership lists and a predecessor tree per component (for hose crediting routes) are rebuilt lazily on
  first use after a bump. A bounded BFS over all conductors costs O(conductors + members). This replaces the per-origin,
  per-tick walk cache (`RM_NetCache`).
- A component larger than `MaxConductors` (PROVISIONAL 3000, counting cells, links and members) is **refused**: its members
  see no store and read "network too large". It is never partly operated (G12).

### 3.2 Tank modes, and the order of moves
- Gizmo on every `Building_LiquidTank`, saved as `rmTankMode`:

  | mode | pumps and machines put in | machines draw from | sends to other tanks | receives from other tanks | pours out open nozzles |
  |---|---|---|---|---|---|
  | **Store** (default) | yes | yes | to Fill tanks | from Empty tanks | no |
  | **Fill** | yes | yes | no | from Empty, then Store tanks | no |
  | **Empty** | no | yes | to Fill, then Store tanks | no | no |
  | **Dump** | yes (so a pump plus a Dump tank irrigates) | no | no | no | yes |

- **Settle.** Once per cycle (250 ticks, at the component's hashed tick), each component runs one settle:
  1. Every Empty tank sends up to `tankUnitsPerCycle` (PROVISIONAL 10).
  2. Every Fill tank receives up to the same.
  3. Every Dump tank pours up to the same, out of open nozzles.

  The settle moves only stock that was present at the start of the settle, so nothing is forwarded twice in one cycle (G9).
  Pairs are matched by liquid: a destination must hold the same liquid or be empty.
- **Fill order** (pumps, machine outputs, settle destinations): the fullest tank that already holds that liquid and has
  room, then an empty tank. Ties go to the lowest `thingIDNumber`.
- **Draw order** (machine inputs, settle sources): the emptiest tank holding that liquid. Ties go to the lowest
  `thingIDNumber`.
- Both orders depend only on stock and id, never on who asks. A 5-unit level may be split across tanks (G8: today
  `TankToFill` needs one tank to take all 5, so 3 + 2 units of room deadlock a pump).
- **Liquid choice** when one move could carry several liquids (for example two Empty tanks of different liquids): the move
  rotates among them by cycle, starting with the liquid of the lowest-id source.

### 3.3 Several pumps
- A pump only moves world → store. **Two pumps cannot fight**, because no reverse pump exists. Pumps on one network share its
  room, and each one fills until the store is full, then reads "store full".
- **No fair-share ledger.** First-come is acceptable because the totals cannot go wrong and a pump that misses its turn
  simply idles. The starvation case that matters is two machines that both consume one liquid. Those are rotated: each cycle
  starts with the machine that was served last-but-one (G9).
- **Irrigation is a pump plus a Dump tank plus an open nozzle.** There is no tankless pass-through path, which keeps the
  world → hose escrow that G7 asked for out of the design entirely.

### 3.4 Hoses
- Each hose has one setting, **Capped / Open**, on the reel gizmo; it is saved as `rmNozzleOpen`, default Capped. It only
  matters when the free end lies free; a coupled end is simply coupled.
- Hoses carry no direction. A relay chain is just conductors. "Which end is the nozzle" never decides anything except where
  the open end is, and the player can see that.
- **Other factions' tanks and machines are not attached.** A non-player `Building_LiquidTank` or machine is a member only if
  it belongs to the player (A5: today `RoleOfThing` gives any faction's tank the Tank role, `Machinery/RM_LiquidNet.cs:96`, and
  `HosePorts.FindAt` couples to any faction's port, `Hose/HoseEnds.cs:12`). Card Q4 asks whether to make it priced theft
  instead.

### 3.5 Open nozzles: draining to the world
- A Dump tank pours through every open nozzle on its components, up to `tankUnitsPerCycle` per tank in total, split in
  nozzle-id order.
- **Where the liquid goes:**
  - an excavated channel cell takes it through the excavation engine's pour;
  - open ground takes it as a FlowWorks surface spill;
  - a liquid with no channel form spills as a typed spill and is never discarded (G10).
- **A blocked cell moves nothing** and reads "outlet blocked". That covers a full channel, a channel of another fluid, and a
  wall.
- An open nozzle needs no pump and no power (ruling #3: *"Taking liquid out of storage to the outside world does not"*).
- With no Dump tank on its network, an open nozzle pours nothing.

### 3.6 Filling from the world needs a pump
- An open nozzle has no intake of its own (ruling #3).
- **Intake through a nozzle (card Q5, recommended yes).** An open nozzle lying in drawable liquid adds that liquid's SOURCE
  cell to the reach of every pump attached to its component. "Drawable" means an excavated channel cell with fill, or an
  `IsSourceCell` cell (A13: never the dry nozzle cell itself).
  - The pump's own predicate still gates it: settings, machine switch, flick and power (G7).
  - A pump's budget is one level per level-slot, across all of its reach cells, not one per nozzle.
- **Pump pour mode is retired** (card Q3). Pouring is a Dump tank's job and needs no pump.
  - A pump saved in pour mode loads **switched off** (flick off). A message names it once per map, so a load never starts
    unintended pumping (G13).
  - The station's radius-wide, deepest-cell-first pour picker (`RM_PumpMath.PickPour`) moves to the open nozzle: a nozzle pours
    into the best cell within 1.5 cells (A14).

### 3.7 A switched-off hose drains out of its open ends (ruling #2)
- Hoses hold no liquid in this model, so there is nothing real to drain. The recommended reading is **visual**: when a hose
  stops carrying, its strand plays the existing Draining state, and a short-lived wet-ground filth appears at each open end.
  A hose stops carrying when hoses are switched off, it is wound, dropped or decoupled, or its nozzle is capped mid-pour. No
  liquid units are created or destroyed.
- Card Q2 offers the real version: every wet hose holds `ceil(cells × 0.2)` units in a saved escrow that is spilled at the
  open ends. It costs:
  - a reel ledger (liquid, units);
  - flush rules for a change of liquid or of mode;
  - save hooks;
  - a conservation selftest;
  - about one build step.

  Both reviews showed that a half-specified escrow destroys or duplicates liquid (A9, G3), so it is all or nothing.

### 3.8 Mixed liquids
- **Any number of liquids per network.** Pipes and hoses hold nothing. Each tank holds one liquid (`LiquidTypes/Building_LiquidTank.cs`,
  "one stored LiquidDef"). Every move pairs a liquid with a compatible destination. So the classic pooled-net failure, two
  fluids in one pipe, cannot occur.
- **Draining one liquid of several** is choosing which tank is on Dump or Empty, so no per-hose liquid filter is needed (A8).

### 3.9 Joins

| join | result |
|---|---|
| pipe — pipe (cardinal) | one component |
| pipe — tank (cardinal, or under) | tank attached; never joins two components |
| pipe — machine (8-way, or under) | machine attached |
| tank — machine (8-way) | the machine's store includes the tank |
| laid hose coupled at an end to a pipe, relay, tank or machine | the hose joins that pipe or relay's component; a tank or machine attaches |
| hose free end | Capped: nothing. Open: outlet for Dump tanks, intake for pumps if it lies in liquid |
| our pipe — VE/DBH pipe | drawn as a coupling, never joins (FINAL §3.1 G1.7); liquid crosses only at an adapter |

### 3.10 Foreign pipe networks (ruling #1: *"plugs into other pipe networks cleanly"*)
- **The clean plug is the existing `CompLiquidPipeAdapter`.** It is a VE `CompResourceStorage` on the VE side and a
  FlowWorks machine on ours (`Machinery/CompLiquidPipeAdapter.cs:10-19`). One adapter def per VE resource, as a 1×1 fitting
  where the two pipe kinds meet; the rigid pipe's art (ruling #8) draws a matching flange.
- **Modes: Send into the VE net / Take from it / Shut.** A newly built adapter starts **Shut**, so two adapters cannot quietly
  churn a loop through a foreign net (A16).
- **Conservation at the boundary (G5).**
  - Send: read the VE storage's `AmountCanAccept`, remove that many units from our tank, call `AddResource`, read
    `AmountStored` again, and put back any shortfall.
  - Take: the mirror image.
  - A reflection failure or a non-finite ratio fails closed: the adapter shuts itself and logs one red line.
  - The fractional remainder of `resourcePerUnit` is carried in a saved field, never rounded away.
- **DBH and Rimefeller get no adapter in v1.** They are seams only, because their nets are not VE PipeSystem (§2).

### 3.11 Save compatibility
- **Tanks:** `rmTankMode`, default Store. An old save loads with every tank on Store, which behaves exactly like today's
  machines.
- **Behaviour change:** today a hose with a tank at one end evens the levels across it (`Machinery/RM_LiquidNet.cs`
  `TankFeedTick`). Here a hose only connects. The player sets one of the two tanks to Empty or Fill to move liquid, and a
  one-line message appears on a map that holds such a hose. FlowWorks is not released, so no player save depends on the
  old behaviour.
- **Reels:** `rmNozzleOpen`, default Capped. If Q2 picks the real version, add `rmHoseHeld` and `rmHoseHeldLiquid`. An
  unknown liquid is quarantined and logged, as `Building_LiquidTank.cs:120` does today.
- **Pumps:** `RM_pumpPourMode=true` → the pump is flicked off, with the §3.6 message. The key is read once and then dropped.
- **Adapters:** `RM_adapterFeedNet` true → Send, false → Take. New `RM_adapterShut`, default false on load (keeps old saves
  running); new builds start Shut.
- **Settings:** `tanksFeedHoses` is read once into `tankModesEnabled`. When that is off, every tank behaves as Store, so the
  modes are inert (they never fall back to equalising).

## 4. The simulation: a ledger, not a circuit

- **No pressure, no flow rate through pipes, no pipe contents, no solver.** Components are a BFS per topology revision.
  Movers do bounded, discrete transfers. Pumps and settles run per 250-tick cycle; converters, reactors, baths and adapters
  run per rare tick. This is VE PipeSystem's pooled budget (§2), reduced further: there are no continuous per-tick
  producers or consumers.
- **One transfer service.** Every move goes through `RM_LiquidTransfer.Move(source, destination, liquid, units)`:
  1. validate both legs;
  2. remove;
  3. add;
  4. on refusal, put the units back;
  5. credit hoses and counters only after a committed move.

  This fixes the existing order bugs both reviews found:
  - pump draw debits the world before adding to the tank (`LiquidTypes/Building_LiquidPump.cs:155-164, 176-185`);
  - pour credits the world before removing from the tank (`:247-254`);
  - converter output goes ahead after a failed input removal (`Machinery/CompLiquidConverter.cs:233-240`);
  - the adapter removes before it invokes (`Machinery/CompLiquidPipeAdapter.cs:136, 155`).

  A world-side mutation that cannot be undone (`TryTakeLevel`, `TryDebit`, `TryPourLevel`) runs **after** the tank leg is
  reserved, so the only remaining failure is the world refusing, and that is checked before anything changes.
- **Order:** movers spread across ticks by hashed interval. Every mover is bounded and conservative, so order changes who
  gets room first, never totals.
- **Cost bounds:**
  - Component rebuild is O(conductors + members) per topology revision, capped at 3000.
  - Per cycle: one settle per component that has a non-Store tank, at most O(tanks in it), plus O(1) store lookups per
    mover from the cached membership.
  - Routes for hose crediting come from the component's predecessor tree: O(route length), with no per-crossing route copies.
    GPT G12 found that `RM_LiquidNetKernel.cs:137` copies a route at every crossing, which makes long relay chains
    quadratic.
  - Budget fixture (FINAL §3.5 plus this design): 20 reels, 4 pumps, 10 tanks, 3 Empty/Fill/Dump tanks, 2 open nozzles.
    The bar is ≤ 0.05 ms per tick mean **and ≤ 1 ms worst tick**, rebuild included (A11).
- **Edge cases that break naive pooling, and the rule for each:**
  - *Loops (pipe or hose rings):* a component is a set, so a ring is nothing special. There are no directed links, so
    there are no directed cycles.
  - *Two pumps fighting:* impossible (§3.3).
  - *A tank that is both source and sink:* allowed. A Store tank is a buffer that a pump fills and a machine drains. An Empty
    tank never receives and a Fill tank never sends to tanks, so a single settle cannot ping-pong.
  - *A tank shared by two components:* a member of both. Its mode applies in each, and its stock is counted once.
  - *Two Fill tanks, or two Empty tanks, on one component:* Fill tanks take from Empty and Store tanks only, never from each
    other. Two Empty tanks both send. Nothing circulates.
  - *A full sink:* nothing moves, nothing is credited, and the tank reads "nowhere to send" or "full".
  - *A too-large network:* refused, never partly operated (§3.1).
  - *A pump drawing from the pond a Dump tank pours into:* the same body, debited and credited by the same volume table.
    This needs a round-trip selftest (A15): units drawn from a body = units poured back, ±0.

## 5. Candidate models compared (option portfolio)

The decision can be interrogated on four different questions:
- *Where does the player put intent:* the hose, the tank, the pump, or nowhere?
- *Does the engine move liquid by itself?*
- *How much physics?*
- *Does the setting stay true when things are moved?*

One best candidate per question:

| | **E. Tank modes + open nozzles (recommended)** | A. Directed hoses (owner's candidate, corrected per GPT) | C. Level equalisation | D. Directed pumps |
|---|---|---|---|---|
| intent lives on | the tank: Store / Fill / Empty / Dump; the hose: Capped / Open | the hose: Connected / Send to nozzle / Take from nozzle / Shut | nowhere: tanks seek one level | each pump has an in-side and an out-side |
| ship tank ← base | ship tank Fill | hose "Send" or "Take", depending on which end the reel is at | moves half | a pump on the line |
| drain one liquid to the ground | that tank on Dump, open the nozzle | hose Send + a per-hose liquid filter (G10) | needs an outlet anyway | the pump pours |
| setting survives carrying the reel to the other side | yes (tanks do not move) | no: Send flips meaning (A10); the gizmo must name both ends | n/a | n/a |
| relay chains | just conductors | needs chain-mode inheritance, or Send moves nothing (A6) | n/a | n/a |
| fits rulings #3 and #9 | yes | yes | yes (that is today's `TankFeedTick`) | no (#3: draining would need a pump) |
| precedent | Rimefeller `AllowInlet/AllowOutlet/DrainTank`, VE `markedForTransfer` | none (no mod has portable hoses) | DBH-like | none |
| engine | components + one settle per component | components + a side resolution per directed hose + directed-cycle diagnostics + forwarding limits | pair equalising every cycle, never quiet | a real directed graph |
| code delta | medium (§6) | medium-plus (§6 plus the side resolver, filters and chain modes) | none, but it cannot fill a ship | large |

**Recommendation: E.**
- It answers the owner's question ("how to select whether a hose is filling a tank or emptying a tank") with one click on
  the tank being filled or emptied.
- It keeps his "everything else simply connected".
- It matches what the established mods do (§2).
- Its settings stay true when hoses are carried around, and it needs neither a liquid filter nor relay-chain rules.

**A is a real alternative and GPT chose it.** GPT's argument: tank permissions "do not replace hose direction" for portable
loading. That argument answers inlet/outlet *permissions* (B in the draft). E has Fill and Empty, which do load and unload.
A is the better pick if the owner thinks of the hose, not the tank, as the thing he operates during a raid; that is card Q1.
C cannot express "fill the ship". D is the circuit simulation the owner wants to avoid.

## 6. Delta against the code and the FINAL design (build steps)

Sized as one commit each, in order. Each builds the FlowWorks DLL, passes `run_selftests.py`, and keeps a settings screen.

| # | step | files | change | gate |
|---|---|---|---|---|
| L1 | **Transfer service + conservation fixes** | new `Machinery/RM_LiquidTransfer.cs` (Verse-free core); `Building_LiquidPump.cs`, `CompLiquidConverter.cs`, `Kits/RM_LiquidReaction.cs`, `Kits/RM_LiquidBath.cs`, `CompLiquidPipeAdapter.cs`, `RM_LiquidNet.TankFeedTick` | every mutation through `Move`; world leg reserved and checked first; adapter reads back VE amounts; converter keeps unplaced item output pending (G6) | selftest per site: an injected refusal on each leg leaves totals unchanged; caller-coverage lint (FINAL's 11 sites + new ones) |
| L2 | **Components per topology revision** | `RM_LiquidNetKernel.cs` (components, membership, predecessor tree, cap refusal), `RM_LiquidNet.cs` (revision bumps, `StoreOf(member)`), `RM_HoseLinks` (built per revision, not per tick) | §3.1; `RM_NetCache` deleted; `Walk`/`Across` replaced by `Components`; routes from predecessors | kernel selftests: tank between two runs is in both, runs do not merge; tank–hose–tank is one component; machines do not conduct; revision bump on each listed event; truncation refuses |
| L3 | **Fill and draw order, split levels** | `RM_LiquidNet` (`TankToFill` → `FillPlan`, new `DrawPlan`), all callers | §3.2 orders; a level split across tanks; consumer rotation | selftests: 3 + 2 room takes a level; two origins get the same plan; rotation |
| L4 | **Tank modes + settle** | `Building_LiquidTank.cs` (mode, gizmo, inspect), new settle in the map component; delete `TankFeedTick`, `FeedTarget`, `TankFeedUnits` equalising | §3.2 table | selftests: ship Fill from base; ship Empty to base; two Fill tanks; Empty + Fill + Dump on one component; epoch-start stock only |
| L5 | **Open nozzles: outlet** | `CompHoseReel.cs` (`rmNozzleOpen`, gizmo), `HoseEnds.cs` (free-end kind as a component port), `PickPour` moved to the nozzle, spill path | §3.5 | selftests on the pour picker; live bar `NS_dump_tank_drains_without_pump` |
| L6 | **Retire pump pour; intake through a nozzle** | `Building_LiquidPump.cs` (`TryPour`, `pourMode`, gizmo deleted; `ReachCells` + component nozzles) | §3.6, as card Q3/Q5 rule | selftest: a pour-mode save loads flicked off; live bars `NS_intake_needs_pump`, `NS_pond_roundtrip_conserves` |
| L7 | **Faction rule** | `RM_LiquidNet.RoleOfThing`, `HosePorts.FindAt` | §3.4, as card Q4 rules | selftest: a non-player tank is not a member |
| L8 | **Adapter modes + boundary** | `CompLiquidPipeAdapter.cs` | §3.10 | save-key mapping test; injected short accept puts units back |
| L9 | **Off-hose drain** | `CompHoseReel.cs`, `HoseMath` | §3.7, as card Q2 rules (visual: small; real: + escrow) | visual: none lost; real: conservation selftest |
| L10 | **Settings + perf** | `RM_HoseSettings.cs`, `RM_MachinerySettings.cs`, perf probe | `tankModesEnabled`, `tankUnitsPerCycle`, `nozzleOutletsEnabled`, `nozzleIntakeEnabled`; typed registry rows (FINAL §3.10); worst-tick bar | registry equality test; perf fixture §4 |

**Deleted from code:**
- `RM_LiquidNet.TankFeedTick`;
- `RM_LiquidNetKernel.FeedTarget`, `TankFeedUnits` and `Across`;
- `RM_NetCache` and the per-origin, per-tick walk;
- the pump's pour mode and its gizmo and strings;
- `tanksFeedHoses`, migrated.

**Deleted from FINAL:**
- step 9, "open nozzle extends the coupled pump's reach", which L6 replaces;
- §3.5's per-tick cache;
- the §3.1 sentence "links are crossed from the origin, from pipe cells and from relay vertices, never from a tank", which
  is restated on components.

**Kept:**
- the tank-endpoint invariant, now on components;
- hose eligibility (FINAL §3.1), crediting at committed moves, the flow lease and tint rules (FINAL §3.2-3.4);
- the VE/DBH visual-only rule;
- one liquid per tank.

**For the build agent waiting on this:**
- L1 does not depend on any card and fixes real conservation bugs, so it can start now.
- L2 and L3 depend only on the component rule, which is not a card question.
- L4 waits on Q1, L6 on Q3 and Q5, L7 on Q4, and L9 on Q2.

## 7. Adversarial review (independent opus subagent, 2026-10-11, against draft `bb58eb122`)

Told to break the draft on exploits, degenerate builds, player confusion, perf, contradictions, and the alternative model.
Each finding was checked against the cited code before its disposition was set.

| id | sev | finding | disposition |
|---|---|---|---|
| A1 | BLOCKER | a Connected hose with a tank at each end is never crossed, because the kernel stops at tanks (`RM_LiquidNetKernel.cs:142`, links crossed only from the origin, pipes and relays `:176-177`), so "joins the two into one store" was false | ACCEPT: the hose is a conductor and tanks attach (§3.1) |
| A2 | BLOCKER | the walk cannot start from a pipe cell or relay: `OriginTanks`/`OriginPipeCells` need a Thing (`RM_LiquidNet.cs:168-194`), the cache is keyed by `thingIDNumber` | ACCEPT: components replace per-origin walks (§3.1, L2) |
| A3 | BLOCKER | free nozzles have no representation: a link needs a far end with a role (`RM_LiquidNet.cs:524-533`), and outlets on uncrossed Send hoses are invisible to pumps | ACCEPT: an open nozzle is a component port (§3.5, L5); the tankless pass-through is dropped (§3.3) |
| A4 | BLOCKER | pour and draw already break conservation on failure (`Building_LiquidPump.cs:157-164, 178-185, 249-259`) | ACCEPT: transfer service, L1 first |
| A5 | MAJOR | carry a nozzle to a visitor's tank and drain it for free: any faction's tank is a Tank (`RM_LiquidNet.cs:96`, `HoseEnds.cs:12`) | ACCEPT: player-owned only by default, card Q4 |
| A6 | MAJOR | a relay chain set to Send moves nothing | ACCEPT as an argument for E: hoses carry no direction |
| A7 | MAJOR | "network" is relative to the starting point; the draft's "both ends on one network" test was false | ACCEPT: components (§3.1) |
| A8 | MAJOR | an outlet drains every liquid on the network | ACCEPT: only Dump tanks pour (§3.5) |
| A9 | MAJOR | held liquid contradicts "hoses hold nothing" and is under-specified | ACCEPT: visual drain recommended; real escrow is all-or-nothing on card Q2 (§3.7) |
| A10 | MAJOR | "Send to nozzle" flips when the reel is carried to the other side | ACCEPT as an argument for E; under A the gizmo must name both endpoints |
| A11 | MAJOR | bursty walks; whole index rebuilt per tick; a mean-per-tick budget hides spikes | ACCEPT: per-revision components, hashed settle, worst-tick bar (§4) |
| A12 | MAJOR | default Connected makes ruling #9 moot in practice | ACCEPT in part: under E the tank passes liquid to whatever the hose reaches. Machines draw through it at once; moving tank to tank needs one click (Empty/Fill). Ruling #9 says the tank *passes on* liquid "without a pump", and E needs none. Card Q1 notes it |
| A13 | MINOR | the nozzle intake added a dry cell to the pump's reach | ACCEPT: add the source cell (§3.6) |
| A14 | MINOR | retiring pour loses the station's area pour picker | ACCEPT: `PickPour` moves to the nozzle (§3.6) |
| A15 | MINOR | pond ↔ tank unit arbitrage unmeasured | ACCEPT: round-trip selftest (§4, L6) |
| A16 | MINOR | two adapters churn through a VE net | ACCEPT: new adapters start Shut (§3.10) |
| A17 | — | model B as a hybrid beats A: intent on stationary tanks, hoses pure connectors, outlets pour only from drain tanks | ACCEPT: this is model E (§5). The draft had misread Rimefeller's gates as "empties into everything" |

## 8. GPT consultation (gpt-6.1-sol, effort high, 2026-10-11)

How it ran:
- **Tool:** `python3 src/RimMandrake/Utils/gpt_consult.py`.
- **Prompt:** `design/RimMandrake/liquid_network_semantics_gpt_2026-10-11/prompt.md`.
- **Files sent (8, 94,860 chars):**
  - the draft design and the 2026-10-11 rulings;
  - `RM_LiquidNet.cs`, `RM_LiquidNetKernel.cs` and `CompLiquidPipeAdapter.cs`;
  - `Building_LiquidPump.cs` and `Building_LiquidTank.cs`;
  - `CompLiquidConverter.cs`.
- **Raw answer:** `design/RimMandrake/liquid_network_semantics_gpt_2026-10-11/gpt_answer.md`.

| id | sev | finding | disposition |
|---|---|---|---|
| G1 | BLOCKER | "one network, one store" is incompatible with the walker; define components of conductors with tanks and machines attached | ACCEPT (§3.1); same as A1/A7 |
| G2 | BLOCKER | directed transfer cannot reuse `Across`/`Walk` (`RM_LiquidNetKernel.cs:66, 83`; `RM_LiquidNet.cs:175`) | ACCEPT; moot under E, required under A |
| G3 | BLOCKER | hose contents contradictory; needs typed escrow or an owner ruling for a cosmetic drain | ACCEPT: card Q2 asks exactly that (§3.7) |
| G4 | BLOCKER | pump, converter and `TankFeedTransfer` mutation paths assume success | ACCEPT: L1 |
| G5 | BLOCKER | adapter boundary unchecked: removes before `AddResource`, adds before `DrawResource` (`CompLiquidPipeAdapter.cs:136, 155`) | ACCEPT: §3.10 read-back, fail closed |
| G6 | MAJOR | converter 2→1 has no accounting model; unplaced item output is lost (`CompLiquidConverter.cs:315`) | ACCEPT in part: pending item output goes into L1. The 2→1 ratio is a recipe's design (refining reduces volume), not a network rule; noted for the converter's own item, not this design |
| G7 | BLOCKER | pump-to-outlet needs world→hose escrow and a full pump predicate | ACCEPT by removal: no tankless pass-through; irrigation uses a Dump tank (§3.3); intake uses the full pump predicate (§3.6) |
| G8 | MAJOR | fragmentation: `TankToFill` needs one tank to take 5 (`RM_LiquidNet.cs:294`) | ACCEPT: split levels (§3.2, L3) |
| G9 | MAJOR | first-come starvation; same-update forwarding around cycles | ACCEPT: consumer rotation; epoch-start stock (§3.2-3.3) |
| G10 | MAJOR | ties, cross-liquid order, liquids without channel forms unspecified | ACCEPT: id ties, liquid rotation, typed spills (§3.2, §3.5) |
| G11 | MAJOR | `Live` does not validate changed ports; `IntVec3` always "spawned" (`RM_LiquidNet.cs:458, 471`) | ACCEPT: revision bump on port/coupling changes; commit re-checks member identity (§3.1) |
| G12 | MAJOR | `MaxVisits` bounds only enqueued vertices; route copies are quadratic (`RM_LiquidNetKernel.cs:128, 137`) | ACCEPT: cap counts everything; refuse when over; predecessor tree (§3.1, §4) |
| G13 | MAJOR | converting pour pumps to draw starts unintended pumping; disabled-mode rules | ACCEPT: pour pumps load flicked off; modes-off = all Store (§3.11) |
| G14 | MAJOR | §6 understated the delta; the draft mischaracterised B | ACCEPT: §6 rewritten as L1-L10; B corrected into E |
| verdict | — | "Choose a corrected A … B is useful for optional reserve protection, but adds controls without eliminating the need to direct portable loading and drainage." | **NOT FOLLOWED, with the reason stated.** GPT judged B as inlet/outlet permissions only. E adds Fill/Empty/Dump, which cover portable loading, unloading and drainage. The disagreement goes to the owner as card Q1, with A offered as GPT's pick |

## 9. Owner questions (card-ready, recommended option first)

**Q1. Where do you choose "fill this" or "empty this"?**
- **(a) On the tank (recommended).** Each tank gets Store / Fill / Empty / Dump. Hoses and pipes just connect, and a hose's
  nozzle is Capped or Open.
  - Trade: one click on the tank you care about; it never flips when you carry a reel around; draining one liquid is just
    picking that tank. This is how Rimefeller does it.
  - Cost: you click the tank, not the hose.
- **(b) On the hose (your first idea; GPT's pick).** Each hose gets Connected / Send to nozzle / Take from nozzle / Shut.
  - Trade: you set it right where you are working.
  - Cost: "send" depends on which end the reel is at, so the button must name both ends; relay chains need a rule, and
    draining one liquid needs a liquid picker on the hose.
- **(c) Both.** Tank modes, plus a hose Shut switch for a quick stop.
  - Trade: most flexible.
  - Cost: two places to look when something does not move.

**Q2. "A hose switched off drains out of its open ends": how real?**
- **(a) Visual (recommended).** The hose visibly empties, and a wet patch appears at the open end. No liquid is gained or lost.
  - Trade: cheap and safe.
  - Cost: the drained liquid is not "real".
- **(b) Real.** Every hose holds a little liquid (about 1 unit per 5 cells), taken from the tank when it fills and spilled at
  the open end when it stops.
  - Trade: true to life, and you can lose a bit of rare liquid.
  - Cost: about one extra build step, plus save data.

**Q3. Does the pump keep its "pour into channels" mode?**
- **(a) No, retire it (recommended).** Pouring is a Dump tank plus an open nozzle and needs no pump, matching your rule that
  draining takes no work. The pump's smart "fill the deepest cell first" moves to the nozzle.
  - Cost: old pour-mode pumps load switched off, with a message.
- **(b) Keep it** as a powered, wide-area pour next to the pump.
  - Trade: nothing changes for existing builds.
  - Cost: two ways to do one thing.

**Q4. Can you hook a hose to another faction's tank?**
- **(a) No (recommended).** Only your own tanks and machines join your network.
  - Trade: no free-liquid exploit.
- **(b) Yes, as theft.** Priced like power theft (2 goodwill per day, 12-cell notice).
  - Trade: a fun raid option.
  - Cost: one more theft rule to build and test.
- **(c) Yes, freely.**
  - Cost: an exploit.

**Q5. An open nozzle lying in a pond: can a pump on that network draw through it?**
- **(a) Yes, if a working pump is on the same network (recommended).** The pump does the work, as your rule says; the hose
  lets the pump stand back from the shore.
  - Trade: the tanker raid's pump can sit by the ship.
- **(b) No.** The pump must stand at the water itself.
  - Trade: simpler.
  - Cost: hoses only carry stored liquid, never pond water.
