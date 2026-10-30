# TESTPILOT_HARDEN_SELFTEST_MUTANTS_ROUND3

Filed (BENCH): testpilot selftest: 13 of 21 new independent mutants survive (n15 epoch check likely equivalent; 12
real gaps): abort attribution n1-n5, n7/n8/n9 crash quarantine, n10 park counters, n12 carry supersede, n17 hot-apply
profile/tier, n18 MOD hotfix flag. List `D:\ClaudeWork\rimmandrake\arena_testpilot\indep6\mine6.py`, results
`D:\ClaudeWork\rimmandrake\arena_testpilot\indep6\mut_mine6.txt`. Blocks ARENA_TESTPILOT_BUILD_RELOAD_SCALED_BY_COST.

## verify
- L0: the 21 mutants re-run against the hardened selftest: each of the 12 real gaps killed; n15 either killed or shown
  equivalent in the note. Run by an agent other than the one that wrote the tests; the mutant list is not edited to pass.
- Stopping point: finish.

## criteria
- A1 L0: 12 real-gap mutants killed, n15 killed or proven equivalent
