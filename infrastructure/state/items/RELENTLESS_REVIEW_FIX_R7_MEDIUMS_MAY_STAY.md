## What
Severity-graded Codex review r7 of `src/RimMandrake/rimflow/relentless.py` (RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN, 2026-11-06) left MEDIUM and LOW findings that do not block clean under the owner's card of 2026-11-06 ("smaller bugs can stay"). Each is unverified: triage (fix with a red row, or reject with the reason); line numbers are as of 67f7524638.

Raw reviews: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\review\r7\rev_part0.txt` .. `rev_part8.txt`, `rev_whole1.txt`, `rev_whole2.txt`; HIGH triage in `triage.md` beside them.

Named from the final whole-file pass and the HIGH triage:
1. `retire()`: reads the raw `lease` where enrolment uses `lease_live()`, so a retained expired lease can retire a queued item for good.
2. `check_resume()`: refreshes `at` but keeps the old `deadline`, so a checker resumed past it does work no verdict can record (it now expires instead of trapping, since e8c7158e6f, but the work is wasted).
3. `help_step()`: consult admission ignores quarantine holds.
4. `account_lost()`: a pilot session cut by the account can resume as a builder (`sat_gen`).
5. Surviving quarantined runs are not counted toward `max_workers` (graded down from HIGH: each needs a failed kill and raises an alarm; counting them lets one unkillable unit stop all work at cap 1).
6. `contract()`: a proof-only worker replaces its proof without `rebind`'s screen (graded down from HIGH: the blind Marker still judges each clause).

RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN ran its own r7 alongside; check its landings before fixing anything here.
