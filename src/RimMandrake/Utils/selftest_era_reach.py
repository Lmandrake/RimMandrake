#!/usr/bin/env python3
"""selftest for era_reach.py (item RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES): a planted git repo with
one era module and its importers; the walk must find exactly the functions and methods live code calls.

    python3 src/RimMandrake/Utils/selftest_era_reach.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


ERA = '''
import relentless_sub as S
CONST = 3
def live():
    return helper() + CONST
def helper():
    return S.used()
def dead():
    return S.unused()
def via_sup(sup):
    return 0
class C:
    def __init__(self):
        self.x = 1
    def m(self):
        return 1
    def n(self):
        return 2
def main():
    dead()
if __name__ == "__main__":
    main()
'''
SUB = '''
def used():
    return 1
def unused():
    return 2
def called_by_sup(sup):
    return sup.tick_only()
'''
LIVE = '''
import relentless as R
def f():
    return R.live() + R.C().m()
'''
TEST = '''
import relentless as R
R.dead()
'''


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_era_reach_"))
    rf = tmp / "src/RimMandrake/rimflow"
    rf.mkdir(parents=True)
    (rf / "relentless.py").write_text(ERA)
    (rf / "relentless_sub.py").write_text(SUB)
    (rf / "user.py").write_text(LIVE)
    (rf / "selftest_user.py").write_text(TEST)
    subprocess.run(["git", "init", "-q", str(tmp)], check=True, timeout=120)
    subprocess.run(["git", "-C", str(tmp), "add", "."], check=True, timeout=120)
    walk = str(HERE / "era_reach.py")
    live = json.loads(subprocess.run([sys.executable, walk, str(tmp), "live"], capture_output=True, text=True, timeout=120,
                                     check=True).stdout)
    m = live["modules"]["relentless"]
    check(set(m["live"]) == {"live", "helper", "C", "C.__init__", "C.m"}, "live: the called chain and C.m (%s)" % m["live"])
    check(set(m["dead"]) == {"dead", "via_sup", "C.n", "main"}, "dead: dead, via_sup, C.n, main (%s)" % m["dead"])
    check(m["live_consts"] == ["CONST"], "a constant a live function reads is live (%s)" % m["live_consts"])
    s = live["modules"]["relentless_sub"]
    check(s["live"] == ["used"] and set(s["dead"]) == {"unused", "called_by_sup"}, "sub: used live, the rest dead (%s)" % s)
    check(live["roots"].get("relentless.live") == ["src/RimMandrake/rimflow/user.py"], "the root names its call site")
    st = json.loads(subprocess.run([sys.executable, walk, str(tmp), "selftests"], capture_output=True, text=True, timeout=120,
                                   check=True).stdout)
    check("dead" in st["modules"]["relentless"]["live"], "selftests mode: a test's call makes it reached")
    ex = json.loads(subprocess.run([sys.executable, walk, str(tmp), "live", "--exclude-roots", "user.py"],
                                   capture_output=True, text=True, check=True, timeout=120).stdout)
    check(ex["modules"]["relentless"]["live"] == [], "an excluded root reaches nothing")
    om = json.loads(subprocess.run([sys.executable, walk, str(tmp), "live", "--only-methods", "relentless.C=__init__"],
                                   capture_output=True, text=True, timeout=120, check=True).stdout)["modules"]["relentless"]
    check("C.m" not in om["live"] and "C.__init__" in om["live"], "--only-methods: a method used by name but not named stays dead (%s)" % om["live"])
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
