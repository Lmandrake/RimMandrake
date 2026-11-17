# RIMMANDRAKE_FIX_SWITCHING_PLAN_EXCEPTION_MARKERS

## spec
Codex full-file review 2026-11-17 of `src/RimMandrake/Utils/switching_plan.py` (+ exceptions selftest). Findings,
each a concrete scenario; report `/mnt/d/ClaudeWork/rimmandrake/conductor/codex_reviews_20261117.md`, raw
`/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r1.txt`. Nothing fixed in this item's filing.

1. **URGENT, live today (med).** `decide()` line 412 (the markers loop): a done/`under` marker for an account left at its
   standing line keeps it out of `elig` until its reset, ignoring that a dated exception has since lowered that line.
   Live: marker `use_steven_to_system_20261118` (steven left at 52% on 11-12, under=true) + exception
   `STEVEN_AFTER_SYSTEM_TO_35_UNTIL_HIS_RESET` (steven usable down to 35%). When system hits its line the engine will
   pick lukas / hard-stop, leaving steven's ~20% (55% -> 35%) unspent. Acceptance (exit 0 when fixed; exit 1 on base,
   measured 2026-11-17): `python3 /mnt/d/ClaudeWork/rimmandrake/conductor/cr/probe_marker_exception.py`
   (control with markers={} picks steven). Fix idea: a marker excludes only while the line it recorded still binds
   (record the line / compare against the line in force now).
2. (med) line 594 `pool()`: the present budget's deadline `e` ignores exception expiry, so a budget made accessible only by an
   exception that ends in 2 h is reported as due at the reset (pace understated).
3. (med) line 602 `pool()`: later refills (`ef + k*WEEK`, k>=1) reuse the first refill's exception-adjusted `fln`, so
   refills past the exception's end are overstated (65% instead of 48% in the reviewer's case).
Acceptance for 2-3: write a pool() case in selftest_switching_plan_exceptions.py that fails on base first.

Files: src/RimMandrake/Utils/switching_plan.py, src/RimMandrake/Utils/selftest_switching_plan_exceptions.py

## refs
file: src/RimMandrake/Utils/switching_plan.py
file: src/RimMandrake/Utils/selftest_switching_plan_exceptions.py

## criteria
- probe_marker_exception.py exits 0; findings 2 and 3 each have a selftest case that failed on base.

## verify
python3 /mnt/d/ClaudeWork/rimmandrake/conductor/cr/probe_marker_exception.py && python3 src/RimMandrake/Utils/run_selftests.py --only selftest_switching_plan_exceptions selftest_switching_plan
