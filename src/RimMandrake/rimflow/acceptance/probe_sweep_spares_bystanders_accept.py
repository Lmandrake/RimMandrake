#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_SPARE_OTHER_RUNS_PROBE_UNITS_SWEEP_KILLED_DRILL.

control_promise_breaks_accept.py stopped EVERY user unit with `rm-probe` in its name before each named test, so a
sibling run's drill on real systemd died with it (2026-11-19 06:54:24 PST: the real-agent drill's write-now agent, its
claude scope and its escalation timer, 5 s after the order). A test's cleanup may stop only the units that name its
own store. This starts two bystanders that name no test store: a `rm-probe-bystander-<pid>` service and a
`rm-control-escalate-rm-probe-bystander-<pid>` timer, runs the breaks acceptance on one promise, and checks both are
still there.

  exit 0  PASS: both bystanders survived the run
  exit 1  FAIL: a bystander was stopped (named)
  exit 3  COULD NOT LOOK: user systemd cannot be reached, a bystander never started, or the breaks run did not pass"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "rm-probe-bystander-%d" % os.getpid()
SVC, TMR = TAG + ".service", "rm-control-escalate-%s.timer" % TAG


def sc(*a):
    return subprocess.run(["systemctl", "--user"] + list(a), capture_output=True, text=True, timeout=30)


def active(u):
    return sc("is-active", u).stdout.strip()


def main():
    try:
        if sc("is-system-running").stdout.strip() not in ("running", "degraded"):
            print("COULD NOT LOOK probe_sweep_spares_bystanders: user systemd is not running")
            return 3
        subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", TAG, "/bin/sleep", "600"],
                       capture_output=True, timeout=30)
        subprocess.run(["systemd-run", "--user", "--quiet", "--collect", "--unit", TMR[:-len(".timer")],
                        "--on-active=600", "/bin/true"], capture_output=True, timeout=30)
        if active(SVC) != "active" or active(TMR) != "active":
            print("COULD NOT LOOK probe_sweep_spares_bystanders: a bystander never started (%s %s, %s %s)" % (
                SVC, active(SVC), TMR, active(TMR)))
            return 3
        r = subprocess.run([sys.executable, os.path.join(HERE, "control_promise_breaks_accept.py"), "--only",
                            "next-fits-a-screen"], capture_output=True, text=True, timeout=900,
                           cwd=os.path.dirname(HERE))
        last = (r.stdout or "").strip().splitlines()[-1:] or [(r.stderr or "").strip()[-200:]]
        if r.returncode != 0:
            print("COULD NOT LOOK probe_sweep_spares_bystanders: the breaks run exited %d: %s" % (r.returncode, last[0]))
            return 3
        gone = [u for u in (SVC, TMR) if active(u) != "active"]
        if gone:
            print("FAIL probe_sweep_spares_bystanders: the breaks run stopped another run's unit(s): %s" % ", ".join(gone))
            return 1
        print("PASS probe_sweep_spares_bystanders: %s and %s survived the breaks run" % (SVC, TMR))
        return 0
    finally:
        for u in (SVC, TMR):
            sc("stop", u)
            sc("reset-failed", u)


if __name__ == "__main__":
    sys.exit(main())
