#!/usr/bin/env python3
"""selftest: done means running (LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING). live_line.py's check, the `live` verb's
projection, and `close`/`implemented` refusing a promise that does not hold, on a throwaway git repo and ledger.

    python3 src/RimMandrake/rimflow/selftest_live_gate.py
"""
import json
import os
import shutil
import subprocess as SP
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_live_gate_")
import live_line as L  # noqa: E402
import model  # noqa: E402

FAILS = []
NOW = 1_800_000_000.0


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def sysd(enabled="enabled", active="active", last="1800000000"):
    def run(argv, **kw):
        out = {"is-enabled": enabled, "is-active": active}.get(argv[2], "@" + last)
        return SP.CompletedProcess(argv, 0, out, "")
    return run


def lines():
    r = L.parse("unit=rm-a.timer reading=/x max_age=6h")
    check(r == {"kind": "unit", "unit": "rm-a.timer", "reading": "/x", "max_age_s": 21600}, "unit with a reading parses")
    check(L.parse("unit=rm-a.timer max_age=2d")["reading"] is None, "a timer is its own reading")
    check(L.parse("role=Operations max_age=2d")["max_age_s"] == 172800, "role parses")
    for bad in ("unit=rm-a.service max_age=1h", "unit=rm-a.timer", "once:", "hook=a b", "nonsense", ""):
        try:
            L.parse(bad)
            check(False, "must refuse %r" % bad)
        except ValueError:
            check(True, "refuses %r" % bad)
    check(L.needs_line(["a/b.py", "src/RimMandrake/Utils/systemd/rm-x.timer"]) == ["src/RimMandrake/Utils/systemd/rm-x.timer"],
          "a unit obliges a line, code does not")
    check(L.needs_line([".claude/hooks/block_x.py", "src/RimMandrake/rimflow/dispatcher_schedule.json",
                        "src/RimMandrake/Utils/ops_watch_rules.json"]).__len__() == 3, "hook, schedule and rules oblige")

    # unit checks
    u = "unit=rm-a.timer max_age=1h"
    check(L.check(u, now=NOW + 60, runner=sysd()) is None, "fresh timer holds (last firing in whole seconds)")
    check("old" in L.check(u, now=NOW + 7200, runner=sysd()), "a timer that stopped firing is broken")
    check("is-active" in L.check(u, now=NOW, runner=sysd(active="inactive")), "stopped is broken")
    check("is-enabled" in L.check(u, now=NOW, runner=sysd(enabled="disabled")), "disabled is broken")
    check("no last firing" in L.check(u, now=NOW, runner=sysd(last="0")), "never fired is broken")
    check("predates" in L.check(u, now=NOW + 60, not_before=NOW + 30, runner=sysd()), "a firing before the commit proves nothing")
    r = os.path.join(TMP, "reading")
    open(r, "w").close()
    os.utime(r, (NOW, NOW))
    v = "unit=rm-a.timer reading=%s max_age=1h" % r
    check(L.check(v, now=NOW + 60, runner=sysd(last="1")) is None, "the reading, not the timer, decides when one is named")
    check("old" in L.check(v, now=NOW + 7200, runner=sysd()), "a stale reading is broken")
    check("future" in L.check(v, now=NOW - 7200, runner=sysd()), "a reading dated ahead proves nothing")
    check("absent" in L.check("unit=rm-a.timer reading=/no/such max_age=1h", now=NOW, runner=sysd()), "an absent reading is broken")

    # hooks
    d = os.path.join(TMP, "proj", ".claude")
    os.makedirs(os.path.join(d, "hooks"))
    s = os.path.join(d, "settings.json")
    json.dump({"hooks": {"Pre": [{"command": "python3 .claude/hooks/block_foo.py"}]}}, open(s, "w"))
    check("absent" in L.check("hook=block_foo.py", settings=s), "wired but the file is gone is broken")
    open(os.path.join(d, "hooks", "block_foo.py"), "w").close()
    check(L.check("hook=block_foo.py", settings=s) is None, "wired hook holds")
    check("not wired" in L.check("hook=foo.py", settings=s), "a name inside another hook's name is not wired")
    json.dump({"hooks": {"Pre": [{"command": "python3 /no/where/else_foo.py"}]}}, open(s, "w"))
    check("absent" in L.check("hook=else_foo.py", settings=s), "a hook wired at any path must exist there")
    json.dump({"hooks": {"Pre": [{"command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/block_foo.py\""}]}}, open(s, "w"))
    check(L.check("hook=block_foo.py", settings=s) is None, "the project variable resolves")
    json.dump({"hooks": {"Pre": [{"command": "python3 $HOME/gone/block_bar.py"}]}}, open(s, "w"))
    check("absent" in L.check("hook=block_bar.py", settings=s), "a variable in the path does not skip the check")
    json.dump({"disableAllHooks": True, "hooks": {"Pre": [{"command": "python3 .claude/hooks/block_foo.py"}]}}, open(s, "w"))
    check("disables" in L.check("hook=block_foo.py", settings=s), "hooks switched off are not wired")
    check("unreadable" in L.check("hook=x.py", settings="/no/such"), "unreadable settings is broken")

    # roles
    st = os.path.join(TMP, "state.json")
    json.dump({"roles": {"R": {"done": {"2027-01-14 event#1": "launch", "2027-01-15 Tue,Fri 15:00": "daily cap"}}}}, open(st, "w"))
    t = time.mktime((2027, 1, 15, 12, 0, 0, 0, 0, -1))
    check(L.check("role=R max_age=1d", now=t, state_path=st) is None, "a launch keys by its date, whatever follows it")
    check("last launched" in L.check("role=R max_age=1d", now=t + 3 * 86400, state_path=st), "an idle role is broken")
    check("predates" in L.check("role=R max_age=9d", now=t, not_before=t, state_path=st), "an old launch proves no new commit")
    check("no recorded" in L.check("role=Q max_age=1d", now=t, state_path=st), "an unknown role is broken")
    check(L.can_see(lambda a, **k: SP.CompletedProcess(a, 0, "degraded", "")), "a degraded user manager still sees")
    check(not L.can_see(lambda a, **k: SP.CompletedProcess(a, 1, "", "")), "no bus is blind")
    def raises(a, **k):
        raise OSError("no systemctl")
    check(not L.can_see(raises), "no systemctl is blind")


