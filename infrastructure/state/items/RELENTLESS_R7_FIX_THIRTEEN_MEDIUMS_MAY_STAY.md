## spec
Medium findings from the graded Codex reviews r7 and r8 of relentless.py. Under the owner's bar (card 2026-11-06, standing_rulings.md §Code review) they do not block CLEAN; they are filed so nothing is lost. Unverified unless marked; verify each before fixing, and note that any edit here makes relentless.py DIRTY again.

Raw reviews: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN\r7\rev_part*.txt`, `...\r7\adjudicate.txt`, `...\r8\rev_whole.txt`. Line numbers are r7's, at c16d068cd3.

1. `capped_copy` (184-192): the timeout is not enforced while blocked in `stdout.read`, so a silent stalled child holds the tick.
2. `landing_key`/`_patch_ids` (1266-1304): a failed patch-id calculation reads as an empty commit, and the subject-and-author fallback can then match the wrong commit.
3. `proof_gate` (1953-1974): calls `weak_reads_pass(st)` without the store, losing its historical-verdict fallback; an old `proof_only` record can stall on `proof_unchanged`.
4. `work_sha`/`ledger_close` (3103-3155): the blind PASS on a ledger-only candidate is also recorded at the older work commit, which never ran the check. Adjudicated MEDIUM: the proof did pass on the candidate; this is wrong close provenance, not an unproven close.
5. `_carry_late` (2688-2733): a writer already waiting on the original inode can append after the suffix read, leaving that event only in the backup.
6. `worker_changed` (4039-4054): a commit a worker cherry-picks by hand keeps its old author time and drops out of proof_gate's rework count. The supervisor's own `restore_commits` case was fixed at 35fbf75bb7; commit time cannot be used, since `selftest_relentless_proof_gate_mend.py` row 3 requires a mend re-committed inside a run to stay out.
7. Mod reservation (5192-5197): `taken |= mods` runs before `enrol_put` succeeds, so a refused item can stall another item on the same mod.
8. `marker_fail_record` (5676-5678): `step` ignores a False return and continues before the owed FAIL is recorded.
9. Owner-pause rule (5275-5289): non-object JSON in the pause file raises AttributeError in every affected tick. Check this one first: a hand-written `true` could halt ticks.
10. `help_retry` (6335-6376): a retry keeps the old room-wait timestamp, so time spent running can use up the next attempt's admission wait.
11. `check_resume` (r8 #1): a resumed checker keeps its original deadline, so `verdict()` rejects its answer as late. The sibling's e8c7158e6f stops a late verdict wedging the check; this waste remains.
12. `retire` (r8 #2): any recorded ledger lease retires a queued item, including an expired or released one, while `eligible` uses `lease_live`.
13. `help_step` (r8 #3): consult launch ignores a quarantine or manual hold.

Overlap: RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY holds 11-13 above (its 1-3) plus three more; work the two items as one batch so relentless.py is reviewed once.

Done when: each is fixed with a red-without-fix selftest row, or rejected in writing with its reason; then relentless.py gets its own review again, because the edits dirty it.

Source: RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN.

## outcome (the Done-when clauses, gen 3)
- Findings: 1-4 and 7-13 fixed with rows in `src/RimMandrake/rimflow/selftest_relentless_r7_thirteen.py` (run by `selftest_relentless_r7_mediums.py`); 5 and 6 rejected with reasons in that selftest's docstring.
- The review again: on `relentless.py` at 80e7d60318, its last edit (sha256 1c406d67...), the final bytes. r1 (full file, high effort): two HIGH, one MEDIUM; r1's first HIGH is this item's finding 4, adjudicated MEDIUM earlier and fixed; the other two fixed with rows 14-16. r2 (full file, the same prompt, `--lockdown --effort medium` after two high-effort tries timed out at 510 s, the setting of the r8 review whose answer found three mediums): `VERDICT: NO-HIGH`, `none`, job consult-20261106-151251-150189-db5061. Text: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_R7_FIX_THIRTEEN_MEDIUMS_MAY_STAY\r2\rev_whole.txt`.
- Clean under the owner's bar for this file (card 2026-11-06, `design/RimMandrake/standing_rulings.md`, Code review): mark at 06a1bcde8f, one commit after the sha the first blind check tested, so that check rightly read DIRTY there. `python3 src/RimMandrake/Utils/code_review_status.py check src/RimMandrake/rimflow/relentless.py` reads CLEAN from that commit on, until the next edit.
