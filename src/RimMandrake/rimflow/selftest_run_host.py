#!/usr/bin/env python3
"""selftest_run_host.py: one test per promise of design/specs/2026-11-24-run-on-steve/boundary.md. Offline.

The second half (wsl_door .. host_account_gate) was written red first for
RIMMANDRAKE_FINISH_STEVE_HOST_LAUNCH_NEVER_RAN_ON_REAL_MACHINE: the measured live read of 2026-11-24 10:06 AM PST read
no fact at all (Windows door, no login PATH, a brief path on Archmagi, a clone nobody made, account names in code).
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_host as R

GOOD = {"reachable": True, "claude": "2", "account": "a", "picked_account": "a", "push": True, "launcher": True,
        "clone": "~/rm/relentless/clones/X.det", "free_gb": 9}


def P(facts=GOOD, **kw):
    kw.setdefault("budget", 5)
    return R.plan("stevedesktop", "X", "/b", facts, **kw)


def t_refused_by_name():
    assert R.plan("steve9", "X", "/b", GOOD, budget=5)["verdict"] == "REFUSED"
    assert P(dict(GOOD, account="b"))["verdict"] == "REFUSED"
    assert P(dict(GOOD, push=False))["verdict"] == "REFUSED"
    assert P(dict(GOOD, launcher=False))["verdict"] == "REFUSED"
    assert P(dict(GOOD, clone="~/rm/runner"))["verdict"] == "REFUSED"
    assert P(budget=None)["verdict"] == "REFUSED", "no spend cap is no launch, as on this machine"


def t_could_not_look_named():
    for k in GOOD:
        r = P(dict(GOOD, **{k: None}))
        assert r["verdict"] == "COULD NOT LOOK" and k in r["why"], (k, r)


def t_no_spend_stated():
    assert "max-budget-usd" not in " ".join(P()["argv"])


def t_wsl_door():
    """HOSTS goes through the WSL door; the bare alias lands in Windows PowerShell (measured 2026-11-24)."""
    door = R.HOSTS["stevedesktop"]
    assert door.endswith("stevedesktop-wsl"), door
    assert P()["argv"][:1] == ["ssh"] and door in P()["argv"]


class Fake:
    """A host: answers each ssh command by the first pattern that matches it; records every argv."""

    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def __call__(self, argv, **kw):
        self.calls.append(argv)
        cmd = argv[-1]
        for pat, out in self.answers:
            if re.search(pat, cmd):
                rc, text = out if isinstance(out, tuple) else (0, out)
                return subprocess.CompletedProcess(argv, rc, text, "")
        return subprocess.CompletedProcess(argv, 127, "", "not found")


HOST = [(r"echo up", "up"), (r"claude --version", "2.1.0 (Claude Code)"),
        (r"claude-account --json status", json.dumps({"ok": True, "live": "acct1"})),
        (r"github-rimmandrake-write", "Hi! You've successfully authenticated"), (r"test -f", "yes"),
        (r"df ", "120")]


def t_login_path():
    """Every fact command runs with ~/.local/bin on PATH (claude is there only in a login shell)."""
    f = Fake(HOST)
    R.read_facts("SteveDesktop", "X", None, runner=f)
    for argv in f.calls:
        assert ".local/bin" in argv[-1], argv
        assert R.HOSTS["stevedesktop"] in argv, argv


def t_every_fact_reads():
    facts = R.read_facts("SteveDesktop", "X", None, runner=Fake(HOST))
    unread = [k for k in R.FACTS if facts.get(k) is None]
    assert not unread, unread
    assert facts["account"] == "acct1" and facts["picked_account"] == "acct1", facts
    assert facts["clone"] == "~/rm/relentless/clones/X.det" and facts["launcher"] is True and facts["free_gb"] == 120
    assert R.plan("SteveDesktop", "X", "/b", facts, budget=5)["verdict"] == "REMOTE"


def t_account_from_the_machine():
    """The account is the machine's own JSON reading; the code names no account."""
    facts = R.read_facts("SteveDesktop", "X", "other", runner=Fake(HOST))
    assert facts["account"] == "acct1" and R.plan("SteveDesktop", "X", "/b", facts, budget=5)["verdict"] == "REFUSED"
    bad = Fake([(p, o) for p, o in HOST if "claude-account" not in p] + [(r"claude-account", "not json")])
    assert R.read_facts("SteveDesktop", "X", None, runner=bad)["account"] is None
    src = open(R.__file__, encoding="utf-8").read().lower()
    for name in ("lukas", "steven", "'system'"):
        assert name not in src, name


