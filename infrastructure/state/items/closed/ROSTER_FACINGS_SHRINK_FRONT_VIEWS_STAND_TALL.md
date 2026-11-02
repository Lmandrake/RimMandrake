# ROSTER_FACINGS_SHRINK_FRONT_VIEWS_STAND_TALL

## calibration pass (BENCH helper, 2026-10-16) - MEASURED, evidence in Transient/facing_lint_calibration_2026-10-16/PROGRESS.md
- Lint calibrated per body plan (src/RimMandrake/Utils/art/facing_body_plan.py from BodyDef parts; bands = vanilla envelope + 2%, leave-one-out vanilla flag rate 4.7%; in-sample 0%).
- Roster after: 349 FLAG of 721 measured (was 470, 65.2%); item scope 336 of 701 (was 458). 76 pictures are also too big by vanilla's own top-down envelope (`beyond_vanilla`) - the hard cases.
- Known positives hold: FireWasp and Anooba old art flag on S and N, Furnace beast old art flags on N only (S 1.295 now inside the quadruped band); all three new art pass.
- Honest limit: vanilla has no fish, 1 serpent, 1 blob, 2 bipeds, so those plans use the all-vanilla band. And vanilla's own S/E ratio (quadruped median 1.30) exceeds ours (1.23): the ~270 FLAGs that are not beyond_vanilla are over the owner's ground-camera standard, not over vanilla practice. Whether to rescale those is the owner's call (cosmetic).
- NEXT: owner picks the standard for the roster rescale - ground-camera (S/N = E, ~270 more pictures) or vanilla-envelope only (the 76 beyond_vanilla); then `facing_scale_lint.py fix` on that set. No art was changed.
