# BOUNDARY: a red decider whose red run is stale is rerun before a builder is spent, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation_dispatch.py` (`stale_red`, `red_deciders`, `stale_key`). The callers that
route on them stay as they are: `cert_red_decide`, `cert_rerun_decide`, `cert_wait`, and the rerun worker's `key_after`.
Item: `RIMMANDRAKE_RERUN_STALE_RED_DECIDER_BEFORE_ANY_BUILDER_RUNS`, written 2026-11-23. The case: Explosive
Knockback's T_SETTINGS_SCREEN was recorded red with the unscoped command (855/856, the failing row was FlowWorks').
The table's command was then scoped to `--mod ExplosiveKnockback` (7/7, rc 0). The certificate refused the decider on
`green` and on `ran_on_this_build`. `red_deciders` read it as red, so the tick would have launched an offline builder on
Knockback for a red that one zero-token rerun clears.
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_stale_red_rerun_first.py`.
This page covers only these three functions; the rest of the file has its own pages.

## ACCEPTS (the only inputs this is built for)

- **a-certificate-reading.** The dict from `judge_certificate.certify`: `rows`, each with `test`, `clause` and `status`.
  A missing or non-dict certificate reads as no rows.

## DOES NOT SURVIVE (not promised)

- **a-decider-that-changes-what-it-reads.** A rerun that leaves the decider stale again is not handled here. It is the
  rerun's own "left its own build stale" wait in `cert_rerun_decide`.

## PROMISES (each one is owed a test of the same name)

- **a-stale-red-decider-gets-the-free-rerun-not-a-builder.** A decider refused on `green` and also on
  `ran_on_this_build` (its red run is of an older build or an older command) is not in `red_deciders`. `stale_key`
  gives a key for it, so the tick starts the zero-token rerun.
- **a-fresh-red-decider-still-gets-the-builder.** A decider refused on `green` whose run is on this build stays in
  `red_deciders`, and `stale_key` is None, as before.
- **a-fresh-red-beside-a-stale-red-sends-the-builder-on-the-fresh-one-only.** With one fresh red decider and one stale
  red decider, `red_deciders` names only the fresh one.
- **a-key-for-stale-stamps-alone-is-unchanged.** A certificate that refuses only `ran_on_this_build` rows gets the same
  key as before this change.

Later lists beside this page: `polish.md` (none yet) and `next_version.md` (none yet).
