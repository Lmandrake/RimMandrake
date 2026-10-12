# Natural bodies of water as filled canals — feasibility, gotchas, conservation tests (2026-10-11)

Item: `POND_BED_DESIGN_LAKES_ARE_TALL_CANALS` (BENCH). Design only: no C# or defs were touched.
Offline test written: `src/RimMandrake/FlowWorks/northstar/selftest_conservation_roundtrip.py` (10 round trips, PASS;
picked up by `run_selftests.py`). GPT review: `natural_bodies_as_canals_gpt_review_2026-10-11.md`; its dispositions are
the last section here.

The owner's ask (verbatim, 2026-10-11): *"please do a deep design dive on the feasibility of natural bodies of water
becoming the same thing as filled canals … Start with A filled, then move it into tanks, then move it into empty
reservoir B of a bigger size. Then drain B back into the tanks and back into A... and A looks the same. … looking for
gotchas both in the expansion of the concepts as well as NOT expanding them."* Earlier: *"what's left after the pond is
drained? It kind of should be a lowered area of ground just like would be required to hold the water on the other side,
right? So it would be a ~circular (pond-shaped) depressed region of emptiness that would then be filled again if the
water were returned."*

---

## Summary (one screen)

**Today a pond and a canal are two different kinds of thing that only pretend to be the same.** A canal is integer
levels in a dug cell (depth D 1–4, fill F 0–D, bytes). A pond is one decimal-number stock for the whole body. Its
budget is 5 levels per cell, but the code reads every pond cell as "depth 4, full". When the stock falls, cells become
flat **Mud at ground level**. They do not become a hollow.

**The owner's round trip works for dug reservoirs and fails for a natural pond, at the very last step.**
- Dug A → tanks → bigger dug B → tanks → dug A: **exact**. Every leg moves whole levels: 1 level = 5 tank units, and
  tanks hold whole units. A full A comes back identical.
- A half-full A comes back with the **same amount of water in a different shape**. The engine moves water to a deeper
  cell or out of a brimming one. It never evens out partly filled cells of equal depth.
- **Natural A: nothing can put water back into a pond.** A pump pours only into dug cells. An outflow end refuses
  water terrain, and on the dry Mud it makes a spill (filth). So the water either waits in the tanks or is lost as
  filth, and A refills only from seepage and rain. The existing C# selftest `Pump_pond_round_trip_conserves` passes only because it pours
  back through a hand-written `pond++` that the game does not have (MEASURED, below).
- **"Equal volume" is not equal.** A natural cell is worth 5 levels (the 5:1 budget), but the deepest dug cell holds 4.
  So a 25-cell pond drained into a 25-cell pit leaves 25 levels with nowhere to go.
- Fractional water lives in the pond stock (and in the rain carry-over between pulses). Seepage and rain add fractions
  to the stock. A fraction below
  one level stays visible as one wet cell that no pump can draw.

**Recommendation: Option B, "the pond keeps its bed".** A receded pond cell becomes a hollow (a dry bed whose depth
comes from the terrain recorded before it dried), not flat mud. Any way water can enter a dug cell (pump, outflow, rain,
a canal running back) can also refill the pond's stock. The pond stays one decimal-number reservoir, so oceans, rivers
and big lakes cost nothing. We do **not** rebuild every lake as canal cells (Option C). That would cost us vanilla
fishing (Odyssey's water bodies follow base terrain), the lake art, and the speed on big lakes. All of that buys a
"same thing" the player cannot see. First, fix the not-expanding gotchas G1–G7 (Option A). They bite whatever we choose.

---

## 1. The current model, precisely

| quantity | type | unit | where |
|---|---|---|---|
| canal depth D | `byte` 0..4 | level | `RM_MapComponent_Excavation.depthGrid` (:45); `RM_ExcavationDepth.MaxDepth = Superdeep = 4` (RM_ExcavationDepth.cs:38-40) |
| canal fill F | `byte` 0..D | level | `fillGrid` (:48), clamped on read (`FillAt` :586-599) |
| natural cell D/F | not stored; **read through** as 4/4 | level | `DepthAt`/`FillAt` (:567-599), `IsSourceCell` = base terrain `IsWater` at D=0 (:544-559) |
| body stock, capacity | `float` | fill-unit (= `volumePerTile`, 1 for every shipped fluid) | `RM_LiquidBody.stock/capacity` (RM_LiquidBody.cs:37-40) |
| body capacity | `cells × canalCellsPerSourceCell(5) × volumePerTile(1) × budgetMultiplier` | fill-unit | `RM_StockMath.BodyCapacity` (RM_StockMath.cs:63-70); set full at formation (RM_LiquidStock.cs:165-170) |
| tank contents | `int storedUnits`, cap 300 × multiplier | tank unit | `Building_LiquidTank.cs:65-69` |
| level ↔ tank units | 1 level = **5** units | — | `RM_PumpMath.TankUnitsPerLevel` (RM_PumpMath.cs:13); ladder bottle 1 / bucket 5 / barrel 25 (`flowworks_mod_definition.md` §5a) |
| hose held volume | `int heldUnits` | tank unit | `RM_LiquidSpill.DrainHeld` (RM_LiquidSpill.cs) |
| rain into canals | `float rainAccumulator`, released in whole levels | level | `ApplyRain` (RM_MapComponent_Excavation.cs:~1391-1415) |
| refill of a body | `float`, per pulse, clamped to capacity | fill-unit | `RM_LiquidStock.Refill` (:329-353), `RM_StockMath.RefillPerDay/RefillForPulse` |

**Transfer legs, each in whole levels:**
- Flow pulse: a source donor costs `TryDebitLevel` = `TryDebit(volumePerTile)`. A dug donor gives −1 and the recipient
  gets +1 (`RM_FlowKernel.ResolveComponent` :320-360). A per-component check (before vs after, :255-382) tests each pulse.
- Pump draw from a body: `TryDebit(volumePerTile)` adds +5 tank units (Building_LiquidPump.cs:352-357). Pump draw from a
  canal: `TryTakeLevel` adds +5 units (:337-345).
- Pump pour: −5 units, then +1 level into the **dug** cell in reach with the most room (`TryPour`, :378-456;
  `RM_PumpMath.PickPour`).
- Outflow end: `RM_LiquidSpill.Outlet` takes a dug cell that has room. **Water terrain is Blocked.** Dry standable
  ground takes the water as a **spill (filth)**, which never turns back into liquid (RM_LiquidSpill.cs:26-58).
- World-to-world move (tankless): the source take can be undone with `TryCredit` (Building_LiquidPump.cs:315).
- Fill-in displacement: `F-(D-1)` levels go first to channel cells and then to the body through `CreditLevels`. Only
  whole levels are credited. Whatever finds no room is **destroyed and disclosed** (`Displace`/`ReportOverflow`,
  RM_MapComponent_Excavation.cs:~770-912).

**Where volume legitimately enters or leaves:**
- Enters: a limitless body (a flag, not a number), refill (seepage × rain × season), rain into canals, debug fills.
- Leaves: edge sinks (`sinkTransferredTotal`), burning (`BurnOffLevel`), fill-in overflow (`overflowDestroyedTotal`,
  the one sanctioned loss), spills becoming filth, hose drain off-map (logged).
- There is **no map-wide ledger** that sums bodies + canals + tanks + hoses. The checks are per component per pulse
  (kernel) and per move (`RM_LiquidTransfer.Move`, :152-179). A leak *between* systems shows up nowhere.

**Recession and restore.**
- Recession works from the outside in. The tests run in this order: cells feeding a channel go last, then cells with the
  fewest same-body neighbours, then the farthest from the centroid, then cell index. A cell whose removal would split
  the body is passed over. At most 64 cells move per pulse (RM_LiquidStock.cs:385-472).
- `DryNaturalCell` records the original terrain (the first record wins) and writes `FluidDef.recededTerrain`, which is
  vanilla **Mud** for every shipped fluid, at **D = 0** (RM_MapComponent_Excavation.cs:1024-1047).
- Restore pops the receded list last-in-first-out and writes the recorded terrain back. It skips, and **forgets**, a
  cell that has been dug since (RM_LiquidStock.cs:589-622).

**Limitless** is sticky, set at formation. It applies when the body is truncated (more than 4000 cells), or when it
touches the edge and has at least `MinLimitlessBodyCells` cells (RM_StockMath.cs:87-94). A limitless body is never
debited and accepts any credit (:355-371).

**Saves.** Bodies are scribed whole: id, limitless, stock, capacity, truncated, fluid, cells, receded
(RM_LiquidBody.cs:79-100). The original-terrain dictionary, the overflow, sink and rain totals and the grids are all
scribed (RM_MapComponent_Excavation.cs:418-440).

---

## 2. Gotchas of NOT expanding (bugs in today's design that bite whatever we choose)

Labels: **MEASURED** = read directly from the cited code; **INFERRED** = follows from code plus engine behaviour not yet
run live.

**G1. A natural body has no inflow except seepage, rain and fill-in displacement. MEASURED.**
- `TryPour` keeps only cells where `IsExcavated` is true (Building_LiquidPump.cs:413-420).
- `CanPourLevel` requires `IsExcavated` (RM_MapComponent_Excavation.cs:1138-1148).
- `Outlet` returns Blocked on water terrain, and on the receded Mud it returns **Ground**, which is a spill
  (RM_LiquidSpill.cs:52-57).
- The flow kernel never credits a source: sources are donors only (RM_FlowKernel.cs:341-351).

Consequences:
- The owner's trip cannot finish with a natural A. The water either waits in the tanks (a direct pump Pour over the bed
  stalls) or becomes filth (an Outflow end over the Mud bed). It does not come back as water.
