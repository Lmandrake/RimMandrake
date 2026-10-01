# PYRELANDS_GREEN_FULL_1 — Pyrelands north star GREEN on the full mod list

**For:** FOUNDRY (bridge; one owner-present step possible). **Parent:** PYRELANDS_NORTHSTAR_TRIAL_1.
**Plan:** `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md` §3.1 (full-list route), §8 finding 19.
**Depends on:** PYRELANDS_GREEN_MINIMAL_1 and BIOME_MOD_UNIFICATION_1.

## acceptance

- [ ] Boot `ModsConfig.FULL.LATEST.xml` to the menu. ⛔ No `start_debug_game_ready` on the full list.
- [ ] Load a **scratch** full-list save, never the campaign save. If none exists, the owner makes
      one through the menu once, and it is recorded here.
- [ ] Re-tile a 2-ring patch, then `world_tile_map_generate` to get a **freshly generated** map under
      the full list. Loading a tier-made fixture does not count.
- [ ] Bars 1, 2 and 4 are censused on the interior tile, with a quadrant split to separate
      biometransitions bleed from injection.
- [ ] Every bar passes. The run is recorded with `rimflow verify … --config full-latest`.
