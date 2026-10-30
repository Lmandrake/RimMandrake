# ARENA_CLOSE_GUARD_FIX_MISSES_WRONG_SHAS

close_sha_unrelated catches 2 of 6 planted wrong closes: read the subject, not the trailers

## Finding
The guard (41b33b771a) can see but is weak. Planted end to end on a copy of the real ledger: 6 pool closes pointed at another pool item's fix, 2 rejected, 4 kept. All 56,792 wrong pairs of the 239-task pool: 52.3% caught. Real ledger: 0 rejected, for two reasons.
1. Word overlap reads %B, so the two commits that do score 0 on their subject are saved by one incidental body word: ART_PAINTERLY_RESTORATION_1 (a1739f13d4, 'gate') and BRASKEEN_REDRAW_VARIATIONS_ON_E (0da53c8071, 'owner'). Both are truly wrong: each close recorded HEAD of that moment (no fix commit existed), minutes after an unrelated commit. Trailers add noise too (code, session, claude, opus are in nearly every message).
2. Gate order: all 90 score-0 of 1001 resolved closes fall to earlier rejects; FINDMOD goes as build-only, so it never reaches the guard.

## Change (arena_tasks.py, close_sha_unrelated)
Keep the iid test on %B; run the word test on the subject only:
    body = _git(repo, 'log', '-1', '--format=%B', fix)
    subject = _git(repo, 'log', '-1', '--format=%s', fix)
    return iid not in body and not (_related_tokens(iid + ' ' + title) & _related_tokens(subject))
Measured: wrong pairs caught 70.0% (39,740 of 56,792); real pool rejects exactly those two items, nothing else. A stricter option (trailers stripped, tokens in under 10 pool commits) catches 82.8% but rejects 4 further real fixes, so it is not recommended. Fix the docstring's 'score 0' claim. Pool expected 239 -> 237. The guard remains a weak filter: 30% of wrong closes still pass.

## Done when
selftest t_wrong_commit has a fixture whose wrong commit shares a word only in its body and in a trailer, and it is rejected; census on the real ledger rejects those two.

## Evidence
D:\ClaudeWork\rimmandrake\arena\census\guard_probe (probe2.out, probe3.out, probes)
