#!/usr/bin/env python3
"""selftest: the close gate's live check asks the pipeline host when this machine is not it
(design/specs/2026-11-24-live-gate-on-pipeline-host/boundary.md; RESTART_JOIN_BUILD_EVERY_GOODBYE_ENDS). One test per
promise of that page, with a fake runner: no systemd, no ssh.

    python3 src/RimMandrake/rimflow/selftest_live_where_run.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_line as L  # noqa: E402

FAILS = []
LINE = "unit=rm-metronome.timer max_age=1h"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class R:
    def __init__(self, out="", rc=0):
        self.stdout, self.returncode, self.stderr = out, rc, ""


def runner(local_units, remote_out=None, remote_rc=0, raise_ssh=False):
    """A fake subprocess.run: systemctl answers from local_units {unit: 'enabled'|...}; ssh prints remote_out."""
    calls = []

    def run(argv, **kw):
        calls.append(list(argv))
        if argv[0] == "ssh":
            if raise_ssh:
                raise subprocess.TimeoutExpired(argv, 60)
            return R(remote_out or "", remote_rc)
        if argv[:2] == ["systemctl", "--user"]:
            verb, unit = argv[2], argv[-1]
            if verb == "is-enabled":
                return R(local_units.get(unit, "not-found"))
            if verb == "is-active":
                return R("active" if local_units.get(unit) == "enabled" else "inactive")
            if verb == "show":
                return R("@%d" % int(L.time.time() - 10) if local_units.get(unit) == "enabled" else "")
        return R("", 1)
    run.calls = calls
    return run


def ssh_calls(run):
    return [c for c in run.calls if c and c[0] == "ssh"]


def test_local_holds_first():
    run = runner({"rm-metronome.timer": "enabled"}, remote_out="WHY should not be asked")
    got = L.check_where_run(LINE, runner=run, env={})
    check(got is None and not ssh_calls(run), "local-holds-first: a local hold passes, no ssh (%r)" % (got,))


def test_pipeline_host_is_final():
    run = runner({"rm-deadman.timer": "enabled"}, remote_out="HOLDS")
    got = L.check_where_run(LINE, runner=run, env={})
    check(got and "not-found" in got and not ssh_calls(run),
          "pipeline-host-is-final: with the deadman local, the local failure stands (%r)" % (got,))


def test_off_host_asks_the_host():
    run = runner({}, remote_out="noise\nHOLDS\n")
    got = L.check_where_run(LINE, not_before=123.0, runner=run, env={})
    calls = ssh_calls(run)
    joined = " ".join(calls[0]) if calls else ""
    check(got is None and len(calls) == 1 and "mandrake@archmagi-wsl" in calls[0] and "python3 -B" in joined
          and "~/rm/dispatch" in joined and "123.0" in joined,
          "off-host-asks-the-host: the host's HOLDS passes, read-only, from the deadman clone (%r %s)" % (got, joined[:200]))
    run = runner({}, remote_out="WHY rm-metronome.timer: is-enabled says 'disabled', wanted 'enabled'\n")
    got = L.check_where_run(LINE, runner=run, env={})
    check(got and "disabled" in got and "mandrake@archmagi-wsl" in got and not L.not_yet(got),
          "off-host-asks-the-host: the host's failure is the answer, naming the host (%r)" % (got,))
    run = runner({}, remote_out="NOTYET reading x predates the commit it should prove; not yet\n")
    got = L.check_where_run(LINE, runner=run, env={})
    check(got and L.not_yet(got), "off-host-asks-the-host: a NotYet stays a NotYet (%r)" % (got,))


def test_blind_never_passes():
    for kw, what in (({"raise_ssh": True}, "timeout"), ({"remote_rc": 255}, "ssh exit 255"),
                     ({"remote_out": "Traceback ..."}, "no verdict")):
        run = runner({}, **kw)
        got = L.check_where_run(LINE, runner=run, env={})
        check(got is not None and "mandrake@archmagi-wsl" in got and "COULD NOT LOOK" in got,
              "blind-never-passes: %s reads COULD NOT LOOK, never a pass (%r)" % (what, got))


def test_stay_local_when_empty():
    run = runner({}, remote_out="HOLDS")
    got = L.check_where_run(LINE, runner=run, env={"RIMFLOW_LIVE_SSH": ""})
    check(got and "not-found" in got and not ssh_calls(run), "stay-local-when-empty: no ssh, local answer (%r)" % (got,))


def test_close_gates_use_it():
    src = open(os.path.join(HERE, "cli.py"), encoding="utf-8").read()
    check(src.count("live_line.check_where_run(") >= 2 and "why = live_line.check(line" not in src,
          "the two close gates in cli.py call check_where_run, not the local-only check")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("FAIL: %d failure(s)" % len(FAILS) if FAILS else "ALL OK")
    sys.exit(1 if FAILS else 0)
