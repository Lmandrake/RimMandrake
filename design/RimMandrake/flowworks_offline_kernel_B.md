# FlowWorks offline liquid kernel — Approach B (2026-10-06)

Approach B of `design/RimMandrake/flowworks_playtest_automation_2026-10-06.md`: test the liquid logic with no game.

## Phase 1 — generated action sequences over the existing pure math (SHIPPED)

`src/RimMandrake/FlowWorks/Source/SelfTest/SequenceFuzz.cs`, called from `Program.cs`, run by the existing
`python3 src/RimMandrake/Utils/selftest_flowworks_stock.py` (so `run_selftests.py` runs it on every commit).
Every number comes from a production function; the *composition* (which cell touches which body, call order) is
the test's own small model, not the game's grid walk. That gap is what phase 2 closes.

| family | what a case is | invariants |
|---|---|---|
| cell/body/tank sequences | 1–6 cells, 1–3 bodies (random fluid, volumePerTile 0.5–3, limited/limitless, random budget), 5–80 random actions: Deepen, FillIn, Supply, Pump, Pour, Burn, Refill, Rain; then every cell filled back in | `0 ≤ F ≤ D ≤ 4`; wet ⇔ fluid recorded; a wet cell never changes fluid; limited stock in `[0, capacity]`; `CanSupply` ≡ `CanDebit` on the same unit; `CreditableLevels × unit` is exactly what `CreditAccepted` takes; `DisplacedLevels` ∈ {0,1} per raise; `SupportedCells` ∈ `[0, cells]`; fire accumulator conserves ticks; **per-fluid ledger** = start + declared inputs (limitless supply, refill, rain) − declared outputs (burn, overflow, limitless absorb), tanks counted at `TankUnitsPerLevel`; restoration ends at D=0, F=0 |
| flow and recession orders | random key triples | `MayFlowBetween` irreflexive, asymmetric, no 3-cycles (a level can never come back); `PrefersCandidate` a strict total order; `ViscosityStride` ≥1 and monotone; a viscous donor moves exactly once per stride |
| converter | random recipe, budget, tank refills/drains over ≤500 rare ticks | never spends input it lacks, never overfills output room, never spends budget it has not accrued, consumed:produced exactly the recipe |
| pit width | random 8×8 superdeep grids | measured width fits, width+1 does not, digging more never narrows a pit |

A failing case is shrunk (delta debugging over the action list) and printed as `seed N: message | actions`.
**Sanity probe (mutation):** flooring → ceiling in `CreditableLevels` fails as
`seed 75: CreditableLevels promised 1 level(s) = 3 units but CreditAccepted took 1.598 | Deepen(c1) Rain(c1)`;
halving `CanSupply`'s threshold fails as `seed 35: CanSupply and CanDebit disagree | Deepen(c4) Supply(c0)`.
Both restored. **Result on shipped code: 0 failures.**

## Timing (measured 2026-10-06, Archmagi, Release build)

| family | cases | steps | seconds |
|---|---|---|---|
| cell/body/tank sequences | 20,000 | 896,848 | 1.45 |
| orders | 200,000 | — | 0.04 |
| converter | 5,000 | 1,246,180 | 0.03 |
| pit width | 20,000 | 40,000 | 0.05 |
| **all fuzz** | **245,000** | **2,183,028** | **1.57** |

Whole wrapper (dotnet build-check + 96 cases incl. the 92 pre-existing): **~3.9 s wall**. Zero live-game minutes.

## Phase 2 — RM_FlowKernel (extracted; game path calls it)

**Done inside the time box, no mocking of rooms, pawns or terrain caches needed.**
`src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs` (Verse-free) now holds the pulse's grid transition:
component resolution (`RM_StockMath.CollectComponent`), sink drain, flow order (`ComputeFlowOrder`/`HopsFrom`),
recipient order (`CompareDeepestFirst`), donor pick (`PickDonor`), the transfer loop and the per-component
conservation ledger — on `z*width+x` indices and the component's own `depthGrid`/`fillGrid` byte arrays.
It also holds `CollectBody`, the 8-way footprint walk `RM_LiquidStock.FormBody` used inline.

Everything else stays in the adapter: `RM_MapComponent_Excavation` implements `RM_IFlowWorld` (natural-liquid
terrain, body supply/debit, donor and cell fluid, fluid-palette claim, ticksPerTile, sinks, re-render per
component); rain, burn, stock refill/recession, terrain writes and Scribe are untouched. The kernel calls the
world in the same order the old code did, so lazy body formation happens at the same moments. Neighbour orders
are Verse's, checked in the decompiled source (`GenAdj.CardinalDirections` N,E,S,W; `AdjacentCells`
N,E,S,W,SE,NE,NW,SW; `OnEdge`). Only visible change: dev-mode ledger warnings are logged after the pulse instead
of between components.

