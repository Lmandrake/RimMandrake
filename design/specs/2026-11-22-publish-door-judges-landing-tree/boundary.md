# BOUNDARY: ./publish's whole-tree checks judge the tree that lands, Design Version 0.1.0

Code: `src/RimMandrake/Utils/publish.py` (`tree_checks`, `landing_rev`, `replay`, `rebase`, `died_on_enomem`).
Item: `RIMMANDRAKE_CHECK_PUBLISH_TREE_ON_REBASED_HEAD_NOT_STALE`, written 2026-11-22. A clone 19 commits behind origin had
`./publish` refused twice by `selftest_modledger_tree.py` for mod-ledger lines that origin had already restored; the
refusal named the ledger, and the real repair was `./sync`. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_publish_tree_checks.py`. This page covers only the parts named; the rest of the file
has no page.

## ACCEPTS (the only inputs this is built for)

- **a-clone-with-a-commit-at-head.** A git work tree whose top is the repo top, with a commit at HEAD. A plain folder
  (a test fixture with no git) is judged where it stands, as before.
- **an-origin-that-may-be-ahead.** `origin/main` may hold commits HEAD lacks. The door fetches it first; a fetch that
  fails leaves the last tracking ref, and the door judges against that.

## DOES NOT SURVIVE (not promised)

- **origin-moving-between-the-door-and-the-push.** The door judges the replay onto the origin it fetched. If origin
  moves again before the push, `land` replays onto the newer tip and nothing re-runs the checks. The window is the
  checks' own wall time (about 15-30 s).
- **a-replay-that-stops-on-a-conflict.** When the local commits cannot be replayed onto origin (a real conflict, a
  merge commit), the door judges HEAD as before, and `land` then refuses on the conflict itself.
- **the-pipeline-checks.** `pipeline_checks` still judges HEAD and excuses a red its merge base shares
  (`split_pre_existing`). The whole-tree checks have no such excuse, by the owner's card of 2026-11-12 ("refuses on
  red"); this page does not change that.

## PROMISES (each one is owed a test of the same name)

- **the-door-judges-the-tree-that-lands.** When HEAD is behind a fresh `origin/main`, the whole-tree checks run on a
  full checkout of HEAD's local commits replayed onto that origin (the same `replay` that `land` uses), and the
  output says so with origin's sha. When HEAD is on top of origin, they run on HEAD, as before.
- **the-landing-tree-sees-origin-main-as-landed.** In the throwaway checkout of the landing tree, `origin/main` is the
  landing commit, so a check that asks whether a cited sha is on origin/main (`selftest_modledger_tree.py`
  SHA_NOT_ON_BASE) sees every commit origin holds. A sha on no branch is still red.
- **a-red-origin-already-repaired-does-not-refuse.** A clone that branched while origin was red on a whole-tree check,
  and that publishes an unrelated path after origin repaired the check, lands: `publish` prints `PUBLISHED`.
- **a-red-the-commit-makes-is-refused-on-the-landing-tree.** A commit that turns a whole-tree check red is refused on the
  replayed tree, naming the check and its fix, and the commit is undone, whether the clone is behind origin or not.
- **a-red-origin-has-not-repaired-is-still-refused.** When origin itself is still red on a whole-tree check, a clone
  behind it is refused naming that check, as an up-to-date clone is.
- **a-check-that-died-on-enomem-runs-again.** A check whose last output line is an `OSError: [Errno 12]` or `MemoryError`
  traceback measured nothing: it runs once more, alone, and the output says so. The second reading stands, so a red
  one, or a second out of memory, is refused. A check's own FAIL text that names the words is a red and runs once
  (`RIMMANDRAKE_RERUN_DOOR_CHECK_DEAD_ON_ENOMEM_NOT_RED`, a sound landing refused 2026-11-23).
