#!/usr/bin/env python3
"""A read-only rimflow verb answers with no seat named (NIGHTLY_COP_FIX_RED_HPZIOX_GMAU).

The nightly sweep runs from a timer: no RIMFLOW_SEAT, no AGENT_SEAT, no session role file. `rimflow incidents` only
reads told.jsonl, yet it refused there ("I cannot tell which seat I am"), so selftest_incident went red every night
while passing in any agent window. This runs each reading verb with every seat source stripped.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def seatless_env(tmp):
    env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID")}
    env["RM_OPS_WATCH_DIR"] = os.path.join(tmp, "ops")      # an empty told ledger: never the live one
    os.makedirs(env["RM_OPS_WATCH_DIR"], exist_ok=True)
    return env


def main():
    tmp = tempfile.mkdtemp(prefix="seatless_")
    env = seatless_env(tmp)
    for argv in (["incidents"], ["incidents", "--all"]):
        out = subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + argv, env=env, cwd=tmp,
                             capture_output=True, text=True, timeout=120)
        check("seatless: rimflow %s answers" % " ".join(argv),
              out.returncode == 0 and "cannot tell which seat" not in out.stderr, (out.returncode, out.stderr[-300:]))
    # the control: a verb that writes still refuses with no seat, so the strip above really removed the seat
    out = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "note", "NO_SUCH_ITEM_SEATLESS", "--text", "x"], env=env,
                         cwd=tmp, capture_output=True, text=True, timeout=120)
    check("control: a writing verb with no seat still refuses", "cannot tell which seat" in out.stderr,
          (out.returncode, out.stderr[-300:]))
    print("selftest_readonly_seatless: %s" % ("FAIL (%d fails)" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