def verb():
    def world(*evs):
        w = model.World()
        for i, e in enumerate(evs):
            e = dict({"ts": "2026-10-31T00:00:%02dZ" % i, "tsn": i + 1, "seat": "BENCH"}, **e)
            model._apply(e, i, w, True)
        return w
    filed = {"event": "file", "id": "A_FIX_B", "for": "BENCH", "title": "t", "kind": "task"}
    closed = {"event": "close", "id": "A_FIX_B", "sha": "abcdef1", "live": "hook=x.py"}
    broken = {"seat": "RUNNER", "event": "live", "id": "A_FIX_B", "result": "broken", "detail": "gone"}
    kept = {"seat": "RUNNER", "event": "live", "id": "A_FIX_B", "result": "kept"}
    w = world(filed, closed)
    it = w.items["A_FIX_B"]
    check(it.state == "done" and it.live == "hook=x.py", "close records the promise")
    w = world(filed, closed, broken)
    it = w.items["A_FIX_B"]
    check(it.state == "ready" and it.live_repeats == 1 and it.live_broken == "gone", "broken reopens the same item")
    w = world(filed, closed, broken, broken)
    check(w.items["A_FIX_B"].live_repeats == 1, "one outage counts once")
    w = world(filed, closed, broken, kept, broken)
    it = w.items["A_FIX_B"]
    check(it.state == "ready" and it.live_repeats == 2, "the second outage is counted on the same item")
    w = world(filed, closed, broken, kept)
    it = w.items["A_FIX_B"]
    check(it.state == "done" and it.live_broken is None and it.live_from is None, "kept puts it back")
    w = world(filed, closed, broken, {"event": "close", "id": "A_FIX_B", "sha": "abcdef2"})
    it = w.items["A_FIX_B"]
    check(it.state == "done" and it.live == "hook=x.py" and not it.live_broken, "a re-close ends the outage and keeps the promise")
    for bad, why in (({"event": "live", "id": "A_FIX_B", "result": "broken"}, "only RUNNER writes a reading"),
                     (dict(broken, result="maybe"), "a bad result is refused")):
        try:
            world(filed, closed, bad)
            check(False, why)
        except model.LedgerError:
            check(True, why)
    try:
        world(filed, {"event": "drop", "id": "A_FIX_B", "reason": "x"}, broken)
        check(False, "a dropped item stays dropped")
    except model.LedgerError:
        check(True, "a dropped item stays dropped")
    try:
        world(filed, closed, {"event": "claim", "id": "A_FIX_B"})
        check(False, "`live` is the ONLY way out of done")
    except model.LedgerError:
        check(True, "`live` is the ONLY way out of done")
    try:
        world(filed, dict(kept, id="A_FIX_B"))
        check(False, "kept with no outage must not close an item")
    except model.LedgerError:
        check(True, "kept with no outage must not close an item")
    w = world(filed, closed, broken, {"event": "start", "id": "A_FIX_B"}, kept)
    check(w.items["A_FIX_B"].state == "doing", "kept leaves a repair someone started in their hands")
    s = {"event": "spawn", "seat": "RUNNER", "from": "A_FIX_B", "for": "BENCH", "name": "LIVE_RESTORE_RM_A", "title": "t"}
    w = world(filed, s, dict(broken, id="LIVE_RESTORE_RM_A"), dict(kept, id="LIVE_RESTORE_RM_A"))
    check(w.items["LIVE_RESTORE_RM_A"].state == "done", "a spawned alarm closes itself on recovery")


