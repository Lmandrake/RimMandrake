# BELT RiverWorks slice 2 — 2026-10-05

## Milestones
- start
- settings + IsWaterCell seam written
- weir/silt/drift/ferry/levee C# written; RiverCurrent pool+rope wiring
- TerminalBiomes rewired (dep on riverworks, arrester->RM_CompRiverArrester, 1x2 genstep spot, seams registered, sea silt patch); both DLLs build
- RiverWorks+TB build ok; selftests 182/184, 2 FlowWorks fails (checking)

## Landed (written by the FlowWorks builder; the slice-2 builder went silent after its commit)
- 456d00ca2 River Works slice 2 (weir 1x2 + slack pool, fish + biome drift catch, breach washes catch, stake-line levee, silt table, rope ferry; bank works moved out of TerminalBiomes, which now depends on River Works); bd25c2f21 art-ledger records for its 4 placeholder textures (the push guard had refused them).
- NEW ROWS NEEDED (River Works validation.py, live): static_call RM_RiverWorksProofWorks.ProofWeirPlace / ProofWeirPool (slack ~8 cells upstream) / ProofWeirCatch (fish + biome-relevant drift) / ProofBreach (catch washed downstream) / ProofSilt / ProofFerry / ProofLeveeFact (continuous stake-line holds a spring flood). settings: bankWorksEnabled, breachEnabled, stakeLineLevee, weirCatchesFish, weirCatchesDrift, breachWashesCatch, siltRichening, ferryEnabled.

## NEW ROWS NEEDED (slice-2 builder, per mechanic; all in validation.py chain "works", static_call RM_RiverWorksProofWorks)
- place.weir_bank_edge — ProofWeirPlace: bank-edge accepted, all-dry and all-wet rejected. Settings: bankWorksEnabled.
- weir.arrest_and_pool — ProofWeirPool: wet end arrests; >0 pool cells drop a lane (~8 upstream, 3 wide). Settings: bankWorksEnabled, weirPoolLength.
- weir.fish_draws_stock — ProofWeirCatch 20: fish rolls >0 and WaterBody.Population drops (Notify_Fished). Settings: weirCatchesFish, weirCatchIntervalHours, weirHeldCatchCap.
- weir.biome_drift — ProofWeirCatch driftRolls on a vanilla-biome river map (RM_RiverDriftDef; no WoodLog). Settings: weirCatchesDrift, weirDriftChance. Our biomes need their own drift defs (per-biome sitting).
- breach.wash — ProofBreach: held catch leaves the weir, strands on a bank ~breachWashCells downstream. Settings: breachEnabled, breachWashesCatch, breachWashCells, breachHpFraction.
- breach.cascade_order — UNCOVERED: live walk: stake-line below a breached weir snaps nearest-downstream first, upstream stakes spared. Settings: stakeSnapTicksPerCell.
- levee.holds / levee.gap_leaks — only the engine fact (ProofLeveeFact stakeIsEdifice) is read; live walk owed: spawn SeasonalFlood behind a continuous stake-line, then remove one post. Settings: stakeLineLevee (off = Harmony postfix on Flood.CanFloodSpreadInto lets stake cells flood).
- silt.richen_and_revert — ProofSilt: Soil/GrasslandSoil/MarshyTerrain -> SoilRich, Clog reverts. Settings: siltRichening, siltIntervalDays. Sea pair patched in by TerminalBiomes.
- ferry.rope — ProofFerry: two posts across the current pair; rope cell not carried. Settings: ferryEnabled, ferryMaxSpan. Known limit: undrafted pathing does not prefer the rope yet.
- sea.unchanged — TerminalBiomes suite: Twilight weir (now 1x2, genstep picks a free rotation) still arrests and breaches on undersurge.
