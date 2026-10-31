# SLUICE_BOX_PROVE_THE_DAILY_WASH

Split from FLOWWORKS_QUARRY_DIGGING_1 (superseded) by owner direction 2026-10-31 ("perhaps the digging finds, sluice mining, and gold panning can be broken down into smaller tickets that can be independently checked and debugged"), then fully equipped with the parent's context at his request. River half, sluice only. Siblings: DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE (canal digging, the failing one), GOLD_PANNING_PROVE_THE_COLONIST_STAYS, PLACER_STOCK_PROVE_FLOOD_REFILL (the shared stock this box draws on).

## why

What the feature is for the player. Owner request 2026-10-03: "sluice mining slowly producing ore out of a stream/river". Ruled by question card 2026-10-03: the mineral registry gains a separate per-biome "what the rivers carry" column (placer gold where hills have none); sluice box and panning live in River Works; fully ruled, build per design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md section 2b. The player builds a box on a river bank edge and, once a day, it washes a little ore out of the water onto the bank, drawing from the river's finite placer stock (sibling ticket).

Defaults (RM_QuarrySettings.cs, RM_PlacerMath.cs): sluiceBoxEnabled true; sluiceYieldMultiplier 1; one roll per in-game day (SluiceIntervalTicks 60000); expected 1.2 units a day on an ordinary river (SluicePerDay) scaled by lane rate, river size factor (creek 0.5, river 1, great river 1.5 per design) and the multiplier. All values PROVISIONAL.

## spec

### Current state (built)
Built by FOUNDRY e569931e6 (2026-10-11). Read 2026-10-31:
- Building: RM_Building_SluiceBox (Source/Quarry/RM_PlacerWorks.cs:367). 1x2 bank edge, placed by RM_PlaceWorker_SluiceBox (317; shallow moving river beside solid bank only). Tick every 250 ticks; first sighting arms nextRollTick = now + 60000, then Wash() each interval (lines 408-425).
- Wash() line 430: outcomes sluice=off, nowater, nothing lane=N, rivercarriesnothing, stockspent, noroom, or sluice=<def>x<n> lane=N. Rolls SluiceYield (RM_PlacerMath.cs:60; (int)(expected + roll)), draws the mineral with RM_PlacerDraw.Draw (provisional pool Gold/Silver/Jade/Uranium from the map's own rock), places first then debits the stock (Available, then Take); credits stock.SluiceUnits.
- Defs: Defs/Rivers/RM_PlacerWorks.xml (RM_SluiceBox, RM_PlacerPool_Vanilla). Inspect string shows "washing" or "water too calm to wash" and "river stock x/y".
- Settings pruned 2026-10-22 (93b24c3d9b: the sluice-GATE settings were excised; the canal door is "sluice gate", the river one "sluice box"; do not confuse them).
- Review-map station: land_panning (review_map_coverage.py 399/405).
- Chain: `placer` in northstar/extensions_rivers.py:510, component sluice_washes_pool_from_stock (line 523, toggle sluiceBoxEnabled): builds its own box via static_call "selfcheck" (RM_PlacerProof.SelfCheck, RM_PlacerWorks.cs:671) and forces the wash.

### Not built / not proven
Nothing unbuilt in the box. Not proven live: the real day timer (every probe forces Wash() through static_call "wash"; the 60000-tick roll through Tick() has never been read), the lane-calm refusal (inspect text) and the sluiceBoxEnabled OFF row beyond the chain's toggle. All UNMEASURED.

## verify

### Acceptance
Chain: `modcheck FlowWorks placer` via testq (SteveDesktop lane steve-targeted), component sluice_washes_pool_from_stock must PASS: a legal box placed on the site's own river washes, the wash lands a placer mineral on the bank, and the stock falls by exactly what landed. An UNMEASURED "the site's rock holds no placer mineral" (extensions_rivers.py:527) is not a pass; it means a rock-less site.
Add if a clean row is wanted for the real timer: advance 60000+ ticks and read LastResult without forcing.

### Last tested code version and whether a run is owed
Last PASS: 2026-10-15 03:32Z, A2, FlowWorks sha 695812d5ec (sluice_washes_pool_from_stock PASS, panning_draws_stock PASS; evidence ext_river.json / Transient/bench_live_20261014_r3). Also PASS in the 2026-10-13 triage run (before the panning site was fixed). That sha does not resolve in this clone, so "code changed since" is shown by dated commits only: Quarry/ and Defs/Rivers/ were touched afterwards by 17a082d2d0 (2026-10-15, GPT fixes B; same day as the pass, order against 03:32Z UNMEASURED; it touched panning skipping an empty pool), 93b24c3d9b (2026-10-22, sluice-gate settings excised), d27815fcf5 (2026-10-22, player text), 463f9a2385 (2026-10-22, settings Reset helper). Verdict: ONE run is owed, because the code changed after the last pass. No run has been made since 2026-10-15. A3 and A4 (the sluice and panning separate reads) were never read.

### History
- 2026-10-11: built (e569931e6), chain placer added.
- 2026-10-13 triage: sluice_washes_pool_from_stock PASS; panning_draws_stock and flood_refill UNMEASURED (SITE: FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY, nobody swept away).
- 2026-10-15 R3: A1 (defs resolve, 0 Config errors) and A2 PASS at 695812d5ec.
- No failure, finding or INVALID/HARNESS run has ever been recorded against the sluice. Of the parent's 58 findings, 0 belong here (they are all "dig job never finished" and sit on DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE). 0 + 0 + 0 here; do not move any in.
- False theories to avoid: do not blame the sluice for the 26 to 29 red dig_finds runs; a different chain (dig_finds) and different code. The parent's "validated" status rested on A1/A2/A5 and was contradicted only by the dig rows.

### Dependencies and do-not-touch
- Shares RM_MapComponent_PlacerStock (RM_PlacerWorks.cs:164) with panning; PLACER_STOCK_PROVE_FLOOD_REFILL owns refill and cap. Do not change Take / Available semantics here.
- Do not touch the canal sluice GATE (separate building, RM_Sluice).
- One live driver at a time on Steve; the placer chain also runs the panning component.

### NEXT action (one)
Queue the placer chain ONCE on SteveDesktop at current HEAD (code changed since 695812d5ec) and read the sluice_washes_pool_from_stock row from the modcheck sheet; if PASS, record it as the new A3-equivalent verify with the sha, otherwise file the failure text under this ticket.
