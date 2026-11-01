## Finding
`later_fixes` in `arena_tasks.py` (41b33b771a) looks to have falsely demoted TANKS_ROW. Its label went suspect because of
6229e947cd "GPT FW review part 5/6 fixes", a 14-file review commit that touches walk_gaps_proof.py. That is a subject
keyword plus file-overlap hit, not a repair of the 7a68931d8a fix. d422858b7f then moved the sanity item off TANKS_ROW
because of that demotion.

`later_fixes` demotes a label; `close_sha_unrelated` rejects a close. They are separate. TANKS_ROW passes
`close_sha_unrelated`, which still rejects 0 on the real ledger (see ARENA_CLOSE_GUARD_FIX_MISSES_WRONG_SHAS).

## Exact change
Exclude wide review commits from `later_fixes`, or require the later commit to change the same lines as the close, or
add a LATER_FIX_CLEARED list holding 6229e947cd for TANKS_ROW. Then decide whether TANKS_ROW returns to the census.

## verify
- L0: TANKS_ROW's label is not suspect; a planted real re-fix of the same lines still demotes.

## criteria
- The demotion count on the real ledger is reported with a sample read by hand.
