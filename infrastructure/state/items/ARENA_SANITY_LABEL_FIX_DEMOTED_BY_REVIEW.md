# ARENA_SANITY_LABEL_FIX_DEMOTED_BY_REVIEW

selftest_arena_tasks real-ledger row fails: later_fixes demotes the new sanity item from Clean

## Finding
selftest_arena_tasks.py: 1 failure, the row 'real ledger: the sanity item remaps to 7a68931d8a, is Clean and holds its discriminating walk-gaps check'. The sha and check parts hold; only Clean fails. Real census: TANKS_ROW_FIX_LEVELS_WHAT_RULING_FORBADE fix 7a68931d8a, label None, label_suspect 6229e947cd. Two commits met in the merge: 6c291fbe0b moved SANITY_ITEM to TANKS_ROW, 41b33b771a added later_fixes, whose LATER_FIX_CLEARED holds only the old pick's commits. ARENA_SANITY_ITEM_FIX_NOT_DISCRIMINATING covers vet discrimination and the sanity default, not this label.
Hand-read: 6229e947cd's only change to walk_gaps_proof.py is thrown_verdict's control (RM_PitExposure, GPT review 6.5), a fall check unrelated to the tanks row; 'fixes' is in the subject. Not a repair of 7a68931d8a.

## Change (arena_tasks.py)
LATER_FIX_CLEARED = frozenset({'59ba780056', '589859a8d6', '6229e947cd'}) and extend the comment above it with this hand-read.

## Done when
selftest_arena_tasks.py passes in full (about 10 min; over run_selftests' 240 s cap); the sanity item reads Clean with empty label_suspect.

## Evidence
D:\ClaudeWork\rimmandrake\arena\census\guard_probe (row.out, selftest_tasks.out)
