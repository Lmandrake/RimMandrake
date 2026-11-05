## What
Round-4 Codex re-review of `src/RimMandrake/rimflow/relentless.py` and `relentless_game.py` at 9d93a4c723 (after
RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN's r3 fixes). Raw reviews: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\review\r4\rev_*.txt`
(prompts and numbered chunks beside them). Each finding is unverified: triage (fix with a test, or reject with the reason).

🔑 **The review is a treadmill.** Rounds found r2 13, r3 12 (11 real), r4 12 so far, each round mostly NEW kinds, some about
the previous round's fixes. Two chunks never answered: `part1` (lines 1321-3192, 1872 lines) and `part3` (3952-5241) timed
out at 525 s; the whole `relentless_game.py` timed out twice, so it is now reviewed in two halves. Split those chunks to
~900 lines. Before another round, decide whether GPT `VERDICT: CLEAN` on ~8000 lines of supervisor is a reachable bar
(a different acceptance for this file is a code-review-ruling change: `standing_rulings.md` §Code review).

relentless_game.py (r4/rev_game0.txt, rev_game1.txt):
1. 433-444 `staged_idle()` measures from process start, so a 25-minute full-list load is idle on its first UP reading.
2. 775-776 `stale_holds()` matches the item id as a substring of the bridge purpose (`ART` in `staging CART`).
3. 1346-1391, 1439 a final waiter's batch timer can enter `stage` while the game reads LOADING, skipping the load guard at 1278-1306.
4. 890-931, 1237-1253 `_env_fix()` returning False after a fresh fix skips a second, unfixable cause's routing; the item falls to `_refuse()`.
5. 1431-1481 remedies are dropped at launch, before staging confirms it ran them.

relentless.py (r4/rev_part0.txt, rev_part2.txt, rev_part4.txt):
6. 604-617 `charge()`: an unreadable yesterday file skips the day write but `st["spent"]` still rises; the run is lost from the day after the file is repaired.
7. 791-813, 1270-1285 a contract-only proof repair on the unchanged sha is refused `proof_unchanged`, while an empty commit carrying the same repair passes.
8. 3849-3889 breaker openings are counted over the whole incident, not within the window.
9. 3296-3300 `hand_check_lint` crashes on a non-string `title_rx` entry (`re.compile(None)` TypeError).
10. 5410-5449 `give_back()` overwrites a hold that landed during `settle_wait()` (reserve_foreign).

When these land, RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN reruns the reviews and marks both files clean on VERDICT: CLEAN.
