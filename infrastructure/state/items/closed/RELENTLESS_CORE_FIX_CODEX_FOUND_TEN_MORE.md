## What
The re-review of RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN (gpt_consult, `src/RimMandrake/rimflow/relentless.py` in 5 chunks
and `src/RimMandrake/rimflow/relentless_game.py` whole, on top of 0c7f2fa842) returned these findings, each unverified.
Triage each: fix it with a selftest row red without the fix, or reject it with the reason. Raw reviews (line numbers are
of that review's numbered copy): `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\review\rev_part0.txt`
.. `rev_part4.txt`, `rev_game.txt`.

relentless.py:
1. (part0 #1, ~589-594) charge: an `estimated` run with tokens=1 reads as measured (`bool(tokens)`), so it is charged
   1 token instead of `run_reserve`; the budget under-counts.
2. (part1 #2, ~2304-2306) run_fixture: a timeout kills only the shell; a backgrounded child keeps writing the books tree.
   Start it in its own session and kill the group.
3. (part1 #3, ~2429-2459) prepare() for the synthetic SHOWINGS clone: a gap plus uncommitted work bundles, then
   `store.load("SHOWINGS")` is None and `cur["bundle"] = ...` raises TypeError.
4. (part2 #1, ~2696-2711) restore_bundle: the fallback ref name `carried/<ref>` can be overwritten by a later off-HEAD
   ref of the same name; a restored commit loses its ref.
5. (part2 #2, ~2650-2655) restore: `tar --skip-old-files` silently skips an untracked file whose path upstream now holds
   as a directory; the loss is not recorded.
6. (part3 #1, ~4960) a suspended checker still `checking` is counted in `active` and admission also asks `extra=1`:
   with capacity 1 it never resumes.
7. (part3 #2, ~5081-5094) help_start calls make_room before checking whether the consult resumes in its own clone; a
   one-clone pool evicts the saved tree it meant to resume.
8. (part4 #1, ~5580-5604) _lease: a `hold --owner-said` landing while prepare() runs outside the lock is not re-read
   before launch; the worker starts on stale state.

relentless_game.py:
9. (game #3, ~1391-1469) a batched passenger's environment remedy is not run, yet the passenger is marked staged; its
   next identical environment failure reads as a failed fix and holds.
10. (game #4, ~1192-1198) a FAIL read after the game restarted grants live iteration on the new process, which may not
    run the failed build.

Rejected in that review and kept rejected: game #1, `step` finishing on ledger `done` without a sha match (a done
ledger item is done; ruled in RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN). Fixed there: game #2 (an owed live criterion
outside the clauses) and part1 #1 (a git-less tree holding only a dir symlink).

## Done when
Every row above is fixed with a test or rejected with a reason, and RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN's full-file
review + mark-clean of both files can then run.
