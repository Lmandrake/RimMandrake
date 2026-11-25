# RIMMANDRAKE_BURN_TO_LINE_WARNING_SWITCHED_AT_THREE

Make both account engines use the live account down to its line. At the warning line each live run is warned (save
a note, publish what is done, keep working), new work still starts, and the switch goes at the line.

Measured 2026-11-24 4:56 PM PST: the engine switched Archmagi from lukas to steven with lukas at 3% left, line 1%.
Cause, in both engines: the warning line was treated as the end of the account. `switching_plan._decide` took the live
account out of the targets at its warning line (`elig[live] = False`) and counted it spent there; `account_plan.decide`
set `under = pl <= warn`. With no live run the switch then went at once.

## refs
file: src/RimMandrake/Utils/switching_plan.py
file: src/RimMandrake/Utils/account_plan.py
file: src/RimMandrake/Utils/account_end.py
file: src/RimMandrake/rimflow/control.py
file: src/RimMandrake/rimflow/detached_helper.py
file: design/specs/2026-11-24-account-end/boundary.md
file: design/specs/2026-11-24-account-plan-one-file/boundary.md
file: skills/rimflow-operations/SKILL.md

## spec
1. At the warning line each live run gets a warning (control mode `warn`, said once by the run's hook): save a note,
   publish what is done, keep working. The warning says the percent, the burn and the minutes to the line. It ends no
   run.
2. New work still starts between the warning line and the line. The notice carries the warning text, and a detached
   run that starts there gets it in its start package (`detached_helper.account_warning`).
3. The switch goes at the line, not at the end of the last run. Zero live runs above the line is not a reason to
   switch.
4. At the line the steps stay as they were: at 1% with a run live the emergency order, the pause, the switch; at a
   line above 1% the save order, and the switch when the last run has ended (or at 1%).
5. No line, order or hold changes. Steven's leave line stays.
6. The texts that said "told to save and end at the warning line" are corrected: docstrings, both boundary pages, the
   order texts, `skills/rimflow-operations/SKILL.md`, `design/RimMandrake/standing_rulings.md`, `switching_plan.json`
   provenance.

## verify
- `python3 src/RimMandrake/Utils/selftest_account_end.py` (promise `the-account-burns-to-its-line`, old engine).
- `python3 src/RimMandrake/Utils/selftest_account_plan.py` (promise `the_account_burns_to_its_line`, new engine).
- Planted faults: `python3 src/RimMandrake/Utils/account_end_mutants.py`, `python3 src/RimMandrake/Utils/account_plan_mutants.py`.

Readings (2026-11-24, PST):
- RED on the parent d84261ed69: selftest_account_end 7 FAIL, all in the new check (system at 3% and 2%, line 1%, no
  run live, lukas with headroom: `do` switch, to lukas); selftest_account_plan 7 FAIL, all in the new check (the same
  frame: switch to lukas; a live run got `at_easy_spot`, a stop order).
- GREEN after the fix: selftest_account_end PASS (0 failed); selftest_account_plan 0 FAIL; account_end_mutants 49 of
  49 caught; account_plan_mutants 74 of 74 caught; the 29 pipeline suites whose inputs the change touches: 28 PASS,
  then the one red (selftest_switching_plan.py, a check that asserted the old switch at 1.5%) corrected and passing.

## criteria
- Live account at 3%, line 1%, zero live runs, another account with headroom: the decision is no switch, and new
  starts are allowed (both engines).
- At 1%: the switch (both engines).
- A live run between the warning line and the line gets a `warn` order, said once, never a stop order.