### Is game behaviour unchanged?

- **Differential vs the Python PulseOracle** (`northstar/validation_v2.py`, a port of the pre-extraction pulse,
  validated once against live data): `src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py`
  generates 3,000 seeded water scenes (3–12 square grids, 1–3 limited/limitless bodies, digs in order, optional
  sink band, 1–60 pulses) and compares every dug cell's F after every pulse plus final stocks:
  **3000/3000 identical, 91,430 pulses; oracle 2.7 s, kernel 3.8 s incl. the dotnet build check (6.6 s wall).**
  Sanity probe: swapping the donor score to `dn*10+fn` makes 8/3000 disagree.
- Mod builds clean (`winbuild.py FlowWorks`, 0 warnings). **Not yet run in game.** The live adapter check the
  GPT runs asked for (a few minutes on the bridge) is still owed; nobody touched the bridge for this.
- Oracle limits: water only (its sources are always water), viscosity stride 1, no rain/recession.
  Multi-fluid behaviour is covered by the fuzz below, not by the differential.

### Kernel fuzz (in `selftest_flowworks_stock.py`, so every commit runs it)

`src/RimMandrake/FlowWorks/Source/SelfTest/FlowKernelFuzz.cs`. The test world is plain arrays; bodies are formed by
the production `CollectBody`.

| family | scenes | pulses | seconds | invariants |
|---|---|---|---|---|
| ledger/bounds/no-mix/settles | 5,000 (4–10 square, water/tar/oil blobs, random digs, limited/limitless, sinks, viscosity) | 328,779 | 1.40 | kernel ledger balances; `0≤F≤D≤4`; no limited stock below 0; total = before + limitless in − sunk; **per fluid** = before + its own inputs − its own sink drain (a transmutation fails); with every source spent, a fixed point within 24 pulses (no shuttle) |
| limitless source fills its component | 2,000 | 591,080 | 0.28 | every excavated cell 4-connected to a limitless water source ends `F = D` |

Failing scenes shrink by deleting digs and print the grid. Sanity probes: making `MayFlowBetween` always true
(the pre-oscillation-fix engine) fails "no fixed point" and "fills its component"; ignoring a failed debit is
**unreachable** (`CanSupply` and `TryDebit` use the same unit, so PickDonor never offers an unaffordable source).

One invariant I first wrote was wrong and is recorded so nobody re-adds it: *"a wet cell never changes fluid
across a pulse"*. Seed 4764: a sink cell drains its last oil level, then tar claims it the same pulse. Legal.
"Never mix" is enforced as per-fluid conservation instead.

## Regression cases for confirmed findings #1 and #2 — both REPRODUCED by the kernel

Both are `KnownDefect_*` cases: they PASS while the defect reproduces and print what they saw; when a fix lands
they fail ("not reproduced") and should be turned into guards.

- **#1 touching water and tar merge** (`RM_LiquidStock.cs` FormBody → now `RM_FlowKernel.CollectBody`): a row
  `water water tar tar`, body formed from a water cell, one-cell channel dug over the tar. Output:
  `REPRODUCED: water+tar formed one 4-cell water body; the channel over the TAR filled with water`.
  The walk adds every natural-liquid neighbour without looking at which liquid it is.
- **#2 reload changes scarce allocation** (`RM_MapComponent_Excavation.cs` DoPulse seed order): a 1-cell pond
  with stock 1 between channels A (x=1) and B (x=3); B dug first. Output:
  `REPRODUCED: same world, session order paid (A,B)=(0, 1), after reload (1, 0)`. In session the seed order
  is dig order (HashSet insertion); after a load `RebuildExcavatedSet` walks cell-index order.

## Timing summary (whole Approach B offline suite)

| run | wall |
|---|---|
| `python3 src/RimMandrake/Utils/selftest_flowworks_stock.py` (100 cases: 92 old + 4 math fuzz + 2 kernel fuzz + 2 known defects; 252k generated cases, 0.92M kernel pulses) | ~5–6 s, of which fuzz 1.5 s + kernel 1.7 s |
| `python3 src/RimMandrake/FlowWorks/Source/SelfTest/selftest_flowworks_kernel_oracle.py` (3,000 scenes) | 6.6 s |

## Not done / next

- Live adapter check of the refactored DLL (one short bridge session: run the existing FlowWorks core flow rows).
- The fill-in displacement walk (`Displace`) and rain are still adapter-only; extracting them is the obvious next
  slice if this approach is kept.
- Fixes for #1 and #2 are design decisions (which liquid wins at a seam; a declared seed order that survives a
  load), not done here.
