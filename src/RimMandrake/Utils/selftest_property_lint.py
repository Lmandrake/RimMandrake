#!/usr/bin/env python3
"""Wires lint_property_defs.py into the sweep: the lint is clean on the real mod, and every planted defect (--plant-check) is caught.

    python3 src/RimMandrake/Utils/selftest_property_lint.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    bad = 0
    r = subprocess.run([sys.executable, os.path.join(HERE, "lint_property_defs.py"), "--quiet"], capture_output=True, text=True)
    clean = r.returncode == 0
    print(("ok   " if clean else "FAIL ") + "lint is clean on the real mod" + ("" if clean else " | " + (r.stdout + r.stderr).strip()[-300:]))
    bad += not clean
    p = subprocess.run([sys.executable, os.path.join(HERE, "lint_property_defs.py"), "--plant-check"], capture_output=True, text=True)
    out = p.stdout + p.stderr
    for line in out.splitlines():
        if line.startswith(("CAUGHT", "MISSED", "PLANT TARGET")):
            print(("ok   " if line.startswith("CAUGHT") else "FAIL ") + line)
    ok = p.returncode == 0 and "MISSED" not in out and "PLANT TARGET NOT FOUND" not in out
    print(("ok   " if ok else "FAIL ") + "every planted defect is caught: " + (out.strip().splitlines()[-1] if out.strip() else "no output"))
    bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
