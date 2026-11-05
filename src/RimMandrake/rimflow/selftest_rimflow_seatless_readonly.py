#!/usr/bin/env python3
"""selftest_rimflow_seatless_readonly.py - a rimflow verb that never writes answers with NO seat.

NIGHTLY_COP_FIX_RED_MTJJIN_ODMC: the nightly sweep runs with no RIMFLOW_SEAT / AGENT_SEAT / session role, and
`namecheck` (a pure read) refused with "I cannot tell which seat I am", so selftest_first_touch's namecheck check went
red on the nightly and green in every seated window. The class: a read-only verb must not demand a seat. Each verb
below is run as a subprocess with every seat source stripped and must not print the seat refusal.
Offline, no ledger write."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.path.join(HERE, "cli.py")
SEAT_VARS = ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")
REFUSAL = "I cannot tell which seat I am"
FAILS = []


def check(name, ok, got=""):
    print("  %s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def run(args, env):
    return subprocess.run([sys.executable, CLI] + args, capture_output=True, text=True, timeout=120, env=env)


def main():
    seatless = {k: v for k, v in os.environ.items() if k not in SEAT_VARS}
    # probe: the instrument can see the refusal (a writing verb with no seat must still refuse)
    probe = run(["note", "NO_SUCH_ITEM_PROBE", "--text", "probe"], seatless)
    check("probe: a writing verb with no seat still refuses", REFUSAL in probe.stdout + probe.stderr,
          (probe.stdout + probe.stderr)[-300:])

    for argv in (["namecheck", "PYRELANDS_DESIGN_FIRST_TOUCH"], ["namecheck", "--bank"], ["show", "NO_SUCH_ITEM_X"]):
        r = run(argv, seatless)
        out = r.stdout + r.stderr
        check("seatless `%s` does not refuse for want of a seat" % " ".join(argv), REFUSAL not in out, out[-300:])
    r = run(["namecheck", "PYRELANDS_DESIGN_FIRST_TOUCH"], seatless)
    check("seatless namecheck accepts a generated id", r.returncode == 0 and "OK" in r.stdout, (r.stdout + r.stderr)[-300:])

    if FAILS:
        print("selftest_rimflow_seatless_readonly: FAIL (%d)" % len(FAILS))
        return 1
    print("selftest_rimflow_seatless_readonly: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
