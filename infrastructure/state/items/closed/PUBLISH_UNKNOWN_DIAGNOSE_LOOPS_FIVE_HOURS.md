## diagnosis (2026-11-06, Relentless builder, gen 1)

Why `fx.published(sha)` returned None for BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME every tick, 2026-11-06 ~00:08-05:00Z:

- The candidate recorded the worker's LOCAL sha `cccf3028b8fcad08cccfaceac3d9ebb6f401acfe` (finish at 00:08:32Z).
  The landing rebased that work onto origin/main under new hashes: `ffa769ba55` (list page drops RUT_FuelSnows) and
  `2052d70878` (selftest reviewed clean, the tip). The worker's clone was then parked/reaped, so `cccf3028b8` never
  became an object in the books clone (`git cat-file -t cccf3028b8` in `/home/mandrake/rm/relentless/books`: fatal).
- The old `published()` ran `git merge-base --is-ancestor <sha> origin/main`; on a missing object git exits 128,
  and 128 mapped to None ("origin could not be asked"). So the tick logged `publish_unknown` and waited, for ever.
  Nothing was wrong with the fetch or with origin; the question named an object nobody had.
- The candidate carries no landing `key` (it predates keys) and its clone is gone: the legacy shape.

## the fix (already landed by another item)

`be37d17c84` (CANDIDATE_SHA_REPAIR_LANDED_UNDER_NEW_HASH, 2026-11-06 06:21Z): `published()` reads an absent object
after a good fetch as False, and `relanded()` / `find_landed()` resolves the candidate to its landed commit. Run
read-only against the books clone with this item's real state, `find_landed(books, None,
"BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME", base=462decb40b, until=finish+1, since=start-1)` returns `2052d70878`
("newest commit naming the item authored by the finish") — the correct tip. Class test:
`src/RimMandrake/rimflow/selftest_relentless_landed_sha.py`, case 2d is exactly this shape.

At diagnosis time (06:25Z) the books clone was 5 commits behind origin/main and did not yet hold `be37d17c84`, so
BAROQUE was still waiting; it resolves on the first tick after books fast-forwards. Nothing further to build here.
