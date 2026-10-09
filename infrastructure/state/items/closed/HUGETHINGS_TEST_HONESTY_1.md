# HUGETHINGS_TEST_HONESTY_1 — Huge Things test apparatus honesty

Filed 2026-10-07 by BENCH from `HUGE_THINGS_GPT_REVIEW_1` (full GPT review of the merged Huge Things, `c954ccdca`). Mod: `src/RimMandrake/HugeThings`. Do not deploy as part of filing.

## spec
Verified fix-now findings from `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (triage `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW_TRIAGE.md`) on the mod's own debug and test tools.

- **C3.7**: `validation.py` `_restore` (`:265-269`) writes `DEFAULTS[field]`, the wake tests (`:582,593`) use it, and the trunk test hard-codes `True` (`:386`). A run overwrites the player's settings. Fix: snapshot with `_raw(get)` before `_put` and restore that in `finally`.
- **C3.8**: at `--fuzz-scale 0`, the plant and seam families run zero iterations and print PASS, and `Program.cs:48` prints ALL PASS. With `--fuzz-seed` the families print "1 cases" having run none (`HugeThingsFuzz.cs:619`, `HugeTitanFuzz.cs:146`). Fix: reject scale ≤ 0 centrally and fail when the total case count is 0.
- **C3.9**: `selftest_hugethings_footprint.py` uses bare `assert`, so `python -O` passes everything. Fix: refuse to run when `not __debug__`.
- **C2.5a**: the `HugeThingsFuzz.cs:15` header says "whole-board flood", but `CasePlanner` floods the window. Fix the claim, or enlarge the board.
- **C2.5c**: `CaseCache.Fresh` (`:465`) returns "-" when blocking is off, which discards selection, and nothing counts recomputes. Fix both.
- **C2.5d**: the kernel `PawnHitbox` union is never fuzzed. Add a case.
- **C2.6**: `CaseBoundary` nudges by 1e-4, inside the oracle's 2e-3 ambiguity band (`:125,180-181,238`). Add exact-equality and ±Eps-outside fixtures.

## verify
Each fix is shown to bite: a zero-scale run fails, `python -O` refuses, and the boundary fixtures fail when the inclusion rule is flipped.

## criteria
A1: the seven bullets are fixed. A2: run_selftests stays green.

NEXT: claim it and fix the bullets in order, citing the review IDs in the commit.
