#!/usr/bin/env python3
"""selftest_run_selftests.py — the suite harness's own classifier.

`run_one` sorts a non-zero child into UNMEASURED ("could not run here") or
FAIL ("something is wrong"). Getting that backwards in the FAIL direction only
makes noise; getting it backwards in the UNMEASURED direction hides a real
failure behind a green-looking summary, so the guard that separates them is
asserted here rather than trusted.

Fixtures are written to a temp dir and run through the real `run_one`.
"""
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_selftests as rs  # noqa: E402
from run_selftests import UNMEASURED_PHRASE, run_one  # noqa: E402

FAILS = []


def eq(got, want, what):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (what, got, want))


CASES = (
    ("passes.py", "print('ok')\n", "PASS",
     "a child that exits 0 is a PASS"),

    ("unmeasured.py",
     f"print('dotnet.exe not found — {UNMEASURED_PHRASE}')\nraise SystemExit(1)\n",
     "UNMEASURED",
     "a non-zero child carrying the phrase could not run and is NOT a failure"),

    # The guard. A child that skips one check for want of a toolchain and then
    # genuinely fails another must read FAIL — the phrase must never launder a
    # real failure in the same file.
    ("mixed.py",
     f"print('dotnet.exe not found — {UNMEASURED_PHRASE}')\n"
     "print('FAIL something that really is broken')\nraise SystemExit(1)\n",
     "FAIL",
     "the phrase does NOT mask a real FAIL in the same output"),

    ("plain_fail.py", "print('assertion blew up')\nraise SystemExit(1)\n", "FAIL",
     "a non-zero child with no phrase is a FAIL"),

    # Owner card 2026-10-08: exit 0 is not enough. A child that prints the phrase
    # and exits 0 skipped its own check (selftest_deployed_biome_refs.py did), so it
    # is UNMEASURED — never a PASS.
    ("phrase_but_green.py", f"print('live dir absent — {UNMEASURED_PHRASE}')\n", "UNMEASURED",
     "a child that exits 0 after printing the phrase is UNMEASURED, not PASS"),

    # A signal death is CRASH even if the phrase was printed first (it used to fall
    # through into UNMEASURED and read green).
    ("phrase_then_sigkill.py",
     f"import os, signal\nprint('{UNMEASURED_PHRASE}', flush=True)\nos.kill(os.getpid(), signal.SIGKILL)\n",
     "CRASH", "a signal death after the phrase is CRASH"),

    ("uncaught.py", "print('starting')\n{}['missing']\n", "CRASH",
     "an uncaught KeyError never reached a verdict: CRASH"),

    ("asserts.py", "assert 1 == 2, 'wrong'\n", "FAIL",
     "a failed assert is a verdict: FAIL"),

    ("sysexit_msg.py", "raise SystemExit('FAIL counted 3, wanted 4')\n", "FAIL",
     "SystemExit with a message is a verdict: FAIL"),
)

with tempfile.TemporaryDirectory() as tmp:
    for name, body, want, what in CASES:
        p = Path(tmp) / name
        p.write_text(body)
        _, status, _, _ = run_one(p)
        eq(status, want, what)

# classify() is pure: pin the branches the fixtures above cannot reach cheaply.
C = rs.classify
eq(C(0, "ok")[0], "PASS", "rc 0, plain output")
eq(C(0, "x", {"oom_kill": 1, "peak": 1, "cap": 2})[0], "CRASH", "a cap kill at rc 0 is CRASH")
eq(C(137, "")[0], "CRASH", "rc 137 is a signal CRASH")
eq(C(1, UNMEASURED_PHRASE + "\nFAILED 2")[0], "FAIL", "rc 1 + phrase + FAIL text stays FAIL")
eq(C(0, UNMEASURED_PHRASE + "\nFAIL x")[0], "UNMEASURED", "rc 0 + phrase is UNMEASURED whatever else printed")
eq(C(1, "Traceback (most recent call last):\n  File x\nAssertionError: no")[0], "FAIL", "AssertionError is FAIL")
eq(C(1, "Traceback (most recent call last):\n  File x\nmodule.SomeError: no")[0], "CRASH", "other exception is CRASH")

