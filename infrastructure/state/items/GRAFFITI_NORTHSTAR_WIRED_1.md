# GRAFFITI_NORTHSTAR_WIRED_1

Parent: `GRAFFITI_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`, §2 (bars and bindings) and §3 (site prep).

## spec
- Rewrite `src/RimMandrake/Graffiti/validation.py` per plan §2:
  - live def sets M_base, M_pool, M_desig and M_all, never Vandal alone;
  - per-painter lanes;
  - paged, variant-pinned galleries;
  - transactional captures;
  - the new state components: `terrain_accepts`, `joy_path_paints`, `spree_paints_repeatedly`,
    `paint_interval_cadence`, the reworked `painting_toggle_blocks`, and the two missing toggles.
- Add `src/RimMandrake/Graffiti/northstar_site.py` (`prep_site`/`preflight`), covering every precondition
  in plan §3.1–3.14.
- Correct the `validation.py` docstring: it says 4 settings, and there are 6; it says there is no
  modExtensions block, and every mark def has one.
- Do not touch the walk's `## north star` section.

## acceptance
- `modcheck floor --all` reads `Graffiti … VALIDATED 8 8 0` (all must-show covered), with no orphans.
- Both cannot-show ids are claimed.
- `suite.toggles` lists all 6 settings, and `floor.uncovered` = [].
- `python3 src/RimMandrake/Utils/run_selftests.py` passes N/N.
- `validation.py` and `northstar_site.py` have had a full-file review and are `mark-clean`.
- Depends on the shared driver's calls in plan §6. Where a call is missing, file it against the driver
  item rather than hand-rolling it.
