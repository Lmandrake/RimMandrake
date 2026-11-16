# RIMMANDRAKE_FIX_PREFLIGHT_BARE_CUT_RED_ON_MAIN

Found by the modledger builder (RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE) on 2026-11-15: origin/main's
`src/RimMandrake/rimflow/ticket_preflight.py` prints a not-PASS check's evidence and fix with bare slices
(`[:220]`, `[:160]`), which `selftest_no_bare_cuts.py` refuses (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS). The lint is
nightly-only, so the door did not catch it. Known fix: route both through `fulltext.clip`, which says the line is cut
and where the whole text is (`rimflow preflight <ID>`). Pipeline self-fix ruling: filed and fixed in the same run.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_no_bare_cuts.py` — watched failing on origin/main 5743a1dabb
(`rimflow/ticket_preflight.py:837 ... c["fix"][:160]`, "1 fail(s)"); passes after the fix (0 fails).

## spec

file: src/RimMandrake/rimflow/ticket_preflight.py — the not-PASS summary line uses `fulltext.clip(text, n, where)`.

## criteria

- `selftest_no_bare_cuts.py` passes; `selftest_ticket_preflight.py` still passes.
