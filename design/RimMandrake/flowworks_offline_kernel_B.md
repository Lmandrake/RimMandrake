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

## Phase 2 — RM_FlowKernel spike
(not started)

## Regression cases for confirmed findings #1 and #2
(not started)
