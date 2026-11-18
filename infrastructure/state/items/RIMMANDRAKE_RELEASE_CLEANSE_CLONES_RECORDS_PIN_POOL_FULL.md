# RIMMANDRAKE_RELEASE_CLEANSE_CLONES_RECORDS_PIN_POOL_FULL

## spec

FINDING (measured 2026-11-17 about 7:08 PM PST): `designer_cleanse.py` `release()` keeps every finished cleanse clone whose
only dirt is untracked `conversations/*.md` (the conversation hook writes them inside the clone). The pool filled to
16 of 16 and the converge fleet crashed 11 biomes at 6:49 AM PST 2026-11-17 (`POOL REFUSED: pool full`). 12 clones read
other dirt 0, ahead of origin/main 0, 1 to 6 conversation files each. They were freed by hand once; their records are
published at c9af9225eb.

FIX: before its dirt check, `release()` carries untracked `conversations/*.md` out of the clone to a place that
outlives it (publish them from the clone, or copy without overwriting into the store's orphan bundle), then releases.
Any other untracked, uncommitted or unpushed file still keeps the clone. A carry that fails keeps the clone and says
why.

FILES: src/RimMandrake/rimflow/designer_cleanse.py; src/RimMandrake/rimflow/selftest_designer_cleanse.py.

ACCEPTANCE TEST: not yet written or watched failing. The builder adds the three cases below to
`selftest_designer_cleanse.py` first and watches them fail on the base commit.

## verify

    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_designer_cleanse

## criteria

- A clone whose only dirt is `conversations/x.md`: release removes it, and `x.md` exists outside the clone afterwards.
- A clone with `conversations/x.md` plus one other untracked file: release keeps it.
- A clone with nothing untracked and nothing unpushed: release removes it (unchanged behaviour).
- A failed carry keeps the clone and the returned line names the failure.
