# GOLD_PANNING_PROVE_THE_COLONIST_STAYS

Split from FLOWWORKS_QUARRY_DIGGING_1 (superseded) by owner direction 2026-10-31 ("perhaps the digging finds, sluice mining, and gold panning can be broken down into smaller tickets that can be independently checked and debugged"), then fully equipped with the parent's context at his request. River half, panning only. Siblings: DIG_FINDS_PROVE_NEVER_FINISHES_ON_STEVE, SLUICE_BOX_PROVE_THE_DAILY_WASH, PLACER_STOCK_PROVE_FLOOD_REFILL (the shared stock).

## why

What the feature is for the player. Owner request 2026-10-03: "panning for gold in a river". Ruled 2026-10-03: panning uses Mining and is ordered via a panning spot on the dry bank; fully ruled, design/RimMandrake/flowworks_quarry_sluice_panning_design_2026-10-03.md section 2c. A colonist works at a spot on the bank beside a shallow river, stands there for a session, learns a little Mining, and takes 0 to 3 units from the river's finite stock. Design: "mostly nothing", per year a dedicated panner earns perhaps 40-80 units (design line 157), less than a sluice, no build beyond the spot.

Defaults (RM_PlacerMath.cs, RM_QuarrySettings.cs): panningEnabled true; panningYieldMultiplier 1; PanSessionTicks 5000 (about 2 in-game hours) divided by the pawn's MiningSpeed (PanTicks line 78); PanHitChance 0.125 times a skill factor 0.4 + 0.06 x Mining (skill 0 = 40%, skill 20 = 160%, line 85) times the multiplier; PanMin 1, PanMax 3. All PROVISIONAL.

## spec

### Current state (built)
Built by FOUNDRY e569931e6 (2026-10-11). Read 2026-10-31, all in Source/Quarry/RM_PlacerWorks.cs:
- Spot placement: RM_PlaceWorker_PanningSpot (348).
- Job offer: RM_WorkGiver_PanForPlacer (493). ShouldSkip when panning off or stock < 1 or no pool (the empty-pool skip was added by 17a082d2d0, 2026-10-15); HasJobOnThing needs an unforbidden spot with an adjacent shallow river cell, reservable and reachable.
- Job: JobDriver_PanForPlacer (526). Reserve the spot, GotoCell, Toils_General.Wait(PanTicks) with a progress bar and Mining XP 0.04 a tick (the colonist "stays" here), then a finish toil that calls RM_PlacerPanning.Session. Fails if the spot despawns / is forbidden or panning is switched off mid-job.
- Session (563): rolls PanSession, draws a mineral, checks stock.Available, places the stack near the pawn, THEN debits stock.Take, adds stock.PanUnits, shows "<pawn> panned N <label> out of the river." Outcomes pan=off / nothing / rivercarriesnothing / stockspent / noroom / <def>xN.
- Defs: Defs/Rivers/RM_PlacerWorks.xml (RM_PanningSpot, RM_PanForPlacerJob, WorkGiver RM_PanForPlacer).
- Chain: placer, component panning_draws_stock (northstar/extensions_rivers.py:532, toggle panningEnabled): raises panningYieldMultiplier to PAN_MULT 10 and placerStockPercent to 10, runs up to PAN_TRIES 8 forced sessions through static_call "selfcheck"/"pan", and checks that the units taken equal the book's PanUnits and the stock fell by that much. Constants PAN_* at lines 497-503; PAN_NO_READING = pan=nothing / stockspent / noroom / nocolonist.

### Not built / not proven
IMPORTANT gap, found 2026-10-31: the chain forces Session() directly. No chain or script in src/ drives the real job (WorkGiver offers it, the colonist walks to the spot, waits 5000/MiningSpeed ticks without being pulled away, then finishes). That is the "colonist stays" half, and the title of this ticket. UNMEASURED. (Search: PanForPlacer / RM_PanningSpot appear only in RM_PlacerWorks.cs, the def XML and the review-map files.)

## verify

### Acceptance
Rows to pass:
1. Chain: `modcheck FlowWorks placer` via testq (SteveDesktop lane steve-targeted), component panning_draws_stock must PASS (stock debit equals units placed; the book agrees). A site with no placer mineral or a lost stock book is UNMEASURED, not a pass.
2. NEW (to write, one small step): a live pan job. Spawn a colonist with Mining priority 1 and a built RM_PanningSpot beside shallow river, run ticks (at least PanTicks, about 5000 at MiningSpeed 1, plus walking), and read that (a) the colonist is on the spot with the pan job the whole session, (b) the session ends once, (c) a mineral or "nothing" results and the stock book moved by exactly what landed. Hold panningYieldMultiplier high and stock raised, as the chain does, so a result is visible.

### Last tested code version and whether a run is owed
Last PASS of row 1: 2026-10-15 03:32Z, A2, FlowWorks sha 695812d5ec (panning_draws_stock PASS, evidence Transient/bench_live_20261014_r3/live/ext_river.json). 2026-10-13: UNMEASURED because of the site (FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY). That sha does not resolve in this clone. Code touched afterwards: 17a082d2d0 (2026-10-15, panning skips an empty pool; order against 03:32Z UNMEASURED), 93b24c3d9b, d27815fcf5, 463f9a2385 (all 2026-10-22). So ONE run of the chain is owed; row 2 has never run, so it is owed regardless. A4 (the separate panning read) was never taken.

### History
- 2026-10-11 built; 2026-10-13 first chain: panning UNMEASURED (SITE); 2026-10-15 A2 PASS.
- No fail, finding or INVALID/HARNESS run has been recorded against panning. 0 of the parent's 58 findings belong here.
- False theories to avoid: a forced Session proves the maths and the stock accounting, not that a colonist does the job; do not call the feature proven on row 1 alone. Do not blame panning for the dig_finds failures.

### Dependencies and do-not-touch
- Shares RM_MapComponent_PlacerStock with the sluice; PLACER_STOCK_PROVE_FLOOD_REFILL owns cap/refill. Keep Available then Take ordering (place first, debit after).
- Do not touch River Works current/sweep code (the spot is on the bank on purpose).
- One live driver on Steve at a time. Never live-test a flyer's flight (not relevant here, but standing).

### NEXT action (one)
Write the live pan-job probe (row 2) beside panning_draws_stock in northstar/extensions_rivers.py:532, keeping the existing forced-session row; then run the placer chain once on SteveDesktop at that new code version and read both rows.