- Pumping into a dried pond bed makes **filth**, not water.
- A canal brim-full beside a pond never runs back into it.

**G2. The C# selftest claims a pond round trip the game cannot do. MEASURED.** `PumpChecks.cs:97-109`
(`Pump_pond_round_trip_conserves`) pours back with `RM_TransferLeg.World(k => true, k => { pond++; ... })`, a path that
no production call has. The live criterion `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` A4 ("pond round trip conserves units")
inherits the same false comfort. Fix: point the case at production (`TryPour` against a body), or mark it plainly as a
model of a leg that does not exist yet.

**G3. A drained pond is flat Mud at ground level, not a hollow. MEASURED.** `recededTerrain` = Mud and D stays 0
(FlowWorks_Fluids.xml:38; `DryNaturalCell`). The owner's mental model (*"a ~circular (pond-shaped) depressed region"*)
breaks in several ways:
- A colonist walks across the bed at grade.
- The bed is not a pit, a trap or a room boundary.
- Rain falling on it is not caught (`ApplyRain` walks dug cells only).

Vanilla Mud has the affordances Walkable, Bridgeable and WaterproofConduitable, path cost 14, and `driesTo` Soil (vanilla
def, MEASURED). So walls and floors cannot be built on it, but **bridges can**, and anything can go on a bridge.

**G4. Refill writes water over whatever stands on the bed. MEASURED for the write, INFERRED for its effects.**
`Restore` does not check pawns, items, plants or buildings (RM_LiquidStock.cs:608-621). Vanilla
`TerrainGrid.DoTerrainChangedEffects` destroys plants that fail fertility, plus blueprints and frames. It leaves
**pawns, items and built things where they are** (vanilla, MEASURED). Results:
- A pawn on a cell that refills as deep water is standing in impassable terrain.
- Items sit underwater.
- A building on a bridge stays, which is correct.
- A plant growing on the bed dies.

**G5. Digging a dried bed and then filling it back in makes lake water out of shovelled earth. MEASURED path.**
1. `DryNaturalCell` records the water terrain first.
2. `Deepen` records only on the surface → dug transition, and the first record wins. So the record stays water
   (RM_MapComponent_Excavation.cs:612-621, 920-937).
3. `Restore` drops the dug cell from `receded` without restoring it (RM_LiquidStock.cs:610-618).
4. Later `FillIn` to the surface calls `RestoreOriginalTerrain`, which writes **water** back. The cell is a source
   again, its stock is unpaid, and the next pulse recedes it again.

No volume is created (the stock is unchanged), but the player sees a fill-in produce water and then flicker. The fix is
small: when a receded cell is first dug, re-record its original terrain as the bed (receded) terrain.

**G6. "Equal volume" mismatch: 5 levels per pond cell vs 4 per deepest canal cell. MEASURED.** Capacity uses
`canalCellsPerSourceCell = 5`, while the read-through depth is 4. Any design that equates a pond cell with a canal cell
gains or loses 20% somewhere. Trip 7 of the selftest quantifies it: a 25-cell pond holds 125 levels and a 25-cell
superdeep pit holds 100. This is an owner decision (§6, Q2), not a bug to fix silently.

