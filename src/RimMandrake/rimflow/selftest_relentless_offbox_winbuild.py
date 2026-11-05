#!/usr/bin/env python3
"""CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK: the Marker's box runs no Windows program (dotnet.exe there says 'Invalid
argument' on the \\\\wsl.localhost staged path, HEAVY_TEXTURES_MEASURE_REAL_VRAM), so a proof that builds the JawaBench
companion goes dark. The repair is a supervisor offbox adapter, jawabench_build_candidate, seeded on the windows_build
reach class.

W1 the adapter is fixed argv (python3 -I -c <script> {repo} {sha}), no shell, and fill_argv fills it from supervisor values
   with the script token untouched; W2 the windows_build class seeds it and still tickets to this item; W3 the script
   compiles and never deploys (no --apply, plan-only build.py --gm, its own staged build root); W4 run for real on a
   fixture repo with no companion sources it refuses with exit 2 and 'NOT BUILT', never a quiet 0. The build itself needs
   dotnet.exe, which the box lacks: RM_WINBUILD_LIVE=1 runs it on this tree's HEAD (W5); the checker's reading is the
   contract's --offbox output."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R            # noqa: E402
import relentless_wall as W       # noqa: E402

FAILS = []
NAME = "jawabench_build_candidate"
SHA = "0123456789abcdef0123456789abcdef01234567"
RULES = json.load(open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8"))


def ok(c, msg):
    print(("PASS " if c else "FAIL ") + msg)
    if not c:
        FAILS.append(msg)


def adapter():
    return W.adapters(RULES).get(NAME) or {}


def t_shape():
    a = adapter()
    argv = a.get("argv") or []
    ok(argv[:3] == ["python3", "-I", "-c"] and argv[4:] == ["{repo}", "{sha}"] and len(argv) == 6,
       "W1 fixed argv python3 -I -c <script> {repo} {sha}: %s" % [x[:30] for x in argv])
    got, why = W.fill_argv(argv, {"sha": SHA, "repo": "/r/c"})
    ok(why is None and got[3] == argv[3] and got[4:] == ["/r/c", SHA], "W1 fill_argv fills the slots only: %s" % why)
    ok(W.check_offbox_names([NAME], RULES) == [NAME], "W1 a contract may name it")


def t_class():
    row = [c for c in RULES["reach_classes"] if c["class"] == "windows_build"]
    ok(len(row) == 1 and row[0]["adapters"] == [NAME] and row[0]["ticket"] == "CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK",
       "W2 windows_build seeds %s and tickets here: %s" % (NAME, row))


def t_script():
    s = (adapter().get("argv") or ["", "", "", ""])[3]
    try:
        compile(s, NAME, "exec")
        good = True
    except SyntaxError as e:
        good = "%s" % e
    ok(good is True, "W3 the script compiles: %s" % good)
    ok("--apply" not in s and "'--gm'" in s and "WINBUILD_ROOT" in s and "rmtree" in s,
       "W3 plan-only build.py --gm in its own staged build root, removed after; never --apply")


def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, check=True).stdout.strip()


def t_no_sources():
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", d], check=True)
        open(os.path.join(d, "README"), "w").write("x\n")
        git(d, "add", "README")
        git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "only a readme")
        sha = git(d, "rev-parse", "HEAD")
        argv, why = W.fill_argv(adapter()["argv"], {"sha": sha, "repo": d})
        got = R.run_bounded(NAME, dict(adapter(), argv=argv), 60)
    ok(got["exit"] == 2 and "NOT BUILT" in got["out"], "W4 no companion sources: exit 2, NOT BUILT: %s %r"
       % (got["exit"], got["out"][-200:]))


def t_live():
    if os.environ.get("RM_WINBUILD_LIVE") != "1":
        print("SKIP W5 the real Windows build (RM_WINBUILD_LIVE=1 runs it; the checker reads the contract's --offbox)")
        return
    repo = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    argv, why = W.fill_argv(adapter()["argv"], {"sha": git(repo, "rev-parse", "HEAD"), "repo": repo})
    got = R.run_bounded(NAME, dict(adapter(), argv=argv), RULES.get("offbox_max_s", 120))
    ok(got["exit"] == 0 and "build.py --gm exit=0" in got["out"] and "GM TOOLS INCLUDED" in got["out"],
       "W5 the companion builds at HEAD outside the wall: %s %r" % (got["exit"], got["out"][-300:]))


if __name__ == "__main__":
    for t in (t_shape, t_class, t_script, t_no_sources, t_live):
        t()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)
