#!/usr/bin/env python3
"""selftest: a fix that died closes only with a class guard test shown failing (REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN, design
idea 5). rimflow close, implemented, verify and the fold; `rimflow guard`'s red; alarm_census.recurring; ops_health's words.

    python3 src/RimMandrake/rimflow/selftest_repeat_guard.py
"""
import json
import os
import shutil
import subprocess as SP
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")
sys.path[:0] = [HERE, UTILS]
TMP = tempfile.mkdtemp(prefix="selftest_repeat_guard_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")      # nothing here reads or writes the real alarm log
import alarm_census as AC  # noqa: E402
import model  # noqa: E402
import ops_health as H  # noqa: E402
import repeat_guard as RG  # noqa: E402

FAILS = []
AFTER = "2027-01-01T00:00:%02dZ"
BEFORE = "2026-10-31T00:00:%02dZ"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def world(stamp, *evs):
    w = model.World()
    for i, e in enumerate(evs):
        e = dict({"ts": stamp % i, "tsn": i + 1, "seat": "BENCH"}, **e)
        model._apply(e, i, w, True)
    return w


FILED = {"event": "file", "id": "A_FIX_B", "for": "BENCH", "title": "t", "kind": "task"}
PASS1 = {"event": "verify", "id": "A_FIX_B", "sha": "abcdef1", "level": "L0", "result": "pass", "config": "c", "evidence": "e"}
PASS2 = dict(PASS1, sha="abcdef2")
CLOSED = {"event": "close", "id": "A_FIX_B", "sha": "abcdef1", "live": "hook=x.py"}
BROKEN = {"seat": "RUNNER", "event": "live", "id": "A_FIX_B", "result": "broken", "detail": "gone"}
KEPT = {"seat": "RUNNER", "event": "live", "id": "A_FIX_B", "result": "kept"}
GUARD = {"event": "guard", "id": "A_FIX_B", "test": "src/selftest_x.py", "testHash": "h", "redExit": 1}
RECLOSE = {"event": "close", "id": "A_FIX_B", "sha": "abcdef2"}
DIED = (FILED, PASS1, CLOSED, BROKEN)


def refused(stamp, *evs):
    try:
        return world(stamp, *evs).items["A_FIX_B"].state != "done"
    except model.LedgerError:
        return True


def fold():
    w = world(AFTER, *DIED)
    it = w.items["A_FIX_B"]
    check(model.guard_owed(it) and it.live_repeats == 1, "a fix that died owes a guard")
    check(not model.guard_owed(world(AFTER, FILED, PASS1, CLOSED).items["A_FIX_B"]), "a fix that never died owes none")
    check(any(k == "guard" for k, _ in model.close_refusals(it, "abcdef2")), "close_refusals names the guard")
    check(any(k == "guard" for k, _ in model.close_refusals(it, "abcdef2", no_code=True)), "--no-code owes it too")
    check(not any(k == "guard" for k, _ in model.close_refusals(it, "abcdef2", owner=True)), "his word on the close lifts it")
    check(refused(AFTER, *DIED, PASS2, RECLOSE), "the fold refuses a close with no guard, from a cli behind the gate")
    check(refused(AFTER, *DIED, dict(RECLOSE, sha="abcdef2", noCode="it cleared", event="close")), "the fold refuses a --no-code close")
    check(not refused(BEFORE, *DIED, PASS2, RECLOSE), "a close before GUARD_GATE_FROM replays as written")
    check(not refused(AFTER, *DIED, PASS2, dict(RECLOSE, ownerSaid="close it")), "his word in the event passes the fold")
    check(not refused(AFTER, *DIED, GUARD, PASS2, RECLOSE), "a guard on record closes")
    # a guard that did not stop the next outage is no guard for it
    second = (*DIED, GUARD, PASS2, RECLOSE, BROKEN)
    check(model.guard_owed(world(AFTER, *second).items["A_FIX_B"]), "an outage after the guard owes a new one")
    check(refused(AFTER, *second, dict(PASS2, sha="abcdef3"), dict(RECLOSE, sha="abcdef3")), "and the close refuses until then")
    check(not model.guard_owed(world(AFTER, *second, GUARD).items["A_FIX_B"]), "a newer guard answers it")
    # every other way to done stops at built
    impl = {"event": "implemented", "id": "A_FIX_B", "sha": "abcdef2", "criteria": []}
    w = world(AFTER, *DIED, PASS2, impl)
    check(w.items["A_FIX_B"].state == "built" and w.items["A_FIX_B"].held, "implemented owing nothing holds at built")
    w = world(AFTER, *DIED, GUARD, PASS2, impl)
    check(w.items["A_FIX_B"].state == "done", "implemented with a guard reaches done")
    crit = {"event": "implemented", "id": "A_FIX_B", "sha": "abcdef2", "criteria": [{"id": "A1", "level": "L1", "text": "x"}]}
    cpass = {"seat": "RUNNER", "event": "verify", "id": "A_FIX_B", "sha": "abcdef2", "criterion": "A1", "level": "L1", "result": "pass",
             "config": "c", "evidence": "e"}
    w = world(AFTER, *DIED, crit, cpass)
    check(w.items["A_FIX_B"].state != "done", "the last criterion's pass does not reach done without the guard")
    w = world(AFTER, *DIED, GUARD, crit, cpass)
    check(w.items["A_FIX_B"].state == "done", "and does with it")
    # `kept` is the sweep's reading, not a close; the census is what sees it
    w = world(AFTER, *DIED, KEPT)
    check(w.items["A_FIX_B"].state == "done" and model.guard_owed(w.items["A_FIX_B"]), "kept returns it to done, still owing")


