# WEIR_BREACH_FIX_CATCH_STRANDS_AT_HOME (MOD, FlowWorks rivers)

**Row:** `extension_proof --live --site river` `breach_wash` (toggle `breachWashesCatch`), and the 6 rows it gates
(silt_richen_and_revert, ferry_rope, ferry_rope_undrafted, levee_engine_fact, levee_holds_and_gap_leaks, breach_cascade_order).

**Measured live 2026-10-12c** (23-mod tier, FlowWorks a9c8e76b, river_site tile 60145 TemperateForest, map 8):
`Transient/bench_live_20261012c/ext_river.json`: `BREACH heldBefore=3 heldAfter=3 breaching=True arrestOff=True at=(112, 0, 52)`.
The weir pool proof on the same weir: `wetCell=112,52 wetDir=6 nbr=...0,-1:-1...` (the wet cell flows S into a cell with
no flow). Last PASS: 2026-10-06 runs (z=12 bank-edge weirs; e.g. heldBefore=4 heldAfter=0).

**Mechanism (read from source, the strand cell itself not read live):** `RM_Weir.WashCatch` walks the flow
`breachWashCells` (4) steps from WaterCell but breaks at the first cell with no flow dir; here that is after ONE step
(112,51). The strand is then the nearest standable no-flow cell within 8 of that end, which sits inside the weir's own
`HeldCatchRadius` (2.5), so `HeldCatch()` still counts every stack: the breach "washes" the catch next to the weir.
Nothing requires the strand to be outside the held radius.

**Fix sketch:** strand only on a cell farther than HeldCatchRadius from the weir (search outward from the walk's end,
skipping the held disc), and/or continue the walk along lane cells when one cell has no dir; add a selftest with a
one-step flow field. Then rerun `extension_proof --live --site river`.

## criteria

- A1 L0: FlowWorks SelfTest `WeirBreach_*` cases pass (live 3x3 scene strands outside HeldCatchRadius+1.5 and downstream; 1988 off-axis bank-edge sites all out of reach, can-fail old rule strands 645 home); DLL built with .srchash.
- A2 L2: `extension_proof --live --site river` `breach_wash` row PASSes (heldAfter < heldBefore) and the 6 rows it gates are measured.

Built e76408e982 (report `Transient/weir_breach_2026-10-12.md`): RM_RiverMath.WashStrand/DownstreamStep; WashCatch calls it.
Not a code regression: the wash was unchanged since the move; ec13854219's river_site change moved the proof weir to (112,52).

NEXT: deploy FlowWorks and run `extension_proof --live --site river`; read breach_wash and the 6 gated rows.
