#!/usr/bin/env python3
"""selftest_live_line_host.py — a `--live` promise on a unit of another machine is checked on that machine.

Instance (2026-11-24, WORKER_CLONES_MONITOR_POOL_NOT_RABBITS): a helper on SteveDesktop closed an Archmagi item with
`unit=rm-scratch-reap.timer reading=... max_age=6h`; the close asked SteveDesktop's own systemd, which has no such
timer ("is-enabled says 'not-found'"), so no SteveDesktop run could ever prove an Archmagi promise. `host=archmagi`
names the machine; off that machine, check() asks it over ssh. Promises: design/specs/2026-11-24-live-line-host/boundary.md.
No network: a fake runner stands in for ssh and systemctl."""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_line  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


class Fake:
    """Records every argv; answers systemctl and stat as a healthy remote machine would."""

    def __init__(self, mtime, fail_ssh=False):
        self.calls, self.mtime, self.fail_ssh = [], mtime, fail_ssh

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        inner = argv[-1] if argv[0] == "ssh" else " ".join(argv)
        if argv[0] == "ssh" and self.fail_ssh:
            return subprocess.CompletedProcess(argv, 255, "", "ssh: connect to host: timed out")
        if "is-enabled" in inner:
            out = "enabled"
        elif "is-active" in inner:
            out = "active"
        elif inner.startswith("stat "):
            out = "%d" % self.mtime
        else:
            out = ""
        return subprocess.CompletedProcess(argv, 0, out + "\n", "")


LINE = ("unit=rm-scratch-reap.timer reading=/home/mandrake/.local/state/rm-scratch-reap/last_run.json max_age=6h "
        "host=archmagi")
NOW = time.time()


def away(mtime, fail_ssh=False):
    os.environ["RM_LIVE_HOSTNAME"] = "SteveDesktop"
    f = Fake(mtime, fail_ssh)
    return f, live_line.check(LINE, now=NOW, runner=f, phases={})


def t_host_line_parses():
    try:
        p = live_line.parse(LINE)
        check("host-line-parses", p.get("host") == "archmagi" and p["unit"] == "rm-scratch-reap.timer", repr(p))
    except ValueError as e:
        check("host-line-parses", False, str(e))


def t_an_unknown_host_is_refused_by_name():
    try:
        live_line.parse("unit=rm-x.timer max_age=1h host=nowhere")
        check("an-unknown-host-is-refused-by-name", False, "parsed")
    except ValueError as e:
        check("an-unknown-host-is-refused-by-name", "unknown host=nowhere" in str(e), str(e))


def t_remote_host_asks_over_ssh():
    f, why = away(NOW - 600)
    ssh = [c for c in f.calls if c[0] == "ssh"]
    check("remote-host-asks-over-ssh", why is None and bool(ssh) and len(ssh) == len(f.calls)
          and any("stat " in c[-1] for c in ssh), "why=%r calls=%r" % (why, f.calls))


def t_a_stale_remote_reading_is_broken():
    _, why = away(NOW - 30000)
    check("a-stale-remote-reading-is-broken", bool(why) and "old" in why, repr(why))


def t_an_unreachable_host_is_a_reason_never_a_pass():
    _, why = away(NOW - 600, fail_ssh=True)
    check("an-unreachable-host-is-a-reason-never-a-pass", bool(why) and "not a live line" not in why, repr(why))


def t_on_its_own_host_it_asks_here():
    os.environ["RM_LIVE_HOSTNAME"] = "Archmagi"
    f = Fake(NOW - 600)
    why = live_line.check("unit=rm-scratch-reap.timer max_age=6h host=archmagi", now=NOW, runner=f, phases={})
    check("on-its-own-host-it-asks-here", bool(f.calls) and not any(c[0] == "ssh" for c in f.calls)
          and "not a live line" not in str(why), "why=%r calls=%r" % (why, f.calls))


def main():
    saved = os.environ.get("RM_LIVE_HOSTNAME")
    try:
        t_host_line_parses()
        t_an_unknown_host_is_refused_by_name()
        t_remote_host_asks_over_ssh()
        t_a_stale_remote_reading_is_broken()
        t_an_unreachable_host_is_a_reason_never_a_pass()
        t_on_its_own_host_it_asks_here()
    finally:
        if saved is None:
            os.environ.pop("RM_LIVE_HOSTNAME", None)
        else:
            os.environ["RM_LIVE_HOSTNAME"] = saved
    print("FAIL" if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
