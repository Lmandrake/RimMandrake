# PYRE_REGROW_BUILD_A_WEEK_IN_MINUTES

- Build: commit c87cbd99a134. Setting `RM_PyrelandsSettings.wildPlantRegrowDaysOverride` (0 = shipped 9 days; Plant art and wild flora group). `RM_PyrelandsDensityEnforcer` re-asserts biome.wildPlantRegrowDays every 250 ticks from it.
- Row `embergrass_regrow` rewritten: burn (5000), then override 0.1 days, 2 x 1500 ticks via safe_advance, restore, read back.
- Selftests: 349/417 pass; only FAIL selftest_flowworks_stock.py (FlowWorks, another seat's uncommitted edits).
- Deploy: compose biomes, FireEcologyHook.dll + srchash only.
- Live (pilot tier 23 mods, fixture NS_Pyrelands_site_1_a32c5db7c6f1_anima0, tile 5): run 1 new plants 0 -> 31 -> 54 of 256 (harness bug: setting read back as string "0"); run 2 (fixed) 0 -> 28 -> 62 of 256 in 3000 ticks. Live biome wildPlantRegrowDays 0.1 during override, 9.0 after restore; setting readback "0".
- Verdict: row UNMEASURED by design (shipped 7-day 25%/60% fractions INFERRED from the 90x-compressed run). Earlier uncompressed 7-day run saw 0 new plants (2026-10-12b), so the compressed run is the first evidence the spawner regrows the burned patch at all.
- Logs: regrow_run.log, regrow_run2.log, Player.regrow_probe.log. Owner ModsConfig md5 ee01dae9e30d121c78d88e474dacd8e8 restored; game down; bridge released.
