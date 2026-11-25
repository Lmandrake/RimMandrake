#!/usr/bin/env python3
"""selftest_steve_worker_wsl_proof.py - a live-proof line written `python3 ...` reaches the bridge on SteveDesktop.

The fault (8 lane attempts, 2026-11-06 .. 2026-11-25, e.g. J20261125T163509Z-d18f1f: 13 of 13 MAP_AWARENESS rows
UNMEASURED): 145 live-proof lines say `python3 <script>`. On Archmagi that reaches the bridge; on SteveDesktop WSL2 is
NAT-mode, so a WSL python dies at connect with rimbridge_client's "cannot reach the bridge from WSL" and the row is
UNMEASURED while the game runs fine. What must hold:
  windows_python_line: every python3 that starts a command (line start, after && ; | or after VAR=x assignments) turns
    into python.exe; the inline VAR names go into WSLENV so the Windows process sees them; a python3 inside an
    argument or a word like python3.11 is left alone; a line with no python3 returns None;
  run_proof_line: a first run that is not the WSL no-route reading is kept as it is (one run); a no-route reading
    runs the line again once under python.exe and its verdict is the one kept; a line with no python3 is never rerun.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import worker as W  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else ": " + detail))
    if not ok:
        FAILS.append(name)


NOROUTE = ("A1 UNMEASURED: RimBridgeError: cannot reach the bridge from WSL, and no amount of retrying will fix it.\n"
           "  RimBridge binds Windows loopback; WSL2 is NAT-mode, so 127.0.0.1:5174 has no route from here.")

f = getattr(W, "windows_python_line", None)
check("windows_python_line exists", callable(f), "worker.py has no windows_python_line")
if callable(f):
    got = f("python3 src/x.py A1 < /dev/null")
    check("plain line", got == "python.exe src/x.py A1 < /dev/null", repr(got))
    got = f("python3 a.py && python3 b.py; python3 c.py | python3 d.py")
    check("every command start", got == "python.exe a.py && python.exe b.py; python.exe c.py | python.exe d.py", repr(got))
    got = f("MODCHECK_SKIP_DEPLOY=1 FOO=a python3 x.py")
    check("assignments kept, names in WSLENV",
          got == "export WSLENV=${WSLENV:+$WSLENV:}MODCHECK_SKIP_DEPLOY:FOO; MODCHECK_SKIP_DEPLOY=1 FOO=a python.exe x.py",
          repr(got))
    got = f("python3 x.py --note 'run python3 later' --py python3.11")
    check("argument words untouched", got == "python.exe x.py --note 'run python3 later' --py python3.11", repr(got))
    check("no python3 -> None", f("python.exe x.py") is None and f("mkdir -p a && rm -f b") is None)

r = getattr(W, "run_proof_line", None)
check("run_proof_line exists", callable(r), "worker.py has no run_proof_line")
if callable(r):
    def fake(results):
        calls = []

        def sh(cmd, log_name=None, timeout=None):
            calls.append(cmd)
            return results[len(calls) - 1]
        return sh, calls

    sh, calls = fake([(0, "A1 PASS")])
    out = r(sh, "python3 p.py A1", "proof_A1.log", 60)
    check("pass kept, one run", out == (0, "A1 PASS") and len(calls) == 1, repr((out, calls)))
    sh, calls = fake([(1, "A1 FAIL: wrong kind")])
    out = r(sh, "python3 p.py A1", "proof_A1.log", 60)
    check("fail kept, one run", out[0] == 1 and len(calls) == 1, repr((out, calls)))
    sh, calls = fake([(2, NOROUTE), (0, "A1 PASS")])
    out = r(sh, "python3 p.py A1 < /dev/null", "proof_A1.log", 60)
    check("no-route reruns under python.exe", len(calls) == 2 and calls[1] == "python.exe p.py A1 < /dev/null"
          and out[0] == 0, repr((out, calls)))
    check("the rerun's tail names the rerun", "python.exe" in (out[1] or ""), repr(out))
    sh, calls = fake([(2, NOROUTE), (2, "A1 UNMEASURED: still no route")])
    out = r(sh, "python3 p.py A1", "proof_A1.log", 60)
    check("rerun at most once", len(calls) == 2 and out[0] == 2, repr((out, calls)))
    sh, calls = fake([(2, NOROUTE)])
    out = r(sh, "python.exe p.py A1", "proof_A1.log", 60)
    check("no python3 -> never rerun", len(calls) == 1, repr(calls))

print("selftest_steve_worker_wsl_proof: %s" % ("FAIL %s" % FAILS if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
