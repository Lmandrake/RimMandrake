# RIMMANDRAKE_DROP_STEVEDESKTOP_PIPELINE_ONLY_LIMIT

## spec

The owner, 2026-11-17 about 11:00 AM PST: "Drop 11-14 limits, old rule. Clear its limitations. We are remeasuring it
for a brand new pipeline. Don't keep telling me we can't do things when it's from pre-maturation pipeline decisions.
Those old decisions are unlikely to be relevant anymore. At least suspect it and ask before refusing."

Delete his 2026-11-14 card's SteveDesktop entry rule (spec §8 18c, "Pipeline tests only") wherever it is enforced or
stated: any mod's token-free live tests and proof chains are submitted and filled on SteveDesktop whatever its pipeline
stage.

Kept (not this ruling's): the owner's hold on six biome mods (`src/RimMandrake/rimflow/mod_owner_hold.json`, 2026-11-16)
stays refused; no flyer flight test; the machine-safety brakes (fault monitor, hardware outage, brake release).

## verify

`python3 src/RimMandrake/Utils/testq/selftest_testq_pipeline_admit.py` and `--mutants`, then
`python3 src/RimMandrake/Utils/run_selftests.py --only` the testq selftests and `selftest_maturation.py --ingame`.

## criteria

- `testq.py submit`, fill, sweep and the fault-window rerun admit a blind-stage mod, `--full` and `--item`, and refuse
  only a held mod (and every test while the hold list is unreadable); ops requesters are never refused.
- The steward has no `IDLE_BY_RULE` state; `coverage.fill_mods` leaves held mods out.
- `src/RimMandrake/Utils/testq/selftest_testq_pipeline_admit.py` (and `--mutants`) pass; it failed on the base.
- The spec, `design/RimMandrake/maturation_pipeline.md`, the build plan and the Stage 6 brief no longer state the limit.
