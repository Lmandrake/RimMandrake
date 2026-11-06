## What
Round-6 Codex full-file review of `src/RimMandrake/rimflow/relentless.py` (7894 lines, 9 chunks of ~870, all 9 answered,
every one FINDINGS, 22 total), done by RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN at 887d8937e4. Raw reviews, prompts, chunks and
the chunker `mk.py`: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN\r6\`. Each finding is
unverified: triage (fix with a red-without-fix test row, or reject with the reason). Inputs not duplicated here:
RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN (r2), RELENTLESS_CORE_FIX_CODEX_KEEPS_FINDING (r4), RELENTLESS_REVIEW_FIX_ROUND_FIVE_DIGS (r5).

🔑 Rounds found r2 13, r3 12, r4 12, r5 21, r6 22: the count is not falling as the file grows (6525 → 7894 lines).
Marking the file CLEAN on GPT `VERDICT: CLEAN` per chunk waits on the owner's call on the review bar
(RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN snag). Fixing these is worth doing either way.

relentless.py, line numbers at 887d8937e4:
1. 697-713 `charge` dedup covers today and yesterday only: a crash before the item's charge marker, recovered two days later, books the run twice.
2. 138-142 restore hashes a tracked symlink with `git hash-object` (target content, not link text): an unchanged symlink's deletion is refused.
3. 1407-1418 state-only push guard uses `--not --remotes`: a commit reachable from any remote-tracking ref (origin/topic) passes as state-only.
4. 1387-1401 `unlanded()` uses `--no-merges`: an unpublished merge carrying a resolution reads as landed.
5. 1234-1256 `landed_commit` with an unreadable worker sha: `landing_key()` None reaches `re.escape(None)` in `find_landed` (TypeError).
6. 1611-1640 `gpt_consult` reads a stale `out` file after a failed vendor call: an old answer is recorded under the new nonce.
7. 2579-2587 derived-file restore `open(src, "wb")` follows a symlink and overwrites its target.
8. 2469-2495, 2590-2594 levelling: reset succeeds, reorder journal write raises, `_unlevel` rewrites origin's shard and drops event B.
9. 2770-2815 first-touch gate tokenizes `Foo_Bar` into foo/bar/foobar while `known` holds `foo_bar`: the Designer pass is skipped.
10. 3374-3410 bundle size limits are checked after tar/patch output is fully written: no protection against filling the disk.
11. 2643-2645 `prose_moves()` sees only `??` destinations: a staged `git mv` close move (`A `) is omitted from publication.
12. 3885-3890 `changed()` ignores a failing `git log base..sha` and returns a partial list (a hook change escapes its live line).
13. 3885-3889 `changed()` `--name-only` without `--no-renames`: a rename's source path (e.g. relentless_live_round.py) is omitted.
14. 3837-3839 `help_checkout()` ignores failure to disable the origin push URL.
15. 5109-5133 owner-pause `pipeline_prefixes` given as a string is iterated per character: any item starting with one of its letters runs (fail open).
16. 5863-5956 checker binding validated before unlocked reads, not re-checked under the final lock when PASS is consumed.
17. 5888-5917 a FAIL moves the item before its ledger veto is recorded; `marker_fail_unrecorded` loses the FAIL for good.
18. 5973-5998 `close_tries` counts ticks spent waiting on `published()`, sending a checked item to `close_stuck`.
19. 6488-6495, 6697-6702 unreserved `give_back()` overwrites a record an owner command just changed to `held`.
20. 6247-6250 `help_resume()` resets `started_at` but keeps the old `deadline` (already expired at resume).
21. 6828-6829 missing sha evidence on an attempt row reads as a matching build in the status SLIs.
22. 7165-7174 game pass `break`s on a waiting expedited item before stepping the staging holder that must release the game.
