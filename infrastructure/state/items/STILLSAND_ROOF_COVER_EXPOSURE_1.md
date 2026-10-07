# STILLSAND_ROOF_COVER_EXPOSURE_1 - Stillsand roof cover above 55 degrees

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Stillsand `sun/sun_roof_cover_above_55deg` FAILED: roofs verified placed (36 cells) but shadegrid_read gave exposure 1.00 under the roof at 60.5 degrees. Unresolved: mod defect (ShadeGrid ExposureAt ignores roof above 55) or stale ShadeGrid cache / read in the same tick as set_roof_batch. Evidence: Transient/green_min_runs2_20261007.md line 32; related item STILLSAND_SUN_LIVE_VERIFY_1 (roof criterion). Test by stepping >=1 tick (and past the grid refresh interval) after the roof batch before reading.

## verify
Quicktest Stillsand map at ~60 degrees; place roof, step ticks, read RM_MapComponent_ShadeGrid ExposureAt on a roofed and an open cell.

## criteria
A1: classified mod vs stale-cache vs harness with the evidence recorded.
A2: after correction, a roofed cell at >55 degrees reads exposure < 1.0 (expected 0 or the documented roof value) and an open cell reads 1.0; sun_roof_cover_above_55deg PASSes in a modcheck run.

## live check
New mechanism never seen: the ShadeGrid roof-cover read above 55 degrees has never been seen correct live.

NEXT: claim this item and start with criterion A1.