def gate():
    repo = os.path.join(TMP, "repo")
    led = os.path.join(TMP, "ledger", "events.jsonl")
    os.makedirs(repo)
    os.makedirs(os.path.dirname(led))
    open(led, "w").close()
    tree = os.path.join(repo, "src", "RimMandrake")
    shutil.copytree(HERE, os.path.join(tree, "rimflow"), ignore=shutil.ignore_patterns("__pycache__", "selftest*", "queue"))
    os.makedirs(os.path.join(tree, "Utils"))
    shutil.copy(os.path.join(HERE, "..", "Utils", "rmpaths.py"), os.path.join(tree, "Utils"))
    env = {k: v for k, v in os.environ.items() if k not in ("AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=led, RIMFLOW_SEAT="BENCH", RIMFLOW_ITEMS=os.path.join(TMP, "items"), RIMFLOW_PROBE="no-reading",
               RIMFLOW_GITINDEX="off", HOME=os.path.join(TMP, "home"), RM_DATA_ROOT=os.path.join(TMP, "data"),
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    os.makedirs(env["HOME"] + "/.claude/hooks", exist_ok=True)
    open(env["HOME"] + "/.claude/hooks/wired_one.py", "w").close()
    hook = os.path.join(env["HOME"], ".claude", "settings.json")
    json.dump({"hooks": {"x": "wired_one.py"}}, open(hook, "w"))

    def g(*a):
        return SP.run(["git"] + list(a), cwd=repo, env=env, capture_output=True, text=True).stdout.strip()
    g("init", "-q", "-b", "main")

    def commit(path, name):
        full = os.path.join(repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "a").write("x\n")
        g("add", "-f", path)
        g("commit", "-q", "-m", name)
        g("update-ref", "refs/remotes/origin/main", "HEAD")
        return g("rev-parse", "HEAD")[:12]

    def rf(*a):
        return SP.run([sys.executable, os.path.join(tree, "rimflow", "cli.py")] + list(a), cwd=repo, env=env,
                      capture_output=True, text=True)
    commit("src/x.py", "seed")
    plain = commit("src/game.py", "plain")
    unit = commit("src/RimMandrake/Utils/systemd/rm-foo.timer", "unit")
    ledger_only = commit("infrastructure/state/ledger/events/BENCH.jsonl", "ledger")
    for i in ("CODE_FIX_ALPHA", "UNIT_FIX_ALPHA", "UNIT_FIX_BRAVO", "UNIT_FIX_CHARLIE", "OPS_FIX_ALPHA", "UNIT_FIX_DELTA"):
        r = rf("file", i, "--for", "BENCH", "--title", "t")
        check(r.returncode == 0, "file %s %s" % (i, r.stderr[-200:]))
    check(rf("close", "CODE_FIX_ALPHA", "--sha", plain).returncode == 0, "ordinary code closes with no new step")
    r = rf("close", "UNIT_FIX_ALPHA", "--sha", unit)
    check(r.returncode and "needs a live line" in r.stderr and "rm-foo.timer" in r.stderr, "a unit commit is refused without a line")
    r = rf("close", "UNIT_FIX_ALPHA", "--sha", unit, "--live", "unit=rm-no-such-unit.timer max_age=1h")
    check(r.returncode and "does not hold" in r.stderr, "a line that does not hold is refused")
    r = rf("close", "UNIT_FIX_ALPHA", "--sha", unit, "--live", "banana")
    check(r.returncode and "does not hold" in r.stderr, "a line that does not parse is refused")
    r = rf("close", "UNIT_FIX_BRAVO", "--sha", ledger_only, "--live", "hook=wired_one.py")
    check(r.returncode and "only the ledger" in r.stderr, "a ledger-only sha is refused")
    r = rf("close", "UNIT_FIX_ALPHA", "--sha", unit, "--live", "once: a real one-off")
    check(r.returncode == 0, "`once:` is the visible escape " + r.stderr[-200:])
    r = rf("close", "UNIT_FIX_BRAVO", "--sha", unit, "--live", "hook=wired_one.py")
    check(r.returncode == 0, "a hook line that holds closes " + r.stderr[-200:])
    r = rf("close", "OPS_FIX_ALPHA", "--sha", plain)
    check(r.returncode and "Operations alarm" in r.stderr, "an Operations alarm needs a line even on plain code")
    r = rf("implemented", "UNIT_FIX_CHARLIE", "--sha", unit, "--none-owed")
    check(r.returncode and "needs a live line" in r.stderr, "implemented is gated the same way")
    r = rf("implemented", "UNIT_FIX_CHARLIE", "--sha", unit, "--none-owed", "--live", "hook=wired_one.py")
    check(r.returncode == 0, "implemented records the line " + r.stderr[-200:])
    r = rf("live", "UNIT_FIX_DELTA", "--result", "broken")
    check(r.returncode != 0, "a window cannot write the sweep's verb")
    env["RIMFLOW_SEAT"] = "RUNNER"
    r = rf("live", "UNIT_FIX_BRAVO", "--result", "broken", "--detail", "hook gone")
    check(r.returncode == 0 and "ready" in r.stdout, "the sweep reopens the closed item " + r.stderr[-200:])
    env["RIMFLOW_SEAT"] = "BENCH"
    r = rf("show", "UNIT_FIX_BRAVO")
    check("BROKEN: hook gone" in r.stdout and "1 outage" in r.stdout, "show says so")
    json.dump({"hooks": {}}, open(hook, "w"))
    r = rf("close", "UNIT_FIX_BRAVO", "--sha", unit)
    check(r.returncode and "does not hold" in r.stderr, "a re-close rechecks the promise the item already holds")


def main():
    try:
        lines()
        verb()
        gate()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
