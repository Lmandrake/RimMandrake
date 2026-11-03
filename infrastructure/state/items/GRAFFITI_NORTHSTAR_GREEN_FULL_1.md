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
