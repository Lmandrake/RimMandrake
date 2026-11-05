## What
Round-5 Codex re-review of `src/RimMandrake/rimflow/relentless.py` (8 chunks of ~870 lines) and `relentless_game.py`
(2 chunks), done after RELENTLESS_CORE_FIX_CODEX_KEEPS_FINDING landed (0a2ec71ec9). Raw reviews, prompts, chunks and the
chunker `mk.py`: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\review\r5\`. 8 of 10 chunks
answered, every one FINDINGS (21 total); `part4` (lines 3477-4343) and `part5` (4344-5187) died on a WSL vsock error
(`log_part4.txt`, `log_part5.txt`) and owe a rerun. Each finding is unverified: triage (fix with a test, or reject with the reason).

🔑 **Before triaging, settle the bar.** Rounds found r2 13, r3 12, r4 12, r5 21 (8 chunks), each mostly new kinds of edge case.
GPT `VERDICT: CLEAN` on every chunk of ~8400 lines of supervisor has not come closer in four rounds. Whether a different
acceptance applies to these two files is a change to the code-review ruling (`standing_rulings.md` §Code review), so the
owner's; RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN is held on that call.

relentless_game.py (rev_game0.txt, rev_game1.txt):
1. 329-346 legacy PASS reuse compares a whole-second row time against a fractional `offline_green.at`: a same-second contract change reads as approved.
2. 381, 397-401 `not_measuring` exit-code regex misses signed codes (`exited -11`), so a signal-killed proof never trips the repeat cutoff.
3. 1396-1425, 1475 the stage path launches with `game_reading()` state None (unread game); the prove path waits there.
4. 916-950 `_env` ignores `since`: an environment row from before the latest staging can hold the item.

relentless.py (rev_part0..3, 6, 7):
5. 809-810 a proof-only worker may replace an existing live line with another (`live or old_live`).
6. 608-626 `charge()` replay after a crash: day file keeps the first booking, the item gets the new amount.
7. 798-803, 844-853 a widening contract may overwrite an existing scenario outside redesign/rebind.
8. 634-645 `run_fixture_cmd` buffers unbounded output before truncating (memory).
9. 369-384, 533-539 account loss advances gen but keeps `pilot_step.sat_gen`, dropping the owed pilot step.
10. 1454-1456 unchanged-proof guard fails open for an old `proof_only` record with no `contract` snapshot.
11. 1561-1663 `hold()` on a blocked item records back=queued; `unhold()` loses the blocker.
12. 1480-1488 push hook reads `.git/relentless.json` where `.git` may be a file (NotADirectoryError -> refuses push).
13. 1940-2068 the reordered-jsonl dirty exemption covers any tracked .jsonl, not only append-only shards.
14. 1908-1912 ancestor collision check follows a symlinked directory.
15. 2249, 2281-2293 upper-case mod names stripped from titles before mod detection (first-touch gate miss).
16. 2813-2820 saved patches use `git diff --binary` without `--no-textconv --no-ext-diff`.
17. 2772-2778 `os.walk` swallows read errors: a gitless tree can read empty and be removed.
18. 2895-2899 a cherry-pick with a modify/delete conflict reads as "already landed" (check unmerged index).
19. 5386-5472 account-loss recovery resumes a helper in a clone a quarantined live predecessor still holds.
20. 6192-6349 a wake-driven `game_pass()` gets a fresh budget, not the tick's remaining one.
21. 6310-6431 a wake consumed during the final flush runs game steps after it, unflushed.
