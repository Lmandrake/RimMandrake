# BOUNDARY: borrowers keep no copy of what the object store holds, Design Version 0.1.0

Code: `dedupe`, `dedupe_targets`, `reaches_store` and `objects_dir` in `src/RimMandrake/Utils/scratch_clone.py`, run
hourly by `infrastructure/stevedesktop/rm_ssd/rm-pool-room.service` before the room reading. Item:
`RIMMANDRAKE_SHRINK_STEVEDESKTOP_CLONES_FOUR_FILL_ITS_EIGHTY_GIG`, written 2026-11-26. Each promise has a test of its
name in `src/RimMandrake/Utils/selftest_scratch_dedupe.py`.

## The failure

SteveDesktop's `~/rm` is an 80 GB disk. On 2026-11-26 its hourly room reading said SHORT (9 runs, not 10) at 3:33 AM,
9:33 AM, 10:33 AM and 12:33 PM PST, and the live promise broke. Two causes were measured:

- Copies of store objects. A clone that fetches while the store is behind origin keeps its own copy of what it
  fetched, and nothing packed it away: runner held 1.27 GB, runner_b 1.25 GB and bench 0.83 GB, all of it also in the
  store (`git repack -a -d -l` left 5, 11 and 6 MB, and `fsck --connectivity-only` stayed clean). The pool clones held
  0.2 to 0.9 GB each.
- The red re-run's trees in `./publish` (10.1 GB in one kept tree), fixed in
  `design/specs/2026-11-25-treecheck-kept-tree/boundary.md`.

## The design

- `dedupe` runs `git repack -a -d -l -q` in every borrower: each repo the sample scan finds with an alternates file
  (`scan_patterns`: the seat clones and the mirror under `RM`) and each pool clone. `-l` packs only the objects that no
  alternate holds, so the clone's own commits stay and its copies of store objects go.
- Only a repo whose alternates reach the store, directly or through another repo's alternates (bench borrows the
  mirror, which borrows the store), is repacked. Any other repo is skipped and named.
- The store sets `gc.pruneExpire=never` and `gc.auto=0` (`STORE_CONFIG`), so an object a borrower dropped stays
  readable there.
- Each run appends one record to `dedupe.jsonl` in the state folder: what it did, the bytes before and after, what it
  skipped and what failed. The command exits 1 when a repo failed, and the unit's `-` keeps the room reading running.

## ACCEPTS (the only inputs this is built for)

- **a-store-that-never-prunes.** The store at `store_path()` with `STORE_CONFIG` applied.
- **borrowers-with-alternates.** Git repos whose `objects/info/alternates` names object folders.

## DOES NOT SURVIVE (not promised)

- **an-object-only-a-middle-repo-holds.** A borrower that reaches the store through another repo (bench, through the
  mirror) also drops the objects that middle repo holds. If the middle repo later drops one that no ref of its own
  reaches, the borrower cannot read it. The mirror's refs are origin's, and origin's history is never rewritten.

## PROMISES (each one is owed a test of the same name)

- **borrowers-keep-no-copy-of-the-store.** A seat clone, a pool clone and a clone that borrows the store through
  another repo drop the objects the store holds. Each still reads its whole history and its own commit, which the store
  lacks. A repo whose alternates do not reach the store is left as it is. A repo that git cannot repack is reported
  failed, and the others are still done. The command exits 1 when one failed, else 0.

## LIMITS

- `DEDUPE_TIMEOUT_S` (900 s per repo) is a hang guard; its danger and evidence are written beside it in
  `scratch_clone.py`.

## PROOF

- 2026-11-26, the selftest: green; five planted faults (no `-l`, every repo taken as a borrower, direct alternates only,
  a failure not reported, pool clones not taken) each read red.
- SteveDesktop, 2026-11-26 12:40 to 12:52 PM PST: the seat clones by hand (3.35 GB freed), then one `dedupe` run over 7
  repos (94 s, 0.99 GB freed, none failed). `~/rm` went from 22 GB free at 12:34 to 37.9 GB at 12:52, with 4 pool clones
  standing.
