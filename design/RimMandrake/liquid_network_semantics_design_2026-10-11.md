# FlowWorks liquid networks: what flows where, and who decides (2026-10-11)

status: DESIGN rev 2. Rev 1 (`faacce017`) went to the owner as five cards, and §0 records his answers. Rev 2 adds the tankless
pump transfer he asked for and re-evaluates every model against it, counting clicks (§5). It now recommends model **H**:

- **Hose free ends** get a role: Intake, Outflow or Capped.
- **The pump** is the only thing that moves liquid out of the world.
- **Tank modes** stay, for storage only.

§7 re-checks every adversarial finding against H; Q1 goes back to him as the revised card in §9. No mod source is changed by
this pass.

**Built (2026-10-11, owner ruled Q1 = H by card 15:45):** L1 `7432ac095a`, L2 `12f1b314c7`, L3 `9d727a3b22`, L4 `25d272ff93`,
L5 `9163cd3d76`, L6 `fe13508b7a`, L7 `5b9a704357`, L8 `8ec0dbef2a`, L9 `e329b72036`, L10 `5ce7f4aae3`, L11 the commit that adds
this line. Each step's guarantee is a `## must be true` line of `design/validation_walks/RimMandrake/FlowWorks.md` arrowed to its
SelfTest cases; the live bars of §6 are owed to a bridge session. Two built readings of this text: theft (§3.4) is detected on the
foreign tank's own stock once per cycle rather than inside `Move`, so no mover can bypass it; with tank jobs off a pump on Pour
drains any tank as before (there is no Dump to mark). Draft history: `bb58eb122` (direction on hoses), `faacce017` (tank modes), this revision (H).

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
- The code at bench `4bd915dde5`. Paths are relative to `src/RimMandrake/FlowWorks/Source/` unless they start with `design/`.

## 0. Owner answers to the rev 1 cards (2026-10-11 15:35, relayed by the coordinator)

- **Q1, where fill/empty is set: NOT RULED.** He typed:
  > *"Need to design with you further. How could we also support having a pump suck water from a lake and put it in a
  > disconnected canal? If we do the tank version, the player would have to allow the tank to fill, then have the tank empty
  > into the canal later. If we do the hose, we could have one hose be intake, and another be outflow, and the pump does the
  > rest. Wouldn't even need to have a tank in the mix really. Please add that into your design and evaluate the
  > interactions needed to supply that need (I have a feeling it will occur)"*

  This revision answers it (§1, §3.3, §5), and the revised card is §9 Q1.
- **Q2, the off-hose drain: RULED real.** He picked the real small volume and added: *"and you have to have colonists "clean
  it up" if it's in a cleanable area."* See §3.7.
- **Q3, pump pour mode: RULED kept.** Card pick, with his words: *"Keep it as faster draining"*. A Dump tank drains slowly
  with no pump; a pump in pour mode drains fast. See §3.6.
- **Q4, another faction's tank: RULED allowed as theft.** Card pick: it is priced like power theft (ruling #7: 2 goodwill
  per day, 12-cell notice). See §3.4.
- **Q5, a pump drawing through an open nozzle: not asked separately.** It is folded into Q1. Under H it stops being a
  question, because an Intake nozzle is exactly "a pump draws through it" and ruling #3 already says intake needs a pump.

## 1. The player's model (rev 2, recommended model H)

1. **Pipes and hoses connect.** Everything joined by rigid pipe or a laid hose is one network. Its tanks are a shared store
   for pumps and machines. Pipes and hoses never mix liquids, and nothing moves between tanks unless a tank is told to.
2. **A hose's free end has a role, set on its reel: Capped (default), Intake or Outflow.** The role belongs to the free end,
   wherever it lies, so it never flips when the reel is carried. An Intake end lying in a lake is where pumps on that
   network suck from. An Outflow end is where liquid leaves the network into the world.
