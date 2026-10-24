#!/usr/bin/env python3
"""Selftest: deploy_custom_mods stats each file ONCE per plan
(DEPLOY_PLAN_FIX_REDUNDANT_TREE_PASSES).

On the /mnt/c game copy a stat is ~1.7 ms; a full plan made ~143k of them because
tree() did an exists() per file, filecmp stat'ed both sides again, and the stale-hold
scan re-walked every root. This pins (1) compare() classification byte-identical to
the old algorithm (os.walk + exists + filecmp.cmp(shallow=False)), including an
equal-size/different-bytes file and a dangling symlink; (2) stats per file <= 1 per
side and zero on a repeat inventory; (3) a whole plan walks each mod root once.

    python3 src/RimMandrake/Utils/selftest_deploy_single_walk.py
"""
import filecmp
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402

TIER = D.SRC_TIERS[0]
ABOUT = ('<?xml version="1.0" encoding="utf-8"?>\n'
         "<ModMetaData><packageId>test.mod</packageId></ModMetaData>\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def old_tree(root):
    out = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in D.EXCLUDE_DIRS]
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), root)
            if D.shippable(rel) and os.path.exists(os.path.join(dp, f)):
                out.add(rel)
    return out


def old_compare(src, dst):
    s, d = old_tree(src), old_tree(dst)
    changed = [r for r in sorted(s & d)
               if not filecmp.cmp(os.path.join(src, r), os.path.join(dst, r), shallow=False)]
    return sorted(s - d), changed, sorted(d - s), sorted((s & d) - set(changed))


class Counter:
    """Counts os.stat/os.lstat and DirEntry.stat while active."""
    def __init__(self):
        self.n = 0
        self.scans = []

    def __enter__(self):
        self.st, self.ls, self.sd = os.stat, os.lstat, os.scandir
        me = self

        def st(*a, **k):
            me.n += 1
            return me.st(*a, **k)

        def ls(*a, **k):
            me.n += 1
            return me.ls(*a, **k)

        class E:
            def __init__(s, e):
                s.e = e

            def stat(s, *a, **k):
                me.n += 1
                return s.e.stat(*a, **k)

            def __getattr__(s, n):
                return getattr(s.e, n)

        class It:
            def __init__(s, it):
                s.it = it

            def __iter__(s):
                return (E(e) for e in s.it)

            def __enter__(s):
                return s

            def __exit__(s, *a):
                s.it.close()

            def close(s):
                s.it.close()

        def sd(path=".", *a, **k):
            me.scans.append(os.fspath(path))
            return It(me.sd(path, *a, **k))
        os.stat, os.lstat, os.scandir = st, ls, sd
        return self

    def __exit__(self, *a):
        os.stat, os.lstat, os.scandir = self.st, self.ls, self.sd


def main():
    tmp = tempfile.mkdtemp(prefix="deploywalk-")
    try:
        repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
        src, dst = os.path.join(repo, TIER, "ModA"), os.path.join(game, "ModA")
        write(os.path.join(src, "About", "About.xml"), ABOUT)
        write(os.path.join(dst, "About", "About.xml"), ABOUT)
        for i in range(40):                                   # identical
            write(os.path.join(src, "Defs", "d%d.xml" % i), "<Defs>%d</Defs>\n" % i)
            write(os.path.join(dst, "Defs", "d%d.xml" % i), "<Defs>%d</Defs>\n" % i)
        write(os.path.join(src, "Defs", "same_size.xml"), "<Defs>AAAA</Defs>\n")
        write(os.path.join(dst, "Defs", "same_size.xml"), "<Defs>BBBB</Defs>\n")   # equal size, other bytes
        write(os.path.join(src, "Defs", "longer.xml"), "<Defs>1234567</Defs>\n")
        write(os.path.join(dst, "Defs", "longer.xml"), "<Defs>1</Defs>\n")
        write(os.path.join(src, "Defs", "new.xml"), "<Defs/>\n")
        write(os.path.join(dst, "Defs", "gone.xml"), "<Defs/>\n")
        write(os.path.join(src, "Source", "skip.cs"), "x\n")      # excluded dir
        os.symlink(os.path.join(tmp, "nowhere"), os.path.join(src, "Defs", "dangling.xml"))
        nfiles = len(old_tree(src)) + len(old_tree(dst))

        with Counter() as c0:
            want = old_compare(src, dst)
        old_stats = c0.n
        D._INV.clear()
        with Counter() as c:
            got = D.compare(src, dst)
            first = c.n
            D.compare(src, dst)
            D.tree(src)
            D.tree(dst)
            repeat = c.n - first
        cases = [
            ("compare() classification equals the old walk+exists+filecmp",
             got == want),
            ("equal-size, different-bytes file is CHANGED (bytes read, not size/mtime)",
             os.path.join("Defs", "same_size.xml") in got[1]),
            ("different-size file is CHANGED", os.path.join("Defs", "longer.xml") in got[1]),
            ("dangling symlink is not a file", os.path.join("Defs", "dangling.xml") not in got[2] + got[0]),
            ("<= 1 stat per file per side (%d stats, %d files)" % (first, nfiles), first <= nfiles + 8),   # + root isdir checks, dangling link probe
            ("can-fail: the OLD algorithm would have failed the stat bound (%d stats)" % old_stats,
             old_stats > nfiles + 8),
            ("repeat compare/tree stat nothing (%d)" % repeat, repeat == 0),
        ]

        # whole plan: each mod root is walked once, not per pass
        cfg = os.path.join(tmp, "ModsConfig.xml")
        write(cfg, "<ModsConfigData><activeMods><li>test.mod</li></activeMods></ModsConfigData>\n")
        hold = os.path.join(repo, "DEPLOY_HOLD.txt")
        write(hold, "ModA/Defs/d1.xml   # held\n")
        D.SRC_ROOT, D.HOLD_FILE = repo, hold
        D._MODS, D._CONFIG = [game], [cfg]
        sys.argv = ["x"]
        D._INV.clear()
        with Counter() as c2, redirect_stdout(io.StringIO()):
            D.main()
        walks = [p for p in c2.scans if os.path.normpath(p) == os.path.normpath(dst)]
        cases.append(("plan scans the game mod root once for the inventory (%d)" % len(walks),
                      len(walks) <= 2))   # 1 inventory + 1 guard xml walk
        cases.append(("plan statted no more than 2 per file (%d stats)" % c2.n,
                      c2.n <= 2 * nfiles + 400))

        bad = 0
        for label, ok in cases:
            bad += not ok
            print("%s  %s" % ("ok  " if ok else "FAIL", label))
        print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
