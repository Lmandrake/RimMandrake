#!/usr/bin/env python3
"""Selftest for three deploy-planner git-history bugs (2026-10-24 review):
DEPLOY_PLAN_FIX_GIT_QUOTED_PATHS    non-ASCII names must match (git -z, not quotepath)
DEPLOY_PLAN_FIX_READDED_FILE_PRUNE  deleted, re-added, then deleted ONLY in the worktree
                                    is uncommitted, not committed-stale
DEPLOY_PLAN_FIX_DIR_CASE_RENAME     a case-only rename of a DIRECTORY converges on a
                                    case-insensitive game folder
Real functions / main() against throwaway git repos.

    python3 src/RimMandrake/Utils/selftest_deploy_git_paths.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deploy_custom_mods as D                                  # noqa: E402
from selftest_deploy_prune import ABOUT, write, git              # noqa: E402
from selftest_deploy_deleted import run, case_insensitive_root, fixture  # noqa: E402


def quoted_and_readded():
    tmp = tempfile.mkdtemp(prefix="deploygp-")
    try:
        mod, gmod = fixture(tmp)
        repo = os.path.join(tmp, "repo")
        uni = "Textures/Café ü.png"
        for f in (uni, "Textures/Re.png"):
            write(os.path.join(mod, f), "x")
        git(repo, "add", "."); git(repo, "commit", "-qm", "add")
        os.remove(os.path.join(mod, uni))
        os.remove(os.path.join(mod, "Textures", "Re.png"))
        git(repo, "add", "-A"); git(repo, "commit", "-qm", "del")
        write(os.path.join(mod, "Textures", "Re.png"), "y")      # re-added ...
        git(repo, "add", "."); git(repo, "commit", "-qm", "readd")
        os.remove(os.path.join(mod, "Textures", "Re.png"))       # ... deleted, uncommitted
        gone = [uni, "Textures/Re.png"]
        return (D.repo_deleted(mod, gone), D.worktree_deleted(mod, gone), uni)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def dir_case(game_root):
    tmp = tempfile.mkdtemp(prefix="deploygp-")
    gtmp = tempfile.mkdtemp(prefix="deploygp-game-", dir=game_root)
    try:
        mod, _ = fixture(tmp)
        shutil.move(os.path.join(tmp, "game"), os.path.join(gtmp, "game"))
        D._MODS = [os.path.join(gtmp, "game")]
        gmod = os.path.join(gtmp, "game", "ModA")
        repo = os.path.join(tmp, "repo")
        for r in (mod, gmod):
            write(os.path.join(r, "Textures", "Foo", "a.png"), "old")
        git(repo, "add", "."); git(repo, "commit", "-qm", "foo")
        git(repo, "mv", os.path.join(mod, "Textures", "Foo"), os.path.join(mod, "Textures", "foo"))
        write(os.path.join(mod, "Textures", "foo", "a.png"), "new")
        git(repo, "add", "."); git(repo, "commit", "-qm", "dir case rename")
        rc, out = run(["--mod", "ModA", "--apply"])
        rc2, out2 = run(["--mod", "ModA"])
        # an emptied old-spelled dir is harmless (only files are inventoried); count dirs holding files
        dirs = sorted(n for n in os.listdir(os.path.join(gmod, "Textures"))
                      if n.lower() == "foo" and os.listdir(os.path.join(gmod, "Textures", n)))
        p = os.path.join(gmod, "Textures", "foo", "a.png")
        return rc, dirs, (open(p).read() if os.path.exists(p) else None), out2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(gtmp, ignore_errors=True)


def main():
    rd, wd, uni = quoted_and_readded()
    emitted, real_emit = [], D._emit_deploy           # review wave 87: a fixture --apply must not reach telemetry
    D._emit_deploy = lambda *a: emitted.append(a)
    try:
        rc4, dirs4, body4, plan4 = dir_case(tempfile.gettempdir())
    finally:
        D._emit_deploy = real_emit
    ci = case_insensitive_root()
    if ci:
        rc5, dirs5, body5, plan5 = dir_case(ci)
    else:
        print("SKIP  directory case rename on a case-insensitive fs (none reachable)")
    cases = [
        ("non-ASCII committed delete is seen by repo_deleted", uni in rd),
        ("re-added then worktree-deleted file is NOT committed-stale", "Textures/Re.png" not in rd),
        ("... and is reported as a worktree delete", "Textures/Re.png" in wd),
        ("dir case rename, case-sensitive fs: old dir gone, new deployed",
         rc4 == 0 and dirs4 == ["foo"] and body4 == "new"),
        ("... plan afterwards is in sync", "in sync" in plan4),
        ("an --apply into a throwaway Mods folder emits no telemetry deploy event (got %d)" % len(emitted),
         not emitted),
        ("... while the real game Mods folder still counts as real", D._is_real_game(D.LOCAL_MODS)
         if hasattr(D, "_is_real_game") else False),
    ]
    if ci:
        cases += [("dir case rename, case-INSENSITIVE fs (%s): directory respelled, exit 0" % ci,
                   rc5 == 0 and dirs5 == ["foo"] and body5 == "new"),
                  ("... plan afterwards is in sync", "in sync" in plan5)]
    bad = 0
    for label, ok in cases:
        print("%-5s %s" % ("PASS" if ok else "FAIL", label))
        bad += not ok
    print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