**G7. Water outside our books.** Several things change water without passing through our accounts. They create or lose
nothing, but they make the books lie.
- **MEASURED that it exists, INFERRED that it interacts:** vanilla's moisture pump (`CompTerrainPumpDry`) dries water to
  its `driesTo` terrain and Mud to Soil.
  - On a body cell, it leaves the body's `cells`, `capacity` and stock unchanged. The stock then sits on fewer visible
    cells and can still be fully drawn.
  - On a receded cell, Restore later writes water over the dried soil anyway.
  - Other terraforming mods do the same.
- **INFERRED:** fishing interacts too. Odyssey's `WaterBodyTracker.Notify_TerrainChanged` drops a receded cell from the
  vanilla water body and re-adds it on restore, and the fish population is per water body. Draining a pond and letting
  it refill may reset or lose its fish. This needs a live row.

**G8. A remainder smaller than one level is stranded. MEASURED.**
- `CanSupply` needs `stock ≥ volumePerTile`, while `recedeKeepsLastCell` keeps one cell wet while `stock > 0`
  (RM_StockMath.cs:164-172, 332-335).
- After a season of seepage, a pond can show one wet cell holding 0.4 that no pump can draw.
- Harmless for conservation. Confusing on screen.

**G9. Float stock and saving. CORRECTED by GPT #20.**
- `Scribe_Values` writes floats with `G9`, which round-trips a float32 exactly, so saving loses nothing.
- The real float risks are float32 accrual (seepage added every pulse), the `floor(stock / perCell)` thresholds, and
  `capacity - stock` subtraction.
- A live row compares with a tolerance sized to the stock's magnitude (float32 epsilon × stock × pulses), never `==`.

**G10. No map-wide ledger. MEASURED (absence).**
- The pulse ledger covers a component within one pulse.
- `Move` covers one transfer.
- Nothing asserts "bodies + canals + tanks + hoses + destroyed + sunk + burned + spilled − refill − rain − limitless
  draw = constant" over time, so a leak *between* subsystems is invisible.
- A cheap fix: a debug/bridge probe that prints the totals (§5, live row L0).

**G11. Limitless by truncation. MEASURED.** An inland lake larger than 4000 cells counts as limitless even when it
touches no edge (RM_LiquidStock.cs:27, RM_StockMath.cs:93). It is rare on a 250² map, but it is an ocean rule applied to
a lake.

**G12. Odds and ends. MEASURED.**
- The bed's look is generic Mud. A tar pond or a slime pond also recedes to Mud (every shipped FluidDef says Mud). The
  player cannot see that this was a tar pit.
- `DryNaturalCell` writes `recededTerrain` through `SetTerrain`. That replaces the base terrain for good, and the record
  is the only way back. **Deleting the `originalTerrain` dictionary (a bad save, a mod removal) launders every dried
  pond into Mud.**

---

## 3. Feasibility: what "a pond is a filled canal" would have to mean

Each item below is a part of the system the design must answer. The last column says which option answers it.

| aspect | question | answer and option |
|---|---|---|
| bed depth | what D does a dry pond cell have? | From the recorded original terrain: shallow water (WaterShallow, WaterMovingShallow, Marsh, ocean shallow) → **D 2**; deep water (WaterDeep, WaterMovingChestDeep, ocean deep) → **D 4**. Derivable from `originalTerrain`, which existing saves already hold. Table proposed, not ruled (Q3). |
| shape | does the hollow keep the pond's outline? | Yes: the footprint `cells` is fixed at formation. |
| volume per cell | 5 (budget) or D (geometry)? | Q2. B keeps 5 and treats the bed as "D 4 plus the off-cell budget". C must pick one. |
| filling and draining | who moves water in a pond? | B: the stock does, and the bed takes any inflow a dug cell would (pump, outflow, rain, canal backflow, displacement), credited to the stock. C: the canal kernel, cell by cell. |
| refill | seepage and rain | B: unchanged (a source term on stock). C: a source term that adds levels into the bed cells, deepest first. |
| "limitless" | oceans, rivers, edge lakes | B: unchanged sentinel. C: cannot be cells (a 40,000-cell ocean in the kernel every pulse); stays a sentinel, so C is never "all water is canals" anyway. |
| when converted | map gen or lazy | Lazy at first contact (formation already is). Map-gen conversion of every lake on every map buys nothing and touches every save. |
| performance | big lakes and rivers | B: the same cost as today's recession, which is NOT O(changed cells). Recede rebuilds the live set and rescans it per pick, about O(64·n); Restore scans the footprint every pulse (GPT #22). It is per body, so many limited bodies add up, and a benchmark is owed. C: the kernel walks every connected wet cell every pulse (cap `MaxComponentCells` 6000); a 4000-cell lake joined to a canal network is a large standing cost. |
| pathing in a dry bed | at grade or a pit? | B and C: the bed reads `DepthAt` = D, so the existing depth path costs, ladders and pit rules apply. A D 4 bed is a trap until refilled. **A dried deep lake becomes a giant superdeep pit.** That needs a design answer (Q4). |
| things in the bed at refill | pawns, items, plants, buildings | Must be decided (G4). Proposed: refill skips a cell holding a pawn or a non-bridge building and retries next pulse. Items get pushed to the shore, or are left to drown as vanilla items do in shallow water (Q5). |
| vanilla keyed on water terrain | fishing (Odyssey), moisture pumps, bridges, terrain affordances, fire, temperature, freezing, swimming and wading | B keeps base water terrain on wet cells, so vanilla systems see real water. C, if wet cells become channel terrain plus temporary fill terrain: vanilla `WaterBodyTracker` keys on terrain `waterBodyType`, so fishing disappears unless every fill terrain carries a water body type (and then a canal becomes fishable too); ice and freezing read `BaseTerrainAt(...).canFreeze` (WaterBody.cs:218) and would stop. |
| other mods | VE pipes, Dubs hygiene wells, Water Freezes etc. | B: invisible to them (water stays water). C: anything reading `TerrainDef.IsWater` loses every converted lake. |
| save compatibility | existing `RM_LiquidBody` saves | B: additive, since bed depth derives from `originalTerrain`; no new scribed field is needed for existing receded cells. C: a one-time migration that writes grids from bodies; irreversible. |
| Mod Settings (every mod ships superb ones) | — | B: "Drained ponds leave a hollow" (on), "Pumps and outflows can refill natural ponds" (on), "Bed depth: shallow water → D" slider (1–3, default 2), "Refill waits for the bed to be clear" (on). All off → today's behaviour. |

---

## 4. Options

Four options, each answering a different question.

### Option A — Don't expand; fix today's gotchas (the floor every option needs)
- What it is: G1's return leg (pour or outflow into a body cell or a receded cell credits the stock, whole levels, only
  up to capacity), G2's honest selftest, G4's refill guard, G5's re-record on dig, a map-wide ledger probe (G10), and
  the stranded remainder shown in the inspect text (G8).
