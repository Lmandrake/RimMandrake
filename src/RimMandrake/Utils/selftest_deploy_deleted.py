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


CI_ROOTS = ("/mnt/d/ClaudeWork/rimmandrake/scratch", r"D:\ClaudeWork\rimmandrake\scratch")


def case_insensitive_root():
    """A scratch root on a case-INSENSITIVE fs (the game folder's kind), or None."""
    for root in [tempfile.gettempdir()] + list(CI_ROOTS):
        try:
            os.makedirs(root, exist_ok=True)
            d = tempfile.mkdtemp(prefix="ciprobe-", dir=root)
        except OSError:
            continue
        try:
            open(os.path.join(d, "A"), "w").close()
            if os.path.exists(os.path.join(d, "a")):
                return root
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return None


def case_rename(game_root):
    """Committed case-only rename Textures/Cap.png -> cap.png, then plain --apply.
    The repo stays on the default (case-sensitive) tmp, like the real clone; only
    the game dir moves under `game_root`.
    -> (rc, game file names under Textures, content of the game copy or None, out)."""
    tmp = tempfile.mkdtemp(prefix="deploycase-")
    gtmp = tempfile.mkdtemp(prefix="deploycase-game-", dir=game_root)
    try:
        mod, gmod = fixture(tmp)
        shutil.move(os.path.join(tmp, "game"), os.path.join(gtmp, "game"))
        D._MODS = [os.path.join(gtmp, "game")]
        gmod = os.path.join(gtmp, "game", "ModA")
        repo = os.path.join(tmp, "repo")
        rel = os.path.relpath(os.path.join(mod, "Textures"), repo)
        write(os.path.join(mod, "Textures", "Cap.png"), "old")
        write(os.path.join(gmod, "Textures", "Cap.png"), "old")
        git(repo, "add", "."); git(repo, "commit", "-qm", "cap")
        git(repo, "mv", os.path.join(rel, "Cap.png"), os.path.join(rel, "cap.png"))
        write(os.path.join(mod, "Textures", "cap.png"), "new")
        git(repo, "add", "."); git(repo, "commit", "-qm", "case rename")
        rc, out = run(["--mod", "ModA", "--apply"])
        names = sorted(n for n in os.listdir(os.path.join(gmod, "Textures"))
                       if n.lower() == "cap.png")
        p = os.path.join(gmod, "Textures", "cap.png")
        body = open(p).read() if os.path.exists(p) else None
        return rc, names, body, out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(gtmp, ignore_errors=True)


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

        # --- case 3: a CHANGED source XML vanishes between compare() and copy()
        # (wellformed() used to raise FileNotFoundError out of --apply)
        bc.stage_rewritten = saved[2]
        bc.folded_ids = lambda root: {}
        bc.folded_names = lambda root: {}
        write(os.path.join(mod, "Defs", "Keep.xml"), "<Defs><!-- edited --></Defs>\n")
        real_compare, calls = D.compare, []

        def compare_then_vanish(src, dst):
            r = real_compare(src, dst)
            if not calls:
                calls.append(1)
                os.remove(os.path.join(src, "Defs", "Keep.xml"))
            return r
        D.compare = compare_then_vanish
        try:
            rc3, out3 = run(["--mod", "ModA", "--apply"])
        finally:
            D.compare = real_compare
        game_keep = os.path.exists(os.path.join(gmod, "Defs", "Keep.xml"))

        # --- case 4: committed case-only rename. Case-sensitive fs: old pruned,
        # new deployed. Case-INSENSITIVE fs (the real game folder): prune used
        # to delete the file copy() had just written into the old spelling.
        rc4, names4, body4, out4 = case_rename(tempfile.gettempdir())
        ci = case_insensitive_root()
        if ci:
            rc5, names5, body5, out5 = case_rename(ci)
        else:
            print("SKIP  case-only rename on a case-insensitive fs (none reachable)")

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
            ("XML vanishing between compare and copy: --apply does not crash",
             isinstance(rc3, int)),
            ("... reported as a failed write, exit 1", rc3 == 1 and "FAILED to write" in out3),
            ("... game copy left in place (no prune after a failed write)", game_keep),
            ("case-only rename, case-sensitive fs: old spelling pruned, new deployed, exit 0",
             rc4 == 0 and names4 == ["cap.png"] and body4 == "new"),
        ]
        if ci:
            cases.append(("case-only rename, case-INSENSITIVE fs (%s): deployed file survives "
                          "under the new spelling, exit 0" % ci,
                          rc5 == 0 and names5 == ["cap.png"] and body5 == "new"))
        bad = 0
        for label, ok in cases:
            bad += not ok
            print("%s  %s" % ("ok  " if ok else "FAIL", label))
        if bad:
            print("--- rc1=%r rc1a=%r rc2=%r rc3=%r" % (rc1, rc1a, rc2, rc3))
        print("\n%d/%d passed" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        bc.folded_ids, bc.folded_names, bc.stage_rewritten = saved
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
