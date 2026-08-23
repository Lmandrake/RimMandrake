## spec
`MEASURE_HELPER_FOR_MANIFEST_1`'s `## verify` block reads:

> *"Plus `selftest_measure.py` still 26/26 and `validate_patch.py`'s own selftest green."*

Wrong twice:

1. 🔴 **`validate_patch.py` had no selftest at all.** The step could never have passed —
   an unrunnable verify step that nobody tried to run.
2. ⚠️ **`26/26` is a frozen tally.** `selftest_measure.py` is **46 tests** now. A verify
   step naming a count goes stale the moment anyone adds a test, and then it either fails
   for the wrong reason or gets edited to whatever that day's number is, which is not a
   check.

## verify
`MEASURE_HELPER_FOR_MANIFEST_1.md` names the suites, not a tally, and both suites exist.

## criteria
The verify step is runnable.

## notes
✅ **CLOSED 2026-08-22.** The line is corrected in place, in the file that carried it —
`nobody reads backwards`, so the correction goes where the wrong claim was, not only here.
Both halves are now true: `selftest_validate_patch.py` exists as of `6d1e2eb5` (8/8), and
the count is gone.

🔑 **The general lesson is in the correction, not just the fix:** a verify step should name
the instrument and its expected VERDICT, never its current tally. `26/26` was true on the
day it was typed and false a week later, and its being false is what made an entire verify
step quietly unrunnable.
