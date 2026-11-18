# RIMMANDRAKE_RESTAMP_PYRELANDS_CONCEPT_TREE_RED_IN_TWO_LANES

## spec

`python3 src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py` is red on origin/main 61582fa4a4 (watched
2026-11-18 ~3:40 PM PST in a throwaway clone, and by Lane J at 1:52 PM): 1 of 18 checks, `gates: concept_tree lint: -
tree cites a root hash that is not the walk's (re-run `write` to restamp it)`. Since 2ff90a9590 the concept_tree
lint refuses a stale root hash on a VALIDATED walk; Pyrelands' tree was not restamped after its walk changed.

## fix

Restamp Pyrelands' concept tree with the concept_tree tool's `write` (the lint names it), by whoever owns the
Pyrelands design state (Designer stage). Never loosen the lint.

## verify

    python3 src/RimMandrake/Pyrelands/selftest_pyrelands_round6_gaps.py

## criteria

The selftest exits 0 (18 of 18). Acceptance test: that command; watched FAIL on 61582fa4a4 (1 of 18).

## refs

file: design/concepts/Pyrelands
