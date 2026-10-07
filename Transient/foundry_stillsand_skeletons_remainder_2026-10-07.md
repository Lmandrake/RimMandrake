# STILLSAND_SKELETONS_REMAINDER_1 — FOUNDRY offline pass 2026-10-07

Status: BUILT offline, never loaded.

## Built
- §2 dune burial: `Building_GiantSkeleton` samples `Map.sandGrid` under its footprint every 2500 ticks;
  hysteresis in `src/RimMandrake/Stillsand/Source/RM_SkeletonBurialLogic.cs` (bury 0.6 / strip 0.3,
  provisional). Buried = sand tint, harp silent, inspect line, message. Toggle `duneBurialEnabled`.
- §6 passers: HerdMigration + ThrumboPasses get the horizon letter/plume/delay and enter from the
  announced bearing (one-shot entry-cell override). Toggle `horizonPassersEnabled`.

## L0 proof
- `winbuild.py` Stillsand: Build succeeded (DLL + .srchash).
- `src/RimMandrake/Utils/selftest_skeleton_burial.py`: PASS 28/28; a mutated hysteresis turns 3 checks red.
- `selftest_stillsand.py`: PASS 106/106 (settings defaults updated in validation.py).
- `run_selftests.py`: 214/216, the two known env failures (tool_metadata, utinnipatches_dump).

## Left
- §4 giant bone (waits DESIGN_MATERIALS_REVIEW_1), §8 live proof (L2).
