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

## 2026-10-12 offline pass (6270be0f7b) — report `Transient/pyre_site_2026-10-12.md`
- Correction: ~60 ticks/s is the stepped route (waits <= 5000). Long waits already run Ultrafast at **~200 ticks/s** (measured
  from the same log); embergrass_regrow alone is ~36 min.
- Driver writes `partial: true` results after every chain; `--chains` / `--skip-chains` split the regrow row into its own run.
- `northstar_site.py --tag anima0` rebuilds site 1 under a new fixture name (the Pyrelands def fingerprint does not change with
  the MandrakePatches anima block, so the old name would collide).
- Harness fixes: biome_probe roster read, sealed spoil/furnace rooms, spoil early stop, ignition-refusal diagnostics.
  MOD filed: SCORCH_FRUIT_FIX_ROLLS_BEFORE_THE_ASHES, PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE.
  HARNESS filed: STATIC_CALL_WIDEN_PAWNS_NEED_NOT_APPLY, PYRE_BURN_LINE_PROVE_TWO_QUIET_DAYS.

NEXT: live (BENCH, bridge) — run the five commands under "Next live commands" in `Transient/pyre_site_2026-10-12.md`
(rebuild with --tag anima0, tick_rate_probe, main run --skip-chains embergrass_regrow, reload, regrow run), then close this item
on a plant_distribution_correct PASS with Plant_TreeAnima 0.
