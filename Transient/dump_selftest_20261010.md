# dump selftest 2026-10-10
Cause: DEF_DUMP capture 2026-10-10T09-00-30Z (live game, ~23 min load; refresh.py cannot rebuild it). Label renames 348100802 landed 09:02:22Z, 2 min after capture. dump_presence_findings skipped absent defs whose file changed after capture but not label drift -> logic gap, not a def defect.
Fix: label drift gets the same changed-after-dump skip (validation.py) + selftest case. Next live dump capture makes the skip moot.
