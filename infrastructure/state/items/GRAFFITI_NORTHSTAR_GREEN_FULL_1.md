# GRAFFITI_NORTHSTAR_GREEN_FULL_1

Parent: `GRAFFITI_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`, §3.1 (full rung), §3.14 and §6.8.

## spec
Run the same suite on the owner's FULL list:
1. a **fresh launch** on that list;
2. verify `RunningModsListForReading` against FULL.LATEST;
3. a fresh quicktest map and site.

Foreign mark defs from SacredGraffiti and GraffitiImperial go into separately reported compatibility
components, never into Graffiti's bars. This needs the driver's full-list mode, which `modcheck run`
cannot do: it records only `min+<mod>`.

## acceptance
- Every Graffiti bar passes on the full list, and the state predicates pass.
- Recorded with config `full`.
- Every full-list-only difference is listed in the sheet: pool members, cleaning mods, camera mods.

## test pilot sitting, gen 11 (2026-11-03, offline, from the A2 live log and its results JSON)
A2 live 2026-11-03T14:36Z (`/home/mandrake/rm/relentless/live/GRAFFITI_NORTHSTAR_GREEN_FULL_1-A2-20261103T143618Z.log`) failed on three separate causes:
1. **HARNESS, proven** — `mental_break_spree` and `spree_wall` force `RM_GraffitiPaintingSpreeBreak` and then wait; the companion's vitals latch reports the painter's new mental state (kind `mental`, severity `threat`, JawaBenchVitalsCore.cs KMental) and `clockgate.resumable_stop` resumes it only inside a declared `clockgate.expected_disturbance`. validation.py declares none, so both rows read UNMEASURED on every run. Guard: `src/RimMandrake/Graffiti/selftest_graffiti_spree_surprise.py` (red now; green with the minimal declaration; red if the declaration also resumes another pawn's Berserk or a painter's death). OWED (code worker): wrap both waits in an expected_disturbance scoped to the painters' own ids and the spree state; then add to validation.py's anti-guessing notes `RULED OUT: the spree mod fails to start` (mentalStateAfter read RM_GraffitiPaintingSpreeState; the stop was the harness).
2. **SITE** — judge_cli died ENOSPC: `/tmp` (tmpfs, 18G) 97% full of other workers' mutation copies. Filed `NSJUDGE_TMPDIR_FIX_TMPFS_FULL_OF_MUTANTS`.
3. **SITE, unproven theories** — `forced_paint_job` stopped on `hostile_arrival: Toughspike (other)` (a wild hostile on the quicktest map; prep does not clear strangers before the wait); `spree_wall.spree_runs` stopped on `death: died: Crush` at 60 ticks (theory: roof collapse after `clear_area` removes supports under an overhead roof). Neither was tested live this sitting.

## test pilot sitting, gen 17 (2026-11-03, live on Archmagi)
Both A2 runs on 913a1f28 (17:55Z, 18:11Z) were REFUSED at pre-flight `site:map_size` (120x120 < 150). **HARNESS, proven live:**
`prove_quicktest_world.py` never starts a fresh game when one is already Playing. `rimworld/start_debug_game_ready` waits
for the entry scene (`blockingReason "A game is already loaded."`) and returns `success:false` after 280 s; the script ignores
that, sees the old game Playing and exits 0, and `northstar_full.py` proceeds on whatever map is current. Here that was a
120x120 RM_GelatinousSlime colony another session generated (TILEGEN_SILENT_REUSE_1 in Player.log). Guard:
`src/RimMandrake/Graffiti/selftest_graffiti_fresh_quicktest.py` (red now; green with the minimal fix). Filed
`QUICKTEST_FRESH_FIX_OLD_GAME_PASSES`. RULED OUT: the quicktest itself makes a 120x120 map (its home map was 0, RM_TheRot);
Graffiti's code makes that map. OWED (code worker): the fresh-map step leaves a Playing game first and exits 1 unless the start
answered success and exactly one map is loaded.
