#!/usr/bin/env python3
"""nightly_scope: the nightly sweep checks FINISHED mods only, and waits, stopped, until there is one.

Item RIMMANDRAKE_PAUSE_NIGHTLY_SWEEP_WRONG_PHASE_UNTIL_MOD_FINISHED. The owner, by card 2026-11-15 ~3:50 PM PST ("Pause
nightly and fixers until a mod passes"): "(3) because I think Nightly tests should check mods with finished versions, not
mods in production. Code is too fluid otherwise. Wrong phase."

FINISHED: design/concepts/<Mod>/version/stage_record.json reads stage "passed", or a record maturation.py next-version
kept (version/stage_record_<v>.json) does: a passed version stays finished while the next one is in production. A mod
still in production is never in the set, and process machinery (Utils, rimflow, hooks, skills) belongs to no mod, so it
is never in it either (the pipeline's own tests are checked at the door instead: pipeline_tests.json, publish.py).
A mod's tests: every selftest*.py under src/<tier>/<Mod>/ at any depth, plus src/RimMandrake/Utils/selftest_<mod>.py and
selftest_<mod>_*.py (the lint and fuzz harnesses' convention), <mod> lowercased.

    nightly_scope.py show [--json]    the finished mods and their tests
    nightly_scope.py run              the nightly unit's sweep: no finished mod -> "RESULT: GREEN ... nothing finished
                                      yet", exit 0, nothing else touched; otherwise refresh the clean clone
                                      ($RM_NIGHTLY_CLONE, default /home/mandrake/rm/nightly) to origin/main and run
                                      `run_selftests.py --nightly` there with ~/.local/bin first on PATH
    nightly_scope.py hold [--apply]   the planned stop of HELD_TIMERS (timers_guard.py hold --until finished-mod): the
                                      timer guard starts them again by itself once a mod's version has passed

run_selftests.py --nightly asks tests_for() for its set, so a sweep started any other way (the catch-up, a hand start)
runs the same set. Selftest: selftest_nightly_scope.py.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ITEM = "RIMMANDRAKE_PAUSE_NIGHTLY_SWEEP_WRONG_PHASE_UNTIL_MOD_FINISHED"
NOTHING = "nothing finished yet"
# the sweep and everything that feeds on it: the sweep, its catch-up, the red reruns that file fix items, their fixers
HELD_TIMERS = ("rm-selftests-nightly.timer", "rm-selftests-nightly-catchup.timer", "rm-ops-reds.timer",
               "rm-red-dispatch.timer")
UNTIL = "finished-mod"
DEFAULT_CLONE = "/home/mandrake/rm/nightly"


def _stage(path):
    try:
        with open(path, encoding="utf-8") as f:
            r = json.load(f)
        return r.get("stage") if isinstance(r, dict) else None
    except (OSError, ValueError):
        return None


def finished_mods(root=REPO):
    """-> sorted mod names with a passed Design Version (the current record or a kept older one)."""
    out = set()
    for vdir in glob.glob(os.path.join(root, "design", "concepts", "*", "version")):
        recs = [os.path.join(vdir, "stage_record.json")] + glob.glob(os.path.join(vdir, "stage_record_*.json"))
        if any(_stage(p) == "passed" for p in recs):
            out.add(os.path.basename(os.path.dirname(vdir)))
    return sorted(out)


def mod_tests(root, mod):
    """-> sorted repo-relative selftests that belong to MOD (see the module doc)."""
    found = set()
    for d in glob.glob(os.path.join(root, "src", "*", mod)):
        if os.path.isdir(d):
            for base, _dirs, files in os.walk(d):
                found |= {os.path.join(base, f) for f in files if f.startswith("selftest") and f.endswith(".py")}
    low = mod.lower()
    utils = os.path.join(root, "src", "RimMandrake", "Utils")
    found |= set(glob.glob(os.path.join(utils, "selftest_%s.py" % low)))
    found |= set(glob.glob(os.path.join(utils, "selftest_%s_*.py" % low)))
    return sorted(os.path.relpath(p, root) for p in found)


def tests_for(root=REPO):
    """-> {"finished": [mod], "by_mod": {mod: [test]}, "tests": [test]} for the nightly."""
    mods = finished_mods(root)
    by = {m: mod_tests(root, m) for m in mods}
    pipe = pipeline_nightly(root)
    return {"finished": mods, "by_mod": by, "pipeline": pipe,
            "tests": sorted({t for ts in by.values() for t in ts} | set(pipe))}


def pipeline_nightly(root=REPO):
    """The pipeline's tests, only when pipeline_tests.json says "nightly": true (false today: they are checked at the
    door instead)."""
    try:
        with open(os.path.join(root, "src", "RimMandrake", "Utils", "pipeline_tests.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return []
    return sorted(c["test"] for c in cfg.get("tests", ()) if cfg.get("nightly") is True)


def held(root=REPO):
    """True while no mod has finished: the condition timers_guard's finished-mod hold waits on."""
    return not finished_mods(root)


