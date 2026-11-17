## spec

See problem and fix below.

## problem

`concept_tree.py lint` (Gate A, the stage-3 check) never compares the tree's `root_hash` with the walk's current
validated hash; only `gate` (stage 5) does. When the north star is re-validated after stage 3 writes the tree and later
reworks hand-edit tree.json, exam and coverage judge both pass a tree the gate can never accept. Pyrelands, 2026-11-17:
walk re-validated 2026-11-16 21:54 PST (6ad3da0a...), tree still cites 1a7028c5...; coverage judge signed
rm-coverage-judge-1794947629, gate refused "tree cites a root hash that is not the walk's".

## fix

Move the root-hash/root-state comparison from `gate` into `lint`, only when the walk is VALIDATED (a not-yet-validated
root stays legal at lint; `gate` still refuses it).

## criteria

lint refuses a mod tree whose root_hash differs from a VALIDATED walk's; gate reports it once.

## verify

`python3 src/RimMandrake/rimflow/selftest_concept_tree.py` prints `selftest_concept_tree: PASS`. Cases
`lint: a stale root hash on a VALIDATED walk` and `gate: a stale root hash is reported once`. Watched fail on base
(3ecb81bada): `FAIL lint: a stale root hash on a VALIDATED walk  got: []`, `selftest_concept_tree: FAIL 1`.

## refs

file: src/RimMandrake/rimflow/concept_tree.py
file: src/RimMandrake/rimflow/selftest_concept_tree.py
