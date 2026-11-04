#!/usr/bin/env python3
"""Offline selftest of call_deadline_lint.py (CALL_DEADLINES_ENFORCE_130_OPEN_ENDED).

    python3 src/RimMandrake/Utils/selftest_call_deadline_lint.py

1. Synthetic tree in a temp dir: an unbounded run() is RED unless allowlisted; timeout= and a **kwargs splat
   are bounded; `import subprocess as sp` and `from subprocess import check_output as co` are followed; one
   call past the allowance is RED; a literal external call (powershell.exe, git push) is RED even when
   allowlisted; a passed burn-down date is RED; selftest files are skipped; an empty tree scans 0 calls.
2. robocopy: in .py an unbounded run, a missing timeout= and any Popen are RED, /R:2 /W:5 with timeout= is
   GREEN; in .ps1 the /R /W bounds decide; a .sh line also needs `timeout N`; comments never count.
3. The repo: the scan sees calls (sanity probe: total > 0 and a known bounded call is counted), the lint
   exits 0, and no allowlist entry is slack (every fixed call has been pruned).
"""
import contextlib
import datetime as dt
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import call_deadline_lint as L  # noqa: E402

FAILS = []
N = [0]


def check(cond, msg):
    N[0] += 1
    if not cond:
        FAILS.append(msg)


SRC = '''import subprocess
import subprocess as sp
from subprocess import check_output as co

def a():
    subprocess.run(["git", "status"])                       # open, local

def b():
    subprocess.run(["git", "status"], timeout=30)           # bounded
    sp.check_call(["ls"], **{"timeout": 5})                 # splat: bounded

def c():
    sp.call(["ls"])                                         # open via alias
    co(["ls"])                                              # open via from-import

def d():
    subprocess.run(["powershell.exe", "-Command", "x"])     # external
    subprocess.run(["git", "-C", ".", "push", "origin"])    # external: git network
'''