def t_launch_argv():
    """argv sends the brief over stdin and runs the host's own launcher, with the call's model and cap."""
    pl = P(model="opus", budget=12, seat="BENCH", next_act_owner="list_dispatch")
    assert pl["verdict"] == "REMOTE" and pl["stdin_path"] == "/b", pl
    cmd = pl["argv"][-1]
    for want in (".local/bin", "~/rm/list_briefs/X.md", "cd ~/rm/bench", "detached_helper.py launch", "--item X",
                 "--model opus", "--budget-usd 12", "--seat BENCH", "--next-act-owner list_dispatch", "--brief-file"):
        assert want in cmd, (want, cmd)
    assert "--model sonnet" not in cmd and "claude -p" not in cmd
    assert R.parse_unit("x\nDETACHED rm-detached-bench-x-1\n  item X") == "rm-detached-bench-x-1"
    assert R.parse_unit("REFUSED: no") is None


def t_record_names_host_unit_item():
    rec = R.record("SteveDesktop", "X", "rm-u", "opus", 12, 100.0)
    assert rec["host"] == "SteveDesktop" and rec["unit"] == "rm-u" and rec["item"] == "X" and rec["status"] == "running"


def t_live_until_the_host_says_ended():
    """Could not look is live, never ended; the end state is the host's own record."""
    rec = R.record("SteveDesktop", "X", "rm-u", "opus", 12, 100.0)
    down = Fake([])
    assert R.remote_status(rec, runner=down)[0] == "running"
    up = Fake([(r"rm-u", json.dumps({"active": "active", "record": {"status": "running"}}))])
    assert R.remote_status(rec, runner=up)[0] == "running"
    done = Fake([(r"rm-u", json.dumps({"active": "inactive", "record": {"status": "finished", "outcome": "success"}}))])
    st, host_rec = R.remote_status(rec, runner=done)
    assert st == "finished" and host_rec["outcome"] == "success", (st, host_rec)
    gone = Fake([(r"rm-u", json.dumps({"active": "inactive", "record": None}))])
    assert R.remote_status(rec, runner=gone)[0] == "dead"
    assert ".local/bin" in down.calls[0][-1] and R.HOSTS["stevedesktop"] in down.calls[0]


def t_stop_runs_the_hosts_pipe():
    rec = R.record("SteveDesktop", "X", "rm-u", "opus", 12, 100.0)
    argv = R.stop_argv(rec, "kill", "he said stop it")
    assert argv[0] == "ssh" and R.HOSTS["stevedesktop"] in argv
    cmd = argv[-1]
    assert "cd ~/rm/bench" in cmd and "./pipe stop rm-u" in cmd and "--kill" in cmd and "he said stop it" in cmd, cmd
    assert "--at-easy-spot" in R.stop_argv(rec, "at_easy_spot", "w")[-1]
    try:
        R.stop_argv({"host": "nowhere", "unit": "u"}, "kill", "w")
        assert False, "an unknown host is refused"
    except ValueError:
        pass


def t_pipe_stop_routes_a_remote_unit():
    """`./pipe stop <unit>` on a unit whose record names a host runs that host's stop, and nothing here."""
    import tempfile
    import control
    import detached_helper as DH
    d = tempfile.mkdtemp(prefix="rh_selftest_")
    rec = R.record("SteveDesktop", "X", "rm-detached-remote-1", "opus", 12, 100.0)
    os.makedirs(os.path.join(d, "detached"), exist_ok=True)
    DH.write_record(rec, root=d)
    ran = []

    def runner(argv, **kw):
        ran.append(argv)
        return subprocess.CompletedProcess(argv, 0, "unit:rm-detached-remote-1 stop --kill (named): dead", "")
    out = control.remote_stop("rm-detached-remote-1", "kill", "w", root=d, runner=runner)
    assert out and out[0] == 0 and ran and "./pipe stop rm-detached-remote-1" in ran[0][-1], (out, ran)
    assert control.remote_stop("rm-not-remote", "kill", "w", root=d, runner=runner) is None


