#!/usr/bin/env python3
"""Selftest for the DEPLOY_HOLD mechanism in deploy_custom_mods.py.

Runs the REAL main() against throwaway directories, never the game install.

The case that matters is the destructive one: `--apply --prune` deleting a file
that a hold was supposed to protect. A retired seat caught it by reading the code before
it landed — the write path was filtered through the hold list and the delete
path was not, so a hold stopped us WRITING a file but not DELETING one. A hold
means "do not change the game's copy of this path", and deleting is a change.

    python3 src/RimMandrake/Utils/selftest_deploy_hold.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402

# Mods live one level below SRC_ROOT since the two-tier src/ split (plan §4
# dep 2). The fake repo must have the same shape or discovery finds nothing.
TIER = D.SRC_TIERS[0]

ABOUT = ('<?xml version="1.0" encoding="utf-8"?>\n'
         "<ModMetaData><packageId>test.mod</packageId></ModMetaData>\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def build(tmp):
    repo = os.path.join(tmp, "repo")
    game = os.path.join(tmp, "game")
    # repo side
    write(os.path.join(repo, TIER, "ModA", "About", "About.xml"), ABOUT)
    write(os.path.join(repo, TIER, "ModA", "Patches", "Ships.xml"), "<Patch />\n")
    write(os.path.join(repo, TIER, "ModA", "Patches", "HeldEdit.xml"), "<Patch>new</Patch>\n")
    # game side
    write(os.path.join(game, "ModA", "About", "About.xml"), ABOUT)
    write(os.path.join(game, "ModA", "Patches", "HeldEdit.xml"), "<Patch>old</Patch>\n")
    write(os.path.join(game, "ModA", "Patches", "HeldGone.xml"), "<Patch />\n")
    write(os.path.join(game, "ModA", "Patches", "Junk.xml"), "<Patch />\n")
    # config: mod is active
    cfg = os.path.join(tmp, "ModsConfig.xml")
    write(cfg, "<ModsConfigData><activeMods><li>test.mod</li>"
               "</activeMods></ModsConfigData>\n")
    hold = os.path.join(repo, "DEPLOY_HOLD.txt")
    write(hold, "ModA/Patches/HeldEdit.xml   # held: differs in both\n"
                "ModA/Patches/HeldGone.xml   # held: game-only, parked\n")
    return repo, game, cfg, hold


def main():
    tmp = tempfile.mkdtemp(prefix="deployhold-")
    try:
        repo, game, cfg, hold = build(tmp)
        D.SRC_ROOT, D.HOLD_FILE = repo, hold
        D._MODS, D._CONFIG = [game], [cfg]
        sys.argv = ["x", "--apply", "--prune"]
        print("--- running deploy --apply --prune against temp dirs ---")
        D.main()
        print("--- checks ---")

        g = lambda *p: os.path.join(game, "ModA", "Patches", *p)          # noqa: E731
        read = lambda p: open(p, encoding="utf-8").read()                 # noqa: E731

        cases = [
            ("held file that differs is NOT overwritten",
             os.path.exists(g("HeldEdit.xml")) and "old" in read(g("HeldEdit.xml"))),
            ("held file present only in GAME survives --prune",
             os.path.exists(g("HeldGone.xml"))),
            ("unheld game-only file IS pruned",
             not os.path.exists(g("Junk.xml"))),
            ("unheld repo file IS deployed",
             os.path.exists(g("Ships.xml"))),
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