- Gains: the owner's round trip works for natural ponds. "A looks the same" is exact, because recession and restore
  are deterministic and last-in-first-out (trip 6 flips to a full round trip once the leg exists).
- Costs: the bed is still flat Mud, so the owner's "depressed region" stays unbuilt.
- Size: small, and FOUNDRY-shaped (2–3 files).

### Option B — The pond keeps its bed (recommended)
- What it is: Option A, plus a receded pond cell reads a non-zero depth derived from its original terrain. `DepthAt`
  returns the bed depth and `FillAt` returns 0 (empty bed). The stock stays the one float. A refill re-wets cells last
  in, first out.
- Gains:
  - The drained pond becomes the hollow he described. Pathing, ladders and pit rules apply.
  - Rain, pumps, outflows and canal backflow can refill it. All of them credit stock.
  - Oceans and rivers are unchanged. Vanilla sees real water wherever it is wet.
  - No migration: existing saves derive bed depths from records they already have.
- Costs:
  - A hybrid: a pond is still not cell-by-cell canal water, so a half-full pond shows as "some cells full, the rest
    dry bed", never "every cell half full". That matches how recession already looks.
  - A dried deep lake is a vast superdeep pit (Q4).
  - Bed terrain art is needed (or reuse `RM_Channel_*` at the bed depth).
- Size: medium.

### Option C — Full unification, lazy (a pond becomes dug cells on first contact)
- What it is: at formation, write D from terrain and F = D into the grids. Original terrain is recorded. The kernel
  owns the water from then on. Refill is a source term. Limitless stays a sentinel (it has to).
- Gains: truly one model: per-cell partial fills, the owner's "same thing" literally true, one conservation ledger.
- Costs:
  - Vanilla identity lost on converted lakes: fishing, freezing, `IsWater` readers, the lake's own art.
  - The kernel's physics is "fill deepest first", not a level water surface, so a big lake drained from one side looks
    wrong.
  - Performance on joined lakes. The 5-vs-4 volume decision is forced.
  - An irreversible save migration. Rivers and oceans stay different anyway, so "everything is canals" is never true.
- Size: large.

### Option D — Unify only small ponds (C below a size threshold, B above it)
- Gains: per-cell realism where the player watches it most (a 20-cell pond), and bounded cost.
- Costs: two models plus a threshold the player cannot see, and vanilla fishing differs between a small pond and a big
  one. Only worth it if B tests badly with him.

**Recommendation: A now, then B.** A is the precondition for every option, and it fixes a false test. B gives the
owner's two asks (a drained pond is a hollow; returned water refills it and it looks the same) at the lowest risk to
vanilla and mods. C's extra fidelity (per-cell partial fill inside a pond) is the only thing B lacks, and it is the
least visible part.

---

## 5. Conservation test plan

### Offline (runs now, no game): `src/RimMandrake/FlowWorks/northstar/selftest_conservation_roundtrip.py`

The model's constants are read from production: `TankUnitsPerLevel`, `Superdeep`, and the water FluidDef's
`volumePerTile` and `canalCellsPerSourceCell`. It detects from the source text whether a pour-into-body leg exists, and
trip 6 flips from "documents the gap" to "demands the full round trip" when one lands. Current output: **PASS 10/10**.

| trip | what | result today |
|---|---|---|
| 1 | dug A 5×5 D4 full → 2 tanks → dug B 8×8 → tanks → A | exact; A identical |
| 2 | equal volumes, one tank, several runs | exact |
| 3 | half-full flat A, pump reach 4 cells | volume exact, **shape different** (no levelling below the brim) |
| 4 | sloped bowl, 40 levels | volume exact; shape same (fills deepest first both times) |
| 5 | B smaller than the load | pour stalls; the remainder waits in the tanks; nothing lost |
| 6 | natural A (20 cells) → tanks → B → tanks → A | **gap**: 500 units stranded in the tanks (G1) |
| 7 | 25-cell pond → 25-cell D4 pit | 25 levels have nowhere to go (G6) |
| 8 | seepage remainder below one level | one wet cell that cannot be drawn (G8) |
| 9 | float stock written as text | 7-digit text drifts about 4e-5 (G9) |
| 10 | limitless draw | never runs out; tanks fill |

**C# SelfTest additions (when FOUNDRY is out of the pump files; not written now because those files are being edited):**
- `Pump_pond_round_trip_production`: drive `TryDraw` and `TryPour` against an `RM_LiquidStock` fake. It must FAIL today
  (G1) and PASS after Option A.
- `Stock_recede_restore_is_lifo_exact`: debit N, credit N, and assert the same wet set (pure `RM_StockMath` plus a list
  model).
- `Displace_receded_dug_cell_does_not_make_water` (G5).

### Live rows (BENCH runs these; the bridge tools exist: `jawa/flowworks_body_report`, `jawa/flowworks_excavation_report`, `flowworks_excavation_drive`)

Settings for every row: `refillEnabled = false`, `rainFillsExcavationsEnabled = false`, weather clear, edge sinks off,
fire none. The test is conservation, not weather.

- **L0 ledger probe** (needed first, G10): a debug action or bridge call that prints the sum of body stocks (limited),
  the canal levels, the tank units, the hose held units, and the destroyed, sunk, burned and spilled totals. Each row
  records it before and after; PASS when the total change is within 1e-3.
