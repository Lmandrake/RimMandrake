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
pending

## 3. Code review of walk-touched files
pending

## 4. JawaBenchPawnKitTools.cs uncommitted diff
pending
