#!/usr/bin/env python3
"""Selftest: --apply (no --prune) prunes game files the REPO deleted (git
history), keeps game-only hand edits, and never deletes outside the mod folder.
Real main() against a throwaway git repo + fake game dir.

    python3 src/RimMandrake/Utils/selftest_deploy_prune.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

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


def git(repo, *a):
    subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                    "-c", "commit.gpgsign=false"] + list(a),
                   check=True, capture_output=True)


def main():
    tmp = tempfile.mkdtemp(prefix="deployprune-")
    try:
        repo, game = os.path.join(tmp, "repo"), os.path.join(tmp, "game")
        mod = os.path.join(repo, TIER, "ModA")
        write(os.path.join(mod, "About", "About.xml"), ABOUT)
        write(os.path.join(mod, "Defs", "Ladder.xml"), "<Defs />\n")
        write(os.path.join(mod, "Defs", "Keep.xml"), "<Defs />\n")
        git(repo, "init", "-q", "-b", "main")
        git(repo, "add", "."); git(repo, "commit", "-qm", "one")
        os.remove(os.path.join(mod, "Defs", "Ladder.xml"))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "delete ladder")
        # game: stale Ladder (repo-deleted), HandEdit (never in repo)
        for f in ("About/About.xml", "Defs/Keep.xml", "Defs/Ladder.xml", "Defs/HandEdit.xml"):
            write(os.path.join(game, "ModA", f), ABOUT if f.endswith("About.xml") else "<Defs />\n")
        cfg = os.path.join(tmp, "ModsConfig.xml")
        write(cfg, "<ModsConfigData><activeMods><li>test.mod</li></activeMods></ModsConfigData>\n")
        hold = os.path.join(tmp, "HOLD.txt"); write(hold, "")
        D.SRC_ROOT, D.HOLD_FILE = repo, hold
        D._MODS, D._CONFIG = [game], [cfg]

        g = lambda f: os.path.join(game, "ModA", "Defs", f)             # noqa: E731
        sys.argv = ["x", "--mod", "ModA"]
        D.main()
        plan_ok = os.path.exists(g("Ladder.xml")) and os.path.exists(g("HandEdit.xml"))
        sys.argv = ["x", "--mod", "ModA", "--apply"]
        D.main()
        cases = [
            ("plan-only deletes nothing", plan_ok),
            ("--apply prunes repo-deleted file without --prune", not os.path.exists(g("Ladder.xml"))),
            ("--apply keeps never-in-repo hand edit", os.path.exists(g("HandEdit.xml"))),
            ("repo file untouched", os.path.exists(g("Keep.xml"))),
            ("inside() accepts in-folder", D.inside(os.path.join(game, "ModA"), "Defs/x.xml")),
            ("inside() refuses ../ escape", not D.inside(os.path.join(game, "ModA"), "../../x.xml")),
        ]
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
