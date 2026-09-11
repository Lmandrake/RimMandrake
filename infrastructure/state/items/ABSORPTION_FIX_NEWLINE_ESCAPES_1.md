# ABSORPTION_FIX_NEWLINE_ESCAPES_1

Found during BESTIARY_ARMOURY_DESC_BACKFILL_1 wave 1 (2026-09-11), by re-running
`gen_additionalmods_absorption.py` to prove that wave's fixes survive a regen.

## Spec

Four entries in `src/RimStarWars/Armoury/Source/absorption_content_fixes.py`'s
`FIXES` table never apply, and have not applied for as long as they have
existed. Their `expected_broken_text` is written in Python source with `\n`
escapes, which Python turns into real newline characters. The donor XML
contains the two literal characters `\` and `n` — not a newline. The equality
check in `apply_content_fixes` therefore fails and the fix is skipped with
`CONTENT FIX SKIPPED (donor text no longer matches expected)`.

Affected defNames:

- `guy762_SWForceLightsabers_CrystalPart_heart`
- `guy762_MalgusArmor`
- `guy762_VisasRobes`
- `guy762_brifle_jurgan`

**Why it matters:** the correct text is currently present in the committed XML
only because it was hand-edited in. Any regen of the owning generator reverts
all four to the donor's broken text. This was observed, not inferred —
`Absorbed_Kotorweapons_TheForceLightsabers_HiltPartDefs_KotORColorCrystals.xml`
was reverted to the donor's copy-paste error during the backfill wave's
verification run and had to be `git checkout`-ed back.

**The fix:** double the backslashes in those four `expected_old` strings (or
make them raw strings) so they match the donor bytes. `new_text` for
`guy762_MalgusArmor`, `guy762_VisasRobes` and `guy762_brifle_jurgan` carries
the same escape and needs the same treatment, or the generator will write real
newlines where the donor pattern uses literal `\n` — check what the sibling
entries in the same donor file actually contain before deciding which of the
two forms is correct for the OUTPUT.

## Verify

Re-run each owning generator and confirm the log prints
`CONTENT FIX APPLIED: <defName> <description>` for all four, and that
`git diff` on the regenerated files is empty (i.e. the generator now produces
what is committed, rather than reverting it).

## Criteria

All four fixes apply on a clean regen, and a regen of
`gen_kotorweapons_absorption.py` / `gen_kotorcore_absorption.py` /
`gen_additionalmods_absorption.py` leaves the committed XML unchanged.

## Watch out

- `apply_content_fixes` skips silently by design when the donor text does not
  match — the skip is only visible as a `note()` line in generator stdout. A
  passing selftest proves nothing here; the selftest fixture does not exercise
  these entries.
- Do not "fix" this by hand-editing the XML again. The whole point of that
  module is that generated files are not hand-edited.
- BESTIARY_ARMOURY_DESC_BACKFILL_1 added a `MISSING` sentinel and `Name=`
  attribute keying to the same function. Those are independent of this bug and
  are proven working; do not revert them while fixing this.
