#!/usr/bin/env python3
"""Selftest for remake/g16_fixture_census.py with a fake Saves dir and a fake tool runner (no real census runs)."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g16_fixture_census as G  # noqa: E402

CALLS = []


class P:
    def __init__(self, rc):
        self.returncode, self.stdout, self.stderr = rc, "out", ""


def runner(cmd, **kw):
    CALLS.append(cmd)
    save = next(c for c in cmd if c.endswith(".rws"))
    tool = os.path.basename(cmd[1])
    if "clean" in save:
        return P(0)
    if "blind" in save and tool == "save_def_census.py":
        return P(2)
    if "slow" in save:
        raise subprocess.TimeoutExpired(cmd, 1)
    return P(1 if tool == "save_class_census.py" else 0)


def run(saves, *argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = G.main(list(argv), saves_dir=saves, runner=runner)
    return rc, buf.getvalue()


def main():
    fails = []

    def check(c, m):
        if not c:
            fails.append(m)

    t = tempfile.mkdtemp(prefix="g16_")
    saves, out, ml = os.path.join(t, "Saves"), os.path.join(t, "out"), os.path.join(t, "ml.xml")
    os.makedirs(saves)
    for n in ("RM_TestSite_clean", "RM_TestSite_dirty", "RM_TestSite_blind", "RM_TestSite_slow", "Other_save"):
        open(os.path.join(saves, n + ".rws"), "w").write("<savegame/>")
    open(ml, "w").write("<ModsConfigData><activeMods/></ModsConfigData>")
    rc, outp = run(saves, "run", "--out", out, "--modlist", ml)
    res = G.load_results(out)
    check(set(res) == {"RM_TestSite_clean", "RM_TestSite_dirty", "RM_TestSite_blind", "RM_TestSite_slow"}, "fixture glob wrong: %s" % sorted(res))
    check(res["RM_TestSite_clean"]["verdict"] == "CLEAN", "clean not CLEAN")
    check(res["RM_TestSite_dirty"]["verdict"] == "CONTAMINATED", "dirty not CONTAMINATED")
    check(res["RM_TestSite_blind"]["verdict"] == "UNMEASURED", "blind tool not UNMEASURED")
    check(res["RM_TestSite_slow"]["rc"]["class"] == 124 and res["RM_TestSite_slow"]["verdict"] == "UNMEASURED", "timeout not 124/UNMEASURED")
    check(rc == 1 and "FATAL Class=" in outp, "table/exit wrong")
    n = len(CALLS)
    run(saves, "run", "--out", out, "--modlist", ml)
    check(len(CALLS) == n, "re-run repeated finished rows (not resumable)")
    rc, outp = run(saves, "quarantine", "--out", out)
    check(rc == 0 and "PLAN 1" in outp and os.path.exists(os.path.join(saves, "RM_TestSite_dirty.rws")), "dry-run quarantine moved")
    check(run(saves, "quarantine", "--out", out, "--apply")[0] == 3, "apply without --game-is-down not refused")
    run(saves, "quarantine", "--out", out, "--apply", "--game-is-down")
    check(not os.path.exists(os.path.join(saves, "RM_TestSite_dirty.rws")), "quarantine did not move")
    if fails:
        print("FAIL selftest_g16_fixture_census:", *fails, sep="\n  ")
        return 1
    print("PASS selftest_g16_fixture_census (10 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
