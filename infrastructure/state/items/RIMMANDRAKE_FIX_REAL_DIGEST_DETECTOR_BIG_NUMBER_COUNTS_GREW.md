## spec
`selftest_delegated_digest.py` test_real fails on current main: `leaks()` counts any 5+ digit number as a money/token
leak (`_BIG`, line 52), and the real dry-run page now legitimately prints source counts above 10000 (ledger 17832,
leftover deletions 12573 [measured 2026-11-18]). The test is red the same way without any change to the digest.
Fix needs a choice (exempt the count table and record-count headings from `_BIG`, keeping it on prose), so it is the
detector's owner's call; do not loosen the detector by raising the threshold.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_delegated_digest.py` exits 0 with the real page still
rejecting a planted dollar or token figure in prose. Watched FAIL today (`big:17832`).

## criteria
- the real-page test passes while a planted dollar or token figure in prose is still refused.
