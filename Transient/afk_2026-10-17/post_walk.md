# Post-walk follow-up 2026-10-17 (BENCH, offline)

## 1. T15 anomaly (red drinker got white's effect)
MOD bug (mechanism inferred from the numbers, not replayed live). `RM_ThirstUtility.noTerrainUntil` is a static
dictionary keyed by thingIDNumber: "this pawn found no drinkable terrain, don't search again for 600 ticks". It survives a
save load. b5 and b6 were each run right after `test_site_saves load calm` (the walk note "fresh load" was true of BOTH,
which is why the walk could not tell them apart). A reload restarts both the thing-ID counter and the tick, so the first
pawn spawned in b5 (red) inherited a mark from the previous calm session's first-spawned pawn; the B2 guard only drops
marks MORE than 600 ticks ahead. Red refused terrain, took a long GotoWander (the only job sampled; RM_Dehydration 0.00825
= ~1,650 ticks at zero vs 0.0015 for the others) and drank the nearest pool when it re-thought: white (its SporeFlesh
0.0022 < white pawn's 0.0096 = drank later). b6 clean because b5 had expired that entry.
False theories ruled out: cached terrain->liquid lookup (same load in b5/b6, other colours right), shared static in
RowEffects / stale hediff (fresh pawn, later drink), driver pawn reuse (every row spawns its own).
Fix: marks cleared when Current.Game changes (WeakReference<Game>), selftest assert added; FlowWorks DLL rebuilt;
selftest_flowworks_stock PASS. Driver: debug record in the docstring, T15 now flags "carries another pool's hediff" and
no longer fails on a missed 60-tick job sample when the drink memory is present; new opt-in row T15R (two reloads of the
calm site; same-ID pawn must drink within 300 ticks) is the red-before-fix check. OWED: deploy FlowWorks DLL (game
RUNNING now), then `thirst_live.py --only T15R` live.

## 2. validation.py reads thirst_live / sprinkler_live results
Done. `validation.py` `driver_rows_at` + `_driver_live_report`: THIRST_LIVE / SPRINKLER_LIVE rows read every
`northstar/{thirst,sprinkler}_live_result_*.json` that is mode live, at the current mod hash AND whose game ran the repo's
FlowWorks DLL (env.assembly_sha256; a run before a deploy certifies nothing); newest row per id wins; T21/T22 come from the
sprinkler driver; absent -> UNMEASURED naming the driver; one FAIL/UNMEASURED row no longer blanks the rest of the chain
(before, the first UNMEASURED set upstream_failed and every later row read "upstream"). New `northstar/driver_stamp.py`
stamps mode/mod/mod_hash/env.running/assembly sha into both drivers' results. Selftest
`FlowWorks/selftest_flowworks_driver_rows.py` (19 checks) PASS.
The walk's own results (Transient/review_walk_2026-10-17/live/) carry no mod_hash and predate today's DLL, so they are NOT
credited: the rows read UNMEASURED-with-command until the next live run writes into northstar/ (default out).
modcheck: `modcheck record` takes only the core v2 result (one entry per mod; any UNMEASURED row -> RED), so the drivers are
not recordable on their own; they now reach modcheck through validation.py's chains, which `modcheck run FlowWorks` records.
PRE-EXISTING RED found (not from this change): `northstar/selftest_extensions.py` and `selftest_flowworks_northstar.py` fail
because `northstar/settings_registry.py` lacks the 8 RM_ThirstSettings fields added in c72cea8a08 (bucketFirefighting,
drinkingReserveLitres, filledBottlesPerColonist, lastResortDrinking, roughDrinkPenalty, saltBreakEnabled,
sanguophageBloodQuenches, snowGathering); also "clean mock run not green" in selftest_extensions. Claimable, not done.

## 3. Code review of walk-touched files
pending

## 4. JawaBenchPawnKitTools.cs uncommitted diff
pending
