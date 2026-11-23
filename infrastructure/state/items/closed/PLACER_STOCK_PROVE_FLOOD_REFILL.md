# PLACER_STOCK_PROVE_FLOOD_REFILL

Split from FLOWWORKS_QUARRY_DIGGING_1 (superseded) by owner direction 2026-10-31 ("perhaps the digging finds, sluice mining, and gold panning can be broken down into smaller tickets that can be independently checked and debugged"), then fully equipped with the parent's context at his request. The shared per-map placer stock behind the sluice and panning, its cap, regrowth and the spring-flood refill. Siblings: SLUICE_BOX_PROVE_THE_DAILY_WASH, GOLD_PANNING_PROVE_THE_COLONIST_STAYS, DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE.

## why

What the feature is for the player. A river does not wash ore forever: sluice and panning draw on one finite stock per map, which regrows through the year and is topped up by a spring flood, so a patient player is rewarded and a farmed river runs dry. Design (design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md section 2b/2g, line 134): yield scales with river size (creek x0.5, river x1, great river x1.5) "and a spring flood refills the stock". Card ruling 2026-10-03: the registry gets a per-biome "what the rivers carry" column; until it exists the pool is the MAP'S OWN ROCK (provisional Gold/Silver/Jade/Uranium).

Defaults (RM_QuarrySettings.cs, RM_PlacerMath.cs): placerFloodRefill true; placerStockPercent 2 (cap = 2% of the placer units the map's rock holds, StockCap line 26); regrows to full once a year (TicksPerYear 3,600,000 = 60 days x 60,000). All PROVISIONAL.

## spec

### Current state (built)
Built by FOUNDRY e569931e6 (2026-10-11). Read 2026-10-31, Source/Quarry/RM_PlacerWorks.cs RM_MapComponent_PlacerStock (line 164):
- Fields: stock (-1 until first asked), units (placer units of the rock), lastTick, floodWas; counters SluiceUnits, PanUnits, Refills. Cap uses CapNow = StockCap(units, placerStockPercent). Saved with ExposeData; a save from before 2026-10-11 stored the cap, so a CapFromUnits inverse recovers units (RM_PlacerMath.cs line 33) or -1.
- MapComponentTick (about line 257): every 2500 ticks, only once stock >= 0 (nothing regrows until a sluice or panner first asks), applies RM_PlacerMath.Regrow(stock, cap, ticks since last), then detects a flood edge: if RM_RiverWorks.FloodActive(map) now and not before, and placerFloodRefill is on, calls Refill().
- Refill() sets stock = CapNow and Refills++ (it never reads the setting; only the edge detector does). Available(want) and Take(want) hand out whole units; PoolAny says whether the rock holds any placer mineral (a cap of 0 means a river that carries nothing).
- Chain: northstar/extensions_rivers.py placer, last block `_owed(t, "flood_refill", ...)` is a stub (about line 577) with the comment: "refill" calls Refill(), which sets stock = cap whatever placerFloodRefill says, so drain + refill could not fail. A real pair raises a flood edge with the setting on and off. validation.py:1575 RIVER_TOGGLES_OWED = ["placerFloodRefill", "takenByLandTraceEnabled"] marks it owed.
- Probe verbs on RM_PlacerProof static_call (RM_PlacerWorks.cs 612+): "" report, "wash", "refill", "drain", "pan", "selfcheck".

### Not built
The flood-refill test: no code stages a flood edge. UNMEASURED whether RM_RiverWorks.FloodActive edge triggers the refill on a live map, and whether the placerFloodRefill OFF case really blocks it. Also UNMEASURED: yearly regrow on a live map (the maths is selftested in Source/SelfTest; no live read), and the cap migration from pre-2026-10-11 saves.

## verify

### Acceptance
Rows to pass (the second pair is the new work):
1. Existing: placer chain components sluice_washes_pool_from_stock and panning_draws_stock PASS (stock falls by exactly what lands). Already green at 695812d5ec on 2026-10-15.
2. NEW flood_refill pair: with placerFloodRefill ON, drain the stock with the "drain" verb, raise a real flood edge (FloodActive false then true; staging method UNMEASURED, find how RM_RiverWorks.FloodActive is driven before building), and read stock back at cap and Refills +1. With placerFloodRefill OFF, repeat and read stock stays at 0 and Refills unchanged. Drive it through the edge, never through "refill".
3. Replace the _owed stub with the pair and drop placerFloodRefill from RIVER_TOGGLES_OWED when it passes.

### Last tested code version and whether a run is owed
Last PASS on rows that touch the stock: 2026-10-15 03:32Z, A2, FlowWorks sha 695812d5ec (does not resolve in this clone). Flood refill: never measured (owed since the 2026-10-11 review; UNMEASURED 2026-10-13). Code touched afterwards in Quarry/Defs/Rivers: 17a082d2d0 (2026-10-15), 93b24c3d9b, d27815fcf5, 463f9a2385 (2026-10-22). One chain run is owed once the flood pair exists (new code version); a run now would only repeat rows 1.

### History
- 2026-10-11 built; review the same day flagged that the forced "refill" ignores the setting, so drain+refill cannot fail (hence the owed stub, not a pass).
- 2026-10-13 triage: panning_draws_stock and flood_refill UNMEASURED (SITE: FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY). 2026-10-15 A2 PASS for sluice and panning; flood_refill stayed owed.
- No fail, finding or INVALID/HARNESS run has been recorded against the stock. 0 of the parent's 58 findings belong here.
- False theory to avoid: calling the stock proven because "refill" works; it proves Refill(), not the flood trigger or the setting.

### Dependencies and do-not-touch
- Sluice and panning tickets read and debit this stock; keep the Available then Take contract and whole-unit rounding they rely on.
- RM_RiverWorks.FloodActive belongs to River Works; read it, do not change it for this ticket.
- Do not add flood staging that the player could trigger by mistake; staging belongs to the probe only.

### NEXT action (one)
Read how RM_RiverWorks.FloodActive is set (grep src/RimMandrake/FlowWorks/Source for FloodActive) and write down the cheapest way to raise a flood edge from a probe; then replace the `_owed(t, "flood_refill", ...)` stub in northstar/extensions_rivers.py with the ON/OFF pair described in row 2.
