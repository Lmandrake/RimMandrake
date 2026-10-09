# GRAFFITI_RULING_CONFORMANCE_1

Caused by `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` (forks ruled by question card 2026-10-09; rulings in that item and `design/RM_GRAFFITI_SCOPE_WIDENING.md` §7). Code: `src/RimMandrake/Graffiti/`.

## spec
- F10: `RM_Graffiti_WarningGlyph` is a `Glyph`-form / `Code`-category default member (was `Taunt`); it keeps `breachLure`. Category only gates Devotional scrub protection, so nothing else moves.
- Source comments cite the wrong fork numbers (rename called F9, scrub called F6, going-over called F7) and say "recommendation stands": rewrite to the ruled numbers (F8, F7, F4) and "ruled 2026-10-09".

## criteria
- O1 L0: the three shipped marks all read `<form>Glyph</form>`/`<category>Code</category>`; WarningGlyph still `<breachLure>true</breachLure>`; Graffiti builds 0 errors; selftests no new failure
