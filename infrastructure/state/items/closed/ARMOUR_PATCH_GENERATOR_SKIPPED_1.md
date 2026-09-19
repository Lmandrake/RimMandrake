# ARMOUR_PATCH_GENERATOR_SKIPPED_1 — the defence generator was never in the pipeline

Found 2026-08-29 during `OFFICIAL_DUMP_REFREEZE_1`'s follow-up `refresh.py --all` run: the
run's own verdict flagged NOT current because `validate (with --live)` failed —
`FAIL TOTAL - 10 file(s), 160 error(s), 318 warning(s)`.

## Cause, read not guessed
`src/Jawa/Jawa_Armoury/Source/` holds TWO separate generators: `gen_armour_patch.py`
(defence — damage categories, armour ratings, penetration, leather) and
`gen_armoury_patch.py` (weapons — melee power, ranged damage, torpedo speed).
`refresh.py:do_patches()` only ever called `gen_armoury_patch.py` (plus
`gen_torpedo_speed.py`) — `gen_armour_patch.py` was never in the pipeline at all. Its
output (`Armour_Leather.xml`, `Armour_Penetration.xml`, `Armour_Ratings.xml`,
`Armour_DamageCategories.xml`) was last generated 2026-08-13 and never touched again,
while every mod-list change since then (582→584 mods, and whatever preceded that)
silently drifted it: `Armour_Leather.xml` referenced 12+ leather defNames
(`Grimstone_Leather_Griffar`, `Leather_Skunk`, `AEXP_Leather_Wildebeest`, `ABYautja_Leather`,
…) that no longer exist in the live game — dead-mod or cherry-pick collateral, patched
against a roster nobody re-checked.

`refresh.py --all` DID regenerate `observed/2026-08-13/inventory/animals.csv` (the input
`gen_armour_patch.py` reads) on every run — the input was fresh, the generator that reads
it just never ran.

## Fix
- `python3 src/Jawa/Jawa_Armoury/Source/gen_armour_patch.py` — regenerated all 4 files
  against the just-frozen `OFFICIAL-2026-08-29` (584-mod) dump. 153 leather operations
  (down from whatever pre-drift count), 132 penetration, 149 ratings, 4 damage categories.
- Re-validated: `OK TOTAL - 10 file(s), 0 error(s), 278 warning(s)` (warnings are the
  advisory add-if-missing `nomatch` shape, expected).
- `refresh.py:do_patches()` now calls `gen_armour_patch.py` before `gen_armoury_patch.py`
  — both run on every `--patches`/`--all`, so this cannot silently re-drift.

## criteria
- [x] Root cause named from the pipeline code, not guessed.
- [x] Stale patches regenerated against the current frozen dump; validate 0 errors.
- [x] `refresh.py` fixed so the gap cannot reopen silently.