- **L1 dug round trip (owner's trip, dug):** dig A 5×5 D4 and fill it from a limitless edge body. Dig B 8×8 D4. Set up
  a pump plus 2 tanks between them (Intake in A, Outflow to B, then reverse). Run until idle. PASS: A's per-cell F
  matches the snapshot, B is empty, the tanks hold 0, and L0 is unchanged.
- **L2 half-full trip:** as L1 with A at F = 2. PASS on L0. Record A's per-cell F as evidence, since a shape difference
  is the expected finding until levelling is decided.
- **L3 natural pond trip:** plot D's limited pond (about 20 cells): drain into tanks, tanks into a dug B, back into
  the tanks, then Outflow toward the pond. **Today: expected FAIL ("water stays in the tanks; the bed takes a spill"),
  labelled a MOD finding for G1.** After Option A it must PASS, with the pond's wet set equal to the snapshot.
- **L4 save/load mid-trip:** do L1 and L3 with a save and reload after the tanks fill. PASS: L0 is unchanged within
  1e-3, and body stock and receded list are equal before and after the reload.
- **L5 limitless endpoints:** draw from an edge lake into tanks, then outflow back toward it. Today the outflow is
  blocked. Record it.
- **L6 refill over things:** drain plot D's pond. Stand a colonist, drop an item and plant a crop on receded cells, then
  turn refill on and accelerate. Record what happens (G4) and attach a screenshot.
- **L7 fishing (Odyssey):** on a pond of at least 75 cells (smaller ones have no common fish, GPT #15), read the fish population and fishing zone, drain it, refill it, and read them again (G7).

---

## 6. Owner decisions (question-card ready)

1. **Should a drained pond leave a hollow you can fall into, or flat mud?** Hollow: the bed takes back water and works
   like a dug pit. Flat mud: today's behaviour; simpler, but the pond cannot be refilled by hand.
2. **How much water is one pond square worth?** 5 levels (today): ponds stay generous, but a pond never fits exactly
   into a dug pit of the same size. 4 levels: pond and pit match exactly, but every pond holds 20% less than today.
3. **How deep is the hollow a drained pond leaves?** Shallow water → 2, deep water → 4 (proposed). Or everything → 4,
   which is simpler but makes every dried pond a trap. Or shallow → 1, which can be walked out of.
4. **A dried-up deep lake would be a giant trapping pit. OK?** Yes, it is a feature (raiders fall in). Or no: a dry
   bed is never a trap, only slow ground. Or traps only at the deepest middle cells.
5. **What happens to things standing in the bed when the water comes back?** Water waits until colonists and buildings
   are clear (items wash to shore). Or water comes back anyway, as nature does (pawns swim out; items sit underwater).

---

## 7. Dispositions of the GPT review (`natural_bodies_as_canals_gpt_review_2026-10-11.md`, gpt-6.1-sol, 26 points)

| # | point | disposition |
|---|---|---|
| 1 | A now, B conditionally; "no migration" unproved | **ACCEPT.** B is gated on #9 (ownership) and #10 (records) being designed first. |
| 2 | G1: an Outflow over the Mud bed turns the water into filth, so it is not "stranded" | **ACCEPT**, G1 and the summary corrected. The water is lost as a spill, which is worse. |
| 3 | dug round trip: production draws locally; equal-depth flow can stall; recession does not spare pump reach | **ACCEPT** as a test limit (model LIMITS docstring). Live L1 is the real proof. Sparing pump-reach cells in recession is added to Option A's list. |
| 4 | G6 is deliberate virtual storage; 5→4 loses 20%, 4→5 gains 25%, 5→D2 loses 60% | **ACCEPT.** Q2 and Q3 carry it, and a B bed depth of 2 must not resize the stock. |
| 5 | `TryCredit` accepts partial amounts, so a partial credit plus a tank rollback creates water | **ACCEPT, top priority for Option A.** The return leg must accept whole levels or nothing, through `CreditLevels`. Today the only `TryCredit` caller is the world-to-world undo, right after a debit, so it is latent. |
| 6 | credit APIs take no `FluidDef` | **ACCEPT.** The return leg rejects a foreign fluid before any change (Displace already checks the body's fluid). |
| 7 | hoses hold volume; off-map `DrainHeld` does not count | **ACCEPT** for the L0 ledger (hose held units go in it). The off-map drop is disclosed in the log, not counted, and is noted for the ledger item. |
| 8 | refill runs before recede/restore; recession off hides credits; bed rain could be counted twice | **ACCEPT.** Under B, rain on a bed cell goes to stock ONLY, never to both `ApplyRain` and Refill's rain term. |
| 9 | B ownership contradiction: a derived `DepthAt` vs `IsExcavated` | **ACCEPT, design blocker for B.** A bed cell needs its own predicate (`IsNaturalBed`): every receiver that takes water into a dug cell must route bed cells to the stock, and Restore must not treat them as dug. One owner per drop of water. |
| 10 | the G5 fix loses lake provenance; capacity of a removed bed cell | **ACCEPT.** Keep two records, natural-bed and excavation. Digging a bed cell takes it out of the body's footprint and capacity. That needs an owner card (it shrinks the pond). |
| 11 | Restore does not check that it succeeded | **ACCEPT** for Option A: pop only after a verified write. |
| 12 | G4's guard can deadlock the LIFO | **ACCEPT.** Use skip-and-requeue, never block the stack. Q5 stays with the owner. |
| 13 | terrain layers: floors and foundations | **ACCEPT.** "Anything can go on a bridge" is read as "bridges can be built; what goes on them follows vanilla rules". |
| 14 | moisture pumps: phantom storage, terraforming reversed | **ACCEPT** as an open design point: external drying should remove that cell's capacity and stock share and give up its restore rights. Filed under G7. |
| 15 | fishing: removal deletes zones and rerolls population; common fish need at least 75 cells | **ACCEPT.** L7 must use a pond of 75 cells or more. Raised from INFERRED to "likely". |
| 16 | freezing: `TerrainAt` vs `BaseTerrainAt` at formation | **OPEN.** Add a live row for draining and refilling a frozen pond. |
| 17 | C: `waterBodyType` on temporary fill terrain is insufficient (`GetWaterBodyType` reads under it) | **ACCEPT.** C's compatibility note was too optimistic, which strengthens the case against C. |
| 18 | settings bypasses (budget off, unknown bodies debit freely) | **ACCEPT** for the L0 ledger: with the budget off a pond is a free source, and that is stated. |
| 19 | cells added to a truncated body's index are not persisted | **ACCEPT, new bug** (RM_LiquidStock.cs:139-146 vs :70-88), filed with Option A. It affects only bodies over 4000 cells, which are limitless, so no volume leaks, but re-walks cost time. |
| 20 | G9 wrong: Scribe uses G9 | **ACCEPT**, G9 corrected and model comment fixed. |
| 21 | ledger normalisation (`volumePerTile`, read-through excluded, static `SpilledUnits`) | **ACCEPT** as the L0 spec. |
| 22 | performance claim wrong | **ACCEPT**, §3 corrected. |
| 23 | C/D migration double-counts | **ACCEPT.** C is not recommended. |
| 24 | gap detector matched syntax and could match the call site | **ACCEPT, fixed.** It anchors on the `private string TryPour()` declaration, strips comments, and refuses to run if the declaration is missing. |
| 25 | the model's `move` ignored a failed tank removal | **ACCEPT, fixed.** It now needs one tank that can provide a whole level, as production's Store leg does. |
| 26 | trip 4 actually started with 5 levels, not 40 | **ACCEPT, fixed.** It now pours 40 real levels with pulses between and asserts it. Still PASS, shape SAME. |

**Net change to the recommendation:** still A then B, but Option A grows:
1. An atomic whole-level, fluid-checked return leg (#5, #6).
2. Recession spares pump-reach cells (#3).
3. A checked Restore (#11).
4. A skip-and-requeue refill guard (#12).
5. Truncated-body index persistence (#19).
6. The L0 ledger with GPT's normalisation (#21).

B now has a named blocker, the bed-cell ownership predicate (#9), and an owner question about whether digging a bed
shrinks the pond (#10).

## Owner rulings — by question card, 2026-10-12 00:38–00:45 PDT

1. **Direction:** fix today's model first (Option A), then hollow beds (Option B).
2. **Drained pond leaves:** a hollow shaped like the pond.
3. **Bed depth follows the water:** shallow water → depth 2, deep water → depth 4.
4. **Trap pit:** his write-in, verbatim: *"It should be yes to all deep but there is a wrinkle. A deep ditch shouldn't stop you from climbing one or two levels higher but by bit. So if there is a gradual change of height then the player should be able to simply walk out even a deep pit. Please do a design pass about this. I am loathe to make a whole elevation grid concept but it feels like we're heading towards that. Assess how hard it would be to handle this in the game. Is this not so bad or utterly devastating new development to have characters trapped in pits that are "relatively deep" rather than an absolute approximation. If it's too terrible, we will have to make some approximations and limitations. Suggest several alternatives and ask got while you're at it. Natural ponds and lakes when pumped dry would leave just such gradual terrain so no chance to fall in and get stuck. But then we have the same issue when players dig wide gradual pits too."* → design pass `design/RimMandrake/relative_depth_climb_design_2026-10-12.md`.
5. **Refill over an occupied bed:** water waits for people and buildings; items wash ashore.
6. **Digging a dry bed:** the dug square leaves the pond, and filling it back in restores it to the pond (bookkeeping per square; the existing "filled-in bed brings lake water back" bug must be fixed as part of this).
7. **Volume per pond square:** depends on the water — shallow 2 levels, deep 4 (matches the bed depths, so a refilled pond returns to its exact shape).

## 8. One volume per square — design (owner ruling 2026-10-12)

Owner, verbatim (2026-10-12): *"1 tank square, 1 deep water square/pond, 1 deep canal square should all be the same
volume. Right now that's 4 I believe."* It extends ruling 7 above (shallow pond square 2 levels, deep 4).

### 8.1 What the code does today (MEASURED 2026-10-12, read from source)

| thing | levels | tank units | where |
|---|---|---|---|
| 1 level | 1 | **5** | `RM_PumpMath.TankUnitsPerLevel = 5` (Source/RM_PumpMath.cs:13); `volumePerTile` = 1 for every shipped fluid (FlowWorks_Fluids.xml:26, FlowWorks_PitFluids.xml:19) |
| deepest dug canal square | **4** | 20 | `RM_ExcavationDepth.Superdeep = 4`, `MaxDepth = Superdeep` (Source/RM_ExcavationDepth.cs:38-40) |
| natural pond square (any depth) | **5** | 25 | `canalCellsPerSourceCell = 5` for every fluid (FlowWorks_Fluids.xml:35 etc., FlowWorks_PitFluids.xml:22 etc.; C# default FluidDef.cs:91, RM_LiquidStock.cs:32); capacity = cells × 5 × volumePerTile × budgetMultiplier (RM_StockMath.cs:55-70). Ruling 7's 2/4 split is **not built**. |
| `RM_LiquidTank` (2×2) | 60 total, **15 per square** | 300, 75 per square | `BaseCapacityUnits = 300` (Source/LiquidTypes/Building_LiquidTank.cs:36, :67-69); size (2,2) (Defs/LiquidTypes/ThingDefs/RM_LiquidTank.xml:41) |
| `RM_UniversalCargoTank` (2×2) | 120 total, **30 per square** | 600, 150 per square | `baseCapacityUnits 600` (Defs/Machinery/RM_LiquidLogistics.xml:115); size (2,2) (:87) |
| barrel / bucket / bottle (base) | 5 / 1 / 0.2 | 25 / 5 / 1 | RM_LiquidBottles_Base.xml:200, :291 |
| settings that scale it | — | — | `tankCapacityMultiplier` default 1 (RimMandrakeFlowWorksMod.cs:283, slider 0.2–5 :1142); pond `budgetMultiplier` |

The owner's "4" is right for a canal and wrong for the other two: a pond square is 5 levels and a tank square is 15
(30 for the cargo tank). The number 4 is also duplicated: `RM_PitTrapMath.Superdeep` (RM_PitTrapMath.cs:20),
`RM_FlowKernel.Superdeep` (RM_FlowKernel.cs:89) and `RM_PitDrawMath.MaxDepth` (RM_PitDrawMath.cs:28). 5 is duplicated
too, in `TransferChecks.Level` (SelfTest/TransferChecks.cs:60).

### 8.2 The design: one constant

- **New `RM_Volume` (Verse-free, beside `RM_PumpMath`):**
  - `LevelsPerSquare = 4`, the **deep notch** (owner 2026-10-12: deep water is "at least 4 notches deep"). It is its
    own constant, NOT `RM_ExcavationDepth.MaxDepth`: deeper natural beds (§9) never change a tank's size.
  - `UnitsPerLevel = 5`, moved here from `RM_PumpMath.TankUnitsPerLevel`, which becomes an alias and is then deleted.
  - `UnitsPerSquare = LevelsPerSquare × UnitsPerLevel` (20).
  - Every other copy of 4 and 5 above reads these constants. A pond square holds its own bed depth (§9.6), so a
    deep pond square holds at least `LevelsPerSquare`, and more at the middle of a big lake.
- **Deep canal square:** unchanged at `MaxDepth` levels.
- **Pond square:** budget = the bed depth of the cell, from its recorded water terrain:
  - deep water: `LevelsPerSquare`;
  - shallow water: 2 (ruling 7; ruling 3 bed depth).
  - Capacity = Σ cell bed depth × `volumePerTile` × `budgetMultiplier`.
  - `canalCellsPerSourceCell` is deleted from FluidDef.cs and from every FluidDef XML in the same change. Deleting the
    field from C# alone would make every XML that sets it a config error.
- **Tank square:** capacity = footprint area × `UnitsPerSquare` × (2 if tall) × `tankCapacityMultiplier`.
  - Tanks come in many footprints, each with a tall variant (owner ruling 2026-10-12, §8.5): 1×1 = 20 (tall 40),
    1×2 = 40 (80), 2×2 = 80 (160), 3×3 = 180 (360).
  - `RM_LiquidTank` (2×2): 80 units, down from 300; its tall twin 160.
  - `RM_UniversalCargoTank` (2×2): 80 units, down from 600, or 160 as a tall tank.
  - `RM_LiquidTankExtension.baseCapacityUnits` is replaced by `footprint` (from the def's size) and `bool tall`.
- **Multipliers:** at their default of 1, the equality holds exactly. The tooltips for `tankCapacityMultiplier` and
  `budgetMultiplier` say "≠ 1 breaks one square = one square".
- **Containers** (bottle, bucket, barrel) stay in units. A base barrel (25) holds more than one deep square (20).
  That is legal, because a barrel is not a square.

### 8.3 Save compatibility (one-time, versioned)

- `RM_MapComponent_Excavation` scribes `rmVolumeModel` (absent = 1, new = 2). The migration runs once in
  `PostLoadInit` when the stored value is below 2, then sets it to 2.
- **Bodies:**
  - Capacity is recomputed from the footprint (bed depth per cell, from `originalTerrain`, or the live terrain for
    a wet cell). Stock is scaled by newCapacity ÷ oldCapacity, so the fill fraction is preserved.
  - Limitless bodies are untouched.
  - Each body logs one line: "pond N rescaled a → b".
  - This is the one sanctioned volume change. A pond is nature: its volume was a budget, never water the player put
    there.
- **Tanks:** `storedUnits` is kept even when it is over the new capacity, so no water the player stored is ever
  destroyed.
  - An overfull tank refuses input (`CanAccept` already tests `stored + units ≤ Capacity`,
    Building_LiquidTank.cs:86) and drains normally.
  - Its inspect line says "overfull (old save)".
- **Canals:** no change.
- **Rain carry-over and hoses:** no change. They already count in levels or units.

### 8.4 Conservation tests

- **Offline** (`northstar/selftest_conservation_roundtrip.py`, which reads constants from production):
  - Trip 7 flips from "25 levels have nowhere to go" to **exact**: a 25-cell deep pond drains into a 25-cell D 4
    pit and the tanks end empty.
  - New trip 11, **square equals square:** N deep canal squares pumped into tanks of N squares fill them exactly.
    The same tanks pumped back fill the canal exactly, with no remainder.
  - New trip 12, **mixed pond:** a pond of 10 shallow and 10 deep squares holds 60 levels, and returns to the same
    wet set (LIFO, ruling 7).
  - New trip 13, **migration:** an old-model body and an overfull tank load into the new model. Stored tank water is
    conserved exactly, and pond stock is conserved in fraction.
- **C# SelfTest** (`Volume_one_square_is_one_square`):
  - `PerCellBudget(deepBed) × UnitsPerLevel == UnitsPerSquare == tank capacity ÷ footprint area`, with multipliers
    at 1.
  - A source sca### 8.5 Tank sizes — ruled (owner, 2026-10-12)

*"What you're really dealing with is "deep water" is an "at least 4 notches deep" but could be much deeper. A "tall
tank" should hold twice as much. And that's it. There are "big" water units. And yes tanks should come in many sizes.
1x1, 1x2, 2x2, etc. Tall versions too."* So: one tank square = one deep notch (4 levels, 20 units); a tall tank
square = 2 notches (40 units); footprints 1×1, 1×2, 2×2 and up, each with a tall version. Tall tanks need new art
(through the art ledger); a footprint family can share one texture scaled by `graphicData.drawSize`.

## 9. Deep beds: can an elevation grid cover a drained lake? (feasibility, 2026-10-12)

Owner, verbatim (2026-10-12): *"There's nothing wrong with saying the center of ponds or especially large rivers and
lakes and oceans might go down way past 4. That's the "elevation" question we need to evaluate. Can we handle making
an elevation grid over large sections of the map (say when the player drains a very large pond). Is that within
feasibility, or does the design break?"*

### 9.1 Verdict: feasible with changes

The grid itself is cheap and **already exists**. Three things in today's design break at depth > 4, and one breaks
at size > 4000 cells; each has a bounded fix. Nothing here is worldgen: every depth is derived on the map, from the
map's own vanilla water terrain, the first time a body forms (§9.4).

| concern | verdict | numbers |
|---|---|---|
| storage | fine, no new grid needed | `depthGrid` is already a map-sized `byte[]` scribed by `DataExposeUtility.LookByteArray` (RM_MapComponent_Excavation.cs:45, :420; MEASURED, read from source). A byte holds 0..255. A 250² grid deflates to **1.1 KB** (a D≤4 pond of 3.9k cells), **3.7 KB** (D≤20, 8.7k cells), **8.4 KB** (D≤20, 29k cells, half the map) base64 (MEASURED offline: synthetic bowls, zlib level 6; that the game deflates byte grids is ESTIMATED, not re-read in 1.6) |
| flow kernel cost | fine per pulse; must learn to sleep | per pulse it walks every component and moves ≤ `flowPerPulse` (1) level per recipient, so its cost scales with **cell count, not depth** (MEASURED, RM_FlowKernel.cs:175-390). ESTIMATED 1–3 ms for a 6000-cell component (BFS + sort + 4 neighbour reads, HashSet/Dictionary bound) every 250 ticks. Depth only multiplies the number of pulses a fill takes. |
| flow physics | **BREAKS** at depth > 4 | §9.2 |
| pond stock and recession | **BREAKS** (uniform per-cell volume) | §9.3 |
| body size | **BREAKS** above 4000 cells | `MaxBodyCells = 4000` (RM_LiquidStock.cs:27): a truncated body is classified **limitless** and can never be drained (RM_StockMath.IsLimitless, :87-93). Ocean and map-edge bodies are limitless by design too. |
| pathing | fine; the climb design scales | §9.5 |
| rendering | **BREAKS** if the sink is not capped | §9.5 |
| the number 4 | 85 references to `Superdeep`/`MaxDepth` in 27 files (MEASURED, grep of Source/) | §9.6 splits "dig cap / trap depth" from "bed depth" |

### 9.2 What breaks: the kernel compares DEPTH, not water height

`PickDonor` lets a neighbour give to a cell when the recipient is deeper, or when the donor is brimming
(`if (depthR <= dn && fn < dn) continue;`, RM_FlowKernel.cs:550), and sorts recipients deepest first
(`CompareDeepestFirst`, :393). There is no water surface anywhere. At D ≤ 4 the error is at most 3 levels. With a
bowl down to 20, a D 10 cell must fill **completely** (surface at ground level) before its D 9 neighbour takes a drop:
a refilling lake becomes a column of brim-full water standing next to a dry bed 9 levels down. That is visibly wrong.
Natural sources also read as a fixed `Superdeep = 4` donor (:89, :520).

**Fix (bounded, inside the Verse-free kernel):** compare head, not depth. Head of a cell = `fill − depth` (ground =
0). Gravity: a donor gives when its head is higher than the recipient's by at least 1 level; recipients sort by
lowest head, then the existing hop order (which still breaks ties, so FLOWWORKS_CHANNEL_OSCILLATION_1's acyclic order
holds). At D ≤ 4 with flat ground this reproduces today's results on every existing selftest scene except where today
is wrong. A natural source's head is 0 (its surface). ESTIMATED 1–2 agent-days including FlowKernelFuzz rows.

**Sleep:** a drained lake bed becomes excavated cells (Option B), and today every excavated cell is walked every
pulse forever. Add a per-component quiet flag: a component that moved nothing and had no external input sleeps until
a depth/fill write, rain or a driver marks one of its cells. ESTIMATED 0.5 day; it also bounds the cost of every
existing canal network.

`maxComponentCells = 6000` (RM_FlowKernel.cs:72) partitions bigger beds; seam rotation already handles that
(off by default). A 30k-cell drained lake is 5 partitions: correct, slow to level out across seams. Raising the cap to
~20k is a settings change once the kernel sleeps.

### 9.3 What breaks: a pond is a scalar with a uniform per-cell volume

A body is one `stock` scalar plus `PerCellVolume`, and recession gives up cells "fewest wet neighbours first, then
farthest from the centroid" (RM_LiquidStock.cs:373-420). **The scalar survives; the uniform volume does not.**

- **Capacity** = Σ bed depth over the footprint (levels) × `UnitsPerLevel` × `volumePerTile` × `budgetMultiplier`.
- **Which cells are wet** follows from one drawdown number: a flat surface `s` levels below the brim wets every cell
  whose bed depth is greater than `s`. Recession becomes "lower the surface", which empties the shallow rim first, as
  a real lake does, and replaces the centroid ordering. Integer remainder levels go to the deepest cells, ties by cell
  index, so conservation is exact and deterministic (trip 12 extends to a bowl).
- **Bodies over 4000 cells** need the cap lifted for *drainable* bodies (inland, not touching the map edge). The
  footprint walk is O(cells) once per formation; ESTIMATED <10 ms for 30k cells. The body's footprint list
  (`List<int>`, ~15 B per cell in XML) and `originalTerrain` (a scribed `Dictionary<int, TerrainDef>`, ~45 B per
  entry ESTIMATED) grow to ~0.5 MB and ~1.3 MB of save XML at 30k cells. Both should become byte grids (a bed-depth
  grid and a terrain-palette grid like `fluidGrid`), ~4–8 KB each.
- **Limitless bodies** (ocean, map-edge lakes, rivers) need no bed grid until a dam or weir cuts a piece off; their
  depth is only a drawing and fishing question until then. Rivers keep `RM_MapComponent_RiverCurrent`.

### 9.4 Where a natural bed's depth comes from (map-level, not worldgen)

At body formation (already lazy, RM_LiquidStock.BodyAt/FormBody), compute a distance-to-shore transform over the
footprint (one BFS, O(cells)) and set bed depth = shallow water 2 (ruling 3); deep water 4 + floor((d − d0) / s),
capped by a per-biome or per-setting `MaxBedDepth` (PROVISIONAL d0 = 3, s = 4, cap 20). It is a pure function of the
map's own vanilla terrain, so reloads and machines agree, and it writes nothing outside this map: **not a worldgen
feature** (CLAUDE.md rule). The bed is recorded once, so a refill returns the exact shape (ruling 7).

### 9.5 Pathing and rendering at depth 20

- **Pathing:** the climb design's per-band connectivity masks (relative_depth_climb_design §8.5) are 8 edge bits per
  cell per band; their size and cost do not depend on depth (4 B/cell, ~250 KB on 250²). The pocket union-find is
  ~62.5k cells × 4 bands ≈ 250k ops, ESTIMATED 2–5 ms per rebuild, at most once per 60 ticks. While a big lake drains,
  every pulse exposes cells, so it rebuilds about once per pulse (every 250 ticks): affordable. What changes: the
  size table's "huge: never trapped while MaxDepth is 4" becomes "trapped by a sheer step of 5 or more" — a gradual
  bowl still never traps anyone, which is the point.
- **Rendering:** a pawn is drawn `0.3 cells × depth` lower (RM_PitDrawMath.cs:28-40). At D 20 that is 6 cells: the
  sprite would sit far south of its cell, and clicks would miss it. **Fix:** the sink is relative to the lowest lip
  within reach and capped at 4 levels (1.2 cells); absolute depth beyond that is shown by **bed shading**, a
  SectionLayer tint by depth band (vanilla regenerates a 17×17 section only when dirtied), not by moving pawns.
  ESTIMATED 1 day plus art review.

### 9.6 Constants after this section

| constant | value | meaning |
|---|---|---|
| `RM_Volume.LevelsPerSquare` | 4 | one deep notch: a tank square, a deep canal square, the shallowest deep-pond square |
| `RM_Volume.UnitsPerLevel` | 5 | unchanged |
| `RM_ExcavationDepth.MaxDepth` | 4 today | how deep a pawn can **dig** (owner question below) |
| `MaxBedDepth` | 20 PROVISIONAL | deepest natural bed; also the kernel's and draw code's upper bound |
| trap depth | relative (climb design §8) | no absolute 4 anywhere |

### 9.7 Cost and order

ESTIMATED 4–6 agent-days on top of Option B and the climb design: head-based kernel + sleep (2), bed-depth grid,
drawdown recession, lifted cap and byte-grid saves (2), sink cap and bed shading (1), proof rows (1: drain a
5000-cell D≤12 lake through pumps into tanks and back, conservation exact, no pawn trapped on the gradual bed).

### 9.8 Owner question (card-ready)

**Can a player dig deeper than 4?**
- **(a) No — digging stops at 4; only nature is deeper.** Simplest; "deep" stays one notch for everything the
  player makes. A drained lake's middle is the only place deeper than 4.
- **(b) Yes, slowly — each notch past 4 takes a longer job.** Players can make reservoirs and real traps deeper
  than 4; more balance work (trap pits get stronger, digging speed needs tuning).
- **(c) Yes, but only by a machine** (a drill or excavator building). Keeps hand-digging simple and makes deep
  works a tech step; needs a new building.
