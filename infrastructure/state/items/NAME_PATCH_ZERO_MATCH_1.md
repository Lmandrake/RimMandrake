# NAME_PATCH_ZERO_MATCH_1 — gen_name_patch.py matches 0 of the doc's 41 rows against either cast

## Found while resolving `ROSTERS_TO_CAST_BIOMECAST_DEFS_STALE_1`, 2026-09-20 FOUNDRY

While verifying `cast_assignment.csv`'s downstream consumers before regenerating it for
real, `design/Jawa/fauna/gen_name_patch.py` was run (dry, before any commit) against the
newly-corrected CSV. It reported **0 renames**, 41 of 41
`design/Jawa/worldbuilding/creature_names_ashkarr.md` rows unmatched — a wipe of the
shipped 37-rename patch (`design/Jawa/fauna/CreatureNames_Ashkarr.xml`, last written at
`c4a50c968`, "37 creature renames ship wrapped").

**Not caused by the biome-name fix.** Re-run against the OLD (pre-fix, still
pre-migration-named) `cast_assignment.csv` from `HEAD` — **also 0 matches, 41
unmatched**. The doc's label keys (`Andrewsarchus`, `Castoroides`, `smilodon`,
`woolly mammoth`, …) don't match ANY row in the cast today, old CSV or new. This is a
pre-existing drift between `creature_names_ashkarr.md` and whatever cast content
actually produced the shipped 37-rename patch — unrelated to biome defNames.

The accidental overwrite from testing this was reverted (`git checkout --
design/Jawa/fauna/CreatureNames_Ashkarr.xml`); the shipped 37-rename patch is untouched
on disk and in the deployed mod.

## Owed

1. Work out whether `creature_names_ashkarr.md`'s label column drifted (the cast's
   `label` values changed under it — resize/diet-constraint re-runs are named in the
   script's own "NOT missing defs" note) or the matching key itself broke (case,
   whitespace, a defName vs label mismatch).
2. Until fixed, `gen_name_patch.py` cannot be used to add any new rename even though 41
   candidate rows are sitting in the doc — treat any future run's "0 renames" as a red
   flag needing this fixed first, not as "nothing to rename".
