# LARGEPAWNS_BRIDGE_HARDENING_1 — Large Pawns bridge hardening

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
From `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`).

- **B3.15 (owed by ruling)**: the closed `TITANIC_CREATURES_MOD_1` (lines 47-49) orders Large Pawns' own `PathClearingUtility` wall-break (three settings bools) turned OFF, so our curated crush table is the only destruction authority (card #3). `LargePawnsBridge.TryReconcile` sets only `size2Min/size3Min/size4Min` and the override rows. No code anywhere touches the clearing switches. Fix: resolve the three bools from the installed Large Pawns (decompile notes: `design/Jawa/worldbuilding/research/large_pawns_decompile_2026-09-09.md`), force them off at startup, and log the result. ⚠️ This exposes the blocked-route gap; pair with `TITAN_BREAKTHROUGH_CLEARING_1`.
- **B3.16**: `TryReconcile` writes settings (`:78-80`), then rows (`:82`), then `NotifyEdited` (`:84-85`, skipped silently if null). The catch (`:91-96`) claims an "untouched ladder" after partial edits, and a missing `sizeOverrides` only warns while success still logs. Fix: resolve every member first, snapshot, apply, roll back on throw, and claim success only after `NotifyEdited` ran.
- Note B3.17 (force-in rows pin adult size while tier uses current size) is PARTLY verified. Read Large Pawns' row precedence while you are in there and record it in this item.

## verify
Live, with Large Pawns active: its three clearing bools read false after startup. A forced exception mid-reconcile leaves its settings byte-identical.

## criteria
A1: wall-break is off and logged. A2: reconcile is atomic. A3: B3.17 precedence is recorded.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