# report(): green iff FAIL+CRASH == 0, per-state N/N, UNMEASURED never green-washes a FAIL.
import contextlib, io
def _rep(states):
    rows = [(Path(f"/x/t{i}.py"), s, 0.1, "why") for i, s in enumerate(states)]
    buf = io.StringIO()
    rs._OUTER[0] = False   # do not overwrite the real last_run.json
    with contextlib.redirect_stdout(buf):
        rc = rs.report([r for r in rows if r[1] != "SKIPPED"], [r for r in rows if r[1] == "SKIPPED"],
                       len(rows), 0.0, "fixture")
    return rc, buf.getvalue()
rc, out = _rep(["PASS", "UNMEASURED", "SKIPPED"])
eq(rc, 0, "PASS+UNMEASURED+SKIPPED is green")
eq("UNMEASURED 1/3" in out and "SKIPPED 1/3" in out and "PASS 1/3" in out, True, "explicit N/N per state")
eq("UNMEASURED (1/3)" in out, True, "UNMEASURED is listed loudly")
eq(_rep(["PASS", "CRASH"])[0], 1, "a CRASH makes the run red")
eq(_rep(["PASS", "FAIL", "UNMEASURED"])[0], 1, "a FAIL makes the run red")

# --only naming a file that does not exist is an error, never a green 0/0.
import subprocess as _sp
r = _sp.run([sys.executable, rs.__file__, "--only", "/nonexistent/selftest_nope.py"],
            capture_output=True, text=True, env={**os.environ, "RM_SELFTEST_NO_HARNESS": "1", "RM_SELFTEST_NESTED": "1"})
eq((r.returncode, "no such file" in r.stdout), (1, True), "--only on a missing path is rc 1")

# The memory pen's report line: stripped from stderr, parsed, and only that line.
err, rep = rs._split_marker("real stderr\n" + rs._MARKER + '{"ok": true, "oom_kill": 2}\nmore\n')
eq(err, "real stderr\nmore\n", "wrapper marker is removed from the test's stderr")
eq(rep, {"ok": True, "oom_kill": 2}, "wrapper marker parses")

# Planted break, live where the pen exists: a test that blows a 128 MiB cap must come
# back KILLED (never PASS, never a plain FAIL), even though it would exit 0 if it lived.
pen_note = "memory pen: UNMEASURED here"
harness, why = rs.probe_harness()
if harness:
    rs._HARNESS = harness
    try:
        with tempfile.TemporaryDirectory() as tmp:
            bomb = Path(tmp) / "bomb.py"
            bomb.write_text("hog = [b'x' * (64 << 20) for _ in range(8)]\n")  # 512 MiB
            _, status, _, detail = run_one(bomb, cap=128 << 20, est=0)
            eq(status, "CRASH", "a test over its cap is CRASH")
            eq(detail.startswith("memory cap"), True, "CRASH detail names the memory cap")
            ok = Path(tmp) / "ok.py"
            ok.write_text("print(open('/proc/self/cgroup').read())\n")
            _, status, _, _ = run_one(ok, cap=256 << 20, est=0)
            eq(status, "PASS", "a small test passes inside the pen")
    finally:
        rs._HARNESS = None
    # Fail closed: outside the pen the wrapper refuses to run the test at all.
    if not rs._in_harness(rs._cgroup_of("self")):
        import subprocess
        r = subprocess.run([sys.executable, rs.__file__, "--_harness-child", "--",
                            sys.executable, "-c", "print('TEST RAN')"], capture_output=True, text=True)
        eq((r.returncode, "TEST RAN" in r.stdout), (rs._PLACEMENT_RC, False),
           "wrapper outside rm-harness.slice refuses and never runs the test")
    pen_note = "memory pen: cap kill reads CRASH, small test PASSes in the pen"
else:
    print(f"memory pen probe failed ({why}) — those checks are UNMEASURED here")

if FAILS:
    print("FAIL selftest_run_selftests.py")
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("ok  selftest_run_selftests.py — PASS/FAIL/UNMEASURED/CRASH classification, report N/N, "
      "and the guard that stops an unmeasured child masking a real failure; " + pen_note)
