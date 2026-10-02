# BELT: FLOWWORKS_CHANNEL_OSCILLATION_1 fix — progress (2026-10-02)

## 0. Started
- skeleton written

## 1. Failing oracle test
- read: DoPulse/ResolveComponent/PickDonor/CompareDeepestFirst live in `RM_MapComponent_Excavation.cs` l.762-1025 (NOT Flood_FlowWorks.cs, which is the legacy release walker). DoPulse is `private void DoPulse()`; signature kept.
- C# SelfTest/ compiles only RM_StockMath.cs, so the engine itself has no C# test; oracle is the test.
- writing O6 in validation_v2_DRAFT.py: PulseOracle(algo='old'|'fixed')


## 2. Fix design
(pending)

## 3. Oracle proof of fix
(pending)

## 4. C# build + selftests
(pending)

## 5. Deploy
(pending)
- O6 written; with fixed==old it FAILED on every fixed-algo assertion (E3/N3 never fill, direction-dependent vectors, plot-D stalls at stock 94) while every OLD assertion PASSED (E/N period-2 for n=3,4,6,12; W/S fill; doc vectors E3/E6; live plot-D vectors + stock 94). Root cause CONFIRMED.

## 2. Fix design
- One static strict order per component per pulse: key = (BFS hops from a SUPPLYING source, -hops to nearest sink cell), then depth. Non-source donor n -> r allowed only if key(n) < key(r) (overflow or gravity as before) or key equal and D_r > D_n (gravity). Strict order => acyclic => no unit returns => no shuttle; geometry-only => direction-independent.
- Recipient sort: (-D, key, index) (index now only breaks true ties).
- Unchanged: source score 1000/CanSupply/TryDebit budget, sinks drained first at FlowPerPulse, FlowPerPulse cap, ledger.
- Pure gate goes in RM_StockMath.MayFlowBetween so SelfTest/ can test it.

## 3. Oracle proof (validation_v2_DRAFT.py --offline: O1-O6 PASS)
- fixed: E/N/W/S give IDENTICAL per-pulse vectors and fill full for n=3,4,6,12 at D=1 and D=3, first full at exactly n*D pulses (the 1-level/pulse mouth lower bound) and then at rest.
- plot-D live geometry: full (all 3) at pulse 36, stock 125->89 (old: stalls at 94, oscillates).
- limited stock: sum(F)+stock conserved every pulse; delivers exactly the stock then rests (all dirs).
- spent 5-level pond into 8-cell run: comes to rest (old flickered forever).
- sink drain: same end state as old (D=1 empties, D=2 keeps bottom level), at rest.
- 300 random 9x9 nets (0-2 sources limitless/limited, sinks on/off, per 1-3): ledger balances and a fixed point is reached in <400 pulses.

## 4. C# (in progress)
- RM_StockMath.cs: + MayFlowBetween (pure gate). SelfTest/Program.cs: + 4 FlowOrder cases (incl. exhaustive antisymmetry).
- RM_MapComponent_Excavation.cs: + pulseSourceHops/pulseSinkHops/pulseHopFrontier/pulseComponentSet, ComputeFlowOrder()+HopsFrom() called in ResolveComponent after sink drain; CompareDeepestFirst -> (-D, srcHops, -sinkHops, index); PickDonor gates non-source donors through MayFlowBetween. DoPulse signature untouched.
- winbuild FlowWorks: Build succeeded, 0 warnings/errors; DLL + .srchash copied back.
- C# SelfTest (winbuild csproj + dotnet.exe run): 56/56 passed (52 prior + 4 new FlowOrder).
- run_selftests.py: 117/117 PASS (incl. selftest_flowworks_northstar.py, selftest_flowworks_stock.py)

## 5. Deploy
- dry run: only Assemblies/RimMandrakeFlowWorks.dll + .srchash drift; --apply: "Deployed 2 file(s) ... VERIFIED in sync". Game not launched, bridge untouched.
- NOTE for FOUNDRY: the live suite's E2_channels_fill comment in validation_v2_DRAFT.py ("EXPECTED RED on east/north until FLOWWORKS_CHANNEL_OSCILLATION_1") is now stale; it was outside the oracle part I was cleared to edit. oracle_for() now defaults to algo="fixed", so E2/E3 live predictions are the fixed engine's.
- NOT committed (brief forbade git). Files changed listed in final report.
