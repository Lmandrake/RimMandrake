## spec
The indep7 independent round (BENCH, 2026-10-30, against 4c2c14c6af) wrote 30 new mutants of
src/RimMandrake/Utils/arena/testpilot.py in areas no earlier round targeted. 10 die; 20 survive the selftest.
No surviving mutant is a behaviour defect in the pilot as committed. Each one is a guard that
selftest_arena_testpilot.py does not have. Likely equivalent: g10 (taint_note already refuses a note on a PASS)
and g27 (in_flight is cleared before every non-live status). g4 and g12 err toward re-running, so they are
low value. Add a guard for each of the rest, or record why it is equivalent:
- g1 _read keeps an unterminated tail line (torn jsonl)
- g3 an Assemblies/ path not classed cs; g4 a /defs/ path without .xml classed live
- g6 a parent from another item accepted; g8 the auto parent is the oldest attempt instead of the newest
- g9 the repair key ignores the plan entry (scn_hash); g11 an uncertain parent taint does not win
- g12 argv flags counted as footprint files
- g13 reload cost ignores profile/tier; g14 the cheap threshold is strict (<120 instead of <=120)
- g17 every needed candidate counted as sealed; g18 the drain counts other lanes' tests
- g19 reload_save keeps canary_red; g20 a failed reload_save never resolves
- g21 the default taint is None; g24 live fails counted per record instead of per distinct candidate
- g26 the churn alarm never fires; g29 duplicate scenario ids accepted
Hygiene in the same file: presence remnants no test uses. Delete them: FakeDriver.owner_back and
owner_returned (about l57, l136); fresh(owner_playing=) writing cfg archmagi.owner_playing (about l164-169);
the dead "yield" action checks (about l893, 937, 952). The classify() docstring says "Unknown changes are never
live", but classify(None, False, []) with no mods returns live. Correct the docstring or the code.

## verify
Re-run D:\ClaudeWork\rimmandrake\arena_testpilot\indep7\mut8.py mine8 against the new HEAD tree: every
non-equivalent g-mutant RED. The prior sets (builder, mine, mine6, mine7) stay RED, except n15 and f4, which
are judged equivalent.

## criteria
- A1 L0: the 18 non-equivalent mine8 survivors die, and prior sets do not regress

## evidence
D:\ClaudeWork\rimmandrake\arena_testpilot\indep7\mine8.py, mut_mine8.txt, PROGRESS.md
