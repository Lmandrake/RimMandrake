# PYRE_SITE_REBUILD_ANIMA_STILL_SAVED (HARNESS/SITE, Pyrelands)

The Pyrelands northstar fixture `NS_Pyrelands_site_1_a32c5db7c6f1` (fingerprint a32c5db7…) was generated BEFORE the anima-tree block
(MandrakePatches/Patches/AnimaTree_NoRandomSpawn.xml, 7ed954bd49). `northstar_site.py --reload-only` reloads that save, so the gen
census still holds the tree: BENCH 2026-10-12 rerun read EmberGrass 33029 / Quickgrass 21580 / **Plant_TreeAnima 1**, identical to
2026-10-11, and `plant_distribution_correct` FAILs on a map the fix can no longer affect
(`Transient/bench_live_20261012/pyre_ns.log`). A fresh quicktest home map with the block deployed has Plant_TreeAnima 0 of 24,595 plants
(`Transient/bench_live_20261012/anima_census.json`).

Also measured the same run: the full Pyrelands suite cannot finish in 50 min on this tier. `embergrass_regrows` waits 180,000 ticks
and `step_game_ticks` advances ~60 ticks/s (595 ticks in 10.1 s), so that row alone is ~50 min; the driver was killed by the shell
timeout inside it (no result JSON). Last sitting the same row ended early on "clock stalled", not on a pass.

NEXT: regenerate the site fixture with mandrake.rm.patches in the tier (new fingerprint), and give the 180,000-tick waits a faster clock (or split them into their own run), then rerun the Pyrelands driver.
