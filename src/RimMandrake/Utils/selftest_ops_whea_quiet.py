#!/usr/bin/env python3
"""selftest_ops_whea_quiet.py -- `ops_watch.py whea-quiet`, the outcome check of DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING.

Page: design/specs/2026-11-26-whea-quiet-check/boundary.md. Each case plants the collector's raw lines (EV|id|level|iso,
then END|n) in a file RM_OPS_WHEA_EVENTS names and runs the real CLI, so the exit code is the one list_effect reads:
0 quiet, 1 not quiet, 2 could not look. No Windows program runs."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_whea_quiet_"))
NOW = time.time()
FAILS = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def ev(i, level=3, age_h=1.0):
    # the 7-digit fraction Windows' ToString('o') prints (measured 2026-11-06)
    t = NOW - age_h * 3600
    return "EV|%d|%d|%s.8832041Z" % (i, level, time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)))


def lines(*evs):
    return list(evs) + ["END|%d" % len(evs)]


def run(name, body, want, says, *extra):
    d = TMP / name
    d.mkdir()
    f = d / "whea.txt"
    if body is not None:
        f.write_text("\r\n".join(body) + "\r\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "whea-quiet", *extra], capture_output=True, text=True,
                       timeout=120, env={**os.environ, "RM_OPS_WHEA_EVENTS": str(f)})  # hang guard; a real run is ~1 s
    out = r.stdout.strip()
    check("whea-quiet %s: exit %d, %r" % (name, want, says), r.returncode == want and out.startswith(says),
          (r.returncode, out, r.stderr[-300:]))


def t_whea_quiet_exits_0_only_on_a_quiet_window():
    run("old_and_cpu", lines(ev(17, age_h=72.5), ev(17, age_h=100), ev(19, age_h=1)), 0, "QUIET")
    run("windows_zero", ["END|0"], 0, "QUIET")
    run("hours_flag", lines(ev(17, age_h=30)), 0, "QUIET", "--hours", "24")


def t_whea_quiet_exits_1_on_any_drive_event():
    run("one_corrected_71h", lines(ev(17, age_h=71.5), ev(17, age_h=100)), 1, "NOT QUIET: 1")
    run("one_fatal", lines(ev(18, level=2, age_h=2)), 1, "NOT QUIET: 1")


def t_whea_quiet_exits_2_when_it_could_not_look():
    run("missing", None, 2, "UNMEASURED")
    run("no_end", [ev(17, age_h=100)], 2, "UNMEASURED")
    run("ahead", lines(ev(17, age_h=-10 / 60.0)), 2, "UNMEASURED")
    run("past_query", lines(), 2, "UNMEASURED", "--hours", "200")


def main():
    t_whea_quiet_exits_0_only_on_a_quiet_window()
    t_whea_quiet_exits_1_on_any_drive_event()
    t_whea_quiet_exits_2_when_it_could_not_look()
    print("selftest_ops_whea_quiet: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
