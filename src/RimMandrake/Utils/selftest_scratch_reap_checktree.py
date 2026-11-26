#!/usr/bin/env python3
"""selftest_scratch_reap_checktree.py -- the cleaner does not refuse a clone for the check tree that ./publish left in
its own git dir (incident disk-20261115210535: two clones, 25 GB, refused "a repo nested inside:
<clone>/.git/rm-treecheck-kept/.git" from 2026-11-25 to 2026-11-26 while / stood at 52%).

A check tree is `<clone>/.git/rm-treecheck-<name>/`: a throwaway checkout that publish.py makes and removes
(design/specs/2026-11-25-treecheck-kept-tree/boundary.md). It holds a `.git` of its own, which is not a foreign repo.
Cases:
  A. a check tree's `.git` is not in Tree.nested;
  B. a repo vendored inside the clone's work tree still is (the refusal that guards real work stays);
  D. a check tree made inside a kept check tree's git dir is not nested either;
  C. a repo hidden inside a check tree's deeper path still is.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import scratch_reap as R  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        d = Path(t) / "clone"
        for rel in (".git/objects", ".git/rm-treecheck-kept/.git/objects", ".git/rm-treecheck-q3dvxzdj/.git/objects",
                    "vendored/.git/objects", ".git/rm-treecheck-kept/sub/deeper/.git/objects",
                    ".git/rm-treecheck-kept/.git/rm-treecheck-fan29ffb/.git/objects", ".git/rm-treecheck-kept/.git/other/.git/objects"):
            (d / rel).mkdir(parents=True)
        (d / "a.txt").write_text("x")
        tree = R.Tree(d)
        rel = sorted(n[len(str(d)) + 1:] for n in tree.nested)
        check(".git/rm-treecheck-kept/.git" not in rel and ".git/rm-treecheck-q3dvxzdj/.git" not in rel,
              f"A a check tree's own .git is not a nested repo (nested: {rel})")
        check(not [r for r in rel if "rm-treecheck-fan29ffb" in r],
              f"D a check tree inside a check tree's git dir is not a nested repo (nested: {rel})")
        check(".git/rm-treecheck-kept/.git/other/.git" in rel, f"E a foreign repo in a check tree's git dir is still nested (nested: {rel})")
        check("vendored/.git" in rel, f"B a repo vendored in the work tree is still nested (nested: {rel})")
        check(".git/rm-treecheck-kept/sub/deeper/.git" in rel,
              f"C a repo deeper inside a check tree is still nested (nested: {rel})")
    print("FAILED: " + "; ".join(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
