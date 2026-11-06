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

## Triage (2026-11-06, each fix has a red-without-fix row in `src/RimMandrake/rimflow/selftest_relentless_r7_mediums.py`)
1. `retire()` raw lease: HELD, FIXED. A lapsed or released lease on a queued item (proof-lines jobs included) is read as no lease, as enrolment reads it. A live lease still retires.
2. `check_resume()` old deadline: HELD, FIXED. The resume sets a new deadline with its new start, the way the consult's resume already did.
3. `help_step()` quarantine: HELD, FIXED for starts. A wanted consult waits while quarantined and its room wait starts over, so the hold never reads as a failed consult. A consult already running when the quarantine lands is left to finish: bounded by `help_max_s`, already paid for, and its retry waits too. RELENTLESS_R7_FIX_THIRTEEN_MEDIUMS_MAY_STAY also weighs manual holds; this item does not pin them either way.
4. `account_lost()` pilot resumed as builder: HELD, FIXED at the lease. The session the account cut goes on as the pilot (pilot agent, sitting moved to the new generation). If the lease moved in between, a fresh pilot sits the step.
5. Quarantined runs not counted toward `max_workers`: REJECTED. Each one needs a kill that failed, raises the `quarantine` alarm, is retried by `reap_quarantined` every tick and has its `run_reserve` held in `spend_holds`. Counting them lets one unkillable unit stop all work at cap 1, which is worse than the overrun.
6. `contract()` proof-only change skips `rebind`'s screen: REJECTED. The change still passes the reach screen and the typed-number refusal, and the blind Marker judges each clause on the item's own text, so a hollow proof reads WEAK or FAIL. Sending it through the judge would add judging machinery, which the Relentless freeze (owner card 2026-11-06) forbids.
