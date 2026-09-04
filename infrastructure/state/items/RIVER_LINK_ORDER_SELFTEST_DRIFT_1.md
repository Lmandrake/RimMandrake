# RIVER_LINK_ORDER_SELFTEST_DRIFT_1

`selftest_river_link_order.py` fails: 266 produced vs 292 accepted rows,
link SET differs (26 accepted-only rows), order+orientation differs.
Root cause: `world/ASHKARR_WORLDMAP_links.csv` was substantially
hand-rewritten in three 2026-08-22 commits after the emitter's
mouth-first order-test froze on 2026-08-21 — the reconstructed-input
approach this test uses (rebuild `acc`/`down`/`chan` from the accepted
file itself, since the frozen `tiles.csv` can't be re-painted) can no
longer round-trip that many hand-edited rows.

## Partial resolution — owner ruling, 2026-09-03

The specific worry that spawned `ASHKARR_UPHILL_RIVER_LINKS_DECISION_1`
(four LargeRiver/HugeRiver/Creek segments climbing 254-304m, possibly a
backwards-link bug) is **closed: keep as authored, not a bug** ("Just
accept the river item for now please."). None of those four rows need
hand-editing.

## What's still open

That ruling answers "are these four rows backwards" — it does not, by
itself, explain the other ~22 accepted-only rows or the full order
mismatch. Two live possibilities, undistinguished:
1. The hand-authoring commits (crater relocation, Kiln pan, river death
   point move — 2b0e9031/68aa7ef2/20e492bf) changed the drainage graph
   enough that this test's reconstruction approach is simply no longer
   valid for the current file — the test would need to be rebased or
   retired, not the emitter fixed.
2. A genuine emitter bug independent of those edits (unlikely per the
   "not the rename migration" finding already recorded, but not ruled
   out for the newer commits either).

**Deprioritized per the owner's "for now"** — not re-blocking on him
again without more to show. Whoever picks this back up: rerun
`python3 src/RimMandrake/Utils/selftest_river_link_order.py`, diff the
26 accepted-only rows against the three 2026-08-22 commits' actual
changes (`git show <sha> -- world/ASHKARR_WORLDMAP_links.csv`) to see if
they cluster around the crater/Kiln/death-point edits specifically —
that would point at (1) over (2).

## verify

Selftest passes clean (0 diffs), or the test is deliberately retired
with a documented reason and removed from `run_selftests.py`'s count.

## criteria

Not ruled — this is FOUNDRY's own scoping, not an owner decision. Follow
the investigation above before proposing either fix.
