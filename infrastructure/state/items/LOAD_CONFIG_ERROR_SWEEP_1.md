# LOAD_CONFIG_ERROR_SWEEP_1 — the 19 third-party config errors, and a baseline

## spec

Every load of the full 589-mod list logs the same 31 `Config error in …` lines
and 5 `Could not resolve cross-reference` lines. MEASURED 2026-09-03 and frozen
as a baseline in `infrastructure/state/facts/config_error_baseline_2026-09-03.txt`.

**12 are ours and are ACCEPTED, not defects** (owner, 2026-09-03): the Fire
Ecology ash ladder deliberately gives a burned terrain a flammable `burnedDef`
so ground burns to trace ash and trace ash burns onward (0.6 → 0.4 → 0.2 → 0,
terminating at `RSW_FE_Ash_Deep`). Vanilla's `TerrainDef.ConfigErrors()` assumes
`burnedDef` is terminal; the check is advisory and never blocks the load or the
mechanism. ⛔ **Do not "fix" these by zeroing Flammability or clearing burnedDef
— that deletes the ecology.** Both `AshLadder.xml` and `ScorchableGround.xml`
carry that note in the file itself.

**19 are third-party** and are this item: nine sign buildings ("impassable,
player-buildable building that can be shot/seen over"), a handful of pawnkind
`ConfigErrors()` null-refs (`CannibalPirate`, `PirateYttakin`), two
`MissingMethodException: Default constructor not found for type System.String`,
and a missing `AudioClip`. The 5 cross-reference failures are quest-reward stack
defs that do not exist (`MealSimple10`, `Chemfuel60`, `Steel75`,
`ComponentIndustrial12`, `Silver120`).

Low priority: none of this affects play. The value is **a clean baseline** — with
31/5 as the known floor, a genuinely NEW error becomes visible instead of hiding
in the crowd, which is the only reason to spend anything here.

## verify

A load produces no `Config error` or cross-reference line that is not in the
baseline file; anything new is investigated, and the baseline is only ever
updated deliberately with a note saying what changed and why.

## criteria

1. **The 12 Fire Ecology lines stay.** They are ruled accepted; removing them is
   a regression, not progress.
2. Any third-party fix is a patch in our own mod, never an edit to someone
   else's mod folder — the game loads from Steam and a hand-edit there is lost
   on the next Workshop update.
3. A patch that matches nothing logs nothing: validate with `validate_patch.py`
   using both `--live` and `--defs`, and confirm the error count actually drops
   against the baseline rather than assuming it did.