with tempfile.TemporaryDirectory() as td:
    root = os.path.join(td, "src", "pkg")
    os.makedirs(root)
    open(os.path.join(root, "m.py"), "w").write(SRC)
    open(os.path.join(root, "selftest_m.py"), "w").write(SRC)       # skipped
    total, opened, unparsed = L.scan_deadlines(td, ("src/pkg",))
    check(total == 7, "fixture: 7 blocking calls in m.py only, got %d" % total)
    keys = sorted((s, c, e) for _r, s, c, _l, e in opened)
    check(keys == [("a", "run", False), ("c", "call", False), ("c", "check_output", False),
                   ("d", "run", True), ("d", "run", True)], "fixture: open calls %s" % keys)
    check(not unparsed, "fixture: unparsed %s" % unparsed)

    today = dt.date(2026, 11, 3)
    reds = L.check_deadlines(opened, {"calls": {}}, today)
    check(len(reds) == 5, "no allowlist: 5 reds, got %d" % len(reds))
    allow = {"burn_down_by": "2027-01-31", "calls": {
        "src/pkg/m.py::a::run": 1, "src/pkg/m.py::c::call": 1, "src/pkg/m.py::c::check_output": 1,
        "src/pkg/m.py::d::run": 2}}
    reds = L.check_deadlines(opened, allow, today)
    check(len(reds) == 2 and all("never allowlisted" in r for r in reds), "external stays red: %s" % reds)
    local = [o for o in opened if not o[4]]
    check(L.check_deadlines(local, allow, today) == [], "allowlisted local calls are green")
    check(len(L.check_deadlines(local + [local[0]], allow, today)) == 1, "one call past the allowance is red")
    check(any("burn-down" in r for r in L.check_deadlines(local, allow, dt.date(2027, 2, 1))),
          "a passed burn-down date is red")
    allow["calls"]["src/pkg/m.py::gone::run"] = 1
    check(sorted(L.slack(local, allow)) == ["src/pkg/m.py::d::run", "src/pkg/m.py::gone::run"],
          "slack finds fixed calls (and an external entry, which can never count)")

    empty = os.path.join(td, "src", "empty")
    os.makedirs(empty)
    check(L.scan_deadlines(td, ("src/empty",))[0] == 0, "empty tree scans 0")

    # robocopy
    open(os.path.join(td, "r.py"), "w").write(
        'import subprocess\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/E"])\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/R:2", "/W:5"])\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/R:2", "/W:5"], timeout=900)\n'
        'subprocess.Popen(["robocopy.exe", "a", "b", "/R:2", "/W:5"])\n'
        '# subprocess.run(["robocopy", "x"]) in a comment\n'
        'x = "robocopy in a plain string is not a call"\n')
    open(os.path.join(td, "c.ps1"), "w").write(
        "# robocopy a b in a comment\nrobocopy a b /E\nrobocopy a b /E /R:2 /W:5\nrobocopy a b /R:9 /W:5\n")
    open(os.path.join(td, "s.sh"), "w").write(
        "robocopy.exe a b /R:2 /W:5\ntimeout 600 robocopy.exe a b /R:2 /W:5\n")
    reds = L.scan_robocopy(td, ["r.py", "c.ps1", "s.sh"])
    lines = sorted(r.split(" ")[0] for r in reds)
    check(lines == ["c.ps1:2", "c.ps1:4", "r.py:2", "r.py:3", "r.py:5", "s.sh:1"], "robocopy reds %s" % lines)
    check(any("Popen" in r for r in reds), "Popen robocopy names the fix")
    # the caps themselves (/R:<=5, /W:<=30), pinned at the boundary in every file kind
    open(os.path.join(td, "cap.py"), "w").write(
        'import subprocess\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/R:6", "/W:5"], timeout=60)\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/R:2", "/W:31"], timeout=60)\n'
        'subprocess.run(["robocopy.exe", "a", "b", "/R:5", "/W:30"], timeout=60)\n')
    open(os.path.join(td, "cap.ps1"), "w").write(
        "robocopy a b /R:6 /W:5\nrobocopy a b /R:2 /W:31\nrobocopy a b /R:5 /W:30\n")
    open(os.path.join(td, "cap.sh"), "w").write(
        "timeout 60 robocopy a b /R:6 /W:5\ntimeout 60 robocopy a b /R:2 /W:31\n"
        "timeout 60 robocopy a b /R:5 /W:30\n")
    creds = L.scan_robocopy(td, ["cap.py", "cap.ps1", "cap.sh"])
    clines = sorted(r.split(" ")[0] for r in creds)
    check(clines == ["cap.ps1:1", "cap.ps1:2", "cap.py:2", "cap.py:3", "cap.sh:1", "cap.sh:2"],
          "robocopy caps: /R:6 and /W:31 red, /R:5 /W:30 green: %s" % clines)

# 3. The repo itself.
total, opened, _u = L.scan_deadlines()
check(total > 100, "repo sanity: the scan sees %d calls (expected hundreds)" % total)
pub = os.path.join(L.REPO, "src/RimMandrake/Utils/publish.py")
check(any(c == "run" and L._bounded(n) for _s, c, n in L.calls_in(pub) or []),
      "repo sanity: publish.py's bounded git run is visible")
check(not any(o[4] for o in opened), "repo: no external call without timeout=")
allow = L.load_allowlist()
check(allow.get("burn_down_by"), "repo: allowlist has a burn-down date")
check(not L.slack(opened, allow), "repo: allowlist slack, run call_deadline_lint.py --prune: %s"
      % sorted(L.slack(opened, allow))[:5])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = L.main([])
check(rc == 0, "repo lint exit %d:\n%s" % (rc, buf.getvalue()[-1500:]))

for f in FAILS:
    print("FAIL " + f)
print("RESULT: %d/%d %s" % (N[0] - len(FAILS), N[0], "PASS" if not FAILS else "FAIL"))
sys.exit(1 if FAILS else 0)