def red():
    d = os.path.join(TMP, "red")
    os.makedirs(os.path.join(d, "src"))
    for name, body in (("selftest_fails.py", "import sys\nprint('FAIL  instance')\nsys.exit(1)\n"),
                       ("selftest_passes.py", "print('ok')\n"),
                       ("selftest_asserts.py", "assert 1 == 2, 'instance'\n"),
                       ("selftest_crashes.py", "import no_such_module_here\n"),
                       ("selftest_slow.py", "import time\ntime.sleep(5)\n"),
                       ("plain_test.py", "print('ok')\n")):
        open(os.path.join(d, "src", name), "w").write(body)
    t = lambda n, **k: RG.run(d, "src/" + n, **k)   # noqa: E731
    check(RG.red_problem(*t("selftest_fails.py")) is None, "a failing test is a red")
    check(RG.red_problem(*t("selftest_asserts.py")) is None, "an AssertionError is a red")
    check("passed" in RG.red_problem(*t("selftest_passes.py")), "a pass is no red")
    check("crashed" in RG.red_problem(*t("selftest_crashes.py")), "an import crash is no red")
    check("died" in RG.red_problem(*t("selftest_slow.py", timeout=1)), "a timeout is no red")
    check(RG.test_problem(d, "src/selftest_fails.py") is None, "a selftest under a root may guard")
    check("selftest" in RG.test_problem(d, "src/plain_test.py"), "a test the nightly sweep does not find may not")
    check("no such file" in RG.test_problem(d, "src/selftest_gone.py"), "nor one that is not there")
    check("relative" in RG.test_problem(d, os.path.join(d, "src", "selftest_fails.py")), "nor an absolute path")


