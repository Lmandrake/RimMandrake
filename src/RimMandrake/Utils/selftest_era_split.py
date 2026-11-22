#!/usr/bin/env python3
"""selftest for era_split.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES): a planted era module is
split by its measured reach; the new module holds the live nodes, the old one the dead nodes and imports the live back.
Needs a python with pyflakes in PYFLAKES_PYTHON; without one it reports UNMEASURED and exits 2.

    PYFLAKES_PYTHON=/path/to/venv/bin/python python3 src/RimMandrake/Utils/selftest_era_split.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []
ERA = '''"""old doc"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


# the live one
def live():
    return helper() + 1


def helper():
    return len(HERE)


def dead():
    return live() * 2


class C(object):
    def m(self):
        return 1

    def n(self):
        return 2


if __name__ == "__main__":
    dead()
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    if not os.environ.get("PYFLAKES_PYTHON"):
        print("UNMEASURED, not a pass or a fail: no PYFLAKES_PYTHON (a python with pyflakes); era_split.py cannot run")
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="selftest_era_split_"))
    rf = tmp / "src/RimMandrake/rimflow"
    rf.mkdir(parents=True)
    (rf / "relentless_x.py").write_text(ERA)
    (rf / "user.py").write_text("import relentless_x as X\nX.live()\nX.C().m()\n")
    subprocess.run(["git", "init", "-q", str(tmp)], check=True, timeout=60)
    subprocess.run(["git", "-C", str(tmp), "add", "."], check=True, timeout=60)
    reach = subprocess.run([sys.executable, str(HERE / "era_reach.py"), str(tmp), "live"], capture_output=True,
                           text=True, check=True, timeout=120).stdout
    (tmp / "reach.json").write_text(reach)
    r = subprocess.run([sys.executable, str(HERE / "era_split.py"), str(tmp / "reach.json"), str(rf / "relentless_x.py"),
                        str(rf / "newx.py"), "newx.py -- the live part"], capture_output=True, text=True, timeout=120)
    check(r.returncode == 0, "split runs (%s)" % r.stderr[-200:])
    new, old = (rf / "newx.py").read_text(), (rf / "relentless_x.py").read_text()
    check("def live(" in new and "def helper(" in new and "class C(" in new and "def dead(" not in new,
          "the new module holds the live nodes only")
    check("# the live one" in new, "a comment above a live node moves with it")
    check("def dead(" in old and "def live(" not in old and "from newx import" in old, "the old module keeps the dead "
          "and imports the live back")
    check("import os" in new, "a used import is kept")
    probe = subprocess.run([sys.executable, "-c", "import relentless_x as X, newx; print(X.dead(), X.live is newx.live)"],
                           cwd=str(rf), capture_output=True, text=True, timeout=60)
    check(probe.stdout.split() == [str(2 * (len(str(rf)) + 1)), "True"], "dead code still runs against the moved live "
          "code (%s %s)" % (probe.stdout.strip(), probe.stderr[-200:]))
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
