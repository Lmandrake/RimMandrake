# CONTAGION_ARMS_UNTANGLE_SITE_ALREADY_SICK

Filed by BENCH 2026-10-16 (sites tooling b4d14d44c8). Packet: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md`
§1.2 row 2; live order `Transient/biome_sprint_live_order_2026-10-16.md` step 4.

## Mechanism (read first)
- `src/RimMandrake/Contagion/northstar_site.py` refused any RM_Contagion map, so the driver refused the saved site.
- Inside the suite only two components need a stock map: `repulsor_clear.site_ready_baseline` (the Repulsor's
  off-Contagion code path) and `site.retile_to_contagion` (its control). Every Contagion code path decides on the
  live `Map.Biome` alone (`RM_ContagionSky.ExtFor`), and `RM_SkyKernel.Tick` resets the sky to `Fresh` at its first
  poll off the biome.

## Built (offline)
- `validation.py` `_off_contagion`: on a sick start re-tile the map's own tile to `AridShrubland`, wait one sky poll,
  record the START biome; both stock-map components call it; `site_restore` returns the START biome (RM_Contagion on
  the saved site). A stock start is unchanged. Off-retile that does not take -> UNMEASURED, never PASS/FAIL.
- `northstar_site.preflight` no longer refuses RM_Contagion; it still needs a >=150 map with a world tile.
- `selftest_contagion.py`: a sick-start healthy run is 80/80 PASS, takes the map off first and ends on RM_Contagion;
  a sick start whose off-retile no-ops reads UNMEASURED (no red); the preflight accepts the sick map. Sanity: with
  the off-retile removed the sick start goes red (`repulsor_clear.holds_sky_clear` FAIL).

## criteria
- L0: offline selftests and the Contagion preflight green on the change.
- L1: one full live driver run on the loaded `contagion` saved site, recorded, with `repulsor_clear.*` and
  `site.retile_to_contagion` read on the off-retiled map and `site_restore.restore_tile` returning RM_Contagion.
