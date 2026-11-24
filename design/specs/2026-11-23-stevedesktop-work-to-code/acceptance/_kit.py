"""Shared by the acceptance scripts beside this file: each check that cannot run FAILS; the verdict line is PASS n/n or FAIL k/n."""
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
TESTQ = os.path.join(REPO, "src", "RimMandrake", "Utils", "testq")
sys.path[:0] = [TESTQ, os.path.join(REPO, "src", "RimMandrake", "rimflow"), os.path.join(REPO, "src", "RimMandrake")]


def run(checks):
    ok = 0
    for name, fn in checks:
        try:
            got = fn()
        except Exception as e:  # noqa: BLE001 - a check that dies did not pass
            got = "%s: %s" % (type(e).__name__, e)
        ok += got is True
        print("%s %s%s" % ("ok  " if got is True else "FAIL", name, "" if got is True else "  -> %s" % (str(got)[:160])))
    print("%s %d/%d" % ("PASS" if ok == len(checks) else "FAIL", ok, len(checks)))
    return 0 if ok == len(checks) else 1
