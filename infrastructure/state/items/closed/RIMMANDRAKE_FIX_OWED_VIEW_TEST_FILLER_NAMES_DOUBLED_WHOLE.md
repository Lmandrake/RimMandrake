## spec
`src/RimMandrake/rimflow/acceptance/owed_view_accept.py` builds its 45 filler ids with
`"RIMMANDRAKE_PAD_SANDBOX_OWED_FILLER_%s" % "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i % 26] * (1 + i // 26)`. `%` and `*` bind
left to right, so for i >= 26 the WHOLE name is doubled (`..._FILLER_ARIMMANDRAKE_PAD_..._FILLER_A`, 74 chars, 11 words)
and `rimflow file` refuses it by namecheck. Only 26 fillers are filed, the view holds 31 lines, and the clause "past 40
lines the view ends with the --all line" cannot be met by any correct build.

Smallest fix: parenthesise the repeat, `% ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i % 26] * (1 + i // 26))`. Nothing else changes.
Measured 2026-11-15 by the E1 builder (RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE): the unedited test gives
`FAIL 16/17` on the build (only that clause red); a copy with only that fix gives `PASS 17/17`.
After the fix, close RIMMANDRAKE_LIST_CONDUCTOR_OWES_FIRST_AT_EVERY_WAKE with its build sha (its A1 is this test).

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/owed_view_accept.py` exits 0 with `PASS 17/17`. Watched failing
on the E1 build (2026-11-15): `FAIL 16/17`, exit 1, the `--all` clause red.
