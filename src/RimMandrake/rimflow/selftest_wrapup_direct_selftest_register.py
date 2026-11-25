#!/usr/bin/env python3
"""A selftest run by hand (`python3 selftest_x.py`, not through run_selftests.py) never writes the LIVE wrap-up register.

RIMMANDRAKE_FENCE_DIRECT_SELFTEST_DEBTS_OFF_LIVE_REGISTER: on 2026-11-25 two fixers ran
`python3 src/RimMandrake/Utils/modcheck/selftest_helpers.py` by hand. Its SettingsTransaction cases against a FakeWorld
left 35 unpaid "storyteller off" debts on the live register, owed to ArchBig, and the wrap-up alarm fired
(incident wrapup-20261125193511). run_selftests.py sets RM_UNDER_SELFTEST for its children; a direct run had nothing.

Checks: a script named selftest*.py gets the selftest register; a script with any other name still gets the live
register (negative control: the fence must not hide a real stager's debts); RM_WRAPUP_DIR still wins over both.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = ("import sys; sys.path.insert(0, %r); import wrapup; print(wrapup.state_dir())" % HERE)
fails = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if detail and not cond else ""))
    if not cond:
        fails.append(name)


def state_dir_of(script_name, extra_env=None):
    d = tempfile.mkdtemp(prefix="rm_wrapup_direct_")
    p = os.path.join(d, script_name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(PROBE + "\n")
    env = dict((k, v) for k, v in os.environ.items() if k not in ("RM_WRAPUP_DIR", "RM_UNDER_SELFTEST"))
    env.update(extra_env or {})
    r = subprocess.run([sys.executable, "-I", p], capture_output=True, text=True, env=env, timeout=120)  # hang guard
    return r.stdout.strip() or ("ERROR " + r.stderr.strip()[-300:])


def main():
    sys.path.insert(0, HERE)
    import wrapup
    live = wrapup.DEFAULT_DIR_WINDOWS if os.name == "nt" else wrapup.DEFAULT_DIR
    got = state_dir_of("selftest_probe_settings.py")
    check("a selftest run by hand writes debts away from the live register", got != live and not got.startswith("ERROR"),
          got)
    got = state_dir_of("stage_probe.py")
    check("a stager that is not a selftest still writes the live register", got == live, got)
    own = os.path.join(tempfile.gettempdir(), "rm_wrapup_direct_own")
    got = state_dir_of("selftest_probe_settings.py", {"RM_WRAPUP_DIR": own})
    check("RM_WRAPUP_DIR still wins for a selftest", got == own, got)
    print("%s: %d failed" % ("FAIL" if fails else "PASS", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
