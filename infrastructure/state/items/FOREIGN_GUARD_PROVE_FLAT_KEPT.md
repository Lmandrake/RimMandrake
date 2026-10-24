## spec
codex_image.py `_detail_corr` (45c565b398) returns None for a flat (featureless) image, and `match()` then keeps the coarse
16x16 verdict. That branch has no unit test: a later edit that treats None as "not confirmed" would let a byte-different
copy of a flat-fill or near-flat picture (a plain tile, a silhouette) through with every selftest green.
Reviewer probe (no crash on 1x1, flat, alpha-only, faint alpha, L/P/I;16, 4000x3, truncated):
/home/mandrake/.seat-tmp/FOUNDRY/probe/p3.out.

## failing test (sketch)
In selftest_codex_image.py: a cache file that is a flat 200x200 colour, the placed file the same colour resized to 64x64
(bytes differ). Assert `ci.foreign_source(placed, home, before)` is not None. Passes today; it guards the branch.

## verify
Add the test; run --only selftest_codex_image.
