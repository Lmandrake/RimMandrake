#!/usr/bin/env python3
"""Selftest (DEPLOY_PLANNER_FIX_CRASH_ON_DELETED): a git-TRACKED file that is
deleted in the working tree (uncommitted -- another helper mid-move) must show
as a `-` line labelled as a repo-side deletion, never crash the planner and
never be pruned from the game by a plain --apply. Also covers the crash itself:
a mod whose deployed copy is STAGED (MayRequire rewrite -> symlink farm) and a
source file that vanishes after staging (dangling symlink -> FileNotFoundError
in filecmp, as seen on SWBestiary with Karrask.png, 2026-10-24).
Real main() against a throwaway git repo + fake game dir.

    python3 src/RimMandrake/Utils/selftest_deploy_deleted.py
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
from selftest_deploy_prune import ABOUT, write, git              # noqa: E402

TIER = D.SRC_TIERS[0]


def run(argv):
    """-> (rc or exception repr, stdout)."""
    sys.argv = ["x"] + argv
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = D.main()
    except BaseException as e:                     # the crash we are testing for
        rc = "%s: %s" % (type(e).__name__, e)
    return rc, buf.getvalue()


def fixture(tmp):
    repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
    mod = os.path.join(repo, TIER, "ModA")
    files = {"About/About.xml": ABOUT, "Defs/Keep.xml": "<Defs />\n",
             "Defs/Guarded.xml": '<Defs><ThingDef MayRequire="old.folded"><defName>X'
                                 '</defName></ThingDef></Defs>\n',
             "Textures/K.png": "png", "Textures/V.png": "png", "Textures/S.png": "png"}
    for f, t in files.items():
        write(os.path.join(mod, f), t)
        write(os.path.join(game, "ModA", f), t)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "."); git(repo, "commit", "-qm", "one")
    cfg = os.path.join(tmp, "ModsConfig.xml")
    write(cfg, "<ModsConfigData><activeMods><li>test.mod</li></activeMods></ModsConfigData>\n")
    hold = os.path.join(tmp, "HOLD.txt"); write(hold, "")
    D.SRC_ROOT, D.HOLD_FILE = repo, hold
    D._MODS, D._CONFIG = [game], [cfg]
    return mod, os.path.join(game, "ModA")


def main():
    tmp = tempfile.mkdtemp(prefix="deploydel-")
    bc = D.biomes_compose
    saved = (bc.folded_ids, bc.folded_names, bc.stage_rewritten)
    try:
        mod, gmod = fixture(tmp)
        # --- case 1: tracked K.png deleted in the worktree, uncommitted
        os.remove(os.path.join(mod, "Textures", "K.png"))
        rc1, out1 = run(["--mod", "ModA"])
        line = [ln for ln in out1.splitlines() if "Textures/K.png" in ln]
        # --- case 1b: tracked S.png deleted with `git rm` (STAGED, uncommitted)
        git(os.path.join(tmp, "repo"), "rm", "-q", os.path.relpath(
            os.path.join(mod, "Textures", "S.png"), os.path.join(tmp, "repo")))
        rc1b, out1b = run(["--mod", "ModA"])
        line1b = [ln for ln in out1b.splitlines() if "Textures/S.png" in ln]
        rc1a, out1a = run(["--mod", "ModA", "--apply"])
        kept = (os.path.exists(os.path.join(gmod, "Textures", "K.png"))
                and os.path.exists(os.path.join(gmod, "Textures", "S.png")))

        # --- case 2: staged copy (folded MayRequire) + V.png vanishes after staging
        bc.folded_ids = lambda root: {"old.folded": "new.composed"}
        bc.folded_names = lambda root: {}

        def stage_then_vanish(src, *a, **k):
            r = saved[2](src, *a, **k)
            v = os.path.join(src, "Textures", "V.png")
            if os.path.exists(v):
                os.remove(v)                       # another helper's delete, mid-run
            return r
        bc.stage_rewritten = stage_then_vanish
        rc2, out2 = run(["--mod", "ModA"])
        line2 = [ln for ln in out2.splitlines() if "Textures/V.png" in ln]

        cases = [
            ("worktree-deleted tracked file: plan does not crash", isinstance(rc1, int)),
            ("... shows a `-` line", bool(line) and line[0].lstrip().startswith("-  ")),
            ("... labelled a repo-side deletion, not a hand edit",
             bool(line) and "deleted in repo working tree" in line[0]),
            ("staged `git rm` (index delete): labelled a repo-side deletion too",
             isinstance(rc1b, int) and bool(line1b)
             and "deleted in repo working tree" in line1b[0]),
            ("... plain --apply does not crash", isinstance(rc1a, int)),
            ("... plain --apply keeps both (uncommitted deletes are not pruned)", kept),
            ("file vanishing after staging: plan does not crash", isinstance(rc2, int)),
            ("... vanished file reported as a `-` line", bool(line2)),
            ("staging really happened (instrument can see)", "MayRequire: rewrote" in out2),
        ]
        bad = 0
        for label, ok in cases:
            bad += not ok
            print("%s  %s" % ("ok  " if ok else "FAIL", label))
        if bad:
            print("--- rc1=%r rc1a=%r rc2=%r" % (rc1, rc1a, rc2))
        print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        bc.folded_ids, bc.folded_names, bc.stage_rewritten = saved
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
