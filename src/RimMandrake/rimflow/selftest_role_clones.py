#!/usr/bin/env python3
"""selftest_role_clones.py — no Dispatcher role run and no daemon writes in the Conductor's seat clone
(RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES). Offline: fixtures and fake runners only, no git push.

The item's one-line acceptance test walked every "clone" key in dispatcher_schedule.json, the seats block included;
seats.BENCH IS the Conductor's window (the seat whose clone this is), so the check here walks roles[] only.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))

FAILS = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def main():
    import role_clones as RC
    import role_launch as RL
    import wrapup
    import seat_dirt

    seat = "/home/mandrake/rm/bench"
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    roles = [r for r in sch["roles"] if isinstance(r, dict) and r.get("clone")]
    check(len(roles) >= 8, "the schedule has its role rows (%d)" % len(roles))
    in_seat = [r["name"] for r in roles if os.path.normpath(r["clone"]) == seat]
    check(not in_seat, "no role row runs in the seat clone (%s)" % (in_seat or "none"))
    own = [r["name"] for r in roles if os.path.normpath(r["clone"]) != RC.clone_of(r["name"])]
    check(not own, "every role row's clone is its own %s/<Name> (%s)" % (RC.ROOT, own or "all"))
    check(len({r["clone"] for r in roles}) == len(roles), "no two role rows share a clone")

    unit = open(os.path.join(REPO, "src", "RimMandrake", "Utils", "systemd", "rm-artpiped.service")).read()
    check("/rm/bench" not in unit and "%h/rm/bench" not in unit, "rm-artpiped.service names no seat clone")
    check("WorkingDirectory=%s" % RC.clone_of("artpiped") in unit, "rm-artpiped runs in its own clone")
    check("ExecStartPre=" in unit and "./sync" in unit, "rm-artpiped levels its clone before it starts")
    check("ExecStopPost=" in unit and "role_clones.py land --clone %s" % RC.clone_of("artpiped") in unit,
          "rm-artpiped publishes what it left in its clone when it stops")

    # the unit: ./sync first (a stale clone never runs), then the role's own steps; landed at ExecStopPost
    rc = RC.clone_of("Operations")
    role = {"name": "Operations", "seat": "BENCH", "clone": rc, "model": "opus", "run_max_s": 1000,
            "pre_launch": ["python3", "x.py"]}
    a = RL.launch_argv(role, "u1", "msg", "/o", "/e", "/bin/claude")
    tail = a[a.index("--") + 1:]
    check(tail[:2] == ["/bin/sh", "-c"] and tail[2].startswith("./sync") and "exit %d" % RC.SYNC_FAILED_EXIT in tail[2],
          "a role clone's unit runs ./sync before anything else, and stops on a failed sync")
    check("x.py" in " ".join(tail[3:]), "the role's pre_launch still runs after the sync")
    posts = [a[i + 1] for i, w in enumerate(a) if w == "-p" and a[i + 1].startswith("ExecStopPost=")]
    check(len(posts) == 2 and "role_clones.py" in posts[0] and "land" in posts[0] and rc in posts[0]
          and "wrapup.py" in posts[1], "ExecStopPost lands the role clone, then the wrap-up runs")
    plain = RL.launch_argv(dict(role, clone="/c"), "u2", "msg", "/o", "/e", "/bin/claude")
    check("role_clones.py" not in " ".join(plain) and "./sync" not in " ".join(plain),
          "a clone that is not a role clone (Relentless, a fixture) gets neither step")

    # a missing role clone is refused before systemd-run, naming the command that makes it
    called = []
    ok, out, rec = RL.launch(dict(role, clone=RC.clone_of("SelftestNoSuchRole")), "u3", "m", "/tmp",
                             "/bin/claude", runner=lambda *a, **k: called.append(a))
    check(not ok and not called and "role_clones.py ensure" in out, "a missing role clone is refused, not launched")

    # wrap-up: a role clone lives on, like the seat clone
    row = wrapup.check_clone(None, rc, False)
    check(row["act"] == "carried", "wrapup carries a role clone (%s)" % row["act"])

    # land: the seat's shard is published only when dirty; the safe classes land at settle 0
    calls = []

    def runner(argv, **kw):
        calls.append(argv)
        out = " M infrastructure/state/ledger/events/BENCH.jsonl\n" if argv[:2] == ["git", "status"] else "PUBLISHED abc1234\n"
        return subprocess.CompletedProcess(argv, 0, out, "")
    res = RC.land(rc, "BENCH", runner=runner, tidy=lambda c, settle_min: "nothing to land", exists=lambda p: True)
    pub = [c for c in calls if c[:1] == ["./publish"]]
    check(len(pub) == 1 and pub[0][-1] == "infrastructure/state/ledger/events/BENCH.jsonl" and res["ok"],
          "a dirty shard is published from the role clone")
    calls.clear()
    res = RC.land(rc, "BENCH", runner=lambda argv, **kw: (calls.append(argv), subprocess.CompletedProcess(argv, 0, "", ""))[1],
                  tidy=lambda c, settle_min: "nothing to land", exists=lambda p: True)
    check(not [c for c in calls if c[:1] == ["./publish"]] and res["ok"] and res["shard"] == "clean",
          "a clean shard publishes nothing")
    res = RC.land(rc, "BENCH", runner=runner, tidy=lambda c, settle_min: "x", exists=lambda p: False)
    check(not res["ok"] and "missing" in res["why"], "landing a missing clone is a failure with its cause, not 'clean'")
    order = []
    RC.land(rc, "BENCH", runner=lambda argv, **kw: (order.append(argv[0]), runner(argv, **kw))[1],
            tidy=lambda c, settle_min: order.append("tidy:%s" % settle_min) or "nothing to land", exists=lambda p: True)
    check(order == ["git", "./publish", "tidy:0"],
          "the shard is published before the tidy (a just-filed item's prose is safe only once its event is on origin)")

    def boom(argv, **kw):
        raise subprocess.TimeoutExpired(argv, 60)
    res = RC.land(rc, "BENCH", runner=boom, tidy=lambda c, settle_min: "nothing to land", exists=lambda p: True)
    check(not res["ok"] and "TimeoutExpired" in (res["why"] or ""), "a git timeout is a named failure, never a raise")

    # seat_dirt's parser: a rename's source path is not an entry; a deletion or a conflict is never a safe class
    real = seat_dirt.git
    try:
        seat_dirt.git = lambda clone, *a, **k: "R  conversations/new.md\0conversations/old.md\0?? x.txt\0"
        got = seat_dirt.dirty("/nowhere")
        check(got == [("R ", "conversations/new.md"), ("??", "x.txt")], "a rename record is one entry (%s)" % got)
        seat_dirt.git = lambda clone, *a, **k: "D  conversations/a.md\0UU conversations/b.md\0?? conversations/c.md\0"
        c = seat_dirt.classify("/nowhere", now=10 ** 10, settle_min=0)
        check(c["landable"] == ["conversations/c.md"] and sorted(c["stale"]) == ["conversations/a.md", "conversations/b.md"],
              "a staged deletion and an unmerged conversation are dirt, not landable (%s)" % c)
    finally:
        seat_dirt.git = real

    # the dirt reading covers every role clone, not the seat clone alone
    root = tempfile.mkdtemp()
    for n in ("Operations", "artpiped", "notaclone"):
        os.makedirs(os.path.join(root, n, ".git") if n != "notaclone" else os.path.join(root, n))
    got = seat_dirt.clones(seat=seat, role_root=root)
    check(got == [seat, os.path.join(root, "Operations"), os.path.join(root, "artpiped")],
          "seat_dirt.clones lists the seat clone and each role clone (%s)" % got)

    print("%d check(s) failed" % len(FAILS) if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
