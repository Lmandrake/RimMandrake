#!/usr/bin/env python3
"""prove_equivalence.py BASE_SHA - the old unit homes against the one folder, on the same inputs.

Old path 1: the 18 unit texts seven installers held in Python strings at BASE_SHA, rendered with the arguments each
installer passed (the deploy, the script path, the testq clone and GIT_ENV, steve_cpu_retest's HOME).
Old path 2: the files installed in ~/.config/systemd/user (the recorded inputs: what systemd runs today).
New home: src/RimMandrake/Utils/systemd/ in this checkout.
Prints one row per text (old-rendered vs installed vs folder) and the units verdict of ops_clocks over every installed
file; exit 0 only when every old text equals its folder file. Read-only.
"""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
import ops_clocks as OC  # noqa: E402

R = "src/RimMandrake/Utils/"


def consts(sha, path):
    src = subprocess.run(["git", "-C", str(ROOT), "show", "%s:%s" % (sha, path)], capture_output=True, text=True,
                         check=True).stdout
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except (ValueError, SyntaxError):
                pass
    return out


def old_texts(sha, dep):
    rows = []
    for f, unit in (("deadman_check.py", "rm-deadman"), ("timers_guard.py", "timer-guard"), ("ops_watch.py", "rm-ops-watch")):
        c = consts(sha, R + f)
        rows += [(f, unit + ".service", c["UNIT"].format(deploy=dep)), (f, unit + ".timer", c["TIMER"])]
    for f in ("account_usage.py", "switching_plan.py"):
        c = consts(sha, R + f)
        rows += [(f, c["UNIT"] + ".service", c["SERVICE"].format(script=dep + "/" + R + f)),
                 (f, c["UNIT"] + ".timer", c["TIMER"])]
    c = consts(sha, R + "testq/testq.py")
    rows += [("testq/testq.py", n, t.format(clone=dep, git_env=c["GIT_ENV"])) for n, t in c["UNITS"].items()]
    c = consts(sha, R + "steve_cpu_retest/steve_cpu_retest.py")
    home = "/mnt/d/ClaudeWork/rimmandrake/steve_diag/retest"   # its HOME default (STEVE_RETEST_HOME unset in the unit)
    rows += [("steve_cpu_retest.py", "steve-cpu-retest.service", c["UNIT"].format(path=home + "/steve_cpu_retest.py")),
             ("steve_cpu_retest.py", "steve-cpu-retest.timer", c["TIMER"])]
    return rows


def main(argv):
    sha = argv[1] if len(argv) > 1 else "HEAD"
    dep = OC.deploy()
    folder, inst = OC.folder_units(), OC.installed_units()
    bad = 0
    print("old embedded text (%s) vs installed vs folder" % sha[:10])
    for f, name, text in old_texts(sha, dep):
        i, fo = inst.get(name), folder.get(name)
        a = "same" if i == text else ("missing" if i is None else "DIFF")
        b = "same" if fo == text else ("missing" if fo is None else "DIFF")
        bad += b != "same"
        print("  %-22s %-28s installed:%-7s folder:%s" % (f, name, a, b))
    real = {n: t for n, t in (inst or {}).items() if t is not OC.MASK}
    masks = sorted(n for n, t in (inst or {}).items() if t is OC.MASK)
    probs = OC.judge_units(folder, inst)
    print("installed files in scope: %d (%d unit or drop-in texts, %d masks); folder files: %d"
          % (len(inst or {}), len(real), len(masks), len(folder)))
    print("units verdict over them: %d problem(s)" % len(probs))
    for p in probs:
        print("  " + p)
    print("%s: %d of %d old texts differ from their folder file" % ("OK" if not bad else "FAIL", bad,
                                                                   len(old_texts(sha, dep))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