def gate():
    repo = os.path.join(TMP, "repo")
    led = os.path.join(TMP, "ledger", "events.jsonl")
    os.makedirs(repo)
    os.makedirs(os.path.dirname(led))
    open(led, "w").close()
    tree = os.path.join(repo, "src", "RimMandrake")
    shutil.copytree(HERE, os.path.join(tree, "rimflow"), ignore=shutil.ignore_patterns("__pycache__", "selftest*", "queue"))
    os.makedirs(os.path.join(tree, "Utils"))
    for f in ("rmpaths.py", "bridge_holder.py"):
        shutil.copy(os.path.join(UTILS, f), os.path.join(tree, "Utils"))
    env = {k: v for k, v in os.environ.items() if k not in ("AGENT_SEAT", "CLAUDE_SESSION_ID", "RIMFLOW_GITINDEX")}
    env.update(RIMFLOW_LEDGER=led, RIMFLOW_SEAT="BENCH", RIMFLOW_ITEMS=os.path.join(TMP, "items"), RIMFLOW_PROBE="no-reading",
               RIMFLOW_GITINDEX="off", HOME=os.path.join(TMP, "home"), RM_DATA_ROOT=os.path.join(TMP, "data"),
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    os.makedirs(env["HOME"] + "/.claude/hooks", exist_ok=True)
    open(env["HOME"] + "/.claude/hooks/wired_one.py", "w").close()
    json.dump({"hooks": {"x": "wired_one.py"}}, open(os.path.join(env["HOME"], ".claude", "settings.json"), "w"))

    def g(*a):
        return SP.run(["git"] + list(a), cwd=repo, env=env, capture_output=True, text=True).stdout.strip()
    g("init", "-q", "-b", "main")

    def commit(path, name, body="x\n"):
        full = os.path.join(repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").write(body)
        g("add", "-f", path)
        g("commit", "-q", "-m", name)
        g("update-ref", "refs/remotes/origin/main", "HEAD")
        return g("rev-parse", "HEAD")[:12]

    def rf(*a):
        return SP.run([sys.executable, os.path.join(tree, "rimflow", "cli.py")] + list(a), cwd=repo, env=env,
                      capture_output=True, text=True)

    def run_as(seat, *a):
        env["RIMFLOW_SEAT"] = seat
        try:
            return rf(*a)
        finally:
            env["RIMFLOW_SEAT"] = "BENCH"

    def verified(iid, sha):
        r = rf("verify", iid, "--sha", sha, "--level", "L0", "--result", "pass", "--config", "c", "--evidence", "e")
        check(r.returncode == 0, "the check `close` asks for %s" % r.stderr[-200:])

    commit("src/x.py", "seed")
    # the instance: the bug's flag file is there, so the guard fails; the fix removes it
    flag = os.path.join(repo, "BUG_PRESENT")
    guard_src = "import os,sys\nsys.exit(1 if os.path.exists('BUG_PRESENT') or 'replay' in sys.argv else 0)\n"
    test = "src/selftest_guard_x.py"
    first = commit("src/first.py", "first fix")
    for i in ("ITEM_FIX_ALPHA", "ITEM_FIX_BRAVO", "ITEM_FIX_CHARLIE"):
        check(rf("file", i, "--for", "BENCH", "--title", "t").returncode == 0, "file " + i)
        verified(i, first)
        r = rf("close", i, "--sha", first, "--live", "hook=wired_one.py")
        check(r.returncode == 0, "a first close asks nothing new " + r.stderr[-200:])
        r = run_as("RUNNER", "live", i, "--result", "broken", "--detail", "gone")
        check(r.returncode == 0 and "outage 1" in r.stdout, "the sweep reopens " + i + r.stderr[-200:])
    show = rf("show", "ITEM_FIX_ALPHA").stdout
    check("OWES A GUARD" in show, "rimflow show says what is owed")

    # the instance, shown failing: no guard, no close, whatever the sha or --no-code
    second = commit("src/second.py", "second fix")
    verified("ITEM_FIX_ALPHA", second)
    r = rf("close", "ITEM_FIX_ALPHA", "--sha", second, "--why", "looks fine")
    check(r.returncode and "has not earned its close" in r.stderr and "rimflow guard ITEM_FIX_ALPHA" in r.stderr,
          "close refuses a fix that died, with no guard path, and says the way (relentless reads those words) " + r.stderr[:200])
    r = rf("close", "ITEM_FIX_ALPHA", "--no-code", "it cleared by itself")
    check(r.returncode and "rimflow guard" in r.stderr, "--no-code is no way round it")
    check("ready" in rf("show", "ITEM_FIX_ALPHA").stdout.split("\n")[0], "the item stays open")

    # `rimflow guard` records only a red
    open(os.path.join(repo, "src", "selftest_nope.py"), "w").write("print('ok')\n")
    r = rf("guard", "ITEM_FIX_ALPHA", "--test", "src/selftest_nope.py")
    check(r.returncode and "passed" in r.stderr and "Nothing recorded" in r.stderr, "a guard that passes is not recorded")
    open(os.path.join(repo, "src", "selftest_boom.py"), "w").write("import no_such_module_here\n")
    r = rf("guard", "ITEM_FIX_ALPHA", "--test", "src/selftest_boom.py")
    check(r.returncode and "crashed" in r.stderr, "a guard that crashes is not recorded")
    r = rf("guard", "NO_SUCH_ITEM_HERE", "--test", test)
    check(r.returncode != 0, "no guard for an item that does not exist")
    full = os.path.join(repo, test)
    open(full, "w").write(guard_src)
    open(flag, "w").close()
    r = rf("guard", "ITEM_FIX_ALPHA", "--test", test)
    check(r.returncode == 0 and "shown failing" in r.stdout, "the guard is shown failing on the instance " + r.stderr[-300:])
    check("guard: %s" % test in rf("show", "ITEM_FIX_ALPHA").stdout, "rimflow show names the guard")
    check("OWES A GUARD" not in rf("show", "ITEM_FIX_ALPHA").stdout, "and no longer says it is owed")

    # the close: the same test, committed at that sha, passing
    r = rf("close", "ITEM_FIX_ALPHA", "--sha", second, "--why", "x")
    check(r.returncode and "not the test shown failing" in r.stderr, "the guard must be committed at the close's sha")
    fixed = commit(test, "guard", guard_src)
    verified("ITEM_FIX_ALPHA", fixed)
    r = rf("close", "ITEM_FIX_ALPHA", "--sha", fixed, "--why", "x")
    check(r.returncode and "still fails" in r.stderr, "the guard must pass at the close: the fix is not in yet")
    os.remove(flag)
    r = rf("close", "ITEM_FIX_ALPHA", "--sha", fixed, "--why", "x")
    check(r.returncode == 0, "red then green closes " + r.stderr[-300:])

    # an edited test is not the test that was shown failing
    verified("ITEM_FIX_BRAVO", fixed)
    open(flag, "w").close()
    check(rf("guard", "ITEM_FIX_BRAVO", "--test", test).returncode == 0, "the second item shows it failing")
    os.remove(flag)
    edited = commit(test, "guard made vacuous", "print('ok')\n")
    verified("ITEM_FIX_BRAVO", edited)
    r = rf("close", "ITEM_FIX_BRAVO", "--sha", edited, "--why", "x")
    check(r.returncode and "not the test shown failing" in r.stderr, "a guard edited after its red does not close")

    # --instance replays it when the fix is already in; his word lifts the rule
    restored = commit(test, "guard back", guard_src)
    r = rf("guard", "ITEM_FIX_BRAVO", "--test", test, "--instance", "replay")
    check(r.returncode == 0, "--instance replays the instance on a fixed tree " + r.stderr[-200:])
    verified("ITEM_FIX_BRAVO", restored)
    r = rf("close", "ITEM_FIX_BRAVO", "--sha", restored, "--why", "x")
    check(r.returncode == 0, "and the close reruns it plain, green " + r.stderr[-200:])
    verified("ITEM_FIX_CHARLIE", restored)
    r = rf("close", "ITEM_FIX_CHARLIE", "--sha", restored, "--owner-said", "close it")
    check(r.returncode == 0, "his word on the close lifts it " + r.stderr[-200:])


def census():
    it = lambda **k: types.SimpleNamespace(**dict({"state": "done", "live_repeats": 0, "guard": None}, **k))   # noqa: E731
    guard = {"test": "t", "outages": 1}
    rows = [{"aid": "A:a", "event": "crossed"}, {"aid": "A:a", "event": "filed", "item": "OPS_A"}, {"aid": "A:a", "event": "cleared", "item": "OPS_A"},
            {"aid": "A:a", "event": "crossed"}, {"aid": "A:a", "event": "filed", "item": "OPS_A2"},
            {"aid": "ONCE:x", "event": "crossed"}, {"aid": "ONCE:x", "event": "filed", "item": "OPS_ONCE"},
            {"aid": "G:g", "event": "crossed"}, {"aid": "G:g", "event": "filed", "item": "OPS_G"}, {"aid": "G:g", "event": "crossed"},
            {"aid": "RUNWAY_LOW:x", "event": "crossed"}, {"aid": "RUNWAY_LOW:x", "event": "crossed"}]
    items = {"OPS_A": it(), "OPS_A2": it(), "OPS_ONCE": it(), "OPS_G": it(guard=guard), "LIVE_RESTORE_X": it(live_repeats=2),
             "FIX_GUARDED": it(live_repeats=1, guard=guard), "FIX_STALE": it(live_repeats=3, guard=guard),
             "FIX_DROPPED": it(live_repeats=2, state="dropped"), "CLEAN": it()}
    got = AC.recurring(rows, items, ["RUNWAY_LOW:*"])
    kinds = [r["kind"] for r in got]
    check("A:a" in kinds and next(r for r in got if r["kind"] == "A:a") == {"kind": "A:a", "seen": 2, "items": ["OPS_A", "OPS_A2"]},
          "a kind crossed twice with no guard on any of its items is flagged")
    check("ONCE:x" not in kinds, "a kind seen once is not recurring")
    check("G:g" not in kinds, "a guard on an item filed for the kind clears it")
    check("RUNWAY_LOW:x" not in kinds, "an exempt kind is not flagged")
    check("live:LIVE_RESTORE_X" in kinds and "live:FIX_STALE" in kinds, "a fix that died with no guard, or a stale one, is flagged")
    check("live:FIX_GUARDED" not in kinds and "live:FIX_DROPPED" not in kinds and "live:CLEAN" not in kinds, "a guarded, dropped or clean item is not")
    check(kinds[0] == "live:FIX_STALE", "most seen first")
    # read_log: a torn line is skipped, no file is no reading
    p = os.path.join(TMP, "log.jsonl")
    open(p, "w").write('{"aid": "A:a", "event": "crossed"}\n{"aid": "torn\n')
    check(AC.read_log(p) == [{"aid": "A:a", "event": "crossed"}], "a torn log line is skipped")
    try:
        AC.read_log(os.path.join(TMP, "no_such_log"))
        check(False, "a missing log is no reading")
    except OSError:
        check(True, "a missing log is no reading")
    # the published verdict
    os.makedirs(os.environ["RM_OPS_WATCH_DIR"], exist_ok=True)
    w = types.SimpleNamespace(items={})
    c = H.conf({"health": {"guard_exempt_kinds": []}})
    check(H.unguarded(w, c) is None, "no alarm log reads None in the verdict, never an empty list")
    with open(os.path.join(os.environ["RM_OPS_WATCH_DIR"], "alarms_log.jsonl"), "w") as f:
        f.write("\n".join(json.dumps(r) for r in rows) + "\n")
    check([r["kind"] for r in H.unguarded(types.SimpleNamespace(items=items), c)][:1] == ["live:FIX_STALE"], "ops_health reads the census")
    check(H.owes_guard(types.SimpleNamespace(live_repeats=2, guard={"outages": 1})) and not H.owes_guard(types.SimpleNamespace(live_repeats=1, guard={"outages": 1})),
          "ops_health's owes_guard agrees with model.guard_owed")


def words():
    rules = json.load(open(os.path.join(UTILS, "ops_watch_rules.json"), encoding="utf-8"))
    c = H.conf(rules)
    bare = dict(c, not_system=[])       # the word rule alone, with the hand list out of the way
    sys_ = lambda iid, cc=bare: H.is_system(types.SimpleNamespace(id=iid, kind="task"), cc, set())   # noqa: E731
    for iid in ("WATER_LEDGER_DOUBLE_CHARGE_1", "KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS", "HOSE_NET_SELFTEST_FIX_VACUOUS_ISOLATION",
                "HOSE_SELFTEST_FIX_TIMING_BAR_FLAKE", "TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE"):
        check(not sys_(iid), "false friend is content by the words alone: " + iid)
    for iid in ("RELENTLESS_LINE_FIX_ONE_MOD_CLOGS_ALL", "SELFTEST_CLOCK_BUILD_INJECTED_TIME", "BRIDGE_LOCK_CROSS_CLONE_RACE_1",
                "OPS_STAFFING_RESTORE_UNDER_BUDGET", "LEDGER_LEASE_HARDEN_ATTEMPT_TOKEN", "SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL",
                "REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN", "HELPER_RECEIPTS_FIX_KILL_READS_CRASH", "PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET"):
        check(sys_(iid), "system item stays system: " + iid)


if __name__ == "__main__":
    try:
        fold()
        red()
        gate()
        census()
        words()
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("selftest_repeat_guard: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
