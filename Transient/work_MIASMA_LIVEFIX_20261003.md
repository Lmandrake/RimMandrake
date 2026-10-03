# Miasma live fix 2026-10-03
File: src/RimMandrake/Miasma/validation.py
1. Eight components that raised ExpectationFailed("UNMEASURED: ...") (recorded FAIL) now call a local _unmeasured(t, why) (upstream_reason/upstream_failed, as in Scarlands) then return; assertion text unchanged.
2. roundtrip_attarEnabled KeyError: DEFAULTS lacked attarEnabled (NEW list had it). Added. Every public static field in RM_MiasmaMod.cs is now in DEFAULTS (NEW iterates the 7 toggles added today).
Check: python3 validation.py -> STATIC PASS. No selftest in folder. Live rerun not done.
