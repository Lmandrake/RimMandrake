## spec
🔑 **THE WHOLE POINT: three Inhabited items need `save → quit to desktop → reload`,
and the W9 world edits want exactly the same cycle to prove they persist. One quit
serves both.** Doing them separately costs two extra cold loads at ~25 min each.
⚠️ And the Inhabited chain has an order forced on it: `INHABITED_ROUTE_ONE_DAY_1`
and `INHABITED_POOL_ROUND_TRIP_1` both say "depends on ROSTER_SOAK_100_DAYS_1
passing". They are not runnable today unless the gate clears in load 2.

── LOAD 1 ────────────────────────────────────────────────────────────
0. `python.exe src/RimMandrake/Utils/first_light.py` — one minute, all reads.
   Then score `PRELOAD_PREDICTIONS_578_1`, all seven, before touching anything.
1. FREE AT LOAD TIME, costs nothing extra, do it while reading the log:
     `INHABITED_DEFS_LOAD_CLEAN_1`  — the four defs load, the Harmony patch binds
     `CAST_ROSTER_269_LOAD_1`       — the 269 load and one can be looked at
2. W9 stages, in §12 order — the order is not a preference:
     tiles → links → mutators(CLEAR the 817 stale Coast, not import) →
     landmarks(SKIP, no source) → settlements → features → `world_commit`
   🔴 `world_links_import` is stage 2 and its fix is untested. If it refuses,
   stop and debug it there; everything downstream assumes rivers exist.
3. `world_lint`, then LOOK, against `world/view/ASHKARR_WORLDMAP.biome.equirect.png`.
4. Inhabited soak SETUP: dev mode, debug category `Inhabited` —
     `Create place at current tile` · `Stuff roster (3 pawns)` · `Report roster`
   🔴 **KEEP THE REPORT OUTPUT. It is the baseline and it cannot be recovered
   after the quit.** Write it to a file, not to a chat window.
   ✅ **HANDLED IN CODE, 2026-08-20 pre-load — you do not have to copy anything.**
   You were right and the harness was wrong: `Report roster` wrote only to
   `Player.log`, which the launcher ROTATES at every launch, so the baseline
   would have been destroyed by the very quit this plan depends on. Both report
   actions now APPEND to
   `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\InhabitedReports\roster_reports.txt`
   and log one line naming that path. The file is append-only and outside the
   game's data, so load 1's baseline and load 2's comparison end up in the same
   file, stamped with real time, game tick and day. Just run the action twice.
5. **SAVE.** Then quit to desktop.

── LOAD 2 ────────────────────────────────────────────────────────────
6. `Report roster` again → `ROSTER_SOAK_100_DAYS_1`. Compare field by field
   against the baseline: the sibling relation, the missing eye, the Abrasive trait.
7. Re-read the world: `world_tile_validate`, settlement count, named regions.
   That is W6/W7's proof repeated on a world that has actually been authored.
8. Only if step 6 PASSES: `INHABITED_ROUTE_ONE_DAY_1`, and
   `INHABITED_POOL_ROUND_TRIP_1` — which needs a THIRD quit of its own.

## verify
`first_light.py` reports 112 `jawa/` tools and the dump regenerates at 578.

## criteria
load 1 ends with a saved game and a written baseline; load 2 decides the gate.
🔴 The gate is the one that matters: everything else in `Inhabited` rests on a
deep-held, deliberately un-ticked pawn coming back whole. If it fails, the four
items behind it are not "blocked", they are waiting on an architecture change.

## notes
⚠️ **SUPERSEDED IN PART, 2026-08-20 mid-session — read these two first:**
   `RT_PROBE_LOAD_ABORTS_ON_578_1` — load 1 ran on a game that never finished loading.
   `LOAD2_TARGET_IS_SUB7B_1`       — load 2 targets WORLDMAP_gen_sub7b, not rt_probe.
   And the stage list below is now executable as one command:
   `python.exe src/RimMandrake/Utils/w9_run.py --apply --load WORLDMAP_gen_sub7b`
   🔑 **Step 0 is no longer first_light — it is the CANARY.** `w9_run.py` runs it itself and
   refuses to write if the debug `Actions` tree will not enumerate. That check did not exist
   when this plan was written, and its absence cost the whole of load 1.

**from:** CHECK, 2026-08-20. Owner enabled `mandrake.inhabited` and then said to try
Inhabited this session as well. That merges two plans into one, and the merge
SAVES A LOAD rather than costing one.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
