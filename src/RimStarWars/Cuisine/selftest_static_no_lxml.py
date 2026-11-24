#!/usr/bin/env python3
"""selftest_static_no_lxml.py - static_checks on a host with no lxml reads UNMEASURED, never a FAIL of the mod
(CUISINE_LXML_MEND_STEVE_HAS_NONE). Runs `validation.py` in a child whose `import lxml` fails."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = """
import sys
%s
sys.path[:0] = [%r, %r]
sys.argv = ["validation.py"]
import importlib.util
sp = importlib.util.spec_from_file_location("cuisine_validation", %r)
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
try:
    print("RESULT", m.static_checks())
except Exception as e:
    print("RAISED", type(e).__name__, str(e)[:120])
"""


def run(block):
    r = subprocess.run([sys.executable, "-c", CODE % ("sys.modules['lxml'] = None" if block else "", HERE,
                                                      os.path.join(HERE, "..", "..", "RimMandrake", "Utils"),
                                                      os.path.join(HERE, "validation.py"))],
                       capture_output=True, text=True, timeout=120)
    lines = [x for x in r.stdout.splitlines() if x.startswith(("RESULT", "RAISED"))]
    return lines[-1] if lines else "NO LINE: " + r.stderr[-300:]


def main():
    got = run(True)
    ok = got.startswith("RAISED ExpectationFailed UNMEASURED: lxml is not installed")
    print(("ok    " if ok else "FAIL  ") + "no lxml: UNMEASURED, with its cause: " + got)
    want = run(False)
    ok2 = want == "RESULT []" or "No module named 'lxml'" in want or "lxml is not installed" in want
    print(("ok    " if ok2 else "FAIL  ") + "with lxml the checks still run: " + want)
    return 0 if ok and ok2 else 1


if __name__ == "__main__":
    sys.exit(main())
