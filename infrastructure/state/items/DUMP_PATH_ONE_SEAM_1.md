## spec
Prerequisite for the dump restructure the owner called the 2026-08-21 work stop
for, and the half of it that needs no ruling from him: **whatever layout he
picks, it must have one place to change.**

Measured 2026-08-21: **21 files resolved the def dump themselves**, and the repo
carried **two path seams**, not one.

- `src/RimMandrake/Utils/game_paths.py` is the seam and already exported
  `DEF_DUMP`.
- ⚠️ `refresh.py:117-127` ran a **second** one off its own `_LOCALLOW_WIN/WSL`
  literals and re-exported `D_DUMP`, which `gen_armour_patch.py` and
  `gen_megafauna_yield.py` import. Two seams means a move of the dump has two
  places to miss and the second one has no test.
- ⚠️ `refresh._measure_scripts()` was a **verbatim copy** of
  `dump_manifest.skill_scripts()` — the one function whose docstring promises
  that if the skill moves, one file changes. The duplicate made that false.
- 🔴 Three literals were `/mnt/c`-only (`xenotype_check.py`,
  `worldmap_review.py`, `check_load.py`), so those scripts **could never run
  under `python.exe`** — the exact failure `game_paths.py` was written to fix on
  2026-08-13, grown back in three new files.

⛔ **DO NOT collapse these two — a guard that looks like a gap is a guard:**
  `.claude/hooks/block_blind_scan.py:56` and
  `skills/rimworld-start-prep/scripts/sync_mod_state.py:68` keep their own
  copies on purpose. Both must run **standalone**, and the hook's contract is to
  **fail open, always**; adding a repo import gives a guard a new way to die.
  `.claude/hooks/selftest_block_blind_scan.py` uses fixture paths, not real ones.
  `infrastructure/disposing/` is disposed-of code and is out of scope.

## verify
Offline. Every touched file imports; every resolved path re-measured **identical**
to the literal it replaced; `refresh.dump_fingerprint()` still returns
`5ef6eec3daf6c325`, so the freeze record corrected under
`FREEZE_SHA_UNREPRODUCIBLE_1` stays valid. Full selftest sweep:
`selftest_frozen_dumps` 16/16 · `rimflow` model 41/41, cli 24/24, render 16/16,
importer 21/21 · `selftest_block_blind_scan` 17/17 · `measure` 42/42. Plus
`refresh.py --fingerprint` (578 listed / 578 resolved / 0 missing) and
`validate_save_artifact.py` on `The Salvation.rid` (no dangling names).

## criteria
No file outside `game_paths.py` and the two named exceptions contains a
`LocalLow` path literal, and a NEW file that grows one is caught by a test rather
than by review.

## notes
Closed by BUILD 2026-08-21 at `86a26b8`. `game_paths` grew `PLAYER_LOG` on the
way: `harvest_log.py` carried a hand-rolled Windows/WSL pair plus two
`os.path.exists` picks, which is precisely what `resolve()` does.
