# RIVER_SITE_FIX_FISHLESS_ROT_RIVER (presumed SITE, FlowWorks river proof)

**Measured (BENCH 2026-10-12b, harness 9905d543b3, FlowWorks a9c8e76b, 23-mod ratchet_pilot+patches tier):**
`river_site.py` took **tile 9980 RM_TheRot** (current 3,910, fast 1,127). The 2026-10-12 world's tile 825 (TemperateForest) was not
in this quicktest world (70 river tiles among 2,371 flat temperate candidates, against 176 last time). `extension_proof --live
--site river` read 9 PASS / 0 FAIL / 11 UNMEASURED (`Transient/bench_live_20261012b/ext_river.json`):

- `weir_fish_draws_stock` UNMEASURED: `ProofWeirCatch` (`Source/Rivers/RM_RiverWorksProofWorks.cs` ~206) found the weir's
  `WaterBody` with `HasFish == false`, and that ends **7 more rows** in the chain (breach_wash, silt_richen_and_revert, ferry_rope,
  ferry_rope_undrafted, levee_engine_fact, levee_holds_and_gap_leaks, breach_cascade_order).
- `panning_draws_stock` UNMEASURED (`pan=nothing`, site 59,10) ends `flood_refill`.

So one site property silences 8 rows. Presumed SITE: river_site's "flat temperate" filter admits RM_TheRot, whose river body
seems to carry no fish population. Untraced: whether HasFish false is the biome (no fish defs) or the body's population at gen.

**Fix:** river_site.py rejects a candidate whose river WaterBody has no fish (or prefers TemperateForest), and names the
rejection, as it does for geysers.

## criteria
- A1 L1: `river_site.py` then `extension_proof --live --site river` reads `weir_fish_draws_stock` PASS or FAIL (not UNMEASURED
  "no fish stock"), with the chosen tile's biome and HasFish recorded.
