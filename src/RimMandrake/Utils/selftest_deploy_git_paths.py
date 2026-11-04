#!/usr/bin/env python3
"""Selftest for three deploy-planner git-history bugs (2026-10-24 review):
DEPLOY_PLAN_FIX_GIT_QUOTED_PATHS    non-ASCII names must match (git -z, not quotepath)
DEPLOY_PLAN_FIX_READDED_FILE_PRUNE  deleted, re-added, then deleted ONLY in the worktree
                                    is uncommitted, not committed-stale
DEPLOY_PLAN_FIX_DIR_CASE_RENAME     a case-only rename of a DIRECTORY converges on a
                                    case-insensitive game folder, and on a case-insensitive
                                    REPO checkout repo_deleted sees the old spelling as stale
                                    (DEPLOY_SELFTEST_FIX_MUTANT_STILL_PASSES: that clause had
                                    no case, so _gone_for_good reverted to os.path.exists
                                    passed 7/7)
Real functions / main() against throwaway git repos. The repo-checkout clause runs on
a simulated case-blind os.path.exists everywhere, and on a real case-insensitive root
too when one is reachable. --mutant swaps in the pre-fix _gone_for_good: it must FAIL.

    python3 src/RimMandrake/Utils/selftest_deploy_git_paths.py [--mutant]
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


def _case_blind_exists(root, real):
    """os.path.exists as a case-insensitive checkout answers it, for paths under root."""
    root = os.path.normcase(os.path.abspath(root))

    def exists(path):
        ap = os.path.abspath(path)
        if not ap.startswith(root + os.sep):
            return real(path)
        cur = root
        for part in ap[len(root) + 1:].split(os.sep):
            try:
                hit = [n for n in os.listdir(cur) if n.lower() == part.lower()]
            except OSError:
                return False
            if not hit:
                return False
            cur = os.path.join(cur, hit[0])
        return True
    return exists


def repo_case(repo_root, simulate):
    """The repo ITSELF on a case-insensitive checkout: commit Textures/Foo -> foo (a
    directory) and Textures/Cap.png -> cap.png (a file). repo_deleted must report both
    old spellings as committed-stale. -> set returned by repo_deleted."""
    tmp = tempfile.mkdtemp(prefix="deploygp-repo-", dir=repo_root)
    try:
        mod, _ = fixture(tmp)
        repo = os.path.join(tmp, "repo")
        write(os.path.join(mod, "Textures", "Foo", "a.png"), "old")
        write(os.path.join(mod, "Textures", "Cap.png"), "old")
        git(repo, "add", "."); git(repo, "commit", "-qm", "foo")
        for a, b in ((("Textures", "Foo"), ("Textures", "foo")),
                     (("Textures", "Cap.png"), ("Textures", "cap.png"))):
            # two-step mv: a one-step case-only mv is refused on a case-insensitive fs
            git(repo, "mv", os.path.join(mod, *a), os.path.join(mod, *a) + ".tmp")
            git(repo, "mv", os.path.join(mod, *a) + ".tmp", os.path.join(mod, *b))
        git(repo, "commit", "-qm", "case renames")
        gone = ["Textures/Foo/a.png", "Textures/Cap.png"]
        real = os.path.exists
        if simulate:
            os.path.exists = _case_blind_exists(mod, real)
        try:
            return D.repo_deleted(mod, gone)
        finally:
            os.path.exists = real
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _pre_fix_gone_for_good(src, g):
    """The mutant: the code before DEPLOY_PLAN_FIX_DIR_CASE_RENAME (case-blind)."""
    return not os.path.exists(os.path.join(src, g.replace("/", os.sep)))


def main():
    if "--mutant" in sys.argv[1:]:
        D._gone_for_good = _pre_fix_gone_for_good
        print("MUTANT _gone_for_good = os.path.exists (pre-fix); this run must FAIL")
    rd, wd, uni = quoted_and_readded()
    want = {"Textures/Foo/a.png", "Textures/Cap.png"}
    sim = {g.replace(os.sep, "/") for g in repo_case(tempfile.gettempdir(), True)}
    emitted, real_emit = [], D._emit_deploy           # review wave 87: a fixture --apply must not reach telemetry
    D._emit_deploy = lambda *a: emitted.append(a)
    try:
        rc4, dirs4, body4, plan4 = dir_case(tempfile.gettempdir())
    finally:
        D._emit_deploy = real_emit
    ci = case_insensitive_root()
    if ci:
        rc5, dirs5, body5, plan5 = dir_case(ci)
        real_ci = {g.replace(os.sep, "/") for g in repo_case(ci, False)}
    else:
        print("SKIP  directory case rename on a case-insensitive fs (none reachable)")
    cases = [
        ("non-ASCII committed delete is seen by repo_deleted", uni in rd),
        ("re-added then worktree-deleted file is NOT committed-stale", "Textures/Re.png" not in rd),
        ("... and is reported as a worktree delete", "Textures/Re.png" in wd),
        ("repo on a case-insensitive checkout (simulated): committed dir and file case renames "
         "are repo_deleted (got %s)" % sorted(sim), sim == want),
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
                  ("... plan afterwards is in sync", "in sync" in plan5),
                  ("repo itself on the case-INSENSITIVE fs (%s): dir and file case renames are "
                   "repo_deleted (got %s)" % (ci, sorted(real_ci)), real_ci == want)]
    bad = 0
    for label, ok in cases:
        print("%-5s %s" % ("PASS" if ok else "FAIL", label))
        bad += not ok
    print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