def t_host_room_for_the_lane():
    """list_dispatch places on a host only under its max_live and while its account has more than min_left_pct."""
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import list_dispatch as LD
    cfg = {"hosts": {"SteveDesktop": {"max_live": 6, "min_left_pct": 5}}}
    assert LD.host_room(cfg, {"SteveDesktop": {"live": 5, "left": 40.0}}, 0)[0] == "SteveDesktop"
    assert LD.host_room(cfg, {"SteveDesktop": {"live": 5, "left": 40.0}}, 1)[0] is None, "a same-tick launch counts"
    assert LD.host_room(cfg, {"SteveDesktop": {"live": 6, "left": 40.0}}, 0)[0] is None
    assert LD.host_room(cfg, {"SteveDesktop": {"live": 0, "left": 5.0}}, 0)[0] is None
    assert LD.host_room(cfg, {"SteveDesktop": {"live": 0, "left": None}}, 0)[0] is None, "unread left is no room"
    assert LD.host_room(cfg, {"SteveDesktop": {"live": None, "left": 50}}, 0)[0] is None, "unread live is no room"
    assert LD.host_room({}, {"SteveDesktop": {"live": 0, "left": 50}}, 0)[0] is None, "no host configured"


def t_status_reads_a_remote_run_from_its_host():
    """`detached_helper.py status` on Archmagi reads a remote run's state from its host, never from local systemd
    (measured 2026-11-24 6:33 PM PST: a live SteveDesktop run read "DEAD ... finish never ran" on Archmagi)."""
    import detached_helper as DH
    rec = R.record("SteveDesktop", "X", "rm-detached-remote-2", "opus", 12, 100.0)

    def runner(argv, **kw):
        if argv[0] == "ssh":
            return subprocess.CompletedProcess(argv, 0, json.dumps({"active": "active", "record": {"status": "running"}}), "")
        return subprocess.CompletedProcess(argv, 0, "inactive\n", "")   # local systemd has no such unit
    keep = DH.all_records
    DH.all_records = lambda *a, **k: iter([dict(rec)])
    try:
        out = DH.status(runner=runner)
    finally:
        DH.all_records = keep
    line = out.splitlines()[0]
    assert "DEAD" not in line and "running" in line and "SteveDesktop" in line, line


def t_host_live_counts_every_claude_run_there():
    """The host's live count is its own count of live rm-detached units, every run there, not only the lane runs this
    machine recorded (measured 2026-11-24 7:32 PM PST: 9 Claude runs on SteveDesktop, max_live 6, load 25 on 18 cores);
    a count that cannot be read is no room."""
    import list_dispatch as LD
    units = "\n".join("rm-detached-bench-x%d.service loaded active running x" % i for i in range(9))
    units += "\nrm-detached-bench-x0-return.service loaded active running finish"
    assert R.live_units("SteveDesktop", runner=Fake([(r"list-units", units)])) == 9
    assert R.live_units("SteveDesktop", runner=Fake([])) is None, "unreachable is could not look"
    cfg = {"hosts": {"SteveDesktop": {"max_live": 6, "min_left_pct": 5}}}
    host = Fake([(r"list-units", units), (r"claude-account", json.dumps({"live": "a"}))])
    f = LD.host_facts(cfg, {"SteveDesktop": 2}, runner=host)["SteveDesktop"]
    assert f["live"] == 9, f
    assert LD.host_room(cfg, {"SteveDesktop": dict(f, left=50.0)}, 0)[0] is None
    f = LD.host_facts(cfg, {"SteveDesktop": 2}, runner=Fake([]))["SteveDesktop"]
    assert f["live"] is None, f


def main():
    tests = (t_refused_by_name, t_could_not_look_named, t_no_spend_stated, t_wsl_door, t_login_path, t_every_fact_reads,
             t_account_from_the_machine, t_launch_argv, t_record_names_host_unit_item, t_live_until_the_host_says_ended,
             t_stop_runs_the_hosts_pipe, t_pipe_stop_routes_a_remote_unit, t_host_room_for_the_lane,
             t_status_reads_a_remote_run_from_its_host, t_host_live_counts_every_claude_run_there)
    bad = 0
    for f in tests:
        try:
            f()
            print("ok  ", f.__name__)
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("FAIL", f.__name__, type(e).__name__, str(e)[:300])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
