#!/usr/bin/env python3
"""selftest_arena_csharp_check: a hidden check that builds C# runs in the judge's check sandbox
(ARENA_CSHARP_CHECK_BUILD_IN_JUDGE_SANDBOX).

selftest_coldstorage.py, selftest_world_args_core.py and the *_fuzz selftests call winbuild.stage_build, which rsyncs the
tree onto D: and runs Windows dotnet.exe. In the check sandbox that failed at base AND fix, so the vet dropped those C#
tasks as non-discriminating: the stage root was read-only, src/Directory.Build.{props,targets} were not in the tree,
and the tmpfs /proc killed WSL interop (/init reads /proc/self/mountinfo). Pinned here:
  - BUILDS_CSHARP_RE picks the checks that name winbuild / dotnet, and only those;
  - such a check gets a fresh writable WINBUILD_ROOT (removed afterwards) and a WINBUILD_LOCK_DIR in its own scratch,
    and a Windows .exe actually starts inside it (live, when /mnt/c/Windows/System32/cmd.exe exists);
  - FORCED: the same .exe from a check that does not name winbuild fails (the interop shape is what makes it work,
    and an ordinary check still gets the tmpfs /proc and no stage);
  - a stage root inside a judge mask (the arena root) is refused (JudgeError), never bound;
  - materialise always writes BUILD_FILES.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_judge as J  # noqa: E402

CMD = "/mnt/c/Windows/System32/cmd.exe"
FAILS = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


BODY = r'''# a C# check: winbuild.stage_build would stage under WINBUILD_ROOT
import os, subprocess, sys
CMD = %r
root, locks = os.environ.get("WINBUILD_ROOT"), os.environ.get("WINBUILD_LOCK_DIR", "")
open("stage_path.txt", "w").write(root or "")
ok = bool(root) and os.path.isdir(root) and not os.listdir(root)
ok = ok and os.path.realpath(locks).startswith(os.path.realpath(os.getcwd()) + os.sep)
if ok:
    open(os.path.join(root, "probe.txt"), "w").write("x")
if ok and os.path.exists(CMD):
    ok = subprocess.run([CMD, "/c", "exit 0"], cwd=root, capture_output=True, timeout=60).returncode == 0
sys.exit(0 if ok else 1)
''' % CMD

PLAIN_EXE = ("import os, subprocess, sys\nok = os.path.exists(%r) and subprocess.run([%r, '/c', 'exit 0'], "
             "capture_output=True, timeout=60).returncode == 0\nsys.exit(0 if ok else 1)\n" % (CMD, CMD))
PLAIN_ENV = "import os, sys\nsys.exit(1 if os.environ.get('WINBUILD_ROOT') else 0)\n"


def run(tmp, tag, body):
    w = tmp / ("w_" + tag)
    t = w / "tree"
    t.mkdir(parents=True)
    r = J.run_hidden([{"kind": "fix_test", "path": "sel.py", "body": body}], t.resolve(), w.resolve(), timeout=120)[0]
    return r, w


def t_regex():
    hits = ["import winbuild\n", "rc = winbuild.stage_build(p)\n", "d = 'dotnet.exe'\n", "run(['dotnet', 'run'])\n"]
    miss = ["import os\n", "winbuilder = 1\n", "dotnetty = 2\n", "mywinbuild_x = 3\n"]
    check(all(J.BUILDS_CSHARP_RE.search(b) for b in hits), "BUILDS_CSHARP_RE names every winbuild/dotnet body")
    check(not any(J.BUILDS_CSHARP_RE.search(b) for b in miss), "BUILDS_CSHARP_RE leaves look-alike names alone")


def t_csharp_check(tmp):
    r, w = run(tmp, "cs", BODY)
    live = os.path.exists(CMD)
    check(r["result"] == "pass", "a check naming winbuild gets a fresh writable WINBUILD_ROOT, a lock dir in its scratch"
          "%s (%s rc %s %s)" % (" and a live Windows .exe" if live else " (no cmd.exe: interop half SKIPPED)",
                                r["result"], r["rc"], r.get("tail", "")[-300:]))
    sp = (w / "check_00" / "stage_path.txt")
    stage = sp.read_text() if sp.exists() else ""
    check(bool(stage) and not os.path.exists(stage), "the stage dir is removed after the check (%r)" % stage)
    r, _ = run(tmp, "plainenv", PLAIN_ENV)
    check(r["result"] == "pass", "an ordinary check gets no WINBUILD_ROOT (%s rc %s)" % (r["result"], r["rc"]))
    if live:
        r, _ = run(tmp, "plainexe", PLAIN_EXE)
        check(r["result"] == "fail", "forced: the same Windows .exe from a check NOT naming the build fails (tmpfs "
              "/proc, interop dead) -> the interop shape is what makes the C# check work (%s rc %s)"
              % (r["result"], r["rc"]))
    else:
        print("SKIP  forced interop control: %s not present" % CMD)


def t_refuse(tmp):
    os.environ["ARENA_WIN_STAGE_ROOT"] = str(Path(os.environ["ARENA_ROOT"]) / "stage")
    try:
        try:
            run(tmp, "refuse", BODY)
            check(False, "a stage root inside the arena root (a judge mask) is refused")
        except J.JudgeError as e:
            check("overlaps judge mask" in str(e), "a stage root inside the arena root (a judge mask) is refused (%s)"
                  % e)
        check(not (Path(os.environ["ARENA_ROOT"]) / "stage").exists(), "the refused stage root was never created")
    finally:
        os.environ["ARENA_WIN_STAGE_ROOT"] = str(tmp / "stage_root")


def t_build_files(tmp):
    repo = tmp / "repo"
    (repo / "src" / "x").mkdir(parents=True)
    for f in J.BUILD_FILES + ("src/x/a.txt", "src/other.txt"):
        (repo / f).write_text("<Project/>\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "fixture"]):
        subprocess.run(["git", "-C", str(repo)] + args, check=True, env=env, capture_output=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dest = J.materialise(repo, head, [], tmp / "mat", tree_paths=("src/x",))
    check(all((dest / f).exists() for f in J.BUILD_FILES) and (dest / "src/x/a.txt").exists()
          and not (dest / "src/other.txt").exists(), "materialise writes BUILD_FILES, and nothing else outside the set")


def main():
    if not shutil.which("bwrap"):
        print("UNMEASURED: bwrap not installed")
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="arena_cs_check_st_")).resolve()
    keys = ("ARENA_ROOT", "ARENA_CLONES", "ARENA_PRIVATE", "ARENA_JUDGE_WORK", "ARENA_WIN_STAGE_ROOT")
    saved = {k: os.environ.get(k) for k in keys}
    try:
        os.environ.update(ARENA_ROOT=str(tmp / "arena"), ARENA_CLONES=str(tmp / "clones"),
                          ARENA_PRIVATE=str(tmp / "private"), ARENA_JUDGE_WORK=str(tmp / "work"),
                          ARENA_WIN_STAGE_ROOT=str(tmp / "stage_root"))
        for k in ("ARENA_ROOT", "ARENA_CLONES", "ARENA_JUDGE_WORK"):
            Path(os.environ[k]).mkdir(parents=True)
        t_regex()
        t_csharp_check(tmp)
        t_refuse(tmp)
        t_build_files(tmp)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest_arena_csharp_check: %s" % ("%d FAILED" % len(FAILS) if FAILS else "all passed"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
