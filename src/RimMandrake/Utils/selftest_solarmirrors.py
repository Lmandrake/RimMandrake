#!/usr/bin/env python3
"""Offline selftest of the SolarMirrors mod (SOLAR_MIRRORS_BUILD_1): the def lint (lint_solarmirrors_defs.py) and the
mod's own static checks (SolarMirrors/validation.py static_checks). No build, no game; the kernel fuzz is
selftest_solarmirrors_fuzz.py. Exit 0 only when both are clean.

    python3 src/RimMandrake/Utils/selftest_solarmirrors.py
"""
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, "..", "SolarMirrors"))


def main():
    bad = 0
    r = subprocess.run([sys.executable, os.path.join(HERE, "lint_solarmirrors_defs.py"), "--quiet"], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print("lint: " + (out.splitlines()[-1] if out else "(no output)"))
    if r.returncode != 0 or " 0 ERROR" not in out:
        print(out)
        bad += 1
    spec = importlib.util.spec_from_file_location("solarmirrors_validation", os.path.join(MOD, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    problems = v.static_checks()
    print("static: %s" % ("PASS (0 findings)" if not problems else "FAIL"))
    for p in problems:
        print("  - " + p)
    if problems:
        bad += 1
    print("selftest_solarmirrors: %s" % ("OK" if not bad else "FAILED"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
