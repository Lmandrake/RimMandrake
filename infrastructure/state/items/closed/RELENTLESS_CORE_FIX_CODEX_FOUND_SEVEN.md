# RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN

## What
Codex full-file review (SHOWINGS_HARDEN_FLYERS_OUT_SUBJECTS_TIGHT, 2026-11-05) of `src/RimMandrake/rimflow/relentless.py`
(4 chunks, part 4 CLEAN) and `src/RimMandrake/rimflow/relentless_game.py` left these findings, each unverified; triage
each (fix with a test, or reject with the reason), then full-file review again and `code_review_status.py mark-clean`.
Raw reviews: `D:\ClaudeWork\rimmandrake\scratch\SHOWINGS_HARDEN\r2\rev_part0.txt` .. `rev_part2.txt`, `rev_game.txt`.

relentless.py (line numbers as of the SHOWINGS_HARDEN_FLYERS_OUT_SUBJECTS_TIGHT landing):
1. ~714-727, 1092-1099 proof_gate: a proof-only worker may edit a product file by naming it as an argument of its proof
   command (`named` comes from tokenizing the command). Permit only validated proof assets.
2. ~1088-1100: an empty commit above `held["sha"]` (or resubmitting the same sha with `binding`) passes the
   unchanged-proof guard with no proof change.
3. ~2189-2204, 2454-2468: a clone with no `.git` is removed without `bundle_clone` — its untracked files are lost.
   Refuse, or archive the tree first.
4. ~2028-2049, 2665-2669: merge commits: `diff-tree` without `-m`/`--first-parent` lists no paths, so `work_sha` and
   `changed` can miss a hook a merge brought in (low: the repo lands by rebase).
5. ~1542-1544: an unstaged deletion of a tracked ledger shard raises FileNotFoundError before levelling refuses.
6. ~3659-3662 content_paused(): a queued system item in launch cooldown or pending consult still pauses content.

relentless_game.py:
7. ~1001 (implement): an owed GREEN-FULL criterion with no live-proof line never joins the clauses, and the item waits
   at the all-PASS return forever. `selftest_relentless_game.py` t_owed_final_joins_the_clauses pins "Z9 (no proof
   line) does not join" — decide whether Z9 should send the item back (`game_contract`) instead, and change that row
   on purpose if so. Also rejected in review (keep rejected unless shown wrong): `step` finishing on ledger `done`
   without a sha match — a done ledger item is done.

design/RimMandrake/relentless_agent_design_2026-11-01.md (stays DIRTY, Codex `rev_design.txt` in r2/):
8. ~lines 127-134 "Close is checked at close": Codex reads close trusting measured dependencies as contradicting "a
   declared dependency set can be wrong". Judged not a defect (measured reads are not the declared set), but the
   reviewer did not return CLEAN; a reviewer with design standing confirms or rewrites, then marks it clean.

## Outcome (2026-11-06)
Findings 1-7 fixed with rows (0c7f2fa842, 06e52c3c87); item 8 confirmed and marked (7abe189bce). The review bar became "no high-severity issue" by owner card 2026-11-06. Graded review r7: three HIGH claims held and were fixed (e8c7158e6f, rows in `selftest_relentless_codex_seven.py` t_r7_high_rows), two graded down with reasons; the whole-file rerun on e8c7158e6f said NO-HIGH. Non-high findings: RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY. Triage: `D:\ClaudeWork\rimmandrake\relentless\RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN\review\r7\triage.md`.