3. **The pump is the only mover out of the world** (ruling #3). It draws from water in its own reach and from every Intake
   end on its network. It sends that liquid first to the network's Outflow ends, then into its tanks. **So lake → pump →
   disconnected canal needs no tank at all.** Lay one hose from the pump into the lake and set it to Intake. Lay another
   from the pump into the canal and set it to Outflow. The pump does the rest: two clicks.
4. **Tanks keep four storage modes:**
   - **Store** (default) holds liquid for pumps and machines.
   - **Fill** pulls the network's liquid into itself.
   - **Empty** pushes its liquid into the network's other tanks.
   - **Dump** marks a tank whose liquid may leave through Outflow ends.

   A Dump tank drains slowly through Outflow ends with no pump. A pump switched to Pour drains Dump tanks fast, into its own
   reach and out of Outflow ends (Q3: *"Keep it as faster draining"*).
5. **Every drain is explicit.** Liquid leaves storage only from a tank marked Dump and only through an Outflow end or a
   pouring pump. So opening an Outflow never pours away the drinking water by accident.

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
1. **Every one is a pooled ledger, not a pressure solver.**
2. **All of them run one resource per net.** We do not need that rule, only because our pipes hold nothing (§3.8).
3. **Per-tank fill/drain control is the genre's idiom**, as in Rimefeller and VE. H keeps it for storage.
4. **None of them has a portable hose, so none has hose-end roles.** H's Intake/Outflow ends are our own.
5. **No mod joins another mod's pipes.** "Plugs in cleanly" is done with an adapter building (§3.10).

## 3. Rules

### 3.1 Networks (components), computed once per topology change
- **Conductors:** universal-pipe cells (they conduct cardinally), relay reels, and laid hoses that are live (FINAL §3.1
  eligibility: hoses enabled, `Laid`, non-null lay, both ends spawned or the free end lying free). A **component** is a
  connected set of conductors, where each hose counts as one conductor.
- **Members attach; they do not conduct.** A tank or machine attaches to every component it touches:
  - a pipe cardinal to it or under it, for a tank;
  - a pipe 8-way around it or under it, for a machine;
  - a hose whose end is coupled to it.

  A tank between two runs is a member of both, and the runs do not merge. This is FINAL's endpoint invariant
  (`Machinery/RM_LiquidNet.cs:14-17`) stated on components.
- **Ports:** a hose's free end with role Intake or Outflow is a **port** of the hose's component.
- **A member's store** is the set of tanks attached to any component it is attached to, plus tanks 8-way to a machine.
- **Computed per topology revision, not per tick.** A map-level `revision` counter is bumped by:
  - spawn or despawn of a pipe, tank or machine;
  - a reel state or port change;
  - a free-end role change;
  - a settings change.

  Components, membership, ports and a predecessor tree (for hose crediting) are rebuilt lazily after a bump, at a cost of
  O(conductors + members). This replaces the per-origin, per-tick walk cache (`RM_NetCache`).
- A component larger than `MaxConductors` (PROVISIONAL 3000, counting cells, links, members and ports) is **refused** and
  never partly operated.

### 3.2 Tank modes, and the order of moves
- Gizmo on every `Building_LiquidTank`, saved as `rmTankMode`:

  | mode | pumps and machines put in | machines draw from | sends to tanks | receives from tanks | may leave the network (Outflow / pump pour) |
  |---|---|---|---|---|---|
  | **Store** (default) | yes | yes | to Fill tanks | from Empty tanks | no |
  | **Fill** | yes | yes | no | from Empty, then Store tanks | no |
  | **Empty** | no | yes | to Fill, then Store tanks | no | no |
  | **Dump** | yes | no | no | no | **yes**: slowly through Outflow ends with no pump; fast through a pump on Pour |

- **Settle.** Once per cycle (250 ticks, at the component's hashed tick):
  1. Empty tanks send.
  2. Fill tanks receive.
  3. Dump tanks pour through Outflow ends.

  Each step moves up to `tankUnitsPerCycle` (PROVISIONAL 10 for tank-to-tank; the Dump gravity pour is PROVISIONAL 5, the
  slow drain). Only stock present at the start of the settle moves. Liquids are matched: a destination must hold the same
  liquid or be empty.
- **Bottles and tank jobs** (bottle-loop fix, 2026-10-11, code review; `RM_TankBottleRules` in `RM_LiquidNetKernel.cs`).
  A colonist pours a filled bottle into a tank **unasked only when the tank is Fill**; a player's order (right-click a bottle,
  "Prioritize emptying ...") may also pour into a **Store** tank. Empty and Dump tanks never take bottles. Empty bottles are
  filled from **Store, Empty and Dump** tanks, never from a Fill tank, so an ordinary Store tank still fills bottles. Why it
  cannot loop: no tank both takes bottles unasked and gives them back, and liquid in a Fill tank never leaves it for another
  tank (the settle sends from Empty and Store only), so nothing poured in unasked returns to a bottle. Selftested on the
  production settle planner (`RulingsWetDoorWakeBottleChecks`). With tank jobs off every tank is Store, so bottles are
  poured in only on an order.
- **Fill order:** the fullest tank that holds that liquid and has room, then an empty tank. **Draw order:** the emptiest
  tank holding it. Ties go to the lowest `thingIDNumber`. A 5-unit level may be split across tanks. When one move could carry
  several liquids, it rotates among them per cycle.

### 3.3 The pump: the only mover out of the world
- **Sources** (Draw mode, the default): water in the pump's own reach (as today, `Building_LiquidPump.ReachCells`), plus the
  SOURCE cell under or beside every **Intake** end on its components.
  - "Drawable" means an excavated channel cell with fill, or an `IsSourceCell` cell (A13).
  - Reach cells come first, then Intake ends in id order.
- **Destinations, in order:**
  1. **Outflow ends** on its components, rotated by id, each taking at most one level per cycle and only where the cell can
     take the liquid (§3.5);
  2. then its tanks, in fill order.

  **This is the tankless transfer** (lake → pump → disconnected canal). An open Outflow is an explicit instruction, so it
  outranks the tanks. To fill tanks instead, cap the Outflow.
- **World → world move:**
  1. Check that the destination cell can take a level (a new `CanPourLevel` beside the existing `TryPourLevel`,
     `RM_MapComponent_Excavation.cs:1131`).
  2. Take the source level (`TryTakeLevel` `:1114` or `Stock.TryDebit`).
  3. Pour it.

  The pour cannot fail after the check, because the same tick has no other writer to that cell between the two calls. Both
  sides are counted in world levels, so there is no tank-unit conversion and no arbitrage (A15).
- **Budget:** `levelsPerCycle` (the def's, default 1) per 250 ticks, in total across all of its sources and destinations.
  More Intake ends do not make a pump faster.
- **The full pump predicate gates everything:** settings, machine switch, flick and power (G7). An Intake end with no
  working pump on its network does nothing and reads "intake needs a pump" (ruling #3).
- **Pour mode (kept, Q3: *"Keep it as faster draining"*).**
  - It drains **Dump tanks only** on its network, into its own reach (the existing `RM_PumpMath.PickPour`, deepest and
    emptiest cell first) and out of Outflow ends.
  - Its rate is the pump's `levelsPerCycle`, against the Dump tank's slow gravity rate.
  - Today's pour mode drains any tank. Restricting it to Dump tanks is a deliberate change (A8): it means a pump never pours
    out a tank the player did not mark.
- **Several pumps:** each has its own budget; they share sources, destinations and room in pump-tick order. **Two pumps
  cannot fight.** A drawing pump only adds, and a pouring pump only drains Dump tanks, which a drawing pump also fills:
  - The worst case is a churn loop (Draw fills Dump, Pour drains it). It is bounded at one level per pump per cycle, and
    its net effect is zero.
  - The pump's inspect string says "another pump on this network is pouring".
- **Starvation:** two machines that both consume one liquid are rotated each cycle (G9).

### 3.4 Hoses
- **Free-end role on the reel gizmo, saved as `rmFreeEndRole`: Capped (default) / Intake / Outflow.** The label always
  names the free end ("Free end: Intake"). The free end is not a selectable thing (`Hose/HoseEnds.cs` is a static helper, not
  a Thing), so the reel carries the gizmo.
  - A relay chain's role sits on the reel whose hose ends free.
  - The role is inert while the free end is coupled to something. When it is coupled, it is a plain connection.
- Hoses carry no direction along their length, so the reel-flip problem (A10) cannot arise: Intake and Outflow describe what
  happens *at the free end*, and the player can see where that is.
- **Another faction's tank or machine (Q4, ruled: theft).**
  - It attaches to the network like any member.
  - Every committed unit taken from it, or put into it, counts as liquid theft under the power-theft rule (ruling #7):
    2 goodwill per day while it continues, and the same 12-cell notice when a hose couples to it.
  - The theft hook sits in the transfer service (§4), so no mover can bypass it.

### 3.5 Outflow ends: where liquid enters the world
- An Outflow end takes liquid from a drawing pump (fast: the pump's budget) and from Dump tanks (gravity: the slow rate)
  and puts it into the cell under it or the best cell within 1.5 cells (`PickPour`). In that cell:
  - an excavated channel cell takes it through the excavation engine's pour;
  - open ground takes it as a FlowWorks surface spill;
  - a liquid with no channel form spills as that liquid's filth (§3.7).
- **A blocked end moves nothing** and reads "outflow blocked". That covers a full channel, a channel of another fluid, and a
  wall. A pump then falls through to its tanks.
- An Outflow end with neither a pump nor a Dump tank on its network does nothing. Draining needs no pump (ruling #3), but it
  does need a tank marked Dump.

### 3.6 Intake ends and the pump's reach
- An Intake end adds the drawable SOURCE cell under or beside it to the pump's reach, never the dry nozzle cell (A13).
- An Intake end on a network with no working pump does nothing (ruling #3).
- Intake and Outflow ends in the same body of water: the pump moves levels round in a circle. This is bounded, gains
  nothing, and burns power. Inspect says "intake and outflow in the same water".

### 3.7 A hose that stops carrying drains out of its open ends (ruling #2; Q2 ruled real)
- **A hose holds liquid while it carries.** Each live hose that a committed move crossed keeps a saved ledger
  (`rmHoseHeldLiquid`, `rmHoseHeldUnits`). On the first move that crosses it, it fills to
  `ceil(cells × hoseUnitsPerCell)` (PROVISIONAL 0.2 per cell, so a 30-cell hose holds 6 units). That fill is taken from the
  move itself, so less arrives that first cycle. Conservation holds.
- **One liquid at a time.** A move of a different liquid first flushes the held liquid out of the far end, as that move's
  first units, and then refills the hose with the new liquid.
- **When the hose stops carrying,** it drains through its open ends. A hose stops carrying when it is:
  - Capped, or turned off by the mod switch;
  - wound or picked up;
  - dropped or decoupled;
  - destroyed.

  It also drains when it was last used more than the flow lease ago.
  - With a free end, all of the held liquid comes out there.
  - With two coupled ends, it comes out at the reel's cell. It never goes back into a tank, which could be full or hold
    another liquid (A9).
- **Where it lands (owner: *"you have to have colonists "clean it up" if it's in a cleanable area"*):**
  - into a channel or water cell: poured in, as liquid;
  - onto ground: one **spill filth** per `unitsPerFilth` (PROVISIONAL 2) of that liquid. A new LiquidDef field `spillFilth`
    names it: `RM_Filth_Tar` exists; water, chemfuel and the rest need one def each, generated per LiquidDef row.

  Filth in the home area is cleaned by vanilla Clean jobs; outside it, it stays until its def's `disappearsAfterTicks`.
  Filth amount is a world record of the spill, not a stock; nothing ever converts filth back into liquid units.
- **Saves:** an unknown held liquid is cleared with one warning, as `Building_LiquidTank.cs:120` does.

### 3.8 Mixed liquids
- **Any number of liquids per network.** Pipes hold nothing. A hose holds one liquid at a time (§3.7). Each tank holds one
  liquid. Every move pairs a liquid with a compatible destination.
- **Draining one liquid of several** means marking that tank Dump. A pump's world→world transfer carries whatever the source
  water is.

### 3.9 Joins

| join | result |
|---|---|
| pipe — pipe (cardinal) | one component |
| pipe — tank (cardinal, or under) | tank attached; never joins two components |
| pipe — machine (8-way, or under) | machine attached |
| tank — machine (8-way) | the machine's store includes the tank |
| hose end coupled to a pipe, relay, tank or machine | the hose joins that pipe or relay's component; a tank or machine attaches |
| hose free end | Capped: nothing. Intake: a pump source. Outflow: a pump or Dump-tank destination |
| our pipe — VE/DBH pipe | drawn as a coupling, never joins (FINAL §3.1 G1.7); liquid crosses only at an adapter |

### 3.10 Foreign pipe networks (ruling #1)
- **The clean plug is `CompLiquidPipeAdapter`** (`Machinery/CompLiquidPipeAdapter.cs:10-19`): one def per VE resource, as a
  1×1 fitting, with the rigid pipe drawing a matching flange (ruling #8).
- **Modes: Send into the VE net / Take from it / Shut.** A new adapter starts Shut (A16).
- **Conservation at the boundary (G5):** read the VE amount back after `AddResource`/`DrawResource`, put back any shortfall,
  carry the fractional remainder of `resourcePerUnit` in a saved field, and fail closed with one red line on a reflection
  failure.
- **DBH and Rimefeller:** seams only, no adapter in v1.

### 3.11 Save compatibility
- **Tanks:** `rmTankMode`, default Store, which behaves like today for machines.
- **Behaviour change:** today a hose with a tank at an end evens levels across it (`RM_LiquidNet.TankFeedTick`). Under H
  the hose connects, and moving tank to tank is one click (Fill or Empty). The map shows one message when such a hose is
  present. FlowWorks is not released.
- **Reels:** `rmFreeEndRole`, default Capped; `rmHoseHeldLiquid` and `rmHoseHeldUnits`, default empty.
- **Pumps:** `RM_pumpPourMode` is kept (Q3). A pump saved in pour mode now drains only Dump tanks, and every tank loads as
  Store. So it goes idle until a tank is marked Dump, and one message per map says so. Nothing pours unexpectedly.
- **Adapters:** `RM_adapterFeedNet` true → Send, false → Take; `RM_adapterShut` defaults to false on load and true on a new
  build.
- **Settings:** `tanksFeedHoses` is migrated into `tankModesEnabled`. With modes off, every tank behaves as Store; they never
  fall back to equalising.

## 4. The simulation: a ledger, not a circuit

- **No pressure, no flow rate through pipes, no pipe contents, no solver.** Components are a BFS per topology revision.
  Movers do bounded, discrete transfers: pumps and settles per 250-tick cycle; converters, reactors, baths and adapters per
  rare tick. Hoses hold only their small transit ledger (§3.7).
- **One transfer service, `RM_LiquidTransfer.Move(source, destination, liquid, units)`:**
  1. validate both legs, including world `CanPourLevel`/`CanTake`;
  2. remove;
  3. add;
  4. on refusal, put the units back;
  5. then: hose held-volume fill or flush, theft accounting (§3.4), and hose credit.

  This also fixes the existing order bugs:
  - `Building_LiquidPump.cs:155-164, 176-185, 247-254`;
  - `CompLiquidConverter.cs:233-240`;
  - `CompLiquidPipeAdapter.cs:136, 155`.
- **Cost bounds:**
  - Component rebuild is O(conductors + members + ports) per revision, capped at 3000.
  - Per cycle: one settle per component that has a non-Store tank; each pump does O(reach + its ports + tanks) from cached
    membership.
  - Hose credit routes come from a predecessor tree, O(route length).
  - The bar is ≤ 0.05 ms per tick mean and ≤ 1 ms worst tick. The fixture is FINAL §3.5 plus 3 non-Store tanks, 2 Intake and
    2 Outflow ends, and 1 pouring pump.
- **Edge cases that break naive pooling, and the rule for each:**
  - *Rings:* a component is a set, and there are no directed links.
  - *Two pumps:* they cannot fight; the churn loop is bounded and zero-sum (§3.3).
  - *A tank that is both source and sink:* allowed. A Store tank is a buffer. An Empty tank never receives, and a Fill tank
    never sends to tanks.
  - *A shared tank:* a member of both components, with its stock counted once.
  - *Intake and outflow in the same water:* a bounded circle (§3.6).
  - *A full or blocked Outflow:* the pump falls through to its tanks; a Dump tank waits.
  - *A too-large network:* refused.
  - *A pond round trip:* drawn levels equal poured levels (selftest).
  - *A hose changing liquid:* flushed first (§3.7).

## 5. Candidate models, re-evaluated against the owner's canal case

The owner's new requirement (§0): *"have a pump suck water from a lake and put it in a disconnected canal … Wouldn't even
need to have a tank in the mix really."*

**How clicks are counted:** every gizmo change after building and laying. Building a pump, laying a hose and building a tank
are not counted, but **"+ tank"** marks a use case that needs a tank built for it.

| use case | **H. Free-end roles + pump mover + tank modes (recommended)** | E. Tank modes only (rev 1) | A. Directed hoses (Send/Take along the hose) + pump pass-through | R. Free-end roles + pump only, no tank modes |
|---|---|---|---|---|
| lake → disconnected canal | **2** (Intake, Outflow) | **3 + tank**, and broken: the lake-side nozzle is also an outlet, so the tank pours back into the lake | 2 (Take on the lake hose, Send on the canal hose) | 2 |
| lake → tank | **0** (pump at the water) or **1** (Intake hose) | 0 or 1 (Open) | 0 or 1 | 0 or 1 |
| tank → canal | **2** slow (Dump + Outflow); **2** fast if the pump stands at the canal (Dump + Pour), **3** through a hose | 2 (Dump + Open) | 1 (Send), but it drains every liquid on that side, so it needs a liquid filter (+1) | 2 (pump Pour + Outflow); it drains every tank on the network |
| tank → tank (unload the ship) | **1** (ship tank Empty) | 1 | 1, but the meaning flips with the reel side (A10) | not possible without a second pump trick; ruling #9 has the tank pass liquid only to machines |
| drain a tank to the ground | **2** (Dump + Outflow), or **2** with a pump (Dump + Pour) | 2 | 1 + filter | 2, drains everything |
| stays true when the reel is carried elsewhere | yes (roles name the free end) | yes | no | yes |
| accidental drain of the wrong liquid | impossible (only Dump tanks leave) | impossible | possible without a filter | possible |
| relay chains | role on the reel whose end is free | n/a | needs chain-mode rules (A6) | as H |
| new code beyond rev 1 | world→world pump move; free-end ports; pour restricted to Dump | — | side resolver, filters, chain modes, pass-through | as H, minus tank modes |

**Recommendation: H.**
- It does the owner's canal case exactly as he described it: *"one hose be intake, and another be outflow, and the pump does
  the rest"*, with no tank.
- It keeps one-click tank-to-tank for the tanker raid.
- It keeps every drain explicit (Dump).
- Each knob lives where it is physically true: the free end's role, the tank's job, and the pump's speed.

**The others:**
- **E** fails the canal case.
- **A** solves the canal case but brings back the flip and wrong-liquid problems both reviews found.
- **R** is the simplest, but it gives up tank-to-tank moves and explicit drains. It stays on the card as the lean option.

**Model C (equalising) and model D (directed pumps) stay out,** for the reasons given in rev 1: C cannot fill a ship, and D
is circuit simulation.

## 6. Delta against the code and the FINAL design (build steps, rev 2)

One commit each, in order. Each builds the FlowWorks DLL, passes `run_selftests.py`, and keeps a settings screen.

| # | step | files | change | gate | waits on |
|---|---|---|---|---|---|
| L1 | **Transfer service + conservation fixes** | new `Machinery/RM_LiquidTransfer.cs`; pump, converter, reactor, bath, adapter, `TankFeedTick` | every mutation through `Move`; world leg checked first; adapter read-back; converter pending item output (G6) | refusal-injection selftest per site; caller-coverage lint | nothing |
| L2 | **Components per topology revision** | `RM_LiquidNetKernel.cs`, `RM_LiquidNet.cs`, `RM_HoseLinks` | §3.1, incl. free-end ports; `RM_NetCache` deleted | kernel selftests (tank in two runs, tank–hose–tank, ports, revision bumps, refusal) | nothing |
| L3 | **Fill and draw order, split levels, consumer rotation** | `RM_LiquidNet` plans, all callers | §3.2 | 3 + 2 room takes a level; origin-independent plans | nothing |
| L4 | **Tank modes + settle** | `Building_LiquidTank.cs`; settle in the map component; delete `TankFeedTick`, `FeedTarget`, `TankFeedUnits` | §3.2 | ship Fill/Empty; Empty + Fill + Dump on one component; epoch stock | Q1 |
| L5 | **Free-end roles** | `CompHoseReel.cs` (`rmFreeEndRole`, gizmo), `HoseEnds.cs` | §3.4 | save default Capped; role inert when coupled | Q1 |
| L6 | **Pump as world mover** | `Building_LiquidPump.cs`, `RM_MapComponent_Excavation.cs` (`CanPourLevel`) | §3.3: Intake sources, Outflow-first destinations, world→world move, pour restricted to Dump tanks | selftests: lake→canal with no tank; blocked outflow falls to tanks; pour ignores Store tanks; budget shared across intakes; pond round trip | Q1 |
| L7 | **Outflow ends + Dump gravity drain** | settle + `PickPour` at the end + spill path | §3.5 | live bars `NS_canal_from_lake_no_tank`, `NS_dump_tank_drains_without_pump`, `NS_intake_needs_pump` | Q1 |
| L8 | **Held volume + spill filth** | `CompHoseReel.cs`, `LiquidDef.spillFilth`, generator rows for filth defs | §3.7 (Q2 ruled) | conservation selftest across fill, liquid change and stop; filth in home area gets a Clean job (live) | nothing |
| L9 | **Liquid theft** | transfer service hook, the ruling #7 theft code | §3.4 (Q4 ruled) | selftest: units moved from a non-player tank accrue goodwill debt; notice at couple | nothing |
| L10 | **Adapter modes + boundary** | `CompLiquidPipeAdapter.cs` | §3.10 | save-key mapping; a short accept puts the units back | nothing |
| L11 | **Settings + perf** | `RM_HoseSettings.cs`, `RM_MachinerySettings.cs`, perf probe | `tankModesEnabled`, `tankUnitsPerCycle`, `dumpUnitsPerCycle`, `freeEndRolesEnabled`, `hoseUnitsPerCell`, `unitsPerFilth`; typed registry rows | registry equality; perf fixture §4 | nothing |

**Deleted from code:**
- `RM_LiquidNet.TankFeedTick`;
- `RM_LiquidNetKernel.FeedTarget`, `TankFeedUnits` and `Across`;
- `RM_NetCache` and the per-origin, per-tick walk;
- `tanksFeedHoses`, migrated;
- **pour's "any tank" choice**, now Dump tanks only.

**Deleted from FINAL:**
- step 9, which L6 replaces;
- §3.5's per-tick cache;
- the §3.1 "never crossed from a tank" sentence, restated on components.

**Kept:** the endpoint invariant on components; hose eligibility; crediting at committed moves; lease and tint; the VE/DBH
visual-only rule; one liquid per tank; pump pour mode (Q3).

**For the waiting build agent:**
- L1-L3 and L8-L11 depend on nothing still open.
- L4-L7 wait on Q1. L5-L7 are the same under H and R; L4 is dropped under R.

## 7. Adversarial review (independent opus subagent, 2026-10-11, against draft `bb58eb122`), re-checked against H

Rev 1's dispositions stand, and the last column re-checks each finding under H.

| id | sev | finding | rev 1 disposition | under H (rev 2) |
|---|---|---|---|---|
| A1 | BLOCKER | a tank–tank hose was never crossed (`RM_LiquidNetKernel.cs:142, 176-177`) | ACCEPT: hose is a conductor, tanks attach | holds: unchanged |
| A2 | BLOCKER | walks cannot start at a pipe cell or relay (`RM_LiquidNet.cs:168-194`) | ACCEPT: components | holds |
| A3 | BLOCKER | free nozzles have no representation (`RM_LiquidNet.cs:524-533`) | ACCEPT: nozzle port | holds: free ends with a role are component ports (§3.1) |
| A4 | BLOCKER | pour and draw break conservation on failure (`Building_LiquidPump.cs:157-164, 178-185, 249-259`) | ACCEPT: L1 | holds, and gains the world→world case: check the destination, then take, then pour (§3.3) |
| A5 | MAJOR | free liquid from another faction's tank | ACCEPT: player-only, card | **changed by Q4:** allowed, priced as theft in the transfer service (§3.4) |
| A6 | MAJOR | relay chain on Send moves nothing | argued for E | holds: roles name the free end of the chain's last reel, and nothing along the length is directional |
| A7 | MAJOR | "network" relative to the starting point | ACCEPT: components | holds |
| A8 | MAJOR | an outlet drains every liquid | ACCEPT: only Dump tanks pour | holds, and is extended: pump Pour now drains Dump tanks only (§3.3). The pump's world→world move carries only world water, never tank stock |
| A9 | MAJOR | held liquid under-specified | visual recommended | **changed by Q2:** real, fully specified (§3.7): fill taken from the move, flush on liquid change, never back into a tank, spill as liquid or filth |
| A10 | MAJOR | Send flips when the reel is carried | argued for E | holds: roles describe the free end only |
| A11 | MAJOR | bursty walks, per-tick index rebuild | ACCEPT | holds; the fixture adds ports and a pouring pump |
| A12 | MAJOR | default Connected moots ruling #9 | partly accepted | holds: a tank passes liquid to machines through any hose with no click, and tank to tank takes one click |
| A13 | MINOR | intake adds a dry cell | ACCEPT | holds: Intake adds the source cell |
| A14 | MINOR | retiring pour loses the area picker | ACCEPT | **moot by Q3:** pour is kept, and `PickPour` also serves Outflow ends |
| A15 | MINOR | pond ↔ tank arbitrage | ACCEPT: selftest | reduced: the world→world move is in levels on both sides; the round-trip selftest stays for tank legs |
| A16 | MINOR | adapters churn through a VE net | ACCEPT: start Shut | holds |
| A17 | — | model B hybrid beats A | became E | H keeps E's tank modes and adds free-end roles for the canal case |
| **A18** | MAJOR | *(new, own re-check)* Draw and Pour pumps on one network churn a Dump tank | — | bounded and zero-sum; inspect warns (§3.3) |
| **A19** | MAJOR | *(new, own re-check)* intake and outflow in the same lake | — | bounded circle that burns power; inspect warns (§3.6) |
| **A20** | MINOR | *(new, own re-check)* a blocked Outflow silently fills tanks the player meant to keep empty | — | intended fallback, shown in the pump's status ("outflow blocked: filling tanks"). Cap the Outflow or leave no room to stop it |

## 8. GPT consultation (gpt-6.1-sol, effort high, 2026-10-11, against draft `bb58eb122`)

How it ran:
- **Tool:** `python3 src/RimMandrake/Utils/gpt_consult.py`.
- **Prompt:** `design/RimMandrake/liquid_network_semantics_gpt_2026-10-11/prompt.md`.
- **Files sent (8, 94,860 chars):**
  - the draft design and the 2026-10-11 rulings;
  - `RM_LiquidNet.cs`, `RM_LiquidNetKernel.cs` and `CompLiquidPipeAdapter.cs`;
  - `Building_LiquidPump.cs` and `Building_LiquidTank.cs`;
  - `CompLiquidConverter.cs`.
- **Raw answer:** `design/RimMandrake/liquid_network_semantics_gpt_2026-10-11/gpt_answer.md`.

**Not re-run for rev 2.** H is E plus free-end roles and a world→world pump move, and the consult's findings G1-G14 cover the
mechanisms H uses: components, the transfer service, escrow and pump budgets. The coordinator made a re-consult optional.

| id | sev | finding | disposition |
|---|---|---|---|
| G1 | BLOCKER | define components of conductors with tanks and machines attached | ACCEPT (§3.1) |
| G2 | BLOCKER | directed transfer cannot reuse `Across`/`Walk` | moot under H (no directed links) |
| G3 | BLOCKER | hose contents need typed escrow or an owner ruling | ACCEPT: owner ruled real (Q2); typed escrow §3.7 |
| G4 | BLOCKER | mutation paths assume success | ACCEPT: L1 |
| G5 | BLOCKER | adapter boundary unchecked (`CompLiquidPipeAdapter.cs:136, 155`) | ACCEPT (§3.10) |
| G6 | MAJOR | converter accounting; unplaced item output lost (`CompLiquidConverter.cs:315`) | ACCEPT in part: pending output in L1 |
| G7 | BLOCKER | pump-to-outlet needs reserved world capacity and the full pump predicate | **ACCEPT, now built in:** the owner asked for the tankless move, so §3.3 specifies destination check → take → pour, a shared budget, and the full predicate |
| G8 | MAJOR | fragmentation (`RM_LiquidNet.cs:294`) | ACCEPT: split levels |
| G9 | MAJOR | starvation; same-update forwarding | ACCEPT: rotation, epoch stock |
| G10 | MAJOR | ties, liquid order, liquids without channel forms | ACCEPT: id ties, rotation, spill filth |
| G11 | MAJOR | `Live` misses port changes (`RM_LiquidNet.cs:458, 471`) | ACCEPT: revision bumps |
| G12 | MAJOR | visit cap and quadratic route copies (`RM_LiquidNetKernel.cs:128, 137`) | ACCEPT: full cap, refusal, predecessor tree |
| G13 | MAJOR | migrating pour pumps could start unintended pumping | ACCEPT: pour kept (Q3) but restricted to Dump tanks, and every tank loads as Store, so nothing pours on load |
| G14 | MAJOR | delta understated | ACCEPT: §6 L1-L11 |
| verdict | — | "Choose a corrected A" | not followed. H gives the hose its natural role (what happens at its free end) and avoids A's flip and filter costs. The owner decides on Q1 |

## 9. Owner questions (rev 2)

Q2, Q3 and Q4 are ruled (§0). Q5 is folded into Q1: under every option an Intake end works only through a working pump on
its network, which is ruling #3.

**Q1 (revised). How does the player tell liquid where to go?**
- **(a) Hose ends plus tank jobs (recommended).** A hose's loose end is set to Intake, Outflow or Capped, and the pump moves
  everything that comes out of the world. Tanks get Store / Fill / Empty / Dump.
  - Lake → canal: 2 clicks, no tank.
  - Unload the ship: 1 click.
  - Drain a tank to the ground: 2 clicks (Dump plus an Outflow; add a pump on Pour to make it fast).
  - Trade: a setting never flips when you carry a reel around, and only a tank you marked Dump can ever be drained.
  - Cost: two kinds of setting (hose end and tank).
- **(b) Hose ends and pumps only, no tank jobs.** As (a) without the tank settings.
  - Lake → canal: 2 clicks.
  - Trade: the fewest buttons.
  - Cost: no tank-to-tank moves (unloading a ship needs a pump trick), and a pouring pump drains every tank on its network.
- **(c) Direction along the hose.** Each hose is Connected, Send or Take, and the pump pushes through.
  - Lake → canal: 2 clicks.
  - Trade: one kind of setting.
  - Cost: "Send" means the opposite when the reel is at the other end, and draining one liquid needs a liquid picker on the
    hose.
- **(d) Tank jobs only (rev 1).**
  - Trade: one kind of setting.
  - Cost: lake → canal needs a tank in between, and the lake-side hose would pour back into the lake. This fails your canal
    case.
