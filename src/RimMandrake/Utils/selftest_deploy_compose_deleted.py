#!/usr/bin/env python3
"""Selftest (COMPOSE_PLAN_FIX_COMMITTED_DELETES): in a `--compose biomes` plan a
game-only file under Biomes/<key>/ whose SOURCE folder (src/RimMandrake/<source>/)
tracked and later deleted it in a commit is a stale deploy, not a hand edit.
composed_repo_deleted() maps the composed dest path back through the manifest
entry to the source folder's git history (seen live: Biomes/Warscar/.../
RM_TetchikJar.xml, cut in d28a529cff from Scarlands/, labelled 'kept, --pull').

    python3 src/RimMandrake/Utils/selftest_deploy_compose_deleted.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
from selftest_deploy_prune import write, git                     # noqa: E402

TIER = D.biomes_compose.TIER_DIR


def main():
    tmp = tempfile.mkdtemp(prefix="composedel-")
    saved = D.SRC_ROOT
    try:
        repo = os.path.join(tmp, "repo")
        src = os.path.join(repo, TIER, "Scarlands")
        write(os.path.join(src, "Defs", "Jar.xml"), "<Defs />\n")
        write(os.path.join(src, "Defs", "Keep.xml"), "<Defs />\n")
        git(repo, "init", "-q", "-b", "main")
        git(repo, "add", "."); git(repo, "commit", "-qm", "one")
        git(repo, "rm", "-q", os.path.join(TIER, "Scarlands", "Defs", "Jar.xml"))
        git(repo, "commit", "-qm", "cut jar")
        # a committed RENAME (git mv; rename detection would call it R, not D)
        write(os.path.join(src, "Defs", "Moved.xml"), "<Defs><ThingDef><defName>M</defName>"
              "<label>a long enough body that rename detection pairs it</label></ThingDef></Defs>\n")
        git(repo, "add", "."); git(repo, "commit", "-qm", "add moved")
        # renamed INSIDE the mod (pathspec sees both ends, so log pairs them R)
        git(repo, "mv", os.path.join(TIER, "Scarlands", "Defs", "Moved.xml"),
            os.path.join(TIER, "Scarlands", "Defs", "Renamed.xml"))
        git(repo, "commit", "-qm", "rename in place")
        moved = D.repo_deleted(src, [os.path.join("Defs", "Moved.xml")])
        D.SRC_ROOT = repo
        man = {"target": "T", "compose_wave": 1, "entries": [
            {"key": "Warscar", "source": "Scarlands", "wave": 1, "group": "biome"},
            {"key": "Later", "source": "Later", "wave": 5, "group": "biome"}]}
        jar = os.path.join("Biomes", "Warscar", "Defs", "Jar.xml")
        hand = os.path.join("Biomes", "Warscar", "Defs", "HandEdit.xml")
        other = os.path.join("About", "About.xml")
        got = D.composed_repo_deleted([jar, hand, other], man)
        cases = [
            ("committed source delete maps to the composed dest path", jar in got),
            ("game-only hand edit is not called a repo delete", hand not in got),
            ("path outside any entry is not called a repo delete", other not in got),
            ("empty gone -> empty set", D.composed_repo_deleted([], man) == set()),
            ("file renamed inside the mod: old name counts as repo-deleted (UtinniPatches "
             "RUT_Wasteland.xml, 80e0635c30)", bool(moved)),
        ]
        bad = 0
        for label, ok in cases:
            bad += not ok
            print("%s  %s" % ("ok  " if ok else "FAIL", label))
        print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        D.SRC_ROOT = saved
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