def nothing_line():
    return "RESULT: GREEN (green = FAIL 0 and CRASH 0): 0/0 run, %s (no mod has a passed Design Version; %s)" % (
        NOTHING, ITEM)


def _git(cwd, *args, timeout=600):
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)


def refresh_clone(clone, origin):
    """A clean copy of origin/main at CLONE, made or refreshed. -> None, or the reason it failed."""
    if not os.path.isdir(os.path.join(clone, ".git")):
        r = subprocess.run(["git", "clone", "-q", origin, clone], capture_output=True, text=True, timeout=1800,
                           stdin=subprocess.DEVNULL)
        if r.returncode:
            return "git clone: %s" % r.stderr.strip()
    for a in (("fetch", "-q", "origin", "main"), ("checkout", "-q", "-f", "-B", "main", "origin/main"),
              ("clean", "-q", "-fd")):
        r = _git(clone, *a)
        if r.returncode:
            return "git %s: %s" % (a[0], r.stderr.strip())
    return None


def run(root=REPO, clone=None, origin=None, runner=subprocess.run, out=sys.stdout):
    """The nightly sweep. -> exit code."""
    if not tests_for(root)["tests"]:
        print(nothing_line(), file=out, flush=True)
        return 0
    clone = clone or os.environ.get("RM_NIGHTLY_CLONE", DEFAULT_CLONE)
    if origin is None:
        origin = _git(root, "remote", "get-url", "origin").stdout.strip()
    why = refresh_clone(clone, origin)
    if why:
        print("RESULT: RED (green = FAIL 0 and CRASH 0): the clean clone %s could not be made: %s" % (clone, why),
              file=out, flush=True)
        return 1
    env = dict(os.environ)
    env["PATH"] = os.path.expanduser("~/.local/bin") + os.pathsep + env.get("PATH", "")
    r = runner([sys.executable, os.path.join(clone, "src", "RimMandrake", "Utils", "run_selftests.py"), "--nightly"],
               cwd=clone, env=env, stdin=subprocess.DEVNULL)
    return r.returncode


def hold(apply, runner=subprocess.run):
    argv = [sys.executable, os.path.join(HERE, "timers_guard.py"), "hold", "--until", UNTIL, "--per-ruling", ITEM,
            "--why", "the nightly checks finished mods only; none has passed (owner by card 2026-11-15)", *HELD_TIMERS]
    if not apply:
        print("plan only (--apply runs it): " + " ".join(argv))
        return 0
    return runner(argv).returncode


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("--json", action="store_true")
    sub.add_parser("run")
    h = sub.add_parser("hold")
    h.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd == "hold":
        return hold(a.apply)
    t = tests_for()
    if a.json:
        print(json.dumps(t, indent=1))
    elif not t["finished"]:
        print("nightly set: empty, %s" % NOTHING)
    else:
        for m in t["finished"]:
            print("%s: %d tests" % (m, len(t["by_mod"][m])))
        print("nightly set: %d tests from %d finished mods" % (len(t["tests"]), len(t["finished"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
